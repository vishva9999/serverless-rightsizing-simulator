"""
Amazon Cognito JWT Authentication & User Identity Service — Phase 7.

Validates incoming Cognito access / ID tokens using cached JWKS public keys,
verifies cryptographic signatures, expiration, issuer, and client audience,
and maps Cognito identities to application user profiles.
"""

import time
import httpx
import jwt
from typing import Optional, Dict, Any
from app.utils.config import settings
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository

# In-memory cache for Cognito JWKS public keys
_JWKS_CACHE: Dict[str, Any] = {}
_JWKS_CACHE_EXPIRY: float = 0.0
JWKS_CACHE_TTL_SECONDS = 86400  # 24 hours


class CognitoService:
    """Service handling Amazon Cognito JWT validation and user resolution."""

    @classmethod
    def get_issuer_url(cls) -> str:
        region = settings.cognito_region or settings.aws_region
        pool_id = settings.cognito_user_pool_id or "local-pool"
        return f"https://cognito-idp.{region}.amazonaws.com/{pool_id}"

    @classmethod
    def fetch_jwks(cls) -> Dict[str, Any]:
        """Fetches and caches JWKS keys from Cognito's .well-known endpoint."""
        global _JWKS_CACHE, _JWKS_CACHE_EXPIRY
        now = time.time()

        if _JWKS_CACHE and now < _JWKS_CACHE_EXPIRY:
            return _JWKS_CACHE

        issuer = cls.get_issuer_url()
        jwks_url = f"{issuer}/.well-known/jwks.json"

        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(jwks_url)
                res.raise_for_status()
                keys = res.json()
                _JWKS_CACHE = {key["kid"]: key for key in keys.get("keys", [])}
                _JWKS_CACHE_EXPIRY = now + JWKS_CACHE_TTL_SECONDS
                return _JWKS_CACHE
        except Exception:
            # If network error or local test without live AWS, return current cache or empty dict
            return _JWKS_CACHE

    @classmethod
    def set_mock_jwks(cls, jwks_dict: Dict[str, Any]):
        """Helper for unit tests to inject mock JWKS keys."""
        global _JWKS_CACHE, _JWKS_CACHE_EXPIRY
        _JWKS_CACHE = jwks_dict
        _JWKS_CACHE_EXPIRY = time.time() + 3600

    @classmethod
    def validate_cognito_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Cryptographically validates a Cognito JWT token:
        1. Reads token header to extract Key ID (kid)
        2. Retrieves public key from JWKS
        3. Verifies signature, expiration, issuer, and client ID audience
        """
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                return None

            jwks = cls.fetch_jwks()
            key_data = jwks.get(kid)
            if not key_data:
                return None

            # Construct public key using PyJWT's RSA algorithm
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)

            issuer = cls.get_issuer_url()
            audience = settings.cognito_client_id

            # Decode and verify token
            decode_options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": bool(settings.cognito_user_pool_id),
                "verify_aud": False  # Access tokens use client_id instead of aud
            }

            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                issuer=issuer if settings.cognito_user_pool_id else None,
                options=decode_options
            )

            # Check client_id or aud matches
            token_client_id = payload.get("client_id") or payload.get("aud")
            if audience and token_client_id and token_client_id != audience:
                return None

            return payload
        except Exception:
            return None

    @classmethod
    def resolve_cognito_user(cls, token_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves or auto-provisions an application user profile from a valid Cognito JWT payload.
        Maps Cognito 'sub' and 'email' to application organization and role.
        """
        cognito_sub = token_payload.get("sub", "")
        email = token_payload.get("email") or token_payload.get("cognito:username") or f"{cognito_sub}@cognito.aws"
        full_name = token_payload.get("name") or token_payload.get("email", "Cognito User")

        # Check if user already exists in repository by email or cognito_sub
        user = UserRepository.get_by_email(email)
        if not user:
            # Auto-provision user in default organization
            org = OrganizationRepository.get_by_name("Demo Enterprise")
            org_id = org["id"] if org else "default-org"

            # Check if any Cognito groups are present (e.g. "admin", "analyst")
            groups = token_payload.get("cognito:groups", [])
            role = "admin" if "admin" in groups else ("analyst" if "analyst" in groups else "viewer")

            user = UserRepository.create(
                email=email,
                password_hash="COGNITO_MANAGED",
                full_name=full_name,
                organization_id=org_id,
                role=role,
                is_active=True
            )
        else:
            user.pop("password_hash", None)

        return user
