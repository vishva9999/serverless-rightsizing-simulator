"""
Pydantic request and response models for all API endpoints.
Ensures automatic data validation and clear API contracts.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Any, Dict


class HealthResponse(BaseModel):
    """Response model for GET /health"""
    status: str
    message: str


class InfoResponse(BaseModel):
    """Response model for GET /api/info"""
    project_name: str
    version: str
    environment: str
    description: str
    phase: str


class DatasetInfo(BaseModel):
    """Summary of the loaded dataset structure."""
    total_records: int
    date_range_start: Optional[str]
    date_range_end: Optional[str]
    missing_values: dict[str, int]


class MetricsSummary(BaseModel):
    """
    Response model for GET /api/metrics/summary.
    Contains aggregated statistics computed from the synthetic CSV dataset.
    """
    average_cpu_utilization: float
    average_memory_mb: float
    average_latency_ms: float
    total_request_volume: int
    average_availability: float
    total_estimated_cost: float
    average_request_volume_per_interval: float
    dataset_info: DatasetInfo
    note: str


# =============================================================================
# PHASE 2: SIMULATION MODELS
# =============================================================================

class SimulationRequest(BaseModel):
    """
    Input request for POST /api/simulate.
    Validates input parameters according to phase 2 rules.
    """
    scenario_name: str = Field(..., description="Name of the workload scenario (e.g. Normal Traffic)")
    cpu_utilization: float = Field(..., ge=0.0, le=100.0, description="CPU utilization percentage (0-100)")
    memory_mb: float = Field(..., gt=0.0, description="Baseline memory allocation in MB (>0)")
    baseline_latency_ms: float = Field(..., gt=0.0, description="Baseline latency in milliseconds (>0)")
    request_volume: int = Field(..., ge=0, description="Monthly request volume (>=0)")
    current_price: float = Field(..., ge=0.0, description="Current price per unit / GB-sec (>=0)")
    latency_target_ms: float = Field(..., gt=0.0, description="Target maximum latency in ms (>0)")
    availability_target: float = Field(..., ge=90.0, le=100.0, description="Target availability percentage (90-100)")
    pricing_history: Optional[Any] = Field(default=None, description="Optional pricing history data")


class BaselineResult(BaseModel):
    """Summary of the current baseline configuration."""
    memory_mb: float
    estimated_monthly_cost: float
    latency_ms: float
    availability: float


class CandidateConfigResult(BaseModel):
    """Evaluated candidate configuration."""
    memory_mb: float
    estimated_monthly_cost: float
    estimated_latency_ms: float
    estimated_availability: float
    cost_savings_percentage: float
    latency_target_met: bool
    availability_target_met: bool
    feasible: bool


class RecommendationResult(BaseModel):
    """Selected optimal configuration recommendation."""
    memory_mb: float
    estimated_monthly_cost: float
    estimated_latency_ms: float
    estimated_availability: float
    cost_savings_percentage: float


class SimulationResponse(BaseModel):
    """Full simulation result response for POST /api/simulate."""
    simulation_status: str
    scenario_name: str
    baseline: BaselineResult
    configurations: List[CandidateConfigResult]
    recommendation: Optional[RecommendationResult] = None
    explanation: str
    disclaimer: str = "Simulation Estimate: This model is an educational approximation and not an official AWS billing or performance calculation."


# =============================================================================
# PHASE 3: SCENARIO & HISTORY MODELS
# =============================================================================

class ScenarioCreate(BaseModel):
    """Payload for creating a new Scenario (POST /api/scenarios)."""
    name: str = Field(..., min_length=1, description="Scenario name")
    description: Optional[str] = Field(default="", description="Optional description")
    workload_type: str = Field(..., description="Workload type: Low Traffic, Normal Traffic, High Traffic, Custom")
    request_volume: int = Field(..., ge=0, description="Monthly request volume")
    baseline_memory_mb: float = Field(..., gt=0.0, description="Baseline memory size in MB")
    baseline_latency_ms: float = Field(..., gt=0.0, description="Baseline execution duration in ms")
    cpu_utilization: float = Field(..., ge=0.0, le=100.0, description="Average CPU utilization percentage (0-100)")
    current_price: float = Field(..., ge=0.0, description="Price rate per GB-sec")
    latency_target_ms: float = Field(..., gt=0.0, description="Target maximum latency in ms")
    availability_target_percent: float = Field(..., ge=90.0, le=100.0, description="Target availability percentage (90-100)")


class ScenarioUpdate(BaseModel):
    """Payload for updating an existing Scenario (PUT /api/scenarios/{id})."""
    name: Optional[str] = None
    description: Optional[str] = None
    workload_type: Optional[str] = None
    request_volume: Optional[int] = Field(default=None, ge=0)
    baseline_memory_mb: Optional[float] = Field(default=None, gt=0.0)
    baseline_latency_ms: Optional[float] = Field(default=None, gt=0.0)
    cpu_utilization: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    current_price: Optional[float] = Field(default=None, ge=0.0)
    latency_target_ms: Optional[float] = Field(default=None, gt=0.0)
    availability_target_percent: Optional[float] = Field(default=None, ge=90.0, le=100.0)


class ScenarioResponse(BaseModel):
    """Response shape for a single Scenario object."""
    id: str
    name: str
    description: Optional[str] = ""
    workload_type: str
    request_volume: int
    baseline_memory_mb: float
    baseline_latency_ms: float
    cpu_utilization: float
    current_price: float
    latency_target_ms: float
    availability_target_percent: float
    organization_id: Optional[str] = "default-org"
    created_at: str
    updated_at: str


class HistoryItemResponse(BaseModel):
    """Summary item for GET /api/history."""
    id: str
    scenario_id: str
    scenario_name: str
    created_at: str
    recommended_memory_mb: Optional[float] = None
    recommended_cost: Optional[float] = None
    recommended_latency_ms: Optional[float] = None
    recommended_availability_percent: Optional[float] = None
    savings_percent: Optional[float] = None
    status: str
    organization_id: Optional[str] = "default-org"


class HistoryDetailResponse(HistoryItemResponse):
    """Detailed history item containing full simulation JSON response."""
    simulation_detail: Optional[Dict[str, Any]] = None


class HistoryCompareRun(BaseModel):
    id: str
    scenario_id: str
    scenario_name: str
    created_at: str
    recommended_memory_mb: Optional[float] = None
    recommended_cost: Optional[float] = None
    recommended_latency_ms: Optional[float] = None
    recommended_availability_percent: Optional[float] = None
    savings_percent: Optional[float] = None
    status: str


class ComparisonSummary(BaseModel):
    cost_difference: Optional[float] = None
    latency_difference_ms: Optional[float] = None
    same_recommendation: bool


class HistoryCompareResponse(BaseModel):
    """Response shape for GET /api/history/compare/{id1}/{id2}."""
    run_1: HistoryCompareRun
    run_2: HistoryCompareRun
    comparison_summary: ComparisonSummary


# =============================================================================
# PHASE 5: SENSITIVITY ANALYSIS MODELS
# =============================================================================

class SensitivityVariable(BaseModel):
    """Supported sensitivity variable metadata."""
    key: str
    label: str
    unit: str
    description: str


class SensitivityRequest(BaseModel):
    """Payload for POST /api/sensitivity/analyze."""
    scenario_id: str = Field(..., description="Target scenario ID")
    variable: str = Field(..., description="Target input variable key to vary")
    values: List[float] = Field(..., min_length=1, description="List of numeric test values to evaluate (max 20 points)")


class SensitivityPoint(BaseModel):
    """Evaluated sensitivity point result."""
    input_value: float
    recommended_memory_mb: Optional[float] = None
    recommended_cost: Optional[float] = None
    recommended_latency_ms: Optional[float] = None
    recommended_availability_percent: Optional[float] = None
    savings_percent: Optional[float] = None
    simulation_status: str


class SensitivityResponse(BaseModel):
    """Full sensitivity analysis result response."""
    scenario_id: str
    scenario_name: str
    variable: str
    variable_label: str
    baseline_value: float
    points: List[SensitivityPoint]
    insight_summary: str
    disclaimer: str = "Simulation Estimate: Sensitivity analysis results are educational models and not guaranteed AWS performance or cost metrics."


# =============================================================================
# PHASE 6: AUTHENTICATION, ORGANIZATIONS & RBAC MODELS
# =============================================================================

class UserRegister(BaseModel):
    """Registration request payload for POST /api/auth/register."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    full_name: str = Field(..., min_length=1, description="User full name")
    organization_name: str = Field(..., min_length=1, description="Organization name")


class UserLogin(BaseModel):
    """Login request payload for POST /api/auth/login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Public User profile response shape."""
    id: str
    email: str
    full_name: str
    organization_id: str
    role: str
    is_active: bool
    created_at: str
    updated_at: str


class TokenResponse(BaseModel):
    """Access Token response for successful login/registration."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserCreateByAdmin(BaseModel):
    """Payload for Admin creating a new user (POST /api/users)."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1)
    role: str = Field(default="analyst", description="Role: admin, analyst, or viewer")


class UserRoleUpdate(BaseModel):
    """Payload for updating user role (PUT /api/users/{id}/role)."""
    role: str = Field(..., description="Role: admin, analyst, or viewer")


class UserStatusUpdate(BaseModel):
    """Payload for updating user active status (PUT /api/users/{id}/status)."""
    is_active: bool


class OrganizationResponse(BaseModel):
    """Response shape for Organization object."""
    id: str
    name: str
    description: Optional[str] = ""
    member_count: int = 1
    created_at: str
    updated_at: str


class OrganizationUpdate(BaseModel):
    """Payload for updating Organization metadata (PUT /api/organizations/me)."""
    name: Optional[str] = None
    description: Optional[str] = None
