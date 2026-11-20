import json
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import UUID
from zipfile import BadZipFile, ZipFile

from fastapi import UploadFile

from app.application.config.application import Settings
from app.application.dto.profile import ProfileCvResult
from app.core.models.profile import Profile, ProfileEntity
from app.infrastructure.repositories.profile_repository import ProfileRepository


class ProfileCvError(ValueError):
    """Raised when CV processing cannot be started or completed."""


class ProfileJobApplicationsError(ValueError):
    """Raised when job applications cannot be generated from a profile."""


class ProfileService:
    def __init__(
        self,
        repository: ProfileRepository,
        settings: Settings | None = None,
    ):
        self.repository = repository
        self.settings = settings or Settings()

    @staticmethod
    def _to_entity(payload: Profile) -> ProfileEntity:
        values = payload.model_dump()
        values["skills"] = json.dumps(values["skills"], ensure_ascii=False)
        return ProfileEntity(**values)

    @staticmethod
    def _to_profile(entity: ProfileEntity) -> Profile:
        try:
            skills = json.loads(entity.skills)
        except (TypeError, json.JSONDecodeError):
            skills = [
                {"id": f"legacy-{index}", "label": label.strip()}
                for index, label in enumerate(entity.skills.split(","))
                if label.strip()
            ]

        return Profile.model_validate(
            {
                "id": entity.id,
                "lastname": entity.lastname,
                "firstname": entity.firstname,
                "skills": skills,
            }
        )

    def create(self, payload: Profile) -> Profile:
        return self._to_profile(self.repository.create(self._to_entity(payload)))

    def get_all(self) -> list[Profile]:
        return [self._to_profile(entity) for entity in self.repository.get_all()]

    def get_by_id(self, id: UUID) -> Profile | None:
        entity = self.repository.get_by_id(id)
        return self._to_profile(entity) if entity else None

    def update(self, payload: Profile) -> Profile | None:
        entity = self._to_entity(payload)
        updated_entity = self.repository.update(entity)
        return self._to_profile(updated_entity) if updated_entity else None

    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)

    async def send_cv_to_n8n(self, id: UUID, cv: UploadFile) -> Any:
        if self.repository.get_by_id(id, with_job_applications=False) is None:
            raise ProfileCvError("Profile not found")
        if not self.settings.n8n_cv_webhook_url:
            raise ProfileCvError("N8N_CV_WEBHOOK_URL is not configured")

        allowed_types = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        extension = Path(cv.filename or "").suffix.lower()
        content_type = allowed_types.get(extension)
        if content_type is None:
            raise ProfileCvError("Only PDF and DOCX CV files are supported")

        content = await cv.read(10 * 1024 * 1024 + 1)
        if len(content) > 10 * 1024 * 1024:
            raise ProfileCvError("The CV must not exceed 10 MiB")
        if extension == ".pdf" and not content.startswith(b"%PDF"):
            raise ProfileCvError("The uploaded file is not a valid PDF")
        if extension == ".docx":
            try:
                with ZipFile(BytesIO(content)) as archive:
                    names = set(archive.namelist())
            except BadZipFile as exc:
                raise ProfileCvError("The uploaded file is not a valid DOCX") from exc
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ProfileCvError("The uploaded file is not a valid DOCX")

        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.settings.n8n_cv_webhook_url,
                    data={"profile_id": str(id)},
                    files={
                        "cv": (
                            cv.filename or "cv",
                            content,
                            content_type,
                        )
                    },
                )
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError as exc:
                    raise ProfileCvError("n8n returned an invalid JSON response") from exc
        except Exception as exc:
            if isinstance(exc, ProfileCvError):
                raise
            raise ProfileCvError("Could not send the CV to n8n") from exc

    async def generate_job_applications_from_n8n(self, id: UUID) -> list[dict[str, Any]]:
        profile = self.repository.get_by_id(id, with_job_applications=False)
        if profile is None:
            raise ProfileJobApplicationsError("Profile not found")
        if not self.settings.n8n_job_applications_webhook_url:
            raise ProfileJobApplicationsError(
                "N8N_JOB_APPLICATIONS_WEBHOOK_URL is not configured"
            )

        profile_payload = self._to_profile(profile).model_dump(mode="json")
        try:
            import httpx

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.settings.n8n_job_applications_webhook_url,
                    json={"profile_id": str(id), "profile": profile_payload},
                )
                response.raise_for_status()
                raw_response = response.text.strip()
        except httpx.HTTPStatusError as exc:
            raise ProfileJobApplicationsError(
                f"n8n returned HTTP {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise ProfileJobApplicationsError(
                "Could not connect to the n8n job applications webhook"
            ) from exc
        except ValueError as exc:
            raise ProfileJobApplicationsError(
                "n8n returned an invalid JSON response"
            ) from exc
        except Exception as exc:
            raise ProfileJobApplicationsError(
                "Could not generate job applications with n8n"
            ) from exc

        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[-1]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3].rstrip()

        try:
            applications = json.loads(raw_response)
        except json.JSONDecodeError:
            try:
                applications = json.loads(
                    raw_response.replace("\\n", "\n").replace("\\r", "\r")
                )
            except json.JSONDecodeError as exc:
                raise ProfileJobApplicationsError(
                    "n8n response must contain valid JSON"
                ) from exc

        while isinstance(applications, str):
            try:
                applications = json.loads(applications)
            except json.JSONDecodeError as exc:
                raise ProfileJobApplicationsError(
                    "n8n response must contain valid JSON"
                ) from exc

        if isinstance(applications, dict):
            if "job_applications" in applications:
                applications = applications["job_applications"]
            elif "output" in applications:
                applications = applications["output"]
                if isinstance(applications, str):
                    try:
                        applications = json.loads(applications)
                    except json.JSONDecodeError as exc:
                        raise ProfileJobApplicationsError(
                            "n8n response must contain valid JSON"
                        ) from exc
            else:
                applications = None
        elif (
            isinstance(applications, list)
            and len(applications) == 1
            and isinstance(applications[0], dict)
            and "job_applications" in applications[0]
        ):
            applications = applications[0].get("job_applications")

        if (
            isinstance(applications, list)
            and len(applications) == 1
            and isinstance(applications[0], list)
        ):
            applications = applications[0]

        if not isinstance(applications, list):
            raise ProfileJobApplicationsError(
                "n8n response must contain a job_applications array"
            )
        if not all(isinstance(application, dict) for application in applications):
            raise ProfileJobApplicationsError(
                "n8n job_applications must contain objects"
            )
        return applications

    def apply_cv_result(self, id: UUID, result: ProfileCvResult) -> Profile | None:
        profile = self.repository.get_by_id(id, with_job_applications=False)
        if profile is None:
            return None

        if result.firstname is not None:
            profile.firstname = result.firstname
        if result.lastname is not None:
            profile.lastname = result.lastname
        profile.skills = json.dumps(
            [skill.model_dump() for skill in result.skills],
            ensure_ascii=False,
        )

        self.repository.session.flush()
        return self._to_profile(profile)
