import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OwnerProfile(Base):
    __tablename__ = "owner_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(100), default="Belonging Owner", nullable=False)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    public_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Store JSON settings (compatible across PostgreSQL JSONB and SQLite JSON)
    visibility_settings = mapped_column(JSONB().with_variant(Text, "sqlite"), nullable=False, default='{"show_bio": true, "show_avatar": true}')
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="profile")
