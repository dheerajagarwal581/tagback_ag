from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_owner
from app.core.database import get_db
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter()


@router.get(
    "/",
    response_model=ProfileResponse,
    summary="Get owner profile",
)
async def get_profile(user: User = Depends(get_current_owner)):
    profile = user.profile
    return ProfileResponse(
        display_name=profile.display_name if profile else "Belonging Owner",
        public_bio=profile.public_bio if profile else None,
        profile_image_url=profile.profile_image_url if profile else None,
    )


@router.put(
    "/",
    response_model=ProfileResponse,
    summary="Update owner profile",
)
async def update_profile(
    payload: ProfileUpdateRequest,
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    profile = user.profile
    if profile:
        profile.display_name = payload.display_name
        profile.public_bio = payload.public_bio
        if payload.profile_image_url is not None:
            profile.profile_image_url = payload.profile_image_url
        await db.commit()
        await db.refresh(profile)

    return ProfileResponse(
        display_name=profile.display_name if profile else payload.display_name,
        public_bio=profile.public_bio if profile else payload.public_bio,
        profile_image_url=profile.profile_image_url if profile else None,
    )
