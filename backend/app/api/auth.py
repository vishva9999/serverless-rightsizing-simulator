"""
Authentication API Router — Phase 6 Auth Endpoints.

Provides /api/auth/register, /api/auth/login, and /api/auth/me.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.response_models import UserRegister, UserLogin, UserResponse, TokenResponse
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Registers a new user and organization. The first user of an organization is assigned the 'admin' role."
)
def register(payload: UserRegister):
    # 1. Check if email already exists
    existing = UserRepository.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{payload.email}' already exists."
        )

    # 2. Find or create Organization
    org = OrganizationRepository.get_by_name(payload.organization_name)
    if not org:
        org = OrganizationRepository.create(payload.organization_name)
        role = "admin"  # First user in new org gets admin
    else:
        role = "analyst"  # Additional users default to analyst

    # 3. Hash password
    pwd_hash = AuthService.hash_password(payload.password)

    # 4. Create User
    user = UserRepository.create(
        email=payload.email,
        password_hash=pwd_hash,
        full_name=payload.full_name,
        organization_id=org["id"],
        role=role,
        is_active=True
    )

    # 5. Issue JWT access token
    token = AuthService.create_access_token({
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "role": user["role"]
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates email and password, returning a JWT access token."
)
def login(payload: UserLogin):
    # 1. Lookup user by email
    user = UserRepository.get_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 2. Verify password
    if not AuthService.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 3. Check active status
    if not user.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact your organization administrator."
        )

    # 4. Issue JWT access token
    token = AuthService.create_access_token({
        "user_id": user["id"],
        "organization_id": user["organization_id"],
        "role": user["role"]
    })

    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user_data)
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Current User Profile",
    description="Returns the profile details for the currently authenticated user."
)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)
