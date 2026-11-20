from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.application.config.database import open_new_session
from app.application.config.application import Settings
from app.application.dto.profile import ProfileCvResult
from app.application.services.profile_service import (
    ProfileCvError,
    ProfileJobApplicationsError,
    ProfileService,
)
from app.core.models.profile import Profile
from app.core.models.job_application import JobApplication
from app.application.services.job_application_service import JobApplicationService
from app.infrastructure.repositories.job_application_repository import (
    JobApplicationRepository,
)
from app.infrastructure.repositories.profile_repository import ProfileRepository

router = APIRouter(prefix="/profiles", tags=["profiles"])

def get_profile_repository(
    session: Annotated[Session, Depends(open_new_session)],
) -> ProfileRepository:
    return ProfileRepository(session)


def get_profiles_service(
    repository: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> ProfileService:
    settings = Settings()
    return ProfileService(repository, settings=settings)


def get_job_application_service(
    session: Annotated[Session, Depends(open_new_session)],
) -> JobApplicationService:
    return JobApplicationService(JobApplicationRepository(session))


@router.post("", status_code=status.HTTP_201_CREATED)
def post(
    payload: Profile,
    service: Annotated[ProfileService, Depends(get_profiles_service)],
):
    return service.create(payload)


@router.get("")
def get_all(service: Annotated[ProfileService, Depends(get_profiles_service)]):
    return service.get_all()

@router.get("/{id}")
def get_by_id(service: Annotated[ProfileService, Depends(get_profiles_service)], id: UUID):
    found = service.get_by_id(id)
    if found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return found


@router.post("/{id}/cv", status_code=status.HTTP_200_OK)
async def upload_cv(
    id: UUID,
    cv: Annotated[
        UploadFile,
        File(description="PDF or DOCX CV file to send to n8n"),
    ],
    service: Annotated[ProfileService, Depends(get_profiles_service)],
):
    try:
        result = await service.send_cv_to_n8n(id, cv)
    except ProfileCvError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "Profile not found"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return result


@router.post("/{id}/job-applications", status_code=status.HTTP_201_CREATED)
async def generate_job_applications(
    id: UUID,
    service: Annotated[ProfileService, Depends(get_profiles_service)],
    job_application_service: Annotated[
        JobApplicationService, Depends(get_job_application_service)
    ],
):
    try:
        generated = await service.generate_job_applications_from_n8n(id)
        applications = [
            JobApplication.model_validate({**application, "profile_id": id})
            for application in generated
        ]
        return job_application_service.create_many(applications)
    except ProfileJobApplicationsError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "Profile not found"
            else status.HTTP_502_BAD_GATEWAY
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="n8n returned invalid job application data",
        ) from exc


@router.post("/{id}/cv-result")
def apply_cv_result(
    id: UUID,
    result: ProfileCvResult,
    service: Annotated[ProfileService, Depends(get_profiles_service)],
):
    updated_profile = service.apply_cv_result(id, result)
    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return updated_profile


@router.put("/{id}")
def update(
    id: UUID,
    payload: Profile,
    service: Annotated[ProfileService, Depends(get_profiles_service)],
):
    updated = service.update(payload.model_copy(update={"id": id}))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    id: UUID,
    service: Annotated[ProfileService, Depends(get_profiles_service)],
) -> None:
    if not service.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
