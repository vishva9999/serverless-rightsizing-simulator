import enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ResourceTypeEnum(str, enum.Enum):
    AMBULANCE = "AMBULANCE"
    RESCUE_TEAM = "RESCUE_TEAM"
    FIRE_ENGINE = "FIRE_ENGINE"
    FOOD = "FOOD"
    WATER = "WATER"
    MEDICAL_KIT = "MEDICAL_KIT"
    EMERGENCY_VEHICLE = "EMERGENCY_VEHICLE"


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    inventory_records: Mapped[List["ResourceInventory"]] = relationship(
        "ResourceInventory", back_populates="resource", cascade="all, delete-orphan"
    )
