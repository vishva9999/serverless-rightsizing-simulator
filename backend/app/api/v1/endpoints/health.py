import time
from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_db_connection
from app.schemas.health import HealthResponse, DatabaseHealth

router = APIRouter()

# Track startup timestamp
START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Connectivity Status",
    description="Returns current operational status, database connectivity, uptime, and simulation safety indicators.",
)
def get_health() -> HealthResponse:
    uptime = time.time() - START_TIME
    db_status = check_db_connection()

    overall_status = "ok" if db_status.get("connected") else "degraded"

    return HealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc),
        uptime_seconds=round(uptime, 2),
        database=DatabaseHealth(
            connected=db_status.get("connected", False),
            engine=db_status.get("engine", "unknown"),
            is_fallback=db_status.get("is_fallback", False),
            message=db_status.get("message", "Database check completed"),
        ),
        is_simulated=settings.IS_SIMULATION_MODE,
        emergency_services_integrated=settings.EMERGENCY_SERVICES_INTEGRATED,
        simulation_disclaimer="SIMULATED PLATFORM ONLY. Not connected to real-world 911, civil defense, or emergency services.",
    )
