from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.application.services.profile_service import ProfileService
from app.core.models.profile import Profile

router = APIRouter(prefix="/profiles", tags=["profiles"])

def get_profiles(request: Request) -> list[Profile]:
    return request.app.state.profiles

def get_profiles_service(profiles: Annotated[list[Profile], Depends(get_profiles)]) -> ProfileService:
    return ProfileService(profiles)


@router.get("")
def get_all(service: Annotated[ProfileService, Depends(get_profiles_service)]):
    return service.get_all()

@router.get("/{id}")
def get_by_id(service: Annotated[ProfileService, Depends(get_profiles_service)], id: UUID):
    found = service.get_by_id(id)
    if(found):
        return found
