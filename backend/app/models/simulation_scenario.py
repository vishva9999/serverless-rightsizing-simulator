import enum
from typing import List, Optional, Any, Dict
from sqlalchemy import Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class ScenarioStatusEnum(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SimulationScenario(Base, TimestampMixin):
    __tablename__ = "simulation_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    disaster_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    random_seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parameters_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ScenarioStatusEnum.CREATED.value
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Relationships
    creator: Mapped["User"] = relationship("User", back_populates="simulation_scenarios")
    results: Mapped[List["SimulationResult"]] = relationship(
        "SimulationResult", back_populates="scenario", cascade="all, delete-orphan"
    )
