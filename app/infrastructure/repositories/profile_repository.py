from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.models.profile import ProfileEntity


class ProfileRepository:
    """Persistence operations for profiles and their job applications."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, profile: ProfileEntity) -> ProfileEntity:
        self.session.add(profile)
        self.session.flush()
        return profile

    def get_by_id(
        self, profile_id: UUID, *, with_job_applications: bool = True
    ) -> ProfileEntity | None:
        statement = select(ProfileEntity).where(ProfileEntity.id == profile_id)
        if with_job_applications:
            statement = statement.options(selectinload(ProfileEntity.job_applications))
        return self.session.scalars(statement).one_or_none()

    def get_all(self, *, with_job_applications: bool = True) -> list[ProfileEntity]:
        statement = select(ProfileEntity).order_by(ProfileEntity.id)
        if with_job_applications:
            statement = statement.options(selectinload(ProfileEntity.job_applications))
        return list(self.session.scalars(statement).all())

    def update(self, profile: ProfileEntity) -> ProfileEntity | None:
        stored_profile = self.get_by_id(profile.id, with_job_applications=False)
        if stored_profile is None:
            return None

        stored_profile.lastname = profile.lastname
        stored_profile.firstname = profile.firstname
        stored_profile.skills = profile.skills
        self.session.flush()
        return stored_profile

    def delete(self, profile_id: UUID) -> bool:
        profile = self.get_by_id(profile_id, with_job_applications=False)
        if profile is None:
            return False

        self.session.delete(profile)
        self.session.flush()
        return True
