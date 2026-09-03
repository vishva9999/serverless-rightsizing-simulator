"""
Unit tests for Phase 3 Scenario Management & Simulation History.

Verifies:
  1. Create scenario (POST /api/scenarios)
  2. List scenarios (GET /api/scenarios)
  3. Get scenario by ID (GET /api/scenarios/{id})
  4. Update scenario (PUT /api/scenarios/{id})
  5. Delete scenario (DELETE /api/scenarios/{id})
  6. Run simulation from scenario (POST /api/scenarios/{id}/simulate)
  7. Verify automatic history record creation
  8. List history entries (GET /api/history)
  9. Get history detail (GET /api/history/{id})
 10. Delete history entry (DELETE /api/history/{id})
 11. Compare two simulation runs (GET /api/history/compare/{id1}/{id2})
 12. Handling 404 Not Found and validation errors
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient

# Set temporary DB path for tests before importing app
tmp_db_file = os.path.join(tempfile.gettempdir(), "test_simulator.db")
if os.path.exists(tmp_db_file):
    os.remove(tmp_db_file)
os.environ["DB_PATH"] = tmp_db_file

from app.main import app
from app.db.database import init_db
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

init_db()
client = TestClient(app)

# Create real test user in DB for get_current_user lookup
test_user = UserRepository.create(
    email="test_scen_admin@example.com",
    password_hash="hash",
    full_name="Scen Test Admin",
    organization_id="default-org",
    role="admin",
    is_active=True
)

auth_token = AuthService.create_access_token({
    "user_id": test_user["id"],
    "organization_id": "default-org",
    "role": "admin"
})
auth_headers = {"Authorization": f"Bearer {auth_token}"}


def test_1_seed_presets_on_init():
    """Verify that 3 preset scenarios are seeded when DB is created."""
    response = client.get("/api/scenarios", headers=auth_headers)
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) >= 3
    preset_names = [s["name"] for s in scenarios]
    assert "Low Traffic" in preset_names
    assert "Normal Traffic" in preset_names
    assert "High Traffic" in preset_names


def test_2_create_scenario():
    payload = {
        "name": "Custom E-Commerce Peak",
        "description": "Black Friday traffic surge test",
        "workload_type": "Custom",
        "request_volume": 5000000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 180.0,
        "cpu_utilization": 75.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.9
    }
    response = client.post("/api/scenarios", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Custom E-Commerce Peak"
    assert data["workload_type"] == "Custom"


def test_3_get_scenario_by_id():
    payload = {
        "name": "Test Fetch",
        "workload_type": "Normal Traffic",
        "request_volume": 1000000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 50.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.5
    }
    created = client.post("/api/scenarios", json=payload, headers=auth_headers).json()
    scenario_id = created["id"]

    response = client.get(f"/api/scenarios/{scenario_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Fetch"


def test_4_update_scenario():
    payload = {
        "name": "To Update",
        "workload_type": "Custom",
        "request_volume": 1000000,
        "baseline_memory_mb": 512.0,
        "baseline_latency_ms": 200.0,
        "cpu_utilization": 40.0,
        "current_price": 0.00001667,
        "latency_target_ms": 300.0,
        "availability_target_percent": 99.0
    }
    created = client.post("/api/scenarios", json=payload, headers=auth_headers).json()
    scenario_id = created["id"]

    update_payload = {
        "name": "Updated Scenario Name",
        "request_volume": 2500000
    }
    response = client.put(f"/api/scenarios/{scenario_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Updated Scenario Name"
    assert updated["request_volume"] == 2500000


def test_5_delete_scenario():
    payload = {
        "name": "To Delete",
        "workload_type": "Custom",
        "request_volume": 500000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 30.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.0
    }
    created = client.post("/api/scenarios", json=payload, headers=auth_headers).json()
    scenario_id = created["id"]

    del_res = client.delete(f"/api/scenarios/{scenario_id}", headers=auth_headers)
    assert del_res.status_code == 200

    get_res = client.get(f"/api/scenarios/{scenario_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_6_simulate_scenario_and_history_creation():
    payload = {
        "name": "Simulation Runner Scenario",
        "workload_type": "Normal Traffic",
        "request_volume": 2000000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 65.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.9
    }
    created = client.post("/api/scenarios", json=payload, headers=auth_headers).json()
    scenario_id = created["id"]

    sim_res = client.post(f"/api/scenarios/{scenario_id}/simulate", headers=auth_headers)
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["simulation_status"] == "success"
    assert "history_id" in sim_data

    # Verify history entry exists
    history_id = sim_data["history_id"]
    hist_res = client.get(f"/api/history/{history_id}", headers=auth_headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["scenario_id"] == scenario_id
    assert hist_data["recommended_memory_mb"] == 1024.0
    assert "simulation_detail" in hist_data


def test_7_list_and_filter_history():
    hist_list = client.get("/api/history", headers=auth_headers).json()
    assert isinstance(hist_list, list)
    assert len(hist_list) >= 1


def test_8_compare_simulation_runs():
    scenarios = client.get("/api/scenarios", headers=auth_headers).json()
    s1_id = scenarios[0]["id"]
    s2_id = scenarios[1]["id"]

    r1 = client.post(f"/api/scenarios/{s1_id}/simulate", headers=auth_headers).json()
    r2 = client.post(f"/api/scenarios/{s2_id}/simulate", headers=auth_headers).json()

    h1_id = r1["history_id"]
    h2_id = r2["history_id"]

    cmp_res = client.get(f"/api/history/compare/{h1_id}/{h2_id}", headers=auth_headers)
    assert cmp_res.status_code == 200
    cmp_data = cmp_res.json()

    assert "run_1" in cmp_data
    assert "run_2" in cmp_data
    assert "comparison_summary" in cmp_data
    assert cmp_data["run_1"]["id"] == h1_id
    assert cmp_data["run_2"]["id"] == h2_id


def test_9_delete_history_entry():
    scenarios = client.get("/api/scenarios", headers=auth_headers).json()
    s_id = scenarios[0]["id"]
    r = client.post(f"/api/scenarios/{s_id}/simulate", headers=auth_headers).json()
    h_id = r["history_id"]

    del_res = client.delete(f"/api/history/{h_id}", headers=auth_headers)
    assert del_res.status_code == 200

    get_res = client.get(f"/api/history/{h_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_10_scenario_not_found_404():
    res = client.get("/api/scenarios/non-existent-id", headers=auth_headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_11_history_not_found_404():
    res = client.get("/api/history/non-existent-id", headers=auth_headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_12_invalid_scenario_validation():
    invalid_payload = {
        "name": "",  # Empty name
        "workload_type": "Normal Traffic",
        "request_volume": -100,  # Negative request volume
        "baseline_memory_mb": 0.0,  # Invalid memory
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 150.0,  # > 100 CPU
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 80.0  # < 90 availability
    }
    res = client.post("/api/scenarios", json=invalid_payload, headers=auth_headers)
    assert res.status_code == 422
