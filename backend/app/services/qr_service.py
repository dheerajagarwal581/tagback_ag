import io
import qrcode
from qrcode.image.pil import PilImage

from app.core.config import settings
from app.core.security import generate_secure_token


class QRService:
    @staticmethod
    def generate_token() -> str:
        """Generates a high-entropy public token for the permanent QR code."""
        return generate_secure_token(24)

    @staticmethod
    def get_public_url(public_token: str) -> str:
        """Constructs the canonical URL encoded in the QR code."""
        return f"{settings.FRONTEND_URL}/q/{public_token}"

    @staticmethod
    def generate_png_bytes(url: str) -> bytes:
        """Generates a PNG image byte buffer for the provided URL."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img: PilImage = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()


qr_service = QRService()
