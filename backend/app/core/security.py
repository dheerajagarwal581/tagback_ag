import hashlib
import secrets
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session serializer
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token(data: dict) -> str:
    """Creates a signed, tamper-evident session token."""
    return serializer.dumps(data)


def decode_session_token(token: str, max_age: int = settings.SESSION_MAX_AGE_SECONDS) -> dict | None:
    """Validates and decodes a signed session token. Returns payload or None if expired/tampered."""
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None


def generate_secure_token(nbytes: int = 32) -> str:
    """Generates a cryptographically secure URL-safe random string."""
    return secrets.token_urlsafe(nbytes)


def hash_token(token: str) -> str:
    """Computes a SHA-256 hex digest for storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
