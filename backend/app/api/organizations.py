"""
Organizations API Router — Phase 6 Organization Management.

Provides GET /api/organizations/me and PUT /api/organizations/me endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.response_models import OrganizationResponse, OrganizationUpdate
from app.repositories.organization_repository import OrganizationRepository
from app.core.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/organizations", tags=["Organizations"])


@router.get(
    "/me",
    response_model=OrganizationResponse,
    summary="Get Organization Details",
    description="Returns the organization details for the current user's workspace."
)
def get_my_organization(current_user: dict = Depends(get_current_user)):
    org_id = current_user["organization_id"]
    org = OrganizationRepository.get_by_id(org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID '{org_id}' not found."
        )

    member_count = OrganizationRepository.get_member_count(org_id)
    return OrganizationResponse(
        id=org["id"],
        name=org["name"],
        description=org.get("description", ""),
        member_count=member_count,
        created_at=org["created_at"],
        updated_at=org["updated_at"]
    )


@router.put(
    "/me",
    response_model=OrganizationResponse,
    summary="Update Organization",
    description="Updates organization metadata. Administrator role required."
)
def update_my_organization(
    payload: OrganizationUpdate,
    admin_user: dict = Depends(require_admin)
):
    org_id = admin_user["organization_id"]
    updated = OrganizationRepository.update(org_id, payload.name, payload.description)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID '{org_id}' not found."
        )

    member_count = OrganizationRepository.get_member_count(org_id)
    return OrganizationResponse(
        id=updated["id"],
        name=updated["name"],
        description=updated.get("description", ""),
        member_count=member_count,
        created_at=updated["created_at"],
        updated_at=updated["updated_at"]
    )
