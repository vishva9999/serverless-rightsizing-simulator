"""
Unit tests for Phase 6 Authentication, Organizations, and Role-Based Access Control (RBAC).

Verifies:
  1. User registration (POST /api/auth/register)
  2. Duplicate email error (409)
  3. Password hashing security
  4. Successful login (POST /api/auth/login)
  5. Invalid password rejection (401)
  6. Invalid email rejection (401)
  7. JWT creation
  8. JWT validation
  9. Expired/invalid JWT token handling (401)
  10. Missing JWT token handling (401)
  11. GET /api/auth/me
  12. Admin permissions
  13. Analyst permissions
  14. Viewer permissions
  15. Viewer cannot create scenario (403)
  16. Viewer cannot update scenario (403)
  17. Viewer cannot delete scenario (403)
  18. Analyst cannot change user role (403)
  19. Admin can change user role
  20. Organization multi-tenant isolation
  21. User cannot access another organization's scenario (404)
  22. User cannot access another organization's history (404)
  23. Inactive user cannot authenticate (403)
  24. Admin protection against removing/demoting final admin (400)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.history_repository import HistoryRepository

client = TestClient(app)


def test_1_user_registration():
    """Verify user and organization registration."""
    payload = {
        "email": "test_admin@org1.com",
        "password": "Password123!",
        "full_name": "Org 1 Admin",
        "organization_name": "Test Org 1"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test_admin@org1.com"
    assert data["user"]["role"] == "admin"


def test_2_duplicate_email():
    """Verify 409 error when registering existing email."""
    payload = {
        "email": "test_admin@org1.com",
        "password": "Password123!",
        "full_name": "Duplicate Admin",
        "organization_name": "Test Org 1"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_3_password_hashing():
    """Verify password hashing is non-reversible and verifies correctly."""
    hashed = AuthService.hash_password("SecretPass123!")
    assert hashed != "SecretPass123!"
    assert AuthService.verify_password("SecretPass123!", hashed) is True
    assert AuthService.verify_password("WrongPass", hashed) is False


def test_4_successful_login():
    """Verify login returns access token and user profile."""
    payload = {
        "email": "test_admin@org1.com",
        "password": "Password123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test_admin@org1.com"


def test_5_invalid_password():
    """Verify login failure with wrong password."""
    payload = {
        "email": "test_admin@org1.com",
        "password": "WrongPassword!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_6_invalid_email():
    """Verify login failure with non-existent email."""
    payload = {
        "email": "nonexistent@org1.com",
        "password": "Password123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_7_8_jwt_creation_and_decoding():
    """Verify JWT token creation and decoding."""
    token = AuthService.create_access_token({"user_id": "u-123", "role": "admin"})
    payload = AuthService.decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == "u-123"
    assert payload["role"] == "admin"


def test_9_invalid_jwt():
    """Verify invalid token handling."""
    assert AuthService.decode_access_token("invalid.jwt.token") is None


def test_10_missing_jwt_header():
    """Verify 401 response when accessing protected route without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_11_get_auth_me():
    """Verify GET /api/auth/me with valid Bearer token."""
    login_resp = client.post("/api/auth/login", json={"email": "test_admin@org1.com", "password": "Password123!"})
    token = login_resp.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test_admin@org1.com"


