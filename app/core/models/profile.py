import uuid

from pydantic import BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.application.config.database import DatabaseModel
from app.core.models.job_application import JobApplication


class Profile(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    lastname: str
    firstname: str
    skills: str

class ProfileEntity(DatabaseModel):
    __tablename__ = "profiles"
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    lastname: Mapped[str | None] = mapped_column(nullable=True)
    firstname: Mapped[str] = mapped_column(nullable=False)
    skills: Mapped[str] = mapped_column(nullable=False)
    job_applications: Mapped[list["JobApplication"] | None] = relationship(back_populates="profile")