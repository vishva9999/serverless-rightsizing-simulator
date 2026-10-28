from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ZoneRiskHistoryBase(BaseModel):
    zone_id: int
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: str
    rainfall: float = Field(default=0.0, ge=0.0)
    water_level: float = Field(default=0.0, ge=0.0)
    wind_speed: float = Field(default=0.0, ge=0.0)
    road_accessibility: float = Field(default=100.0, ge=0.0, le=100.0)


class ZoneRiskHistoryCreate(ZoneRiskHistoryBase):
    pass


class ZoneRiskHistoryRead(ZoneRiskHistoryBase):
    id: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
