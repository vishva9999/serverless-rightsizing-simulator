from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.models.disaster_zone import DisasterZone, RiskLevelEnum
from app.schemas.disaster_zone import DisasterZoneRead, DisasterZoneCreate
from app.websocket.manager import ws_manager

router = APIRouter()


@router.get("", response_model=List[DisasterZoneRead], summary="List all monitored disaster zones")
def list_disaster_zones(
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    query = select(DisasterZone)
    if risk_level:
        query = query.where(DisasterZone.risk_level == risk_level)
    zones = db.scalars(query).all()
    return zones


@router.get("/{zone_id}", response_model=DisasterZoneRead, summary="Get single disaster zone details")
def get_disaster_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    zone = db.get(DisasterZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Disaster Zone {zone_id} not found")
    return zone


@router.post("", response_model=DisasterZoneRead, status_code=status.HTTP_201_CREATED, summary="Create a new simulated disaster zone")
async def create_disaster_zone(
    zone_in: DisasterZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    zone = DisasterZone(**zone_in.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)

    await ws_manager.broadcast({
        "event": "ZONE_CREATED",
        "zone_id": zone.id,
        "zone_code": zone.zone_code,
        "zone_name": zone.zone_name,
        "risk_level": zone.risk_level,
    })
    return zone


@router.post("/{zone_id}/pulse", response_model=DisasterZoneRead, summary="Simulate hazard perimeter pulse")
async def simulate_hazard_pulse(
    zone_id: int,
    risk_delta: float = Query(10.0, description="Hazard severity increment"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    zone = db.get(DisasterZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Disaster Zone {zone_id} not found")

    zone.risk_score = min(100.0, zone.risk_score + risk_delta)
    if zone.risk_score >= 80:
        zone.risk_level = RiskLevelEnum.CRITICAL.value
    elif zone.risk_score >= 60:
        zone.risk_level = RiskLevelEnum.HIGH.value
    elif zone.risk_score >= 35:
        zone.risk_level = RiskLevelEnum.MEDIUM.value
    else:
        zone.risk_level = RiskLevelEnum.LOW.value

    zone.road_accessibility = max(10.0, zone.road_accessibility - (risk_delta * 0.8))

    db.commit()
    db.refresh(zone)

    await ws_manager.broadcast({
        "event": "HAZARD_PULSE_SIMULATED",
        "zone_id": zone.id,
        "zone_name": zone.zone_name,
        "risk_score": zone.risk_score,
        "risk_level": zone.risk_level,
        "road_accessibility": zone.road_accessibility,
    })

    return zone
