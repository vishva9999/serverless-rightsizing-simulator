from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


SENSITIVE_AUDIT_KEYS = {
    "password",
    "password_hash",
    "token",
    "jwt",
    "access_token",
    "refresh_token",
    "secret",
    "secret_key",
}


def sanitize_audit_payload(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively redacts sensitive authentication keys from audit records."""
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return {"value": "[REDACTED]"} if any(k in str(payload).lower() for k in SENSITIVE_AUDIT_KEYS) else payload

    sanitized = {}
    for k, v in payload.items():
        if any(sensitive in k.lower() for sensitive in SENSITIVE_AUDIT_KEYS):
            sanitized[k] = "[REDACTED_SECURITY_DATA]"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_audit_payload(v)
        elif isinstance(v, list):
            sanitized[k] = [
                sanitize_audit_payload(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            sanitized[k] = v
    return sanitized


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    previous_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_value: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
