from uuid import UUID

from app.core.models.job_application import JobApplication


class JobApplicationService:
    def __init__(self, job_applications: list[JobApplication]):
        self.job_applications = job_applications

    def create(self, payload: JobApplication):
        job: list[JobApplication] = self.job_applications
        job.append(payload)
        return job

    def get_all(self) -> list[JobApplication]:
        return self.job_applications

    def get_by_id(self, id: UUID) -> JobApplication:
        return next((job_application for job_application in self.job_applications if job_application.id == id), None)