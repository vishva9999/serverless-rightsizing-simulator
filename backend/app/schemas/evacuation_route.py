from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EvacuationRouteBase(BaseModel):
    disaster_event_id: int
    source_zone_id: int
    destination_shelter_id: int
    distance_km: float = Field(ge=0.0)
    estimated_time_minutes: float = Field(ge=0.0)
    safety_score: float = Field(default=100.0, ge=0.0, le=100.0)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    congestion_score: float = Field(default=0.0, ge=0.0, le=100.0)
    route_status: str = "SAFE"


class EvacuationRouteCreate(EvacuationRouteBase):
    pass


class EvacuationRouteRead(EvacuationRouteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
