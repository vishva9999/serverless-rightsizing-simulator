"""
Health check endpoint.
Used by monitoring tools and load balancers to verify the service is alive.
"""

from fastapi import APIRouter
from app.models.response_models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Returns the current health status of the API.
    This endpoint does not require any parameters.
    """
    return HealthResponse(
        status="ok",
        message="Serverless Rightsizing Simulator API is running",
    )
