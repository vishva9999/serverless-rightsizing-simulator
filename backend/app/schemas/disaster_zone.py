from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DisasterZoneBase(BaseModel):
    disaster_event_id: int
    zone_code: str
    zone_name: str
    latitude: float
    longitude: float
    population: int = Field(ge=0)
    population_density: float = Field(ge=0.0)
    building_density: float = Field(ge=0.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: str
    road_accessibility: float = Field(ge=0.0, le=100.0)
    evacuation_priority: str
    status: str = "ACTIVE"


class DisasterZoneCreate(DisasterZoneBase):
    pass


class DisasterZoneRead(DisasterZoneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
