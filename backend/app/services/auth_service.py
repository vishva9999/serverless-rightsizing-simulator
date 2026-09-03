"""
Authentication & JWT Security Service — Phase 6 AuthService.

Provides secure password hashing/verification using direct bcrypt and
JWT access token creation/decoding.
Designed for seamless future AWS Cognito replacement.
"""

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.utils.config import settings

JWT_ALGORITHM = "HS256"


class AuthService:
    """Security service handling password verification and JWT token lifecycle."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes plain-text password using bcrypt."""
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies plain-text password against bcrypt hash."""
        try:
            plain_bytes = plain_password.encode("utf-8")
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(plain_bytes, hash_bytes)
        except Exception:
            return False

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates a signed JWT access token containing minimal claims:
        user_id, organization_id, role, exp.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)

        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decodes and verifies JWT signature and expiration.
        Returns payload dict or None if invalid/expired.
        """
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
