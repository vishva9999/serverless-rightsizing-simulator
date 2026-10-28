from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class TimestampMixin:
    """Provides automatic created_at and updated_at UTC timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SystemMetadata(Base, TimestampMixin):
    """Initial core table from Phase 1 for tracking system mode and simulation status."""
    __tablename__ = "system_metadata"

    key: Mapped[str] = mapped_column(primary_key=True, index=True)
    value: Mapped[str] = mapped_column(nullable=False)
