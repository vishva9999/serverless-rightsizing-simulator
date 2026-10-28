from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.core.database import get_db
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.models.audit_log import AuditLog, sanitize_audit_payload
from app.schemas.audit_log import AuditLogRead, AuditLogCreate

router = APIRouter()


@router.get("", response_model=List[AuditLogRead], summary="List cryptographic audit logs")
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    query = select(AuditLog).order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    logs = db.scalars(query).all()
    return logs


@router.post("", response_model=AuditLogRead, status_code=status.HTTP_201_CREATED, summary="Record commander action in audit log")
def record_audit_log(
    log_in: AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    log = AuditLog(
        user_id=current_user.id,
        action=log_in.action,
        entity_type=log_in.entity_type,
        entity_id=log_in.entity_id,
        previous_value=sanitize_audit_payload(log_in.previous_value),
        new_value=sanitize_audit_payload(log_in.new_value),
        ip_address=log_in.ip_address or "127.0.0.1 (Simulated)",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
