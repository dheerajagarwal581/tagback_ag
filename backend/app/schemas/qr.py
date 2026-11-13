from pydantic import BaseModel


class PublicQRProfileResponse(BaseModel):
    public_token: str
    display_name: str
    public_bio: str | None = None
    profile_image_url: str | None = None
    is_active: bool


class QRRegenerateResponse(BaseModel):
    message: str
    new_public_token: str
    qr_url: str
