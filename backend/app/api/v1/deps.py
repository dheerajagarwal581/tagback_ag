import uuid
from fastapi import Cookie, Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_session_token
from app.models.user import User


async def get_current_owner(
    db: AsyncSession = Depends(get_db),
    qr_owner_session: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
    authorization: str | None = Header(default=None),
) -> User:
    token = qr_owner_session

    # Support optional Bearer token header for API testing
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_session_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again.",
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session format.",
        )

    stmt = (
        select(User)
        .options(selectinload(User.profile), selectinload(User.qr_identity))
        .where(User.id == user_id, User.is_active.is_(True))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated.",
        )

    return user
