import enum
from typing import Optional
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class VehicleTypeEnum(str, enum.Enum):
    AMBULANCE = "AMBULANCE"
    RESCUE_VAN = "RESCUE_VAN"
    FIRE_ENGINE = "FIRE_ENGINE"
    SUPPLY_TRUCK = "SUPPLY_TRUCK"
    EMERGENCY_VEHICLE = "EMERGENCY_VEHICLE"


class VehicleStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
    BUSY = "BUSY"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    current_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=VehicleStatusEnum.AVAILABLE.value
    )
    rescue_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("rescue_teams.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    rescue_team: Mapped[Optional["RescueTeam"]] = relationship("RescueTeam", back_populates="vehicles")
