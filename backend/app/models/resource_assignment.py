import enum
from sqlalchemy import Integer, String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class ResourceAssignmentStatusEnum(str, enum.Enum):
    PLANNED = "PLANNED"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ResourceAssignment(Base, TimestampMixin):
    __tablename__ = "resource_assignments"
    __table_args__ = (
        CheckConstraint("assigned_quantity >= 0", name="chk_res_assigned_qty_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disaster_zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_inventory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resource_inventory.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="HIGH")
    estimated_arrival_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ResourceAssignmentStatusEnum.PLANNED.value
    )

    # Relationships
    disaster_zone: Mapped["DisasterZone"] = relationship("DisasterZone", back_populates="resource_assignments")
    resource_inventory: Mapped["ResourceInventory"] = relationship("ResourceInventory", back_populates="assignments")
