import uuid

from pydantic import BaseModel, Field


class JobApplication(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    profile_id: uuid.UUID
    title: str
    company_name: str
    resume: str
    skills: str
    softskills: str
    degree: str