from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.models.job_application import JobApplicationEntity


class JobApplicationRepository:
    """Persistence operations for job applications and their profile."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, job_application: JobApplicationEntity) -> JobApplicationEntity:
        self.session.add(job_application)
        self.session.flush()
        return job_application

    def create_many(
        self, job_applications: list[JobApplicationEntity]
    ) -> list[JobApplicationEntity]:
        self.session.add_all(job_applications)
        self.session.flush()
        return job_applications

    def get_by_id(
        self, job_application_id: UUID, *, with_profile: bool = True
    ) -> JobApplicationEntity | None:
        statement = select(JobApplicationEntity).where(
            JobApplicationEntity.id == job_application_id
        )
        if with_profile:
            statement = statement.options(joinedload(JobApplicationEntity.profile))
        return self.session.scalars(statement).one_or_none()

    def get_all(
        self, *, profile_id: UUID | None = None, with_profile: bool = True
    ) -> list[JobApplicationEntity]:
        statement = select(JobApplicationEntity).order_by(JobApplicationEntity.id)
        if profile_id is not None:
            statement = statement.where(JobApplicationEntity.profile_id == profile_id)
        if with_profile:
            statement = statement.options(joinedload(JobApplicationEntity.profile))
        return list(self.session.scalars(statement).all())

    def update(self, job_application: JobApplicationEntity) -> JobApplicationEntity | None:
        stored_job_application = self.get_by_id(
            job_application.id, with_profile=False
        )
        if stored_job_application is None:
            return None

        stored_job_application.profile_id = job_application.profile_id
        stored_job_application.title = job_application.title
        stored_job_application.company_name = job_application.company_name
        stored_job_application.resume = job_application.resume
        stored_job_application.skills = job_application.skills
        stored_job_application.softskills = job_application.softskills
        stored_job_application.degree = job_application.degree
        self.session.flush()
        return stored_job_application

    def delete(self, job_application_id: UUID) -> bool:
        job_application = self.get_by_id(
            job_application_id, with_profile=False
        )
        if job_application is None:
            return False

        self.session.delete(job_application)
        self.session.flush()
        return True
