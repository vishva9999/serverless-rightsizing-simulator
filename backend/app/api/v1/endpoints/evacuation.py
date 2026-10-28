from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.models.evacuation_route import EvacuationRoute, RouteStatusEnum
from app.schemas.evacuation_route import EvacuationRouteRead
from app.websocket.manager import ws_manager

router = APIRouter()


@router.get("/routes", response_model=List[EvacuationRouteRead], summary="List all evacuation corridors")
def list_evacuation_routes(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    query = select(EvacuationRoute)
    if status_filter:
        query = query.where(EvacuationRoute.route_status == status_filter)
    routes = db.scalars(query).all()
    return routes


@router.get("/routes/{route_id}", response_model=EvacuationRouteRead, summary="Get evacuation corridor details")
def get_evacuation_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    route = db.get(EvacuationRoute, route_id)
    if not route:
        raise HTTPException(status_code=404, detail=f"Evacuation Route {route_id} not found")
    return route


@router.patch("/routes/{route_id}/status", response_model=EvacuationRouteRead, summary="Update corridor status")
async def update_route_status(
    route_id: int,
    new_status: str = Query(..., description="SAFE, CAUTION, or BLOCKED"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    route = db.get(EvacuationRoute, route_id)
    if not route:
        raise HTTPException(status_code=404, detail=f"Evacuation Route {route_id} not found")

    route.route_status = new_status.upper()
    if route.route_status == RouteStatusEnum.BLOCKED.value:
        route.safety_score = 10.0
        route.congestion_score = 95.0
    elif route.route_status == RouteStatusEnum.SAFE.value:
        route.safety_score = 95.0
        route.congestion_score = 25.0

    db.commit()
    db.refresh(route)

    await ws_manager.broadcast({
        "event": "ROUTE_STATUS_CHANGED",
        "route_id": route.id,
        "new_status": route.route_status,
        "safety_score": route.safety_score,
        "congestion_score": route.congestion_score,
    })

    return route


@router.post("/routes/{route_id}/contraflow", response_model=EvacuationRouteRead, summary="Activate or deactivate contraflow lane routing")
async def toggle_contraflow(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    route = db.get(EvacuationRoute, route_id)
    if not route:
        raise HTTPException(status_code=404, detail=f"Evacuation Route {route_id} not found")

    # Contraflow relieves congestion by 40% and shortens estimated travel time by 30%
    if route.congestion_score > 35:
        route.congestion_score = max(15.0, route.congestion_score - 35.0)
        route.estimated_time_minutes = max(10.0, route.estimated_time_minutes * 0.7)
        action = "CONTRAFLOW_ENABLED"
    else:
        route.congestion_score = min(80.0, route.congestion_score + 35.0)
        action = "CONTRAFLOW_DISABLED"

    db.commit()
    db.refresh(route)

    await ws_manager.broadcast({
        "event": action,
        "route_id": route.id,
        "congestion_score": route.congestion_score,
        "estimated_time_minutes": route.estimated_time_minutes,
    })

    return route
