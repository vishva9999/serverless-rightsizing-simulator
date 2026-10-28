import enum
from typing import List, Optional
from sqlalchemy import Integer, String, Float, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class RiskLevelEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvacuationPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DisasterZone(Base, TimestampMixin):
    __tablename__ = "disaster_zones"
    __table_args__ = (
        CheckConstraint("population >= 0", name="chk_zone_population_non_negative"),
        CheckConstraint("population_density >= 0", name="chk_zone_pop_density_non_negative"),
        CheckConstraint("building_density >= 0", name="chk_zone_bldg_density_non_negative"),
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="chk_zone_risk_score_range"),
        CheckConstraint("road_accessibility >= 0 AND road_accessibility <= 100", name="chk_zone_road_access_range"),
        Index("ix_disaster_zones_event_risk", "disaster_event_id", "risk_level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disaster_event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    zone_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    zone_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    population_density: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    building_density: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default=RiskLevelEnum.LOW.value)
    road_accessibility: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    evacuation_priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EvacuationPriorityEnum.LOW.value
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")

    # Relationships
    disaster_event: Mapped["DisasterEvent"] = relationship("DisasterEvent", back_populates="disaster_zones")
    risk_history: Mapped[List["ZoneRiskHistory"]] = relationship(
        "ZoneRiskHistory", back_populates="zone", cascade="all, delete-orphan"
    )
    source_evacuation_routes: Mapped[List["EvacuationRoute"]] = relationship(
        "EvacuationRoute",
        back_populates="source_zone",
        foreign_keys="[EvacuationRoute.source_zone_id]",
        cascade="all, delete-orphan",
    )
    evacuation_assignments: Mapped[List["EvacuationAssignment"]] = relationship(
        "EvacuationAssignment", back_populates="disaster_zone", cascade="all, delete-orphan"
    )
    resource_assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment", back_populates="disaster_zone", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="zone", cascade="all, delete-orphan"
    )
