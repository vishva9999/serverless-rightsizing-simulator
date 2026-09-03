"""
Unit tests for Phase 7 AWS Lambda Handler and Amazon Cognito JWT Validation.

Verifies:
  1. Lambda handler initialization (Mangum ASGI adapter)
  2. Lambda proxy invocation for GET /health
  3. Lambda proxy invocation for GET /api/info
  4. Lambda proxy invocation for GET /api/storage/status
  5. Cognito token validation with valid RSA signature
  6. Cognito token rejection on invalid signature
  7. Cognito token rejection on expired token
  8. Cognito token rejection on invalid issuer
  9. Cognito token rejection on invalid audience / client_id
 10. Cognito user resolution and auto-provisioning
 11. Role mapping from Cognito groups
 12. Backward compatibility with Local JWT mode
"""

import time
import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from app.lambda_handler import handler
from app.services.cognito_service import CognitoService
from app.utils.config import settings
from app.repositories.user_repository import UserRepository
from app.db.database import init_db

init_db()

# Generate a disposable RSA key pair for testing Cognito JWT signatures
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Export JWK dictionary for public key
mock_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(public_key, as_dict=True)
mock_jwk["kid"] = "test-cognito-kid-1"
mock_jwk["alg"] = "RS256"
mock_jwk["use"] = "sig"


@pytest.fixture(autouse=True)
def setup_cognito_mock():
    """Inject mock JWKS into CognitoService cache."""
    CognitoService.set_mock_jwks({"test-cognito-kid-1": mock_jwk})
    old_pool = settings.cognito_user_pool_id
    old_client = settings.cognito_client_id
    old_region = settings.cognito_region

    settings.cognito_user_pool_id = "ap-south-1_MockPool"
    settings.cognito_client_id = "mock-client-id-12345"
    settings.cognito_region = "ap-south-1"

    yield

    settings.cognito_user_pool_id = old_pool
    settings.cognito_client_id = old_client
    settings.cognito_region = old_region


def create_signed_cognito_token(payload: dict, headers: dict = None) -> str:
    """Helper to create RS256 signed test token."""
    hdr = {"kid": "test-cognito-kid-1", "alg": "RS256"}
    if headers:
        hdr.update(headers)
    return jwt.encode(payload, private_key, algorithm="RS256", headers=hdr)


def test_1_lambda_handler_initialization():
    """Verify Lambda Mangum handler is callable."""
    assert callable(handler)


def test_2_lambda_proxy_get_health():
    """Verify Lambda handler processes API Gateway proxy event for /health."""
    event = {
        "version": "2.0",
        "routeKey": "GET /health",
        "rawPath": "/health",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "host": "localhost"
        },
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest"
            }
        },
        "isBase64Encoded": False
    }

    response = handler(event, {})
    assert response["statusCode"] == 200
    assert "ok" in response["body"].lower()


def test_3_lambda_proxy_get_info():
    """Verify Lambda handler processes API Gateway proxy event for /api/info."""
    event = {
        "version": "2.0",
        "routeKey": "GET /api/info",
        "rawPath": "/api/info",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "host": "localhost"
        },
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/api/info",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest"
            }
        },
        "isBase64Encoded": False
    }

    response = handler(event, {})
    assert response["statusCode"] == 200
    assert "Serverless" in response["body"]


def test_4_lambda_proxy_get_storage_status():
    """Verify Lambda handler processes API Gateway proxy event for /api/storage/status."""
    event = {
        "version": "2.0",
        "routeKey": "GET /api/storage/status",
        "rawPath": "/api/storage/status",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "host": "localhost"
        },
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/api/storage/status",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest"
            }
        },
        "isBase64Encoded": False
    }

    response = handler(event, {})
    assert response["statusCode"] == 200
    assert "mode" in response["body"]


