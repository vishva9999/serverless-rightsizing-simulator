from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.deps import require_authenticated_user
from app.models.user import User
from app.models.disaster_zone import DisasterZone
from app.models.shelter import Shelter
from app.models.vehicle import Vehicle, VehicleStatusEnum
from app.models.evacuation_route import EvacuationRoute
from app.models.simulation_result import SimulationResult

router = APIRouter()


@router.get("/summary", summary="Get aggregated operational and analytics telemetry")
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
) -> Dict[str, Any]:
    # Aggregations across tables
    zones = db.scalars(select(DisasterZone)).all()
    total_population = sum(z.population for z in zones)
    critical_zones = sum(1 for z in zones if z.risk_level in ["HIGH", "CRITICAL"])
    avg_risk_score = round(sum(z.risk_score for z in zones) / max(1, len(zones)), 1)
    avg_road_access = round(sum(z.road_accessibility for z in zones) / max(1, len(zones)), 1)

    shelters = db.scalars(select(Shelter)).all()
    total_shelter_capacity = sum(s.total_capacity for s in shelters)
    total_shelter_occupancy = sum(s.current_occupancy for s in shelters)
    shelter_utilization = round((total_shelter_occupancy / max(1, total_shelter_capacity)) * 100, 1)

    vehicles = db.scalars(select(Vehicle)).all()
    ready_vehicles = sum(1 for v in vehicles if v.status == VehicleStatusEnum.AVAILABLE.value)
    deployed_vehicles = sum(1 for v in vehicles if v.status == VehicleStatusEnum.DEPLOYED.value)

    routes = db.scalars(select(EvacuationRoute)).all()
    avg_safety_score = round(sum(r.safety_score for r in routes) / max(1, len(routes)), 1)
    avg_congestion = round(sum(r.congestion_score for r in routes) / max(1, len(routes)), 1)

    latest_sim = db.scalars(select(SimulationResult).order_by(SimulationResult.id.desc())).first()

    return {
        "is_simulated": True,
        "disclaimer": "ALL VALUES ARE MATHEMATICALLY SIMULATED FOR DECISION BENCHMARKING",
        "zones": {
            "total_count": len(zones),
            "critical_count": critical_zones,
            "total_population": total_population,
            "average_risk_score": avg_risk_score,
            "average_road_accessibility": avg_road_access,
        },
        "shelters": {
            "total_count": len(shelters),
            "total_capacity": total_shelter_capacity,
            "current_occupancy": total_shelter_occupancy,
            "utilization_percent": shelter_utilization,
        },
        "fleet": {
            "total_count": len(vehicles),
            "ready_count": ready_vehicles,
            "deployed_count": deployed_vehicles,
            "readiness_percent": round((ready_vehicles / max(1, len(vehicles))) * 100, 1),
        },
        "evacuation": {
            "routes_count": len(routes),
            "average_safety_score": avg_safety_score,
            "average_congestion_percent": avg_congestion,
            "estimated_clearance_hours": round((total_population * 0.45) / 3200, 1),
        },
        "latest_simulation": {
            "id": latest_sim.id if latest_sim else None,
            "average_risk_score": latest_sim.average_risk_score if latest_sim else avg_risk_score,
            "estimated_evacuation_time": latest_sim.estimated_evacuation_time if latest_sim else 4.2,
        },
    }
