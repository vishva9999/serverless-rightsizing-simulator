from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    Token,
    AuthUserResponse,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Operator Login",
    description="Authenticate disaster command center personnel via username or email and password.",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> Any:
    identifier = payload.username_or_email.strip()
    
    # Query user by either username or email
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(or_(User.username == identifier, User.email == identifier.lower()))
    )
    user = db.scalars(statement).first()

    if not user or not verify_password(payload.password, user.password_hash):
        # Do not log passwords or confidential attempts
        logger.warning(f"Failed login attempt for identifier: {identifier}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials: username/email or password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(f"Deactivated user attempted login: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive. Contact command administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWT token
    role_name = user.role.name if user.role else "VIEWER"
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": role_name,
    }
    access_token = create_access_token(token_data)
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    logger.info(f"Operator authenticated successfully: {user.username} (Role: {role_name})")

    safe_user = AuthUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=role_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in_seconds,
        user=safe_user,
    )


@router.get(
    "/me",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current Operator Identity",
    description="Returns verified identity and operational role details for current Bearer token holder.",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    role_name = current_user.role.name if current_user.role else "VIEWER"
    return AuthUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Refresh Session Token",
    description="Exchanges an active valid access token for a refreshed session token.",
)
def refresh_token(
    current_user: User = Depends(get_current_user),
) -> Any:
    role_name = current_user.role.name if current_user.role else "VIEWER"
    token_data = {
        "sub": str(current_user.id),
        "username": current_user.username,
        "role": role_name,
    }
    new_access_token = create_access_token(token_data)
    expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return Token(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=expires_in_seconds,
    )
