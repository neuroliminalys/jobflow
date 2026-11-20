from uuid import UUID

from app.core.models.job_application import JobApplication, JobApplicationEntity
from app.infrastructure.repositories.job_application_repository import (
    JobApplicationRepository,
)


class JobApplicationService:
    def __init__(self, repository: JobApplicationRepository):
        self.repository = repository

    def create(self, payload: JobApplication) -> JobApplication:
        entity = JobApplicationEntity(**payload.model_dump())
        return JobApplication.model_validate(self.repository.create(entity))

    def create_many(self, payloads: list[JobApplication]) -> list[JobApplication]:
        entities = [JobApplicationEntity(**payload.model_dump()) for payload in payloads]
        created_entities = self.repository.create_many(entities)
        return [JobApplication.model_validate(entity) for entity in created_entities]

    def get_all(self, profile_id: UUID | None = None) -> list[JobApplication]:
        return [
            JobApplication.model_validate(entity)
            for entity in self.repository.get_all(profile_id=profile_id)
        ]

    def get_by_id(self, id: UUID) -> JobApplication | None:
        entity = self.repository.get_by_id(id)
        return JobApplication.model_validate(entity) if entity else None

    def update(self, payload: JobApplication) -> JobApplication | None:
        entity = JobApplicationEntity(**payload.model_dump())
        updated_entity = self.repository.update(entity)
        return JobApplication.model_validate(updated_entity) if updated_entity else None

    def delete(self, id: UUID) -> bool:
        return self.repository.delete(id)
