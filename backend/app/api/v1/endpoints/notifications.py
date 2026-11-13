import uuid
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_owner
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.room import NotificationResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[NotificationResponse],
    summary="Get owner notifications",
)
async def get_notifications(
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Notification)
        .where(Notification.owner_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    notifs = result.scalars().all()

    return [
        NotificationResponse(
            id=n.id,
            room_id=n.room_id,
            notification_type=n.notification_type,
            title=n.title,
            content=n.content,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifs
    ]


@router.put(
    "/{notification_id}/read",
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.owner_id == user.id,
    )
    result = await db.execute(stmt)
    notif = result.scalar_one_or_none()

    if notif:
        notif.is_read = True
        await db.commit()

    return {"message": "Notification marked as read."}
