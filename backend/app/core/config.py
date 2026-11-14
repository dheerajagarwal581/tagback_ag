import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    DEBUG: bool = True

    # Server endpoints (Render assigns $PORT dynamically)
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", 8000))
    BACKEND_URL: str = os.environ.get("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000")

    # Database: Auto-normalize Render's postgres:// or postgresql:// to postgresql+asyncpg://
    # Defaults to zero-setup local SQLite file for local dev; Render overrides with PostgreSQL
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./qr_dev.db",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    DB_ECHO: bool = False

    # Security & Session management
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_secret_key_change_in_production_32bytes")
    SESSION_COOKIE_NAME: str = "qr_owner_session"
    GUEST_COOKIE_NAME: str = "qr_guest_session"
    SESSION_MAX_AGE_SECONDS: int = 604800  # 7 days
    SECURE_COOKIES: bool = os.environ.get("SECURE_COOKIES", "false").lower() in ("true", "1") or os.environ.get("APP_ENV") == "production" or "RENDER" in os.environ
    SAME_SITE: str = os.environ.get("SAME_SITE", "lax")

    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        else:
            origins = list(self.ALLOWED_ORIGINS)

        # Include FRONTEND_URL if set and not in origins
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins

    # Rate limiting
    RATE_LIMIT_CONTACT_PER_MINUTE: int = 5
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = 30


settings = Settings()
