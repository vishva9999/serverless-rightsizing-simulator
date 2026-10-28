import enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Integer, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    DISASTER_OPERATOR = "DISASTER_OPERATOR"
    FIELD_OFFICER = "FIELD_OFFICER"
    SHELTER_MANAGER = "SHELTER_MANAGER"
    RESOURCE_MANAGER = "RESOURCE_MANAGER"
    VIEWER = "VIEWER"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
