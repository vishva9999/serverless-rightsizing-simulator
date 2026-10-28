from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class DisasterTypeEnum(str, Enum):
    FLOOD = "FLOOD"
    CYCLONE = "CYCLONE"
    EARTHQUAKE = "EARTHQUAKE"
    URBAN_FIRE = "URBAN_FIRE"
    LANDSLIDE = "LANDSLIDE"


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DamageLevelEnum(str, Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CATASTROPHIC = "CATASTROPHIC"


class EvacuationPriorityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    IMMEDIATE = "IMMEDIATE"


class SimulationInputParams(BaseModel):
    disaster_type: DisasterTypeEnum = Field(..., description="Type of disaster simulated")
    rainfall: float = Field(default=0.0, ge=0.0, le=1000.0, description="Precipitation in mm")
    water_level: float = Field(default=0.0, ge=0.0, le=50.0, description="Flood/river water level in meters")
    wind_speed: float = Field(default=0.0, ge=0.0, le=400.0, description="Wind speed in km/h")
    earthquake_intensity: float = Field(default=0.0, ge=0.0, le=10.0, description="Richter / intensity scale")
    temperature: float = Field(default=28.0, ge=-40.0, le=70.0, description="Ambient temperature in Celsius")
    road_condition: float = Field(default=0.8, ge=0.0, le=1.0, description="Road quality index: 1.0=pristine, 0.0=impassable")
    population_density: float = Field(default=2500.0, ge=0.0, le=100000.0, description="Population density / sq km")
    building_density: float = Field(default=800.0, ge=0.0, le=50000.0, description="Building density / sq km")
    historical_risk: float = Field(default=0.5, ge=0.0, le=1.0, description="Historical disaster vulnerability 0.0-1.0")
    time_of_day: str = Field(default="day", description="'day' or 'night' or hour")
    random_seed: Optional[int] = Field(default=42, description="Seed for deterministic stochastic components")


class ZoneSimulationImpact(BaseModel):
    zone_id: int
    zone_name: str
    risk_score: float
    risk_level: RiskLevelEnum
    affected_population: int
    evacuation_priority: EvacuationPriorityEnum
    road_accessibility_percent: float


class SimulationOutputData(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevelEnum
    affected_population: int = Field(..., ge=0)
    population_at_risk: int = Field(..., ge=0)
    road_accessibility: float = Field(..., ge=0.0, le=100.0)
    estimated_damage_level: DamageLevelEnum
    evacuation_priority: EvacuationPriorityEnum
    estimated_evacuation_time: float = Field(..., ge=0.0)
    resource_shortage_count: int = Field(default=0, ge=0)
    shelter_utilization: float = Field(default=0.0, ge=0.0, le=100.0)
    zone_impacts: List[ZoneSimulationImpact] = Field(default_factory=list)
    is_simulated: bool = Field(default=True)
    disclaimer: str = Field(default="SYNTHETIC SIMULATION DATA ONLY. NOT CONNECTED TO REAL EMERGENCY SERVICES.")


class SimulationScenarioBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    disaster_type: str
    description: Optional[str] = None
    random_seed: Optional[int] = 42
    parameters_json: Dict[str, Any] = Field(default_factory=dict)
    status: str = "CREATED"


class SimulationScenarioCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    disaster_type: DisasterTypeEnum
    description: Optional[str] = None
    random_seed: Optional[int] = 42
    parameters: Optional[SimulationInputParams] = None
    parameters_json: Optional[Dict[str, Any]] = None


class SimulationScenarioRead(SimulationScenarioBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimulationResultBase(BaseModel):
    scenario_id: int
    affected_population: int = Field(default=0, ge=0)
    population_at_risk: int = Field(default=0, ge=0)
    average_risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    estimated_evacuation_time: float = Field(default=0.0, ge=0.0)
    resource_shortage_count: int = Field(default=0, ge=0)
    shelter_utilization: float = Field(default=0.0, ge=0.0, le=100.0)
    result_json: Dict[str, Any] = Field(default_factory=dict)


class SimulationResultCreate(SimulationResultBase):
    pass


class SimulationResultRead(SimulationResultBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimulationRunResponse(BaseModel):
    scenario_id: int
    scenario_name: str
    disaster_type: str
    status: str
    result: SimulationResultRead
    outputs: SimulationOutputData
    is_simulated: bool = True
    disclaimer: str = "SYNTHETIC SIMULATION DATA ONLY. NOT CONNECTED TO REAL EMERGENCY SERVICES."
