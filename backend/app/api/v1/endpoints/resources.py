from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleStatusEnum
from app.models.resource import Resource
from app.models.resource_inventory import ResourceInventory
from app.schemas.vehicle import VehicleRead
from app.websocket.manager import ws_manager

router = APIRouter()


@router.get("/fleet", response_model=List[VehicleRead], summary="List emergency rescue and transport fleet")
def list_fleet(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    query = select(Vehicle)
    if status_filter:
        query = query.where(Vehicle.status == status_filter)
    vehicles = db.scalars(query).all()
    return vehicles


@router.get("/supplies", summary="List vital supply reserves and inventories")
def list_supplies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    query = select(ResourceInventory)
    inventories = db.scalars(query).all()
    
    results = []
    for inv in inventories:
        results.append({
            "id": inv.id,
            "resource_id": inv.resource_id,
            "resource_name": inv.resource.name if inv.resource else f"Resource #{inv.resource_id}",
            "resource_type": inv.resource.resource_type if inv.resource else "SUPPLY",
            "quantity": inv.available_quantity,
            "total_quantity": inv.total_quantity,
            "status": inv.status,
            "location": inv.location_name,
        })
    return results


@router.post("/dispatch", summary="Dispatch simulated fleet vehicle or supply reserve")
async def dispatch_resource(
    vehicle_id: int = Query(..., description="ID of vehicle to deploy"),
    destination: str = Query("Zone-Bravo", description="Target destination sector or shelter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

    vehicle.status = VehicleStatusEnum.DEPLOYED.value
    db.commit()
    db.refresh(vehicle)

    await ws_manager.broadcast({
        "event": "VEHICLE_DISPATCHED",
        "vehicle_id": vehicle.id,
        "vehicle_code": vehicle.vehicle_code,
        "vehicle_type": vehicle.vehicle_type,
        "status": vehicle.status,
        "destination": destination,
    })

    return {
        "success": True,
        "message": f"Simulated dispatch order executed for {vehicle.vehicle_code} to {destination}",
        "vehicle_id": vehicle.id,
        "status": vehicle.status,
    }
