"""
Project info endpoint.
Returns metadata about this project: name, version, environment.
"""

from fastapi import APIRouter
from app.models.response_models import InfoResponse
from app.utils.config import settings

router = APIRouter(prefix="/api")


@router.get("/info", response_model=InfoResponse, tags=["Info"])
def get_info():
    """
    Returns project metadata including name, version, and deployment environment.
    Useful for verifying which version of the API is running.
    """
    return InfoResponse(
        project_name=settings.project_name,
        version=settings.version,
        environment=settings.environment,
        description=(
            "A full-stack simulator that helps startups understand the "
            "relationship between serverless cost and application performance."
        ),
        phase="Phase 1 — Project Foundation (Local, No AWS)",
    )
