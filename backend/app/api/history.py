"""
History API Router — Phase 3, 4 & 6 Simulation History & Run Comparison.

Provides endpoints for retrieving past simulation runs, fetching full simulation JSON details,
deleting historical entries, and comparing two runs side-by-side.
Protected by JWT Authentication, Organization Multi-Tenant Isolation, and Role-Based Access Control.
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from app.models.response_models import (
    HistoryItemResponse,
    HistoryDetailResponse,
    HistoryCompareResponse,
)
from app.repositories.storage_factory import get_history_repository
from app.core.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get(
    "",
    response_model=List[HistoryItemResponse],
    summary="List Simulation History",
    description="Returns past simulation runs for the user's organization, optionally filtered by scenario_id."
)
def list_history(
    scenario_id: Optional[str] = Query(default=None, description="Optional scenario ID to filter history"),
    current_user: dict = Depends(get_current_user)
):
    org_id = current_user["organization_id"]
    repo = get_history_repository()
    return repo.list_all(scenario_id=scenario_id, organization_id=org_id)


@router.get(
    "/compare/{id1}/{id2}",
    response_model=HistoryCompareResponse,
    summary="Compare Two Simulation Runs",
    description="Compares two simulation runs side-by-side by ID within the user's organization."
)
def compare_history_runs(
    id1: str,
    id2: str,
    current_user: dict = Depends(get_current_user)
):
    org_id = current_user["organization_id"]
    repo = get_history_repository()
    comparison = repo.compare(id1, id2, organization_id=org_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"One or both simulation history runs ('{id1}', '{id2}') could not be found in your organization."
        )
    return comparison


@router.get(
    "/{history_id}",
    response_model=HistoryDetailResponse,
    summary="Get History Detail",
    description="Fetches full details for a single simulation run within the organization."
)
def get_history_detail(
    history_id: str,
    current_user: dict = Depends(get_current_user)
):
    org_id = current_user["organization_id"]
    repo = get_history_repository()
    item = repo.get_by_id(history_id, organization_id=org_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation history entry with ID '{history_id}' not found in your organization."
        )
    return item


@router.delete(
    "/{history_id}",
    summary="Delete History Entry",
    description="Deletes a history record by ID. Administrator role required."
)
def delete_history_entry(
    history_id: str,
    admin_user: dict = Depends(require_admin)
):
    org_id = admin_user["organization_id"]
    repo = get_history_repository()
    success = repo.delete(history_id, organization_id=org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation history entry with ID '{history_id}' not found in your organization."
        )
    return {"message": f"Simulation history entry '{history_id}' deleted successfully.", "id": history_id}
