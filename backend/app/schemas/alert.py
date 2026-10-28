from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    disaster_event_id: int
    zone_id: Optional[int] = None
    alert_type: str
    severity: str = "INFO"
    title: str
    message: str
    is_acknowledged: bool = False


class AlertCreate(AlertBase):
    pass


class AlertRead(AlertBase):
    id: int
    created_at: datetime
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
