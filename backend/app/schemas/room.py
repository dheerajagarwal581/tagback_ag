import uuid
from datetime import datetime
from pydantic import BaseModel


class ItemRequestSummary(BaseModel):
    item_name: str
    description: str | None = None
    found_location: str | None = None
    initial_message: str


class RoomSummaryResponse(BaseModel):
    room_id: uuid.UUID
    status: str
    item_name: str
    finder_display_name: str
    found_location: str | None = None
    initial_message: str
    created_at: datetime
    updated_at: datetime


class MessageItem(BaseModel):
    id: uuid.UUID
    sender_type: str
    sender_display_name: str
    content: str
    message_type: str
    created_at: datetime


class RoomDetailResponse(BaseModel):
    room_id: uuid.UUID
    status: str
    item_details: ItemRequestSummary
    owner_display_name: str
    finder_display_name: str
    messages: list[MessageItem]
    created_at: datetime


class NotificationResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    notification_type: str
    title: str
    content: str
    is_read: bool
    created_at: datetime
