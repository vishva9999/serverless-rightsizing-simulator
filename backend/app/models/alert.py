import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class AlertSeverityEnum(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disaster_event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    zone_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("disaster_zones.id", ondelete="SET NULL"), nullable=True, index=True
    )
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default=AlertSeverityEnum.INFO.value
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    disaster_event: Mapped["DisasterEvent"] = relationship("DisasterEvent", back_populates="alerts")
    zone: Mapped[Optional["DisasterZone"]] = relationship("DisasterZone", back_populates="alerts")
