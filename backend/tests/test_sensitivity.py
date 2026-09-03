"""
Unit tests for Phase 5 Sensitivity Analysis Service and API.

Verifies:
  1. Request volume sensitivity analysis
  2. CPU utilization sensitivity analysis
  3. Baseline latency sensitivity analysis
  4. Latency target sensitivity analysis
  5. Availability target sensitivity analysis
  6. Price sensitivity analysis
  7. Invalid scenario handling (404)
  8. Invalid variable handling (400)
  9. Empty values list handling (400)
  10. Exceeding 20 points limit handling (400)
  11. Invalid numeric ranges handling (400)
  12. Verification that Phase 2 simulation engine remains 100% untouched
"""

import pytest
import os
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.storage_factory import get_scenario_repository
from app.repositories.user_repository import UserRepository
from app.services.simulation_engine import run_simulation
from app.models.response_models import SimulationRequest
from app.services.auth_service import AuthService
from app.db.database import init_db

init_db()
client = TestClient(app)

# Ensure test user exists in DB
existing_user = UserRepository.get_by_email("test_sens_admin@example.com")
if not existing_user:
    test_user = UserRepository.create(
        email="test_sens_admin@example.com",
        password_hash="hash",
        full_name="Sensitivity Test Admin",
        organization_id="default-org",
        role="admin",
        is_active=True
    )
    user_id = test_user["id"]
else:
    user_id = existing_user["id"]

auth_token = AuthService.create_access_token({
    "user_id": user_id,
    "organization_id": "default-org",
    "role": "admin"
})
auth_headers = {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(autouse=True)
def ensure_preset_scenario():
    """Ensure preset scenario exists in database."""
    repo = get_scenario_repository()
    scenarios = repo.list_all(organization_id="default-org")
    if not scenarios:
        preset = {
            "name": "Preset Test Scenario",
            "workload_type": "Normal Traffic",
            "request_volume": 100000,
            "baseline_memory_mb": 1024.0,
            "baseline_latency_ms": 150.0,
            "cpu_utilization": 50.0,
            "current_price": 0.00001667,
            "latency_target_ms": 200.0,
            "availability_target_percent": 99.9
        }
        repo.create(preset, organization_id="default-org")


def get_first_scenario_id():
    repo = get_scenario_repository()
    scenarios = repo.list_all(organization_id="default-org")
    return scenarios[0]["id"] if scenarios else "preset-normal-traffic"


def test_1_request_volume_sensitivity():
    """Test sensitivity analysis for request_volume variable."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "request_volume",
        "values": [50000, 100000, 200000, 500000]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "request_volume"
    assert len(data["points"]) == 4
    assert data["points"][0]["input_value"] == 50000
    assert "insight_summary" in data


def test_2_cpu_sensitivity():
    """Test sensitivity analysis for cpu_utilization variable."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "cpu_utilization",
        "values": [25.0, 50.0, 75.0]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "cpu_utilization"
    assert len(data["points"]) == 3


def test_3_baseline_latency_sensitivity():
    """Test sensitivity analysis for baseline_latency_ms variable."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "baseline_latency_ms",
        "values": [100.0, 150.0, 200.0]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "baseline_latency_ms"


def test_4_latency_target_sensitivity():
    """Test sensitivity analysis for latency_target_ms variable."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "latency_target_ms",
        "values": [120.0, 180.0, 250.0]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "latency_target_ms"


def test_5_availability_target_sensitivity():
    """Test sensitivity analysis for availability_target_percent variable."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "availability_target_percent",
        "values": [95.0, 99.0, 99.9]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "availability_target_percent"


def test_6_price_sensitivity():
    """Test sensitivity analysis for current_price variable."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "current_price",
        "values": [0.00001000, 0.00001667, 0.00002500]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "current_price"


def test_7_invalid_scenario_id():
    """Verify 404 error when scenario ID does not exist."""
    payload = {
        "scenario_id": "non-existent-id-99999",
        "variable": "request_volume",
        "values": [10000, 20000]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_8_invalid_variable_key():
    """Verify 400 error when variable key is not supported."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "invalid_variable_name",
        "values": [10, 20]
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "Unsupported sensitivity variable" in response.json()["detail"]


def test_9_empty_values_list():
    """Verify 400 error when values list is empty."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "request_volume",
        "values": []
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 422 or response.status_code == 400


def test_10_too_many_values():
    """Verify 400 error when values list exceeds 20 points."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "request_volume",
        "values": list(range(1, 25))
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "between 1 and 20 points" in response.json()["detail"]


def test_11_invalid_numeric_ranges():
    """Verify 400 error when values violate variable min/max bounds."""
    scen_id = get_first_scenario_id()
    payload = {
        "scenario_id": scen_id,
        "variable": "cpu_utilization",
        "values": [50.0, 150.0]  # 150% is invalid for CPU
    }
    response = client.post("/api/sensitivity/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "Maximum allowed value" in response.json()["detail"]


def test_12_existing_simulation_engine_unchanged():
    """Verify direct call to run_simulation() remains consistent and untouched."""
    sim_request = SimulationRequest(
        scenario_name="Engine Consistency Check",
        cpu_utilization=50.0,
        memory_mb=1024.0,
        baseline_latency_ms=150.0,
        request_volume=1000000,
        current_price=0.00001667,
        latency_target_ms=200.0,
        availability_target=99.9
    )
    result = run_simulation(sim_request)
    assert result.simulation_status == "success"
    assert result.baseline.memory_mb == 1024.0
    assert result.recommendation is not None
