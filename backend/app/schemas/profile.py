from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100)
    public_bio: str | None = Field(default=None, max_length=500)
    profile_image_url: str | None = None


class ProfileResponse(BaseModel):
    display_name: str
    public_bio: str | None = None
    profile_image_url: str | None = None
