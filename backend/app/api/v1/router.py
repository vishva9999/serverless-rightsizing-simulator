from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    version,
    auth,
    simulation,
    ai,
    shelters,
    zones,
    evacuation,
    resources,
    audit_logs,
    analytics,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, tags=["Health & Status"])
api_v1_router.include_router(version.router, tags=["Version"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
api_v1_router.include_router(ai.router, prefix="/ai", tags=["AI & Risk Analytics"])
api_v1_router.include_router(shelters.router, prefix="/shelters", tags=["Shelter Capacity"])
api_v1_router.include_router(zones.router, prefix="/zones", tags=["Disaster Zones"])
api_v1_router.include_router(evacuation.router, prefix="/evacuation", tags=["Evacuation Routes"])
api_v1_router.include_router(resources.router, prefix="/resources", tags=["Emergency Resources"])
api_v1_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Telemetry"])
