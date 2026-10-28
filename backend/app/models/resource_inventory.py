import enum
from datetime import datetime, timezone
from typing import List
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class InventoryStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    LIMITED = "LIMITED"
    DEPLETED = "DEPLETED"
    UNAVAILABLE = "UNAVAILABLE"


class ResourceInventory(Base):
    __tablename__ = "resource_inventory"
    __table_args__ = (
        CheckConstraint("total_quantity >= 0", name="chk_inv_total_non_negative"),
        CheckConstraint("available_quantity >= 0", name="chk_inv_available_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="chk_inv_reserved_non_negative"),
        CheckConstraint(
            "available_quantity + reserved_quantity <= total_quantity",
            name="chk_inv_allocation_balance",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resource_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=InventoryStatusEnum.AVAILABLE.value
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    resource: Mapped["Resource"] = relationship("Resource", back_populates="inventory_records")
    assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment", back_populates="resource_inventory", cascade="all, delete-orphan"
    )
