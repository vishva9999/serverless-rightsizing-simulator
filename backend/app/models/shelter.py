import enum
from typing import List
from sqlalchemy import Integer, String, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class ShelterStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    NEAR_CAPACITY = "NEAR_CAPACITY"
    FULL = "FULL"
    CLOSED = "CLOSED"


class ShelterAccessibilityEnum(str, enum.Enum):
    GENERAL = "GENERAL"
    WHEELCHAIR_ACCESSIBLE = "WHEELCHAIR_ACCESSIBLE"
    MEDICAL_SUPPORT = "MEDICAL_SUPPORT"


class Shelter(Base, TimestampMixin):
    __tablename__ = "shelters"
    __table_args__ = (
        CheckConstraint("total_capacity >= 0", name="chk_shelter_total_capacity_non_negative"),
        CheckConstraint("current_occupancy >= 0", name="chk_shelter_current_occupancy_non_negative"),
        CheckConstraint("current_occupancy <= total_capacity", name="chk_shelter_occupancy_within_capacity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_occupancy: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accessibility: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ShelterAccessibilityEnum.GENERAL.value
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ShelterStatusEnum.AVAILABLE.value
    )

    # Relationships
    capacity_history: Mapped[List["ShelterCapacityHistory"]] = relationship(
        "ShelterCapacityHistory", back_populates="shelter", cascade="all, delete-orphan"
    )
    evacuation_routes: Mapped[List["EvacuationRoute"]] = relationship(
        "EvacuationRoute", back_populates="destination_shelter", cascade="all, delete-orphan"
    )
    evacuation_assignments: Mapped[List["EvacuationAssignment"]] = relationship(
        "EvacuationAssignment", back_populates="shelter", cascade="all, delete-orphan"
    )
