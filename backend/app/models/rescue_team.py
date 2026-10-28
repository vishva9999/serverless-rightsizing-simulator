import enum
from typing import List
from sqlalchemy import Integer, String, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class TeamStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class RescueTeam(Base, TimestampMixin):
    __tablename__ = "rescue_teams"
    __table_args__ = (
        CheckConstraint("team_size >= 0", name="chk_team_size_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    team_name: Mapped[str] = mapped_column(String(100), nullable=False)
    team_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    current_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    current_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=TeamStatusEnum.AVAILABLE.value
    )

    # Relationships
    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="rescue_team")
