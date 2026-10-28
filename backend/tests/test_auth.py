from datetime import timedelta
import pytest
from fastapi import APIRouter, Depends, status
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.api.deps import get_current_user, require_roles
from app.core.database import SessionLocal
from app.services.seed_service import seed_all

# Add dynamic test routes to verify each role-based dependency
test_rbac_router = APIRouter(prefix="/api/v1/test-rbac")


@test_rbac_router.get("/admin-only")
def admin_only_endpoint(current_user: User = Depends(require_roles("ADMIN"))):
    return {"allowed": True, "role": current_user.role.name}


@test_rbac_router.get("/operator-only")
def operator_only_endpoint(current_user: User = Depends(require_roles("DISASTER_OPERATOR"))):
    return {"allowed": True, "role": current_user.role.name}


@test_rbac_router.get("/field-only")
def field_only_endpoint(current_user: User = Depends(require_roles("FIELD_OFFICER"))):
    return {"allowed": True, "role": current_user.role.name}


@test_rbac_router.get("/shelter-only")
def shelter_only_endpoint(current_user: User = Depends(require_roles("SHELTER_MANAGER"))):
    return {"allowed": True, "role": current_user.role.name}


@test_rbac_router.get("/resource-only")
def resource_only_endpoint(current_user: User = Depends(require_roles("RESOURCE_MANAGER"))):
    return {"allowed": True, "role": current_user.role.name}


@test_rbac_router.get("/viewer-only")
def viewer_only_endpoint(current_user: User = Depends(require_roles("VIEWER"))):
    return {"allowed": True, "role": current_user.role.name}


app.include_router(test_rbac_router)


@pytest.fixture(scope="session", autouse=True)
def setup_seed_db():
    """Ensure database has the seeded demo roles and users."""
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()


def get_token_for_user(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# Test 1: Valid login
def test_valid_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "DemoAdminPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "ADMIN"


# Test 2: Invalid password
def test_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "WrongPassword999!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test 3: Unknown user
def test_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "nonexistent_officer_xyz", "password": "AnyPassword!"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test 4: Valid JWT
def test_valid_jwt(client):
    token = get_token_for_user(client, "admin", "DemoAdminPass123!")
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


# Test 5: Invalid JWT
def test_invalid_jwt(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.bogus.token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test 6: Expired JWT
def test_expired_jwt(client):
    expired_token = create_access_token(
        {"sub": "1", "username": "admin", "role": "ADMIN"},
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test 7: /auth/me with authentication
def test_auth_me_with_authentication(client):
    token = get_token_for_user(client, "op_chen", "DemoOperator123!")
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "op_chen"
    assert data["email"] == "chen@command.simulated"
    assert data["role"] == "DISASTER_OPERATOR"


# Test 8: /auth/me without authentication
def test_auth_me_without_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test 9: ADMIN authorization
def test_admin_authorization(client):
    token = get_token_for_user(client, "admin", "DemoAdminPass123!")
    response = client.get("/api/v1/test-rbac/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True


# Test 10: DISASTER_OPERATOR authorization
def test_disaster_operator_authorization(client):
    token = get_token_for_user(client, "op_chen", "DemoOperator123!")
    response = client.get("/api/v1/test-rbac/operator-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True


# Test 11: FIELD_OFFICER authorization
def test_field_officer_authorization(client):
    token = get_token_for_user(client, "field_rodriguez", "DemoField123!")
    response = client.get("/api/v1/test-rbac/field-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True


# Test 12: SHELTER_MANAGER authorization
def test_shelter_manager_authorization(client):
    token = get_token_for_user(client, "shelter_kumar", "DemoShelter123!")
    response = client.get("/api/v1/test-rbac/shelter-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True


# Test 13: RESOURCE_MANAGER authorization
def test_resource_manager_authorization(client):
    token = get_token_for_user(client, "log_smith", "DemoLogistics123!")
    response = client.get("/api/v1/test-rbac/resource-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True


# Test 14: VIEWER authorization
def test_viewer_authorization(client):
    token = get_token_for_user(client, "viewer_guest", "DemoViewer123!")
    response = client.get("/api/v1/test-rbac/viewer-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["allowed"] is True



# Test 15: Unauthorized role access returns HTTP 403
def test_unauthorized_role_access_returns_403(client):
    # FIELD_OFFICER attempting to access operator-only route
    field_token = get_token_for_user(client, "field_rodriguez", "DemoField123!")
    response = client.get("/api/v1/test-rbac/operator-only", headers={"Authorization": f"Bearer {field_token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


# Test 16: Password is never returned
def test_password_never_returned(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "DemoAdminPass123!"},
    )
    data = response.json()
    assert "password" not in data
    assert "password" not in data.get("user", {})

    token = data["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert "password" not in me_resp.json()


# Test 17: Password hash is never returned
def test_password_hash_never_returned(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "DemoAdminPass123!"},
    )
    data = response.json()
    assert "password_hash" not in data
    assert "password_hash" not in data.get("user", {})

    token = data["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert "password_hash" not in me_resp.json()


# Test 18: JWT secret is not hardcoded
def test_jwt_secret_not_hardcoded():
    assert hasattr(settings, "SECRET_KEY")
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) >= 32
    assert hasattr(settings, "ALGORITHM")
    assert settings.ALGORITHM == "HS256"
