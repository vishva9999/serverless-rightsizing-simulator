from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.simulation import DisasterTypeEnum, RiskLevelEnum


class AIRiskPredictionRequest(BaseModel):
    disaster_type: DisasterTypeEnum = Field(..., description="Hazard type: FLOOD, CYCLONE, EARTHQUAKE, URBAN_FIRE, LANDSLIDE")
    rainfall: float = Field(default=120.0, ge=0.0, le=1000.0, description="Rainfall volume (mm)")
    water_level: float = Field(default=2.5, ge=0.0, le=50.0, description="Water level (m)")
    wind_speed: float = Field(default=45.0, ge=0.0, le=400.0, description="Wind speed (km/h)")
    population_density: float = Field(default=3000.0, ge=0.0, le=100000.0, description="Population density (per sq km)")
    building_density: float = Field(default=900.0, ge=0.0, le=50000.0, description="Building density (per sq km)")
    road_accessibility: float = Field(default=80.0, ge=0.0, le=100.0, description="Road accessibility percentage (0-100)")
    historical_risk: float = Field(default=0.5, ge=0.0, le=1.0, description="Historical zone vulnerability index (0-1)")
    selected_model: Optional[str] = Field(default="random_forest", description="'random_forest' or 'gradient_boosting'")


class ModelMetricDetail(BaseModel):
    mae: float
    rmse: float
    r2: float
    accuracy: float


class AIRiskPredictionResponse(BaseModel):
    predicted_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_category: RiskLevelEnum
    model_name: str
    model_version: str
    model_metrics: ModelMetricDetail
    comparison: Dict[str, ModelMetricDetail]
    feature_summary: Dict[str, Any]
    is_simulated: bool = True
    disclaimer: str = "AI prediction based on simulated training data. Strictly synthetic data for demonstration and training drills."
