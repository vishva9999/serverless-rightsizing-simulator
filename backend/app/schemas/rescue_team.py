from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class RescueTeamBase(BaseModel):
    team_code: str
    team_name: str
    team_size: int = Field(default=1, ge=0)
    specialization: str
    current_latitude: float
    current_longitude: float
    status: str = "AVAILABLE"


class RescueTeamCreate(RescueTeamBase):
    pass


class RescueTeamRead(RescueTeamBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
