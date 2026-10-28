from app.schemas.common import ApiResponse, ErrorDetail
from app.schemas.health import HealthResponse, DatabaseHealth, VersionResponse
from app.schemas.role import RoleBase, RoleCreate, RoleRead
from app.schemas.user import UserBase, UserCreate, UserRead
from app.schemas.disaster_event import DisasterEventBase, DisasterEventCreate, DisasterEventRead
from app.schemas.disaster_zone import DisasterZoneBase, DisasterZoneCreate, DisasterZoneRead
from app.schemas.zone_risk_history import ZoneRiskHistoryBase, ZoneRiskHistoryCreate, ZoneRiskHistoryRead
from app.schemas.shelter import (
    ShelterBase,
    ShelterCreate,
    ShelterUpdate,
    ShelterRead,
    ShelterCapacityHistoryRead,
)
from app.schemas.evacuation_route import EvacuationRouteBase, EvacuationRouteCreate, EvacuationRouteRead
from app.schemas.resource import (
    ResourceBase,
    ResourceCreate,
    ResourceRead,
    ResourceInventoryBase,
    ResourceInventoryCreate,
    ResourceInventoryRead,
)
from app.schemas.rescue_team import RescueTeamBase, RescueTeamCreate, RescueTeamRead
from app.schemas.vehicle import VehicleBase, VehicleCreate, VehicleRead
from app.schemas.assignment import (
    EvacuationAssignmentBase,
    EvacuationAssignmentCreate,
    EvacuationAssignmentRead,
    ResourceAssignmentBase,
    ResourceAssignmentCreate,
    ResourceAssignmentRead,
)
from app.schemas.simulation import (
    SimulationScenarioBase,
    SimulationScenarioCreate,
    SimulationScenarioRead,
    SimulationResultBase,
    SimulationResultCreate,
    SimulationResultRead,
)
from app.schemas.alert import AlertBase, AlertCreate, AlertRead
from app.schemas.audit_log import AuditLogBase, AuditLogCreate, AuditLogRead
from app.schemas.auth import (
    LoginRequest,
    Token,
    TokenPayload,
    AuthUserResponse,
    LoginResponse,
)

__all__ = [
    "ApiResponse",
    "ErrorDetail",
    "HealthResponse",
    "DatabaseHealth",
    "VersionResponse",
    "LoginRequest",
    "Token",
    "TokenPayload",
    "AuthUserResponse",
    "LoginResponse",
    "RoleBase",
    "RoleCreate",
    "RoleRead",
    "UserBase",
    "UserCreate",
    "UserRead",
    "DisasterEventBase",
    "DisasterEventCreate",
    "DisasterEventRead",
    "DisasterZoneBase",
    "DisasterZoneCreate",
    "DisasterZoneRead",
    "ZoneRiskHistoryBase",
    "ZoneRiskHistoryCreate",
    "ZoneRiskHistoryRead",
    "ShelterBase",
    "ShelterCreate",
    "ShelterUpdate",
    "ShelterRead",
    "ShelterCapacityHistoryRead",
    "EvacuationRouteBase",
    "EvacuationRouteCreate",
    "EvacuationRouteRead",
    "ResourceBase",
    "ResourceCreate",
    "ResourceRead",
    "ResourceInventoryBase",
    "ResourceInventoryCreate",
    "ResourceInventoryRead",
    "RescueTeamBase",
    "RescueTeamCreate",
    "RescueTeamRead",
    "VehicleBase",
    "VehicleCreate",
    "VehicleRead",
    "EvacuationAssignmentBase",
    "EvacuationAssignmentCreate",
    "EvacuationAssignmentRead",
    "ResourceAssignmentBase",
    "ResourceAssignmentCreate",
    "ResourceAssignmentRead",
    "SimulationScenarioBase",
    "SimulationScenarioCreate",
    "SimulationScenarioRead",
    "SimulationResultBase",
    "SimulationResultCreate",
    "SimulationResultRead",
    "AlertBase",
    "AlertCreate",
    "AlertRead",
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogRead",
]
