from datetime import datetime, timezone
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ZoneRiskHistory(Base):
    __tablename__ = "zone_risk_history"
    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="chk_hist_risk_score_range"),
        CheckConstraint("road_accessibility >= 0 AND road_accessibility <= 100", name="chk_hist_road_access_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    rainfall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    water_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    road_accessibility: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    zone: Mapped["DisasterZone"] = relationship("DisasterZone", back_populates="risk_history")
