import pytest
from app.models import (
    Base,
    Role,
    User,
    DisasterEvent,
    DisasterZone,
    ZoneRiskHistory,
    Shelter,
    ShelterCapacityHistory,
    EvacuationRoute,
    Resource,
    ResourceInventory,
    RescueTeam,
    Vehicle,
    EvacuationAssignment,
    ResourceAssignment,
    SimulationScenario,
    SimulationResult,
    Alert,
    AuditLog,
)


def test_all_18_models_have_tablename():
    """Verify all 18 domain models are mapped with declarative table names."""
    expected_tables = {
        "roles": Role,
        "users": User,
        "disaster_events": DisasterEvent,
        "disaster_zones": DisasterZone,
        "zone_risk_history": ZoneRiskHistory,
        "shelters": Shelter,
        "shelter_capacity_history": ShelterCapacityHistory,
        "evacuation_routes": EvacuationRoute,
        "resources": Resource,
        "resource_inventory": ResourceInventory,
        "rescue_teams": RescueTeam,
        "vehicles": Vehicle,
        "evacuation_assignments": EvacuationAssignment,
        "resource_assignments": ResourceAssignment,
        "simulation_scenarios": SimulationScenario,
        "simulation_results": SimulationResult,
        "alerts": Alert,
        "audit_logs": AuditLog,
    }

    assert len(expected_tables) == 18

    for table_name, model_cls in expected_tables.items():
        assert hasattr(model_cls, "__tablename__")
        assert model_cls.__tablename__ == table_name
        assert issubclass(model_cls, Base)


def test_metadata_contains_all_18_tables():
    """Verify SQLAlchemy metadata contains all 18 tables plus system tracking tables."""
    metadata_tables = set(Base.metadata.tables.keys())
    required_tables = {
        "roles",
        "users",
        "disaster_events",
        "disaster_zones",
        "zone_risk_history",
        "shelters",
        "shelter_capacity_history",
        "evacuation_routes",
        "resources",
        "resource_inventory",
        "rescue_teams",
        "vehicles",
        "evacuation_assignments",
        "resource_assignments",
        "simulation_scenarios",
        "simulation_results",
        "alerts",
        "audit_logs",
    }
    assert required_tables.issubset(metadata_tables)
