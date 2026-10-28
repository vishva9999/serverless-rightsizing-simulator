from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import VersionResponse

router = APIRouter()


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="Application Version & Build Target",
    description="Returns platform semantic version, API prefix, and simulation deployment target.",
)
def get_version() -> VersionResponse:
    return VersionResponse(
        app_name=settings.APP_NAME,
        version="1.0.0-phase1",
        api_version="v1",
        environment=settings.APP_ENV,
        is_simulated=settings.IS_SIMULATION_MODE,
        build_target="command_center_shell",
    )
