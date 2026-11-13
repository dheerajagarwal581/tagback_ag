from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.contact import (
    ContactSubmitRequest,
    ContactSubmitResponse,
    RecoveryResponse,
)
from app.services.room_service import room_service

router = APIRouter()


@router.post(
    "/submit",
    response_model=ContactSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Anonymous finder submits contact request for found belonging",
)
async def submit_contact(
    payload: ContactSubmitRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    qr_guest_session: str | None = Cookie(default=None, alias=settings.GUEST_COOKIE_NAME),
):
    try:
        room, raw_token, guest_identifier, was_reused = await room_service.submit_contact_request(
            db=db,
            payload=payload,
            existing_guest_id=qr_guest_session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # Set ephemeral guest session cookie
    response.set_cookie(
        key=settings.GUEST_COOKIE_NAME,
        value=guest_identifier,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite=settings.SAME_SITE,
        secure=settings.SECURE_COOKIES,
    )

    recovery_url = f"{settings.FRONTEND_URL}/recover/{raw_token}" if not was_reused else f"{settings.FRONTEND_URL}/chat/{room.id}"

    return ContactSubmitResponse(
        room_id=room.id,
        status=room.status,
        recovery_token=raw_token,
        recovery_url=recovery_url,
        reused_existing=was_reused,
        created_at=room.created_at,
    )


@router.get(
    "/recover/{recovery_token}",
    response_model=RecoveryResponse,
    summary="Validate secret recovery link and restore finder chat session",
)
async def recover_session(
    recovery_token: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    try:
        room, guest_session = await room_service.recover_conversation(
            db=db,
            recovery_token=recovery_token,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    # Re-issue authenticated guest session cookie
    response.set_cookie(
        key=settings.GUEST_COOKIE_NAME,
        value=guest_session.guest_identifier,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite=settings.SAME_SITE,
        secure=settings.SECURE_COOKIES,
    )

    item_name = room.item_request.item_name if room.item_request else "Lost Belonging"
    owner_name = room.owner.profile.display_name if room.owner and room.owner.profile else "Owner"

    return RecoveryResponse(
        room_id=room.id,
        status=room.status,
        item_name=item_name,
        owner_display_name=owner_name,
        redirect_url=f"/chat/{room.id}",
    )
