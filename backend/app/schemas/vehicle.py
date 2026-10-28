from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.rescue_team import RescueTeamRead


class VehicleBase(BaseModel):
    vehicle_code: str
    vehicle_type: str
    capacity: int = Field(default=1, ge=1)
    current_latitude: float
    current_longitude: float
    status: str = "AVAILABLE"
    rescue_team_id: Optional[int] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleRead(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    rescue_team: Optional[RescueTeamRead] = None

    model_config = ConfigDict(from_attributes=True)
