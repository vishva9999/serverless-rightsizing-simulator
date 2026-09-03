"""
Sensitivity API Router — Phase 5 & 6 Sensitivity Analysis Endpoints.

Exposes:
  - GET /api/sensitivity/variables: List supported sensitivity variables metadata.
  - POST /api/sensitivity/analyze: Run sensitivity analysis for a scenario and variable.
Protected by JWT Authentication, Organization Multi-Tenant Isolation, and RBAC permissions.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.response_models import (
    SensitivityRequest,
    SensitivityResponse,
    SensitivityVariable
)
from app.services.sensitivity_engine import (
    SUPPORTED_VARIABLES,
    get_supported_variables_metadata,
    run_sensitivity_analysis
)
from app.repositories.storage_factory import get_scenario_repository
from app.core.dependencies import get_current_user, require_analyst_or_admin

router = APIRouter(prefix="/api/sensitivity", tags=["Sensitivity Analysis"])


@router.get(
    "/variables",
    response_model=List[SensitivityVariable],
    summary="List Supported Sensitivity Variables",
    description="Returns metadata for all workload parameters supported for sensitivity analysis."
)
def list_sensitivity_variables(current_user: dict = Depends(get_current_user)):
    return get_supported_variables_metadata()


@router.post(
    "/analyze",
    response_model=SensitivityResponse,
    summary="Run Sensitivity Analysis",
    description="Varies a workload parameter across test points for a scenario and evaluates recommendations. Analyst or Admin role required."
)
def analyze_sensitivity(
    payload: SensitivityRequest,
    current_user: dict = Depends(require_analyst_or_admin)
):
    org_id = current_user["organization_id"]

    # 1. Validate scenario exists in user's organization
    scenario_repo = get_scenario_repository()
    scenario = scenario_repo.get_by_id(payload.scenario_id, organization_id=org_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID '{payload.scenario_id}' not found in your organization."
        )

    # 2. Validate variable is supported
    if payload.variable not in SUPPORTED_VARIABLES:
        supported_keys = ", ".join(SUPPORTED_VARIABLES.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported sensitivity variable '{payload.variable}'. Supported variables are: {supported_keys}."
        )

    # 3. Validate number of points (1 to 20)
    if not payload.values or len(payload.values) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sensitivity values list must contain between 1 and 20 points (received {len(payload.values) if payload.values else 0})."
        )

    # 4. Validate numeric ranges per variable
    var_meta = SUPPORTED_VARIABLES[payload.variable]
    min_val = var_meta["min_val"]
    max_val = var_meta["max_val"]
    label = var_meta["label"]

    for val in payload.values:
        if min_val is not None and val < min_val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value {val} for '{label}'. Minimum allowed value is {min_val}."
            )
        if max_val is not None and val > max_val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid value {val} for '{label}'. Maximum allowed value is {max_val}."
            )

    # 5. Run sensitivity engine using EXISTING simulation engine
    return run_sensitivity_analysis(
        scenario=scenario,
        variable_key=payload.variable,
        test_values=payload.values
    )
