import typing
import uuid

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.application.config.database import DatabaseModel

if typing.TYPE_CHECKING:
    from app.core.models.profile import ProfileEntity


class JobApplication(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    profile_id: uuid.UUID
    title: str
    company_name: str
    resume: str
    skills: str
    softskills: str
    degree: str


class JobApplicationEntity(DatabaseModel):
    __tablename__ = "job_applications"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id"), nullable=False
    )

    title: Mapped[str] = mapped_column(nullable=False)
    company_name: Mapped[str] = mapped_column(nullable=False)
    resume: Mapped[str] = mapped_column(nullable=False)
    skills: Mapped[str] = mapped_column(nullable=False)
    softskills: Mapped[str] = mapped_column(nullable=True)
    degree: Mapped[str] = mapped_column(nullable=True)
    profile: Mapped["ProfileEntity"] = relationship(back_populates="job_applications")
