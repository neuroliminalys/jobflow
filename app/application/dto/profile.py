from pydantic import BaseModel, Field


class ProfileSkill(BaseModel):
    id: str
    label: str


class ProfileCvResult(BaseModel):
    """Validated profile data returned by the CV-processing workflow."""

    firstname: str | None = None
    lastname: str | None = None
    skills: list[ProfileSkill] = Field(default_factory=list)
