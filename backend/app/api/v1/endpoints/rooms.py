import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_owner
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_session_token
from app.models.guest_session import GuestSession
from app.models.message import Message
from app.models.room import ItemRequest, RecoveryCredential, Room
from app.models.user import User
from app.schemas.room import ItemRequestSummary, MessageItem, RoomDetailResponse, RoomSummaryResponse
from app.websocket.connection_manager import manager

router = APIRouter()


@router.get(
    "",
    response_model=list[RoomSummaryResponse],
    summary="List owner conversation rooms filterable by status",
)
async def list_rooms(
    status: str | None = Query(default=None, description="Filter by: Pending, Active, Closed, Recovered"),
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Room)
        .options(
            selectinload(Room.item_request),
            selectinload(Room.guest_session),
        )
        .where(Room.owner_id == user.id)
        .order_by(Room.created_at.desc())
    )

    if status:
        stmt = stmt.where(Room.status == status)

    result = await db.execute(stmt)
    rooms = result.scalars().all()

    response = []
    for r in rooms:
        item_name = r.item_request.item_name if r.item_request else "Belonging"
        found_loc = r.item_request.found_location if r.item_request else None
        init_msg = r.item_request.initial_message if r.item_request else ""
        finder_name = r.guest_session.display_name if r.guest_session else "Finder"

        response.append(
            RoomSummaryResponse(
                room_id=r.id,
                status=r.status,
                item_name=item_name,
                finder_display_name=finder_name,
                found_location=found_loc,
                initial_message=init_msg,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return response


@router.get(
    "/{room_id}",
    response_model=RoomDetailResponse,
    summary="Get detailed room conversation and message history",
)
async def get_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    qr_owner_session: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
    qr_guest_session: str | None = Cookie(default=None, alias=settings.GUEST_COOKIE_NAME),
):
    stmt = (
        select(Room)
        .options(
            selectinload(Room.owner).selectinload(User.profile),
            selectinload(Room.guest_session),
            selectinload(Room.item_request),
            selectinload(Room.messages),
        )
        .where(Room.id == room_id)
    )
    result = await db.execute(stmt)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    # Authorization Check: Caller must be room owner OR room guest
    is_authorized = False
    if qr_owner_session:
        payload = decode_session_token(qr_owner_session)
        if payload and payload.get("sub") == str(room.owner_id):
            is_authorized = True

    if not is_authorized and qr_guest_session:
        if room.guest_session and room.guest_session.guest_identifier == qr_guest_session:
            is_authorized = True

    if not is_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to access this room.")

    item_req = room.item_request
    item_details = ItemRequestSummary(
        item_name=item_req.item_name if item_req else "Belonging",
        description=item_req.description if item_req else None,
        found_location=item_req.found_location if item_req else None,
        initial_message=item_req.initial_message if item_req else "",
    )

    owner_name = room.owner.profile.display_name if room.owner and room.owner.profile else "Owner"
    finder_name = room.guest_session.display_name if room.guest_session else "Finder"

    messages = [
        MessageItem(
            id=m.id,
            sender_type=m.sender_type,
            sender_display_name=m.sender_display_name,
            content=m.content,
            message_type=m.message_type,
            created_at=m.created_at,
        )
        for m in room.messages
    ]

    return RoomDetailResponse(
        room_id=room.id,
        status=room.status,
        item_details=item_details,
        owner_display_name=owner_name,
        finder_display_name=finder_name,
        messages=messages,
        created_at=room.created_at,
    )


@router.post(
    "/{room_id}/accept",
    summary="Owner accepts contact request, enabling two-way chat",
)
async def accept_room(
    room_id: uuid.UUID,
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Room).where(Room.id == room_id, Room.owner_id == user.id)
    result = await db.execute(stmt)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    if room.status != "Pending":
        raise HTTPException(status_code=400, detail=f"Cannot accept room in status '{room.status}'.")

    room.status = "Active"
    await db.commit()

    # Broadcast event via WebSocket
    await manager.broadcast_to_room(
        str(room.id),
        {"type": "ROOM_ACCEPTED", "room_id": str(room.id)},
    )

    return {"message": "Contact request accepted.", "status": "Active"}


@router.post(
    "/{room_id}/reject",
    summary="Owner rejects contact request, terminating communication",
)
async def reject_room(
    room_id: uuid.UUID,
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Room)
        .options(selectinload(Room.recovery_credential))
        .where(Room.id == room_id, Room.owner_id == user.id)
    )
    result = await db.execute(stmt)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    room.status = "Rejected"
    if room.recovery_credential:
        room.recovery_credential.revoked_at = datetime.now(timezone.utc)

    await db.commit()

    # Disconnect any connected sockets
    await manager.close_room(str(room.id), reason="Owner rejected the contact request.")

    return {"message": "Contact request rejected.", "status": "Rejected"}


@router.post(
    "/{room_id}/close",
    summary="Owner closes conversation",
)
async def close_room(
    room_id: uuid.UUID,
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Room)
        .options(selectinload(Room.recovery_credential))
        .where(Room.id == room_id, Room.owner_id == user.id)
    )
    result = await db.execute(stmt)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    room.status = "Closed"
    room.closed_at = datetime.now(timezone.utc)
    if room.recovery_credential:
        room.recovery_credential.revoked_at = datetime.now(timezone.utc)

    await db.commit()

    await manager.close_room(str(room.id), reason="Owner closed the conversation.")

    return {"message": "Conversation closed.", "status": "Closed"}


@router.post(
    "/{room_id}/recover",
    summary="Owner marks belonging as recovered, closing room and recording history",
)
async def mark_recovered(
    room_id: uuid.UUID,
    user: User = Depends(get_current_owner),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Room)
        .options(selectinload(Room.recovery_credential))
        .where(Room.id == room_id, Room.owner_id == user.id)
    )
    result = await db.execute(stmt)
    room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    room.status = "Recovered"
    room.closed_at = datetime.now(timezone.utc)
    if room.recovery_credential:
        room.recovery_credential.revoked_at = datetime.now(timezone.utc)

    await db.commit()

    await manager.close_room(str(room.id), reason="Belonging marked as safely recovered.")

    return {"message": "Belonging marked as safely recovered. Conversation closed.", "status": "Recovered"}
