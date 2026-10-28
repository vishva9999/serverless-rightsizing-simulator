from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ResourceBase(BaseModel):
    resource_code: str
    name: str
    resource_type: str
    description: Optional[str] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceRead(ResourceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceInventoryBase(BaseModel):
    resource_id: int
    location_name: str
    latitude: float
    longitude: float
    total_quantity: int = Field(ge=0)
    available_quantity: int = Field(default=0, ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    status: str = "AVAILABLE"

    @model_validator(mode="after")
    def validate_quantities(self) -> "ResourceInventoryBase":
        if self.available_quantity + self.reserved_quantity > self.total_quantity:
            raise ValueError("available_quantity + reserved_quantity cannot exceed total_quantity")
        return self


class ResourceInventoryCreate(ResourceInventoryBase):
    pass


class ResourceInventoryRead(ResourceInventoryBase):
    id: int
    updated_at: datetime
    resource: Optional[ResourceRead] = None

    model_config = ConfigDict(from_attributes=True)
