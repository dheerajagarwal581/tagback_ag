import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import decode_session_token
from app.models.guest_session import GuestSession
from app.models.message import Message
from app.models.room import Room
from app.models.user import User
from app.websocket.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/room/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
    # 1. Parse room UUID
    try:
        room_uuid = uuid.UUID(room_id)
    except ValueError:
        await websocket.close(code=4400, reason="Invalid room ID format.")
        return

    # 2. Extract session cookies from handshake headers
    cookies = websocket.cookies
    owner_cookie = cookies.get(settings.SESSION_COOKIE_NAME)
    guest_cookie = cookies.get(settings.GUEST_COOKIE_NAME)

    role = None
    participant_id = None
    display_name = "User"

    async with AsyncSessionLocal() as db:
        stmt = (
            select(Room)
            .options(
                selectinload(Room.owner).selectinload(User.profile),
                selectinload(Room.guest_session),
            )
            .where(Room.id == room_uuid)
        )
        result = await db.execute(stmt)
        room = result.scalar_one_or_none()

        if not room:
            await websocket.close(code=4404, reason="Room not found.")
            return

        # Check Owner Auth
        if owner_cookie:
            payload = decode_session_token(owner_cookie)
            if payload and payload.get("sub") == str(room.owner_id):
                role = "owner"
                participant_id = str(room.owner_id)
                display_name = room.owner.profile.display_name if room.owner.profile else "Owner"

        # Check Finder Guest Auth
        if not role and guest_cookie:
            if room.guest_session and room.guest_session.guest_identifier == guest_cookie:
                role = "finder"
                participant_id = str(room.guest_session_id)
                display_name = room.guest_session.display_name

        if not role:
            # Unauthorized handshake
            await websocket.close(code=4403, reason="Not authorized for this room.")
            return

    # 3. Connect to in-memory WebSocket manager
    await manager.connect(room_id, websocket, participant_id, role)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "PING":
                await websocket.send_json({"type": "PONG"})
                continue

            if msg_type == "SEND_MESSAGE":
                content = data.get("content", "").strip()
                if not content:
                    continue

                async with AsyncSessionLocal() as db:
                    # Refresh room status
                    room_check = await db.get(Room, room_uuid)
                    if not room_check:
                        break

                    if room_check.status in ["Rejected", "Closed", "Recovered"]:
                        await websocket.send_json({
                            "type": "ERROR",
                            "code": "ROOM_TERMINATED",
                            "detail": f"Cannot send messages. Room is {room_check.status}.",
                        })
                        continue

                    # Enforce Rule: Owner cannot reply while Pending
                    if room_check.status == "Pending" and role == "owner":
                        await websocket.send_json({
                            "type": "ERROR",
                            "code": "CANNOT_REPLY_PENDING",
                            "detail": "You must accept the contact request before sending replies.",
                        })
                        continue

                    # Persist message
                    msg = Message(
                        room_id=room_uuid,
                        sender_type=role,
                        sender_display_name=display_name,
                        content=content,
                        message_type="text",
                    )
                    db.add(msg)
                    await db.commit()
                    await db.refresh(msg)

                    # Broadcast to room
                    broadcast_payload = {
                        "type": "NEW_MESSAGE",
                        "message": {
                            "id": str(msg.id),
                            "room_id": str(room_uuid),
                            "sender_type": role,
                            "sender_display_name": display_name,
                            "content": content,
                            "message_type": "text",
                            "created_at": msg.created_at.isoformat(),
                        },
                    }
                    await manager.broadcast_to_room(room_id, broadcast_payload)

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
    except Exception:
        manager.disconnect(room_id, websocket)
