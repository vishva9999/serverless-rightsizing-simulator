"""
Users API Router — Phase 6 User Management.

Provides User Management endpoints within an Organization:
  - GET /api/users: List organization users (Admin/Analyst)
  - GET /api/users/{user_id}: Get user detail
  - POST /api/users: Create new user in organization (Admin only)
  - PUT /api/users/{user_id}/role: Change user role (Admin only with final admin protection)
  - PUT /api/users/{user_id}/status: Activate/deactivate user (Admin only with final admin protection)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.response_models import (
    UserResponse,
    UserCreateByAdmin,
    UserRoleUpdate,
    UserStatusUpdate
)
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, require_admin, require_analyst_or_admin

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List Organization Users",
    description="Returns all users belonging to the current user's organization. Admin or Analyst role required."
)
def list_organization_users(current_user: dict = Depends(require_analyst_or_admin)):
    org_id = current_user["organization_id"]
    users = UserRepository.list_by_organization(org_id)
    return [UserResponse(**u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User Detail",
    description="Fetches a user profile by ID within the organization."
)
def get_user_detail(
    user_id: str,
    current_user: dict = Depends(require_analyst_or_admin)
):
    org_id = current_user["organization_id"]
    target = UserRepository.get_by_id(user_id)

    if not target or target.get("organization_id") != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found in your organization."
        )

    target.pop("password_hash", None)
    return UserResponse(**target)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User in Organization",
    description="Creates a new user account in the current organization. Administrator role required."
)
def create_organization_user(
    payload: UserCreateByAdmin,
    admin_user: dict = Depends(require_admin)
):
    org_id = admin_user["organization_id"]

    # 1. Check duplicate email
    existing = UserRepository.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{payload.email}' already exists."
        )

    # 2. Validate role
    role = payload.role.lower()
    if role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: 'admin', 'analyst', 'viewer'."
        )

    # 3. Hash password and create user
    pwd_hash = AuthService.hash_password(payload.password)
    user = UserRepository.create(
        email=payload.email,
        password_hash=pwd_hash,
        full_name=payload.full_name,
        organization_id=org_id,
        role=role,
        is_active=True
    )

    return UserResponse(**user)


@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Update User Role",
    description="Changes a user's permission role. Administrator role required."
)
def update_user_role(
    user_id: str,
    payload: UserRoleUpdate,
    admin_user: dict = Depends(require_admin)
):
    org_id = admin_user["organization_id"]

    # 1. Verify user exists in org
    target = UserRepository.get_by_id(user_id)
    if not target or target.get("organization_id") != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found in your organization."
        )

    new_role = payload.role.lower()
    if new_role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: 'admin', 'analyst', 'viewer'."
        )

    # 2. Final Admin Guard: Prevent demoting the last active admin
    if target["role"] == "admin" and new_role != "admin":
        active_admins = UserRepository.count_active_admins_in_org(org_id)
        if active_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the final active administrator in an organization. Assign another admin first."
            )

    updated = UserRepository.update_role(user_id, new_role, org_id)
    return UserResponse(**updated)


@router.put(
    "/{user_id}/status",
    response_model=UserResponse,
    summary="Update User Active Status",
    description="Activates or deactivates a user account. Administrator role required."
)
def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    admin_user: dict = Depends(require_admin)
):
    org_id = admin_user["organization_id"]

    # 1. Verify user exists in org
    target = UserRepository.get_by_id(user_id)
    if not target or target.get("organization_id") != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found in your organization."
        )

    # 2. Final Admin Guard: Prevent deactivating the last active admin
    if target["role"] == "admin" and not payload.is_active:
        active_admins = UserRepository.count_active_admins_in_org(org_id)
        if active_admins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the final active administrator in an organization."
            )

    updated = UserRepository.update_status(user_id, payload.is_active, org_id)
    return UserResponse(**updated)
