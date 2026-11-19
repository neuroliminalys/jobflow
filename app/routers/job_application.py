from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.application.services.job_application_service import JobApplicationService
from app.core.models.job_application import JobApplication

router = APIRouter(prefix="/job-applications", tags=["job-applications"])


def get_job_applications(request: Request) -> list[JobApplication]:
    return request.app.state.job_applications


def get_job_application_service(
    job_applications: Annotated[list[JobApplication], Depends(get_job_applications)],
) -> JobApplicationService:
    return JobApplicationService(job_applications)

@router.post("")
def post(service: Annotated[JobApplicationService, Depends(get_job_application_service)], payload: JobApplication):
    return service.create(payload)

@router.get("")
def get_all(service: Annotated[JobApplicationService, Depends(get_job_application_service)]):
    return service.get_all()

@router.get("/{id}")
def get_by_id(
    service: Annotated[JobApplicationService, Depends(get_job_application_service)], id: UUID
):
    found = service.get_by_id(id)
    if found:
        return found