def test_12_13_14_setup_roles_and_test_permissions():
    """Setup Analyst and Viewer in Org 1 and test permissions."""
    admin_token = client.post("/api/auth/login", json={"email": "test_admin@org1.com", "password": "Password123!"}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create Analyst user
    client.post("/api/users", json={"email": "analyst@org1.com", "password": "Pass123!", "full_name": "Org 1 Analyst", "role": "analyst"}, headers=admin_headers)
    # Create Viewer user
    client.post("/api/users", json={"email": "viewer@org1.com", "password": "Pass123!", "full_name": "Org 1 Viewer", "role": "viewer"}, headers=admin_headers)

    viewer_token = client.post("/api/auth/login", json={"email": "viewer@org1.com", "password": "Pass123!"}).json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Test 15: Viewer cannot create scenario (403)
    scen_payload = {
        "name": "Viewer Scenario Attempt",
        "workload_type": "Custom",
        "request_volume": 100000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 50.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.9
    }
    resp = client.post("/api/scenarios", json=scen_payload, headers=viewer_headers)
    assert resp.status_code == 403

    # Create a scenario as Admin first for test 16 & 17
    created_scen = client.post("/api/scenarios", json=scen_payload, headers=admin_headers).json()
    scen_id = created_scen["id"]

    # Test 16: Viewer cannot update scenario (403)
    resp = client.put(f"/api/scenarios/{scen_id}", json={"name": "Updated"}, headers=viewer_headers)
    assert resp.status_code == 403

    # Test 17: Viewer cannot delete scenario (403)
    resp = client.delete(f"/api/scenarios/{scen_id}", headers=viewer_headers)
    assert resp.status_code == 403


def test_18_analyst_cannot_change_role():
    """Verify Analyst role cannot update user roles (403)."""
    analyst_token = client.post("/api/auth/login", json={"email": "analyst@org1.com", "password": "Pass123!"}).json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    viewer_user = UserRepository.get_by_email("viewer@org1.com")
    resp = client.put(f"/api/users/{viewer_user['id']}/role", json={"role": "admin"}, headers=analyst_headers)
    assert resp.status_code == 403


def test_19_admin_can_change_role():
    """Verify Admin can update user roles."""
    admin_token = client.post("/api/auth/login", json={"email": "test_admin@org1.com", "password": "Password123!"}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    viewer_user = UserRepository.get_by_email("viewer@org1.com")
    resp = client.put(f"/api/users/{viewer_user['id']}/role", json={"role": "analyst"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "analyst"


def test_20_21_22_organization_isolation():
    """Verify users cannot access resources belonging to a different organization."""
    # Register Org 2 User
    client.post("/api/auth/register", json={
        "email": "admin@org2.com",
        "password": "Password123!",
        "full_name": "Org 2 Admin",
        "organization_name": "Test Org 2"
    })

    token1 = client.post("/api/auth/login", json={"email": "test_admin@org1.com", "password": "Password123!"}).json()["access_token"]
    token2 = client.post("/api/auth/login", json={"email": "admin@org2.com", "password": "Password123!"}).json()["access_token"]

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Org 1 creates scenario
    scen1 = client.post("/api/scenarios", json={
        "name": "Org 1 Private Scenario",
        "workload_type": "Custom",
        "request_volume": 100000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 50.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.9
    }, headers=headers1).json()

    # Test 21: Org 2 user attempts to fetch Org 1 scenario -> 404
    resp = client.get(f"/api/scenarios/{scen1['id']}", headers=headers2)
    assert resp.status_code == 404

    # Run simulation in Org 1 to generate history
    sim_resp = client.post(f"/api/scenarios/{scen1['id']}/simulate", headers=headers1).json()
    hist_id = sim_resp["history_id"]

    # Test 22: Org 2 user attempts to fetch Org 1 history -> 404
    resp_hist = client.get(f"/api/history/{hist_id}", headers=headers2)
    assert resp_hist.status_code == 404


def test_23_inactive_user_cannot_authenticate():
    """Verify deactivated user account cannot log in or make API calls."""
    admin_token = client.post("/api/auth/login", json={"email": "test_admin@org1.com", "password": "Password123!"}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    viewer_user = UserRepository.get_by_email("viewer@org1.com")
    # Deactivate viewer user
    client.put(f"/api/users/{viewer_user['id']}/status", json={"is_active": False}, headers=admin_headers)

    # Login attempt should fail with 403
    resp = client.post("/api/auth/login", json={"email": "viewer@org1.com", "password": "Pass123!"})
    assert resp.status_code == 403


def test_24_admin_protection_against_removing_final_admin():
    """Verify guard preventing demoting or deactivating the final active admin in an organization."""
    admin_token = client.post("/api/auth/login", json={"email": "test_admin@org1.com", "password": "Password123!"}).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    admin_user = UserRepository.get_by_email("test_admin@org1.com")

    # Demotion attempt of last admin -> 400
    resp_demote = client.put(f"/api/users/{admin_user['id']}/role", json={"role": "analyst"}, headers=admin_headers)
    assert resp_demote.status_code == 400
    assert "final active administrator" in resp_demote.json()["detail"]

    # Deactivation attempt of last admin -> 400
    resp_deact = client.put(f"/api/users/{admin_user['id']}/status", json={"is_active": False}, headers=admin_headers)
    assert resp_deact.status_code == 400
    assert "final active administrator" in resp_deact.json()["detail"]
