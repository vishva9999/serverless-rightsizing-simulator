"""
FastAPI Security & Authorization Dependencies — Phase 6 & 7 Core Dependencies.

Provides get_current_user authentication supporting dual modes:
  - Local JWT mode: Decodes HS256 JWT and looks up user in SQLite/local repository.
  - Cognito mode: Validates RS256 token against AWS Cognito JWKS and resolves user identity.

Enforces Role-Based Access Control (RBAC):
  - require_admin
  - require_analyst_or_admin
  - require_authenticated_user
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.utils.config import settings
from app.services.auth_service import AuthService
from app.services.cognito_service import CognitoService
from app.repositories.user_repository import UserRepository

# HTTP Bearer token security scheme
security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    Validates Bearer JWT from Authorization header and returns current authenticated user.
    Routes to Local JWT or Amazon Cognito based on settings.auth_mode.
    Raises 401 Unauthorized if missing/invalid token, or 403 Forbidden if inactive account.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please include a valid Bearer token in the Authorization header.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    # 1. AWS Cognito Authentication Mode
    if settings.auth_mode.lower() == "cognito":
        payload = CognitoService.validate_cognito_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Amazon Cognito authentication token.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user = CognitoService.resolve_cognito_user(payload)

    # 2. Local JWT Authentication Mode (Default)
    else:
        payload = AuthService.decode_access_token(token)
        if not payload or "user_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_id = payload["user_id"]
        user = UserRepository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with token could not be resolved.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.get("is_active", 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact your organization administrator."
        )

    # Sanitize sensitive fields before passing to controllers
    user.pop("password_hash", None)
    return user


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requires current user to have the 'admin' role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Administrator privileges required."
        )
    return current_user


def require_analyst_or_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requires current user to have either 'analyst' or 'admin' role."""
    if current_user.get("role") not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Analyst or Administrator privileges required to perform this action."
        )
    return current_user


def require_authenticated_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Requires user to be authenticated (any role: admin, analyst, viewer)."""
    return current_user
