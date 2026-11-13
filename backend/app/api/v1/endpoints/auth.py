from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_owner
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_session_token, hash_password, verify_password
from app.models.owner_profile import OwnerProfile
from app.models.qr_identity import QRIdentity
from app.models.user import User
from app.schemas.auth import OwnerMeResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.qr_service import qr_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new owner account",
)
async def register(
    payload: UserRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    # Check if email is already registered
    stmt = select(User).where(User.email == payload.email)
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # 1. Create User
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.flush()  # Generate user.id

    # 2. Create Owner Profile
    display_name = payload.display_name or payload.email.split("@")[0]
    profile = OwnerProfile(
        user_id=user.id,
        display_name=display_name,
    )
    db.add(profile)

    # 3. Create Permanent QR Identity
    public_token = qr_service.generate_token()
    qr_identity = QRIdentity(
        user_id=user.id,
        public_token=public_token,
        is_active=True,
    )
    db.add(qr_identity)

    await db.commit()
    await db.refresh(user)

    # Set session cookie
    token = create_session_token({"sub": str(user.id), "email": user.email})
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite=settings.SAME_SITE,
        secure=settings.SECURE_COOKIES,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=profile.display_name,
        public_token=qr_identity.public_token,
    )


@router.post(
    "/login",
    response_model=UserResponse,
    summary="Owner login",
)
async def login(
    payload: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(User)
        .options(selectinload(User.profile), selectinload(User.qr_identity))
        .where(User.email == payload.email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    # Set session cookie
    token = create_session_token({"sub": str(user.id), "email": user.email})
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite=settings.SAME_SITE,
        secure=settings.SECURE_COOKIES,
    )

    display_name = user.profile.display_name if user.profile else user.email.split("@")[0]
    public_token = user.qr_identity.public_token if user.qr_identity else ""

    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=display_name,
        public_token=public_token,
    )


@router.post(
    "/logout",
    summary="Owner logout",
)
async def logout(response: Response):
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        httponly=True,
        samesite=settings.SAME_SITE,
        secure=settings.SECURE_COOKIES,
    )
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=OwnerMeResponse,
    summary="Get current authenticated owner details",
)
async def get_me(user: User = Depends(get_current_owner)):
    display_name = user.profile.display_name if user.profile else user.email.split("@")[0]
    public_token = user.qr_identity.public_token if user.qr_identity else ""
    bio = user.profile.public_bio if user.profile else None
    avatar = user.profile.profile_image_url if user.profile else None

    return OwnerMeResponse(
        user_id=user.id,
        email=user.email,
        display_name=display_name,
        public_token=public_token,
        qr_url=qr_service.get_public_url(public_token),
        public_bio=bio,
        profile_image_url=avatar,
    )