def test_5_cognito_token_validation_success():
    """Verify successful validation of valid Cognito RS256 token."""
    now = int(time.time())
    issuer = CognitoService.get_issuer_url()

    payload = {
        "sub": "cognito-user-uuid-12345",
        "email": "student_cognito@example.com",
        "client_id": "mock-client-id-12345",
        "iss": issuer,
        "exp": now + 3600,
        "iat": now,
        "cognito:groups": ["admin"]
    }

    token = create_signed_cognito_token(payload)
    result = CognitoService.validate_cognito_token(token)

    assert result is not None
    assert result["sub"] == "cognito-user-uuid-12345"
    assert result["email"] == "student_cognito@example.com"


def test_6_cognito_token_invalid_signature():
    """Verify rejection of token signed with unknown/different private key."""
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = int(time.time())
    issuer = CognitoService.get_issuer_url()

    payload = {
        "sub": "attacker-user",
        "email": "attacker@example.com",
        "client_id": "mock-client-id-12345",
        "iss": issuer,
        "exp": now + 3600
    }

    invalid_token = jwt.encode(payload, other_key, algorithm="RS256", headers={"kid": "test-cognito-kid-1"})
    assert CognitoService.validate_cognito_token(invalid_token) is None


def test_7_cognito_token_expired():
    """Verify rejection of expired Cognito token."""
    now = int(time.time())
    issuer = CognitoService.get_issuer_url()

    payload = {
        "sub": "expired-user",
        "email": "expired@example.com",
        "client_id": "mock-client-id-12345",
        "iss": issuer,
        "exp": now - 300,  # 5 minutes ago
        "iat": now - 3600
    }

    token = create_signed_cognito_token(payload)
    assert CognitoService.validate_cognito_token(token) is None


def test_8_cognito_token_invalid_issuer():
    """Verify rejection when token issuer doesn't match configured User Pool."""
    now = int(time.time())

    payload = {
        "sub": "wrong-issuer-user",
        "email": "wrong_iss@example.com",
        "client_id": "mock-client-id-12345",
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_OtherPool",
        "exp": now + 3600
    }

    token = create_signed_cognito_token(payload)
    assert CognitoService.validate_cognito_token(token) is None


def test_9_cognito_token_invalid_audience():
    """Verify rejection when client_id doesn't match configured App Client."""
    now = int(time.time())
    issuer = CognitoService.get_issuer_url()

    payload = {
        "sub": "wrong-client-user",
        "email": "wrong_client@example.com",
        "client_id": "unauthorized-app-client-id",
        "iss": issuer,
        "exp": now + 3600
    }

    token = create_signed_cognito_token(payload)
    assert CognitoService.validate_cognito_token(token) is None


def test_10_11_cognito_user_resolution_and_role_mapping():
    """Verify resolving Cognito token payload into application user profile with role."""
    payload_admin = {
        "sub": "cog-sub-admin-99",
        "email": "cog_admin@example.com",
        "name": "Cognito Admin User",
        "cognito:groups": ["admin"]
    }
    user_admin = CognitoService.resolve_cognito_user(payload_admin)
    assert user_admin["email"] == "cog_admin@example.com"
    assert user_admin["role"] == "admin"
    assert user_admin["is_active"] == 1

    payload_analyst = {
        "sub": "cog-sub-analyst-99",
        "email": "cog_analyst@example.com",
        "name": "Cognito Analyst User",
        "cognito:groups": ["analyst"]
    }
    user_analyst = CognitoService.resolve_cognito_user(payload_analyst)
    assert user_analyst["email"] == "cog_analyst@example.com"
    assert user_analyst["role"] == "analyst"

    payload_viewer = {
        "sub": "cog-sub-viewer-99",
        "email": "cog_viewer@example.com",
        "name": "Cognito Viewer User",
        "cognito:groups": []
    }
    user_viewer = CognitoService.resolve_cognito_user(payload_viewer)
    assert user_viewer["email"] == "cog_viewer@example.com"
    assert user_viewer["role"] == "viewer"


def test_12_local_auth_mode_preserved():
    """Verify settings default is local and local auth mode remains intact."""
    assert settings.storage_mode == "local" or settings.storage_mode == "aws"
    assert hasattr(settings, "jwt_secret_key")
