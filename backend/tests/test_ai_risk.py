import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.services.ai_risk_service import AIRiskPredictionPipeline
from app.schemas.ai import AIRiskPredictionRequest
from app.schemas.simulation import DisasterTypeEnum, RiskLevelEnum


@pytest.fixture
def auth_header(client: TestClient) -> dict:
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "DemoAdminPass123!"},
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── 1. Model Loading & Pipeline Training Tests ────────────────────────────────

def test_ai_pipeline_trains_and_computes_real_metrics():
    """Verify models train, evaluate on test split, and compute authentic non-fabricated metrics."""
    metrics = AIRiskPredictionPipeline.train_models()
    assert "random_forest" in metrics
    assert "gradient_boosting" in metrics

    rf_m = metrics["random_forest"]
    assert 0.0 < rf_m.mae < 15.0  # realistic MAE on 0-100 scale
    assert 0.0 < rf_m.rmse < 20.0
    assert 0.60 < rf_m.r2 <= 1.0   # strong predictive fit on physical synthetic dataset
    assert 0.60 < rf_m.accuracy <= 1.0


def test_ai_predict_deterministic_for_same_input():
    """Verify inference yields reproducible outputs for identical inputs."""
    req = AIRiskPredictionRequest(
        disaster_type=DisasterTypeEnum.FLOOD,
        rainfall=220.0,
        water_level=5.0,
        wind_speed=40.0,
        population_density=3500.0,
        building_density=1100.0,
        road_accessibility=65.0,
        historical_risk=0.7,
        selected_model="random_forest",
    )
    res1 = AIRiskPredictionPipeline.predict_risk(req)
    res2 = AIRiskPredictionPipeline.predict_risk(req)

    assert res1.predicted_risk_score == res2.predicted_risk_score
    assert res1.risk_category == res2.risk_category
    assert res1.model_name == res2.model_name


# ─── 2. Model Comparison Tests ────────────────────────────────────────────────

def test_ai_predict_both_models():
    """Verify user can request prediction via Random Forest or Gradient Boosting."""
    req_rf = AIRiskPredictionRequest(
        disaster_type=DisasterTypeEnum.CYCLONE,
        rainfall=180.0,
        wind_speed=150.0,
        selected_model="random_forest",
    )
    req_gb = AIRiskPredictionRequest(
        disaster_type=DisasterTypeEnum.CYCLONE,
        rainfall=180.0,
        wind_speed=150.0,
        selected_model="gradient_boosting",
    )

    res_rf = AIRiskPredictionPipeline.predict_risk(req_rf)
    res_gb = AIRiskPredictionPipeline.predict_risk(req_gb)

    assert res_rf.model_name == "Random Forest Regressor"
    assert res_gb.model_name == "Gradient Boosting Regressor"
    assert 0.0 <= res_rf.predicted_risk_score <= 100.0
    assert 0.0 <= res_gb.predicted_risk_score <= 100.0
    assert res_rf.is_simulated is True
    assert res_gb.is_simulated is True


# ─── 3. Input Validation Tests ────────────────────────────────────────────────

def test_invalid_inputs_rejected():
    """Verify out-of-range parameters are rejected."""
    with pytest.raises(ValidationError):
        AIRiskPredictionRequest(
            disaster_type=DisasterTypeEnum.FLOOD,
            rainfall=-50.0,
        )

    with pytest.raises(ValidationError):
        AIRiskPredictionRequest(
            disaster_type=DisasterTypeEnum.FLOOD,
            road_accessibility=150.0,
        )


# ─── 4. API Endpoint Tests ───────────────────────────────────────────────────

def test_api_predict_risk_endpoint(client: TestClient, auth_header: dict):
    """POST /api/v1/ai/risk/predict returns structured predictions and metadata."""
    payload = {
        "disaster_type": "URBAN_FIRE",
        "rainfall": 5.0,
        "water_level": 0.0,
        "wind_speed": 65.0,
        "population_density": 4200.0,
        "building_density": 1800.0,
        "road_accessibility": 70.0,
        "historical_risk": 0.8,
        "selected_model": "random_forest",
    }
    res = client.post("/api/v1/ai/risk/predict", json=payload, headers=auth_header)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert "predicted_risk_score" in data
    assert 0.0 <= data["predicted_risk_score"] <= 100.0
    assert data["risk_category"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert data["model_name"] == "Random Forest Regressor"
    assert "model_metrics" in data
    assert "mae" in data["model_metrics"]
    assert "rmse" in data["model_metrics"]
    assert "comparison" in data
    assert data["is_simulated"] is True
    assert "simulated" in data["disclaimer"].lower()


def test_api_predict_unauthenticated_rejected(client: TestClient):
    """Verify endpoint enforces authentication."""
    res = client.post("/api/v1/ai/risk/predict", json={"disaster_type": "FLOOD"})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
