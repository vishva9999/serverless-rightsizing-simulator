from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.core.database import get_db
from app.api.deps import get_current_user, require_authenticated_user, require_roles
from app.models.user import User
from app.models.simulation_scenario import SimulationScenario
from app.models.simulation_result import SimulationResult
from app.schemas.simulation import (
    SimulationScenarioCreate,
    SimulationScenarioRead,
    SimulationResultRead,
    SimulationRunResponse,
    SimulationOutputData,
)
from app.services.simulation_service import DisasterSimulationEngine

router = APIRouter()


@router.post(
    "/scenarios",
    response_model=SimulationScenarioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new disaster simulation scenario",
)
def create_simulation_scenario(
    scenario_in: SimulationScenarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DISASTER_OPERATOR")),
):
    """
    Creates a disaster simulation scenario with specified environmental and infrastructural parameters.
    Requires ADMIN or DISASTER_OPERATOR clearance.
    All scenario records are strictly SIMULATED testbeds.
    """
    scenario = DisasterSimulationEngine.create_scenario(db, scenario_in, current_user.id)
    return scenario


@router.get(
    "/scenarios",
    response_model=List[SimulationScenarioRead],
    summary="List all disaster simulation scenarios",
)
def list_simulation_scenarios(
    disaster_type: Optional[str] = Query(None, description="Filter by disaster type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """
    Lists available simulated scenarios. Automatically ensures the canonical
    'Coimbatore Flood Simulation - DEMO' exists in the database.
    """
    # Ensure demo scenario exists
    DisasterSimulationEngine.get_or_create_demo_scenario(db, current_user.id)

    stmt = select(SimulationScenario)
    if disaster_type:
        stmt = stmt.where(SimulationScenario.disaster_type == disaster_type.upper())
    stmt = stmt.order_by(desc(SimulationScenario.created_at)).offset(skip).limit(limit)

    scenarios = db.scalars(stmt).all()
    return scenarios


@router.get(
    "/scenarios/{id}",
    response_model=SimulationScenarioRead,
    summary="Get simulation scenario by ID",
)
def get_simulation_scenario(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Retrieves metadata and parameter configuration for a specific scenario."""
    scenario = db.get(SimulationScenario, id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation scenario {id} not found",
        )
    return scenario


@router.post(
    "/scenarios/{id}/run",
    response_model=SimulationRunResponse,
    summary="Execute a disaster simulation run",
)
def run_simulation_scenario(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "DISASTER_OPERATOR")),
):
    """
    Executes a deterministic simulation run for the target scenario using its
    configured parameters and random seed. Persists the execution results.
    """
    scenario = db.get(SimulationScenario, id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation scenario {id} not found",
        )

    try:
        updated_scenario, sim_result, outputs = DisasterSimulationEngine.run_scenario(db, id)
        return SimulationRunResponse(
            scenario_id=updated_scenario.id,
            scenario_name=updated_scenario.name,
            disaster_type=updated_scenario.disaster_type,
            status=updated_scenario.status,
            result=SimulationResultRead.model_validate(sim_result),
            outputs=outputs,
            is_simulated=True,
            disclaimer="SYNTHETIC SIMULATION DATA ONLY. NOT CONNECTED TO REAL EMERGENCY SERVICES.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation execution failure: {str(e)}",
        )


@router.get(
    "/scenarios/{id}/results",
    response_model=List[SimulationResultRead],
    summary="Get execution results for a simulation scenario",
)
def get_simulation_results(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Returns history of simulation run results for the specified scenario."""
    scenario = db.get(SimulationScenario, id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation scenario {id} not found",
        )

    stmt = (
        select(SimulationResult)
        .where(SimulationResult.scenario_id == id)
        .order_by(desc(SimulationResult.created_at))
    )
    results = db.scalars(stmt).all()
    return results
