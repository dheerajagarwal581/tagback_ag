import uuid
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    display_name: str | None = Field(default="Belonging Owner", max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    public_token: str

    model_config = {"from_attributes": True}


class OwnerMeResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    display_name: str
    public_token: str
    qr_url: str
    public_bio: str | None = None
    profile_image_url: str | None = None
