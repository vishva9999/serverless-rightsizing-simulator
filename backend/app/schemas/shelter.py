from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ShelterBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    total_capacity: int = Field(ge=0)
    current_occupancy: int = Field(default=0, ge=0)
    accessibility: str = "GENERAL"
    status: str = "AVAILABLE"

    @model_validator(mode="after")
    def check_occupancy_within_capacity(self) -> "ShelterBase":
        if self.current_occupancy > self.total_capacity:
            raise ValueError("current_occupancy cannot exceed total_capacity")
        return self


class ShelterCreate(ShelterBase):
    pass


class ShelterUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_capacity: Optional[int] = Field(default=None, ge=0)
    current_occupancy: Optional[int] = Field(default=None, ge=0)
    accessibility: Optional[str] = None
    status: Optional[str] = None


class ShelterCapacityHistoryRead(BaseModel):
    id: int
    shelter_id: int
    recorded_capacity: int
    recorded_occupancy: int
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShelterRead(ShelterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
