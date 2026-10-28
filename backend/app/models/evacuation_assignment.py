import enum
from sqlalchemy import Integer, String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class AssignmentStatusEnum(str, enum.Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class EvacuationAssignment(Base, TimestampMixin):
    __tablename__ = "evacuation_assignments"
    __table_args__ = (
        CheckConstraint("assigned_population >= 0", name="chk_evac_assigned_pop_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disaster_zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shelter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shelters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evacuation_route_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("evacuation_routes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_population: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="HIGH")
    estimated_time_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=AssignmentStatusEnum.PLANNED.value
    )

    # Relationships
    disaster_zone: Mapped["DisasterZone"] = relationship("DisasterZone", back_populates="evacuation_assignments")
    shelter: Mapped["Shelter"] = relationship("Shelter", back_populates="evacuation_assignments")
    evacuation_route: Mapped["EvacuationRoute"] = relationship("EvacuationRoute", back_populates="evacuation_assignments")
