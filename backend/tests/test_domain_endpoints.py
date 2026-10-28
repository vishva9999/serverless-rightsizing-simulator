import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def auth_headers(client: TestClient):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "DemoAdminPass123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_shelters_endpoint(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/shelters", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_id = data[0]["id"]

    # Toggle intake
    toggle_res = client.post(f"/api/v1/shelters/{first_id}/toggle-intake", headers=auth_headers)
    assert toggle_res.status_code == 200


def test_zones_endpoint(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/zones", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_id = data[0]["id"]

    # Pulse test
    pulse_res = client.post(f"/api/v1/zones/{first_id}/pulse?risk_delta=5.0", headers=auth_headers)
    assert pulse_res.status_code == 200
    assert pulse_res.json()["risk_score"] >= 5.0


def test_evacuation_routes_endpoint(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/evacuation/routes", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_id = data[0]["id"]

    # Contraflow toggle
    cf_res = client.post(f"/api/v1/evacuation/routes/{first_id}/contraflow", headers=auth_headers)
    assert cf_res.status_code == 200


def test_resources_fleet_supplies_endpoint(client: TestClient, auth_headers: dict):
    fleet_res = client.get("/api/v1/resources/fleet", headers=auth_headers)
    assert fleet_res.status_code == 200
    fleet = fleet_res.json()
    assert isinstance(fleet, list)
    assert len(fleet) > 0

    supplies_res = client.get("/api/v1/resources/supplies", headers=auth_headers)
    assert supplies_res.status_code == 200
    assert isinstance(supplies_res.json(), list)

    # Dispatch test
    first_v_id = fleet[0]["id"]
    dispatch_res = client.post(f"/api/v1/resources/dispatch?vehicle_id={first_v_id}&destination=Sector-North", headers=auth_headers)
    assert dispatch_res.status_code == 200
    assert dispatch_res.json()["success"] is True


def test_audit_logs_endpoint(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/audit-logs", headers=auth_headers)
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)

    create_res = client.post(
        "/api/v1/audit-logs",
        headers=auth_headers,
        json={
            "action": "SIMULATED_TEST_DRILL",
            "entity_type": "EXERCISE",
            "entity_id": "DRILL-01",
            "new_value": {"status": "SUCCESS"},
        },
    )
    assert create_res.status_code == 201


def test_analytics_summary_endpoint(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_simulated"] is True
    assert "shelters" in data
    assert "fleet" in data
    assert "zones" in data
    assert "evacuation" in data
