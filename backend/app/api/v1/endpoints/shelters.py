from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.models.shelter import Shelter, ShelterStatusEnum
from app.schemas.shelter import ShelterRead, ShelterUpdate
from app.websocket.manager import ws_manager

router = APIRouter()


@router.get("", response_model=List[ShelterRead], summary="List all emergency evacuation shelters")
def list_shelters(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    query = select(Shelter)
    if status_filter:
        query = query.where(Shelter.status == status_filter)
    shelters = db.scalars(query).all()
    return shelters


@router.get("/{shelter_id}", response_model=ShelterRead, summary="Get single shelter details")
def get_shelter(
    shelter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail=f"Shelter {shelter_id} not found")
    return shelter


@router.patch("/{shelter_id}", response_model=ShelterRead, summary="Update shelter capacity or status")
async def update_shelter(
    shelter_id: int,
    shelter_in: ShelterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail=f"Shelter {shelter_id} not found")

    update_data = shelter_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(shelter, field, val)

    # Recalculate status based on occupancy
    if shelter.total_capacity > 0:
        ratio = shelter.current_occupancy / shelter.total_capacity
        if ratio >= 1.0:
            shelter.status = ShelterStatusEnum.FULL.value
        elif ratio >= 0.8:
            shelter.status = ShelterStatusEnum.NEAR_CAPACITY.value
        elif shelter.status != ShelterStatusEnum.CLOSED.value:
            shelter.status = ShelterStatusEnum.AVAILABLE.value

    db.commit()
    db.refresh(shelter)

    # Broadcast event to connected HUDs
    await ws_manager.broadcast({
        "event": "SHELTER_UPDATED",
        "shelter_id": shelter.id,
        "name": shelter.name,
        "occupancy": shelter.current_occupancy,
        "capacity": shelter.total_capacity,
        "status": shelter.status,
    })

    return shelter


@router.post("/{shelter_id}/toggle-intake", response_model=ShelterRead, summary="Toggle intake status")
async def toggle_shelter_intake(
    shelter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    shelter = db.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail=f"Shelter {shelter_id} not found")

    if shelter.status == ShelterStatusEnum.CLOSED.value:
        shelter.status = ShelterStatusEnum.AVAILABLE.value
    else:
        shelter.status = ShelterStatusEnum.CLOSED.value

    db.commit()
    db.refresh(shelter)

    await ws_manager.broadcast({
        "event": "SHELTER_INTAKE_TOGGLED",
        "shelter_id": shelter.id,
        "status": shelter.status,
    })

    return shelter
