import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class DisasterTypeEnum(str, enum.Enum):
    FLOOD = "FLOOD"
    CYCLONE = "CYCLONE"
    EARTHQUAKE = "EARTHQUAKE"
    URBAN_FIRE = "URBAN_FIRE"
    LANDSLIDE = "LANDSLIDE"


class DisasterStatusEnum(str, enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"


class SeverityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DisasterEvent(Base, TimestampMixin):
    __tablename__ = "disaster_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    disaster_type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=SeverityEnum.MEDIUM.value)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=DisasterStatusEnum.ACTIVE.value)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    disaster_zones: Mapped[List["DisasterZone"]] = relationship(
        "DisasterZone", back_populates="disaster_event", cascade="all, delete-orphan"
    )
    evacuation_routes: Mapped[List["EvacuationRoute"]] = relationship(
        "EvacuationRoute", back_populates="disaster_event", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="disaster_event", cascade="all, delete-orphan"
    )
