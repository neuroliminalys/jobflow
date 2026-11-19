from uuid import UUID

from app.core.models.profile import Profile


class ProfileService:
    def __init__(self, profiles: list[Profile]):
        self.profiles = profiles

    def get_all(self) -> list[Profile]:
        return self.profiles

    def get_by_id(self, id: UUID) -> Profile | None:
        return next((profile for profile in self.profiles if profile.id == id), None)
