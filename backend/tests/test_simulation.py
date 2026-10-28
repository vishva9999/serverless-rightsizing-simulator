import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.services.simulation_service import DisasterSimulationEngine
from app.schemas.simulation import (
    SimulationInputParams,
    DisasterTypeEnum,
    RiskLevelEnum,
    DamageLevelEnum,
    EvacuationPriorityEnum,
)


@pytest.fixture
def auth_header(client: TestClient) -> dict:
    """Fixture to obtain authentication header for admin."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "DemoAdminPass123!"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── 1. Deterministic Seed Behavior Tests ──────────────────────────────────────

def test_deterministic_seed_identical_outputs():
    """Verify that running the engine with the exact same seed produces bit-identical outputs."""
    params1 = SimulationInputParams(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=180.0,
        water_level=3.5,
        wind_speed=40.0,
        road_condition=0.7,
        population_density=3500.0,
        random_seed=12345,
    )
    params2 = SimulationInputParams(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=180.0,
        water_level=3.5,
        wind_speed=40.0,
        road_condition=0.7,
        population_density=3500.0,
        random_seed=12345,
    )

    out1 = DisasterSimulationEngine.calculate_simulation(params1)
    out2 = DisasterSimulationEngine.calculate_simulation(params2)

    assert out1.risk_score == out2.risk_score
    assert out1.affected_population == out2.affected_population
    assert out1.road_accessibility == out2.road_accessibility
    assert out1.estimated_evacuation_time == out2.estimated_evacuation_time
    assert out1.risk_level == out2.risk_level
    assert len(out1.zone_impacts) == len(out2.zone_impacts)
    for z1, z2 in zip(out1.zone_impacts, out2.zone_impacts):
        assert z1.risk_score == z2.risk_score
        assert z1.affected_population == z2.affected_population


def test_different_seeds_produce_variation():
    """Verify different seeds introduce stochastic variations within bounded limits."""
    params1 = SimulationInputParams(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=200.0,
        random_seed=101,
    )
    params2 = SimulationInputParams(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=200.0,
        random_seed=999,
    )
    out1 = DisasterSimulationEngine.calculate_simulation(params1)
    out2 = DisasterSimulationEngine.calculate_simulation(params2)

    # Risk scores should be close due to shared physical parameters but not identical
    assert out1.risk_score != out2.risk_score or out1.affected_population != out2.affected_population


# ─── 2. Valid Disaster Types Tests ─────────────────────────────────────────────

@pytest.mark.parametrize("disaster_type", [
    DisasterTypeEnum.FLOOD,
    DisasterTypeEnum.CYCLONE,
    DisasterTypeEnum.EARTHQUAKE,
    DisasterTypeEnum.URBAN_FIRE,
    DisasterTypeEnum.LANDSLIDE,
])
def test_all_disaster_types_supported(disaster_type: DisasterTypeEnum):
    """Verify each of the 5 disaster types calculates valid outputs."""
    params = SimulationInputParams(
        disaster_type=disaster_type,
        rainfall=150.0,
        wind_speed=80.0,
        earthquake_intensity=6.2,
        temperature=38.0,
        random_seed=42,
    )
    output = DisasterSimulationEngine.calculate_simulation(params)
    assert 0.0 <= output.risk_score <= 100.0
    assert output.risk_level in [RiskLevelEnum.LOW, RiskLevelEnum.MEDIUM, RiskLevelEnum.HIGH, RiskLevelEnum.CRITICAL]
    assert output.estimated_damage_level in [DamageLevelEnum.MINOR, DamageLevelEnum.MODERATE, DamageLevelEnum.SEVERE, DamageLevelEnum.CATASTROPHIC]
    assert output.evacuation_priority in [EvacuationPriorityEnum.LOW, EvacuationPriorityEnum.MEDIUM, EvacuationPriorityEnum.HIGH, EvacuationPriorityEnum.IMMEDIATE]
    assert output.is_simulated is True


# ─── 3. Output Ranges Tests ───────────────────────────────────────────────────

def test_output_ranges_extreme_values():
    """Verify outputs never exceed legitimate domain bounds under extreme inputs."""
    # Maximum stress parameters
    max_params = SimulationInputParams(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=1000.0,
        water_level=50.0,
        wind_speed=400.0,
        earthquake_intensity=10.0,
        temperature=60.0,
        road_condition=0.0,
        population_density=100000.0,
        building_density=50000.0,
        historical_risk=1.0,
        time_of_day="night",
    )
    max_out = DisasterSimulationEngine.calculate_simulation(max_params)
    assert max_out.risk_score <= 100.0
    assert max_out.road_accessibility >= 5.0  # Safe floor
    assert max_out.risk_level == RiskLevelEnum.CRITICAL
    assert max_out.evacuation_priority == EvacuationPriorityEnum.IMMEDIATE

    # Minimum parameters
    min_params = SimulationInputParams(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=0.0,
        water_level=0.0,
        wind_speed=0.0,
        earthquake_intensity=0.0,
        temperature=20.0,
        road_condition=1.0,
        population_density=100.0,
        building_density=50.0,
        historical_risk=0.0,
        time_of_day="day",
    )
    min_out = DisasterSimulationEngine.calculate_simulation(min_params)
    assert min_out.risk_score >= 0.0
    assert min_out.road_accessibility <= 100.0
    assert min_out.risk_level in [RiskLevelEnum.LOW, RiskLevelEnum.MEDIUM]


# ─── 4. Invalid Inputs Tests ───────────────────────────────────────────────────

def test_invalid_input_validation_errors():
    """Ensure out-of-range inputs trigger Pydantic validation errors."""
    with pytest.raises(ValidationError):
        # Negative rainfall
        SimulationInputParams(disaster_type=DisasterTypeEnum.FLOOD, rainfall=-10.0)

    with pytest.raises(ValidationError):
        # Earthquake Richter > 10.0
        SimulationInputParams(disaster_type=DisasterTypeEnum.EARTHQUAKE, earthquake_intensity=15.0)

    with pytest.raises(ValidationError):
        # Road condition > 1.0
        SimulationInputParams(disaster_type=DisasterTypeEnum.FLOOD, road_condition=1.5)


# ─── 5. API Endpoints Tests ───────────────────────────────────────────────────

def test_api_list_scenarios_auto_seeds_demo(client: TestClient, auth_header: dict):
    """GET /api/v1/simulation/scenarios should return scenarios and ensure demo exists."""
    res = client.get("/api/v1/simulation/scenarios", headers=auth_header)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Verify canonical demo exists
    demo = next((s for s in data if s["name"] == "Coimbatore Flood Simulation - DEMO"), None)
    assert demo is not None
    assert demo["disaster_type"] == "FLOOD"


def test_api_create_and_run_simulation_scenario(client: TestClient, auth_header: dict):
    """POST create scenario -> POST run scenario -> GET results."""
    # 1. Create
    payload = {
        "name": "Peelamedu Cyclone Drill - TEST",
        "disaster_type": "CYCLONE",
        "description": "Simulation of severe cyclone landfall in eastern Coimbatore.",
        "random_seed": 777,
        "parameters": {
            "disaster_type": "CYCLONE",
            "wind_speed": 165.0,
            "rainfall": 180.0,
            "water_level": 2.2,
            "temperature": 27.0,
            "road_condition": 0.6,
            "population_density": 4500.0,
            "building_density": 1200.0,
            "historical_risk": 0.6,
            "time_of_day": "night",
            "random_seed": 777,
        },
    }
    create_res = client.post("/api/v1/simulation/scenarios", json=payload, headers=auth_header)
    assert create_res.status_code == status.HTTP_201_CREATED
    scenario = create_res.json()
    scenario_id = scenario["id"]
    assert scenario["name"] == "Peelamedu Cyclone Drill - TEST"
    assert scenario["status"] == "CREATED"

    # 2. Get Scenario
    get_res = client.get(f"/api/v1/simulation/scenarios/{scenario_id}", headers=auth_header)
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["id"] == scenario_id

    # 3. Run Scenario
    run_res = client.post(f"/api/v1/simulation/scenarios/{scenario_id}/run", headers=auth_header)
    assert run_res.status_code == status.HTTP_200_OK
    run_data = run_res.json()
    assert run_data["status"] == "COMPLETED"
    assert "outputs" in run_data
    assert run_data["outputs"]["risk_score"] > 0.0
    assert run_data["outputs"]["is_simulated"] is True
    assert "zone_impacts" in run_data["outputs"]

    # 4. Get Scenario Results
    results_res = client.get(f"/api/v1/simulation/scenarios/{scenario_id}/results", headers=auth_header)
    assert results_res.status_code == status.HTTP_200_OK
    results = results_res.json()
    assert len(results) >= 1
    assert results[0]["scenario_id"] == scenario_id
    assert results[0]["average_risk_score"] > 0


def test_api_unauthenticated_simulation_access_denied(client: TestClient):
    """Verify unauthenticated requests cannot access simulation endpoints."""
    res = client.get("/api/v1/simulation/scenarios")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
