from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.audit_log import sanitize_audit_payload


class AuditLogBase(BaseModel):
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    previous_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None

    @field_validator("previous_value", "new_value", mode="after")
    @classmethod
    def sanitize_values(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return sanitize_audit_payload(v)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
