from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_owner
from app.core.database import get_db
from app.models.owner_profile import OwnerProfile
from app.models.qr_identity import QRIdentity
from app.models.user import User
from app.schemas.qr import PublicQRProfileResponse, QRRegenerateResponse
from app.services.qr_service import qr_service

router = APIRouter()


@router.get(
    "/my-code",
    summary="Get owner permanent QR code details",
)
async def get_my_qr(user: User = Depends(get_current_owner)):
    if not user.qr_identity:
        raise HTTPException(status_code=404, detail="No QR identity found for user.")

    public_token = user.qr_identity.public_token
    return {
        "public_token": public_token,
        "is_active": user.qr_identity.is_active,
        "scan_count": user.qr_identity.scan_count,
        "qr_url": qr_service.get_public_url(public_token),
        "download_url": f"/api/v1/qr/download",
    }


@router.get(
    "/download",
    summary="Download printable QR code image (PNG)",
)
async def download_qr(user: User = Depends(get_current_owner)):
    if not user.qr_identity or not user.qr_identity.is_active:
        raise HTTPException(status_code=404, detail="Active QR code not found.")

    url = qr_service.get_public_url(user.qr_identity.public_token)
    png_bytes = qr_service.generate_png_bytes(url)

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="qr_owner_{user.qr_identity.public_token[:8]}.png"',
        },
    )


@router.post(
    "/regenerate",
    response_model=QRRegenerateResponse,
    summary="Regenerate permanent QR code (revokes old token for future scans)",
)
async def regenerate_qr(
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    if not user.qr_identity:
        raise HTTPException(status_code=404, detail="QR identity not found.")

    new_token = qr_service.generate_token()
    user.qr_identity.public_token = new_token
    user.qr_identity.is_active = True
    user.qr_identity.scan_count = 0

    await db.commit()

    return QRRegenerateResponse(
        message="QR Code regenerated successfully. Previous code is now inactive.",
        new_public_token=new_token,
        qr_url=qr_service.get_public_url(new_token),
    )


@router.get(
    "/public/{public_token}",
    response_model=PublicQRProfileResponse,
    summary="Public endpoint for finders to view owner profile upon scanning",
)
async def get_public_qr_profile(
    public_token: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(QRIdentity)
        .options(selectinload(QRIdentity.user).selectinload(User.profile))
        .where(QRIdentity.public_token == public_token)
    )
    result = await db.execute(stmt)
    qr = result.scalar_one_or_none()

    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found or invalid.",
        )

    if not qr.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This QR code has been deactivated by its owner.",
        )

    # Increment scan telemetry counter
    qr.scan_count += 1
    await db.commit()

    profile = qr.user.profile if qr.user else None
    display_name = profile.display_name if profile else "Belonging Owner"
    public_bio = profile.public_bio if profile else None
    avatar = profile.profile_image_url if profile else None

    return PublicQRProfileResponse(
        public_token=qr.public_token,
        display_name=display_name,
        public_bio=public_bio,
        profile_image_url=avatar,
        is_active=qr.is_active,
    )
