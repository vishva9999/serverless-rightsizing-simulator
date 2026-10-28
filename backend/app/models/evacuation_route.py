import enum
from typing import List
from sqlalchemy import Integer, String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class RouteStatusEnum(str, enum.Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    BLOCKED = "BLOCKED"


class EvacuationRoute(Base, TimestampMixin):
    __tablename__ = "evacuation_routes"
    __table_args__ = (
        CheckConstraint("distance_km >= 0", name="chk_route_distance_non_negative"),
        CheckConstraint("estimated_time_minutes >= 0", name="chk_route_time_non_negative"),
        CheckConstraint("safety_score >= 0 AND safety_score <= 100", name="chk_route_safety_score_range"),
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="chk_route_risk_score_range"),
        CheckConstraint("congestion_score >= 0 AND congestion_score <= 100", name="chk_route_congestion_score_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disaster_event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    destination_shelter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shelters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_time_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    safety_score: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    congestion_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    route_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=RouteStatusEnum.SAFE.value
    )

    # Relationships
    disaster_event: Mapped["DisasterEvent"] = relationship("DisasterEvent", back_populates="evacuation_routes")
    source_zone: Mapped["DisasterZone"] = relationship(
        "DisasterZone", back_populates="source_evacuation_routes", foreign_keys=[source_zone_id]
    )
    destination_shelter: Mapped["Shelter"] = relationship("Shelter", back_populates="evacuation_routes")
    evacuation_assignments: Mapped[List["EvacuationAssignment"]] = relationship(
        "EvacuationAssignment", back_populates="evacuation_route", cascade="all, delete-orphan"
    )
