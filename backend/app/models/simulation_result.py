from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("simulation_scenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    affected_population: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    population_at_risk: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_evacuation_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    resource_shortage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shelter_utilization: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    result_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    scenario: Mapped["SimulationScenario"] = relationship("SimulationScenario", back_populates="results")
