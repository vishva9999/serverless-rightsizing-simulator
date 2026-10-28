from typing import Generator, Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.role import Role

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    Validates the Bearer JWT token, extracts user identity, and fetches
    the active user record along with their role.
    Raises HTTP 401 if token is missing, invalid, expired, or user not found.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: subject missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    statement = select(User).options(joinedload(User.role)).where(User.id == user_id)
    user = db.scalars(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account has been deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying that request is made by an authenticated active operator."""
    return current_user


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    """
    Reusable Role-Based Access Control (RBAC) dependency factory.
    Verifies that the authenticated operator possesses one of the authorized roles.
    Raises HTTP 403 Forbidden if the user's role is not within the authorized set.
    """
    def role_verifier(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.name if current_user.role else ""
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: role '{user_role}' lacks required permissions. Allowed roles: {list(allowed_roles)}",
            )
        return current_user

    return role_verifier
