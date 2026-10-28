from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EvacuationAssignmentBase(BaseModel):
    disaster_zone_id: int
    shelter_id: int
    evacuation_route_id: int
    assigned_population: int = Field(ge=0)
    priority: str = "HIGH"
    estimated_time_minutes: float = Field(default=0.0, ge=0.0)
    status: str = "PLANNED"


class EvacuationAssignmentCreate(EvacuationAssignmentBase):
    pass


class EvacuationAssignmentRead(EvacuationAssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceAssignmentBase(BaseModel):
    disaster_zone_id: int
    resource_inventory_id: int
    assigned_quantity: int = Field(ge=0)
    priority: str = "HIGH"
    estimated_arrival_minutes: float = Field(default=0.0, ge=0.0)
    status: str = "PLANNED"


class ResourceAssignmentCreate(ResourceAssignmentBase):
    pass


class ResourceAssignmentRead(ResourceAssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
