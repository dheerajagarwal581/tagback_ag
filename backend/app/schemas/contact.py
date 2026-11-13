import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ContactSubmitRequest(BaseModel):
    public_token: str = Field(..., description="Unguessable token from owner's QR code")
    item_name: str = Field(..., min_length=1, max_length=150)
    finder_display_name: str = Field(..., min_length=1, max_length=100)
    initial_message: str = Field(..., min_length=1, max_length=2000)
    description: str | None = Field(default=None, max_length=1000)
    found_location: str | None = Field(default=None, max_length=255)
    photograph_url: str | None = None


class ContactSubmitResponse(BaseModel):
    room_id: uuid.UUID
    status: str
    recovery_token: str
    recovery_url: str
    reused_existing: bool = False
    created_at: datetime


class RecoveryResponse(BaseModel):
    room_id: uuid.UUID
    status: str
    item_name: str
    owner_display_name: str
    redirect_url: str
