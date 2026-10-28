from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class DisasterEventBase(BaseModel):
    name: str
    disaster_type: str
    description: Optional[str] = None
    severity: str = "MEDIUM"
    status: str = "ACTIVE"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DisasterEventCreate(DisasterEventBase):
    pass


class DisasterEventRead(DisasterEventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
