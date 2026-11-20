from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.config.database import open_new_session
from app.application.services.job_application_service import JobApplicationService
from app.core.models.job_application import JobApplication
from app.infrastructure.repositories.job_application_repository import (
    JobApplicationRepository,
)

router = APIRouter(prefix="/job-applications", tags=["job-applications"])


def get_job_application_repository(
    session: Annotated[Session, Depends(open_new_session)],
) -> JobApplicationRepository:
    return JobApplicationRepository(session)


def get_job_application_service(
    repository: Annotated[
        JobApplicationRepository, Depends(get_job_application_repository)
    ],
) -> JobApplicationService:
    return JobApplicationService(repository)

@router.post("", status_code=status.HTTP_201_CREATED)
def post(
    service: Annotated[JobApplicationService, Depends(get_job_application_service)],
    payload: JobApplication,
):
    return service.create(payload)

@router.get("")
def get_all(
    service: Annotated[JobApplicationService, Depends(get_job_application_service)],
    profile_id: UUID | None = None,
):
    return service.get_all(profile_id=profile_id)

@router.get("/{id}")
def get_by_id(
    service: Annotated[JobApplicationService, Depends(get_job_application_service)], id: UUID
):
    found = service.get_by_id(id)
    if found is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")
    return found


@router.put("/{id}")
def update(
    id: UUID,
    payload: JobApplication,
    service: Annotated[JobApplicationService, Depends(get_job_application_service)],
):
    updated = service.update(payload.model_copy(update={"id": id}))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    id: UUID,
    service: Annotated[JobApplicationService, Depends(get_job_application_service)],
) -> None:
    if not service.delete(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found")
