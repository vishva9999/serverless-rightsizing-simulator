"""
Scenarios API Router — Phase 3, 4 & 6 Scenario Management.

Provides CRUD endpoints for scenarios and allows running simulations directly from a saved scenario.
Protected by JWT Authentication, Organization Multi-Tenant Isolation, and Role-Based Access Control.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.response_models import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    SimulationRequest,
)
from app.repositories.storage_factory import get_scenario_repository, get_history_repository
from app.services.simulation_engine import run_simulation
from app.services.s3_service import S3Service
from app.core.dependencies import get_current_user, require_analyst_or_admin, require_admin

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])


@router.post(
    "",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Scenario",
    description="Creates a new workload scenario for the current user's organization. Analyst or Admin role required."
)
def create_scenario(
    payload: ScenarioCreate,
    current_user: dict = Depends(require_analyst_or_admin)
):
    org_id = current_user["organization_id"]
    repo = get_scenario_repository()
    scenario = repo.create(payload.model_dump(), organization_id=org_id)
    return scenario


@router.get(
    "",
    response_model=List[ScenarioResponse],
    summary="List Scenarios",
    description="Returns all saved workload scenarios belonging to the current user's organization."
)
def list_scenarios(current_user: dict = Depends(get_current_user)):
    org_id = current_user["organization_id"]
    repo = get_scenario_repository()
    return repo.list_all(organization_id=org_id)


@router.get(
    "/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Get Scenario",
    description="Fetches a single scenario by ID within the current user's organization."
)
def get_scenario(
    scenario_id: str,
    current_user: dict = Depends(get_current_user)
):
    org_id = current_user["organization_id"]
    repo = get_scenario_repository()
    scenario = repo.get_by_id(scenario_id, organization_id=org_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{scenario_id}' not found in your organization."
        )
    return scenario


@router.put(
    "/{scenario_id}",
    response_model=ScenarioResponse,
    summary="Update Scenario",
    description="Updates parameters for an existing scenario within the organization. Analyst or Admin role required."
)
def update_scenario(
    scenario_id: str,
    payload: ScenarioUpdate,
    current_user: dict = Depends(require_analyst_or_admin)
):
    org_id = current_user["organization_id"]
    repo = get_scenario_repository()
    updated = repo.update(scenario_id, payload.model_dump(exclude_unset=True), organization_id=org_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{scenario_id}' not found in your organization."
        )
    return updated


@router.delete(
    "/{scenario_id}",
    summary="Delete Scenario",
    description="Deletes a scenario by ID within the organization. Administrator role required."
)
def delete_scenario(
    scenario_id: str,
    admin_user: dict = Depends(require_admin)
):
    org_id = admin_user["organization_id"]
    repo = get_scenario_repository()
    success = repo.delete(scenario_id, organization_id=org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{scenario_id}' not found in your organization."
        )
    return {"message": f"Scenario '{scenario_id}' deleted successfully.", "id": scenario_id}


@router.post(
    "/{scenario_id}/simulate",
    summary="Run Simulation from Scenario",
    description="Executes simulation engine from scenario parameters. Analyst or Admin role required."
)
def simulate_scenario(
    scenario_id: str,
    current_user: dict = Depends(require_analyst_or_admin)
):
    org_id = current_user["organization_id"]
    scenario_repo = get_scenario_repository()
    history_repo = get_history_repository()

    # 1. Load scenario owned by current organization
    scenario = scenario_repo.get_by_id(scenario_id, organization_id=org_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{scenario_id}' not found in your organization."
        )

    # 2. Map to existing SimulationRequest
    sim_request = SimulationRequest(
        scenario_name=scenario["name"],
        cpu_utilization=scenario["cpu_utilization"],
        memory_mb=scenario["baseline_memory_mb"],
        baseline_latency_ms=scenario["baseline_latency_ms"],
        request_volume=scenario["request_volume"],
        current_price=scenario["current_price"],
        latency_target_ms=scenario["latency_target_ms"],
        availability_target=scenario["availability_target_percent"]
    )

    # 3. Run EXISTING simulation engine
    simulation_result = run_simulation(sim_request).model_dump()

    # 4. Save simulation result to history repository with organization_id
    history_entry = history_repo.create(
        scenario_id=scenario_id,
        scenario_name=scenario["name"],
        simulation_response=simulation_result,
        organization_id=org_id
    )

    # 5. Export JSON artifact to S3 if STORAGE_MODE=aws
    s3_key = S3Service.upload_simulation_artifact(
        scenario_id=scenario_id,
        history_id=history_entry["id"],
        simulation_result=simulation_result
    )

    simulation_result["history_id"] = history_entry["id"]
    if s3_key:
        simulation_result["s3_artifact_key"] = s3_key

    return simulation_result
