from datetime import datetime, timezone
from sqlalchemy import Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ShelterCapacityHistory(Base):
    __tablename__ = "shelter_capacity_history"
    __table_args__ = (
        CheckConstraint("recorded_capacity >= 0", name="chk_hist_capacity_non_negative"),
        CheckConstraint("recorded_occupancy >= 0", name="chk_hist_occupancy_non_negative"),
        CheckConstraint("recorded_occupancy <= recorded_capacity", name="chk_hist_occupancy_within_capacity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shelter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("shelters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_occupancy: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    shelter: Mapped["Shelter"] = relationship("Shelter", back_populates="capacity_history")
