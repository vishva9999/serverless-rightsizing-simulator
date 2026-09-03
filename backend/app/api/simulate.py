"""
Simulation API Router — Phase 2 POST /api/simulate.

Exposes the rightsizing simulation engine to the frontend.
Performs input validation via SimulationRequest and returns SimulationResponse.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.response_models import SimulationRequest, SimulationResponse
from app.services.simulation_engine import run_simulation

router = APIRouter(prefix="/api", tags=["Simulation"])


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Rightsizing Simulation",
    description="Evaluates serverless configurations against performance/availability SLO targets and returns optimal rightsizing recommendation."
)
def simulate_endpoint(request: SimulationRequest) -> SimulationResponse:
    """
    POST /api/simulate

    Executes the rightsizing simulation algorithm for the provided scenario parameters.
    Returns baseline metrics, candidate tier calculations, constraint evaluations,
    the optimal recommended configuration, and a human-readable explanation.
    """
    try:
        response = run_simulation(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Simulation parameter error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation engine error: {str(e)}"
        )
