import uuid
from datetime import datetime, timezone
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import generate_secure_token, hash_token
from app.models.guest_session import GuestSession
from app.models.message import Message
from app.models.notification import Notification
from app.models.qr_identity import QRIdentity
from app.models.room import ItemRequest, RecoveryCredential, Room
from app.models.user import User
from app.schemas.contact import ContactSubmitRequest


class RoomService:
    @staticmethod
    async def get_active_qr(db: AsyncSession, public_token: str) -> QRIdentity | None:
        stmt = (
            select(QRIdentity)
            .options(selectinload(QRIdentity.user).selectinload(User.profile))
            .where(QRIdentity.public_token == public_token, QRIdentity.is_active.is_(True))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def submit_contact_request(
        db: AsyncSession,
        payload: ContactSubmitRequest,
        existing_guest_id: str | None = None,
    ) -> tuple[Room, str, str, bool]:
        """
        Creates a new temporary room or reuses an existing active room for a returning guest.
        Returns: (room, raw_recovery_token, guest_identifier, was_reused)
        """
        # 1. Verify QR token
        qr = await RoomService.get_active_qr(db, payload.public_token)
        if not qr:
            raise ValueError("QR code is inactive or invalid.")

        owner_id = qr.user_id

        # 2. Check for Smart Room Reuse if returning guest has an active room with this owner
        if existing_guest_id:
            guest_stmt = select(GuestSession).where(
                GuestSession.guest_identifier == existing_guest_id,
                GuestSession.expires_at > datetime.now(timezone.utc),
            )
            guest_res = await db.execute(guest_stmt)
            guest = guest_res.scalar_one_or_none()

            if guest:
                # Check for active or pending room with this owner
                room_stmt = (
                    select(Room)
                    .options(selectinload(Room.recovery_credential), selectinload(Room.item_request))
                    .where(
                        Room.owner_id == owner_id,
                        Room.guest_session_id == guest.id,
                        Room.status.in_(["Pending", "Active"]),
                    )
                )
                room_res = await db.execute(room_stmt)
                existing_room = room_res.scalar_one_or_none()

                if existing_room:
                    # Smart Room Reuse: Re-open existing room
                    return existing_room, "existing_session_preserved", guest.guest_identifier, True
        else:
            guest = None

        # 3. Create fresh guest session if not found or no reusable room
        if not guest:
            guest_identifier = generate_secure_token(32)
            guest = GuestSession(
                guest_identifier=guest_identifier,
                display_name=payload.finder_display_name,
            )
            db.add(guest)
            await db.flush()

        # 4. Create new Room in 'Pending' state
        room = Room(
            owner_id=owner_id,
            guest_session_id=guest.id,
            status="Pending",
        )
        db.add(room)
        await db.flush()

        # 5. Record Item Request details
        item_req = ItemRequest(
            room_id=room.id,
            item_name=payload.item_name,
            description=payload.description,
            found_location=payload.found_location,
            photograph_url=payload.photograph_url,
            initial_message=payload.initial_message,
        )
        db.add(item_req)

        # 6. Store opening message
        opening_msg = Message(
            room_id=room.id,
            sender_type="finder",
            sender_display_name=payload.finder_display_name,
            content=payload.initial_message,
            message_type="text",
        )
        db.add(opening_msg)

        # 7. Generate secret recovery link (store SHA-256 hash)
        raw_recovery_token = generate_secure_token(32)
        token_digest = hash_token(raw_recovery_token)
        rec_cred = RecoveryCredential(
            room_id=room.id,
            token_hash=token_digest,
        )
        db.add(rec_cred)

        # 8. Dispatch In-App Notification to Owner
        notif = Notification(
            owner_id=owner_id,
            room_id=room.id,
            notification_type="NEW_REQUEST",
            title=f"New Lost Item Request: {payload.item_name}",
            content=f"{payload.finder_display_name} reported finding your '{payload.item_name}'.",
        )
        db.add(notif)

        await db.commit()
        await db.refresh(room)

        return room, raw_recovery_token, guest.guest_identifier, False

    @staticmethod
    async def recover_conversation(
        db: AsyncSession,
        recovery_token: str,
    ) -> tuple[Room, GuestSession]:
        """Validates a raw recovery token by hashing it and returning the authorized room."""
        token_digest = hash_token(recovery_token)

        stmt = (
            select(RecoveryCredential)
            .options(
                selectinload(RecoveryCredential.room).selectinload(Room.item_request),
                selectinload(RecoveryCredential.room)
                .selectinload(Room.owner)
                .selectinload(User.profile),
                selectinload(RecoveryCredential.room).selectinload(Room.guest_session),
            )
            .where(
                RecoveryCredential.token_hash == token_digest,
                RecoveryCredential.revoked_at.is_(None),
                RecoveryCredential.expires_at > datetime.now(timezone.utc),
            )
        )
        result = await db.execute(stmt)
        cred = result.scalar_one_or_none()

        if not cred or not cred.room:
            raise ValueError("Recovery token is invalid, expired, or has been revoked.")

        return cred.room, cred.room.guest_session


room_service = RoomService()
