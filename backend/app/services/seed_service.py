from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.logging import logger
from app.core.security import get_password_hash
from app.models.role import Role, RoleEnum
from app.models.user import User
from app.models.disaster_event import DisasterEvent, DisasterTypeEnum, DisasterStatusEnum, SeverityEnum
from app.models.disaster_zone import DisasterZone, RiskLevelEnum, EvacuationPriorityEnum
from app.models.zone_risk_history import ZoneRiskHistory
from app.models.shelter import Shelter, ShelterStatusEnum, ShelterAccessibilityEnum
from app.models.shelter_capacity_history import ShelterCapacityHistory
from app.models.evacuation_route import EvacuationRoute, RouteStatusEnum
from app.models.resource import Resource, ResourceTypeEnum
from app.models.resource_inventory import ResourceInventory, InventoryStatusEnum
from app.models.rescue_team import RescueTeam, TeamStatusEnum
from app.models.vehicle import Vehicle, VehicleTypeEnum, VehicleStatusEnum
from app.models.evacuation_assignment import EvacuationAssignment, AssignmentStatusEnum
from app.models.resource_assignment import ResourceAssignment, ResourceAssignmentStatusEnum
from app.models.simulation_scenario import SimulationScenario, ScenarioStatusEnum
from app.models.simulation_result import SimulationResult
from app.models.alert import Alert, AlertSeverityEnum
from app.models.audit_log import AuditLog, sanitize_audit_payload


def seed_roles(db: Session) -> Dict[str, Role]:
    """Seed the 6 canonical roles idempotently."""
    role_definitions = [
        {"name": RoleEnum.ADMIN.value, "description": "System administrator with full access to configuration, users, and audit logs."},
        {"name": RoleEnum.DISASTER_OPERATOR.value, "description": "Incident commander / operational dispatcher managing events and zones."},
        {"name": RoleEnum.FIELD_OFFICER.value, "description": "Field personnel coordinating on-the-ground rescue teams."},
        {"name": RoleEnum.SHELTER_MANAGER.value, "description": "Personnel managing shelter occupancy, accessibility, and supplies."},
        {"name": RoleEnum.RESOURCE_MANAGER.value, "description": "Logistics coordinator managing emergency resource inventories."},
        {"name": RoleEnum.VIEWER.value, "description": "Read-only access for analysts, observers, and drill evaluators."},
    ]
    roles_by_name = {}
    for r_data in role_definitions:
        existing = db.scalars(select(Role).where(Role.name == r_data["name"])).first()
        if not existing:
            role = Role(name=r_data["name"], description=r_data["description"])
            db.add(role)
            db.flush()
            roles_by_name[r_data["name"]] = role
        else:
            existing.description = r_data["description"]
            roles_by_name[r_data["name"]] = existing
    db.commit()
    return roles_by_name


def seed_users(db: Session, roles: Dict[str, Role]) -> Dict[str, User]:
    """Seed the 5 demo users idempotently."""
    user_definitions = [
        {
            "username": "admin",
            "email": "admin@command.simulated",
            "full_name": "Commander Sarah Vance (DEMO)",
            "role_name": RoleEnum.ADMIN.value,
            "password": "DemoAdminPass123!",
        },
        {
            "username": "op_chen",
            "email": "chen@command.simulated",
            "full_name": "Operations Lead David Chen (DEMO)",
            "role_name": RoleEnum.DISASTER_OPERATOR.value,
            "password": "DemoOperator123!",
        },
        {
            "username": "field_rodriguez",
            "email": "rodriguez@command.simulated",
            "full_name": "Field Officer Maria Rodriguez (DEMO)",
            "role_name": RoleEnum.FIELD_OFFICER.value,
            "password": "DemoField123!",
        },
        {
            "username": "shelter_kumar",
            "email": "kumar@command.simulated",
            "full_name": "Shelter Coordinator Rajesh Kumar (DEMO)",
            "role_name": RoleEnum.SHELTER_MANAGER.value,
            "password": "DemoShelter123!",
        },
        {
            "username": "log_smith",
            "email": "smith@command.simulated",
            "full_name": "Logistics Chief Alex Smith (DEMO)",
            "role_name": RoleEnum.RESOURCE_MANAGER.value,
            "password": "DemoLogistics123!",
        },
        {
            "username": "viewer_guest",
            "email": "viewer@command.simulated",
            "full_name": "Simulation Analyst Alex Rivers (DEMO)",
            "role_name": RoleEnum.VIEWER.value,
            "password": "DemoViewer123!",
        },
    ]
    users_by_username = {}
    for u_data in user_definitions:
        existing = db.scalars(select(User).where(User.username == u_data["username"])).first()
        role = roles[u_data["role_name"]]
        if not existing:
            user = User(
                username=u_data["username"],
                email=u_data["email"],
                full_name=u_data["full_name"],
                password_hash=get_password_hash(u_data["password"]),
                role_id=role.id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            users_by_username[u_data["username"]] = user
        else:
            existing.email = u_data["email"]
            existing.full_name = u_data["full_name"]
            existing.role_id = role.id
            existing.is_active = True
            users_by_username[u_data["username"]] = existing
    db.commit()
    return users_by_username


def seed_disaster_events(db: Session) -> Dict[str, DisasterEvent]:
    """Seed 2 simulated disaster events idempotently."""
    now = datetime.now(timezone.utc)
    event_definitions = [
        {
            "name": "Coimbatore Flood Simulation - DEMO",
            "disaster_type": DisasterTypeEnum.FLOOD.value,
            "description": "Simulated severe monsoon urban inundation exercise. All data synthetic.",
            "severity": SeverityEnum.HIGH.value,
            "status": DisasterStatusEnum.ACTIVE.value,
            "start_time": now,
        },
        {
            "name": "Nilgiris Landslide Drill - DEMO",
            "disaster_type": DisasterTypeEnum.LANDSLIDE.value,
            "description": "Simulated seismic-induced hillside slope failure drill. All data synthetic.",
            "severity": SeverityEnum.CRITICAL.value,
            "status": DisasterStatusEnum.ACTIVE.value,
            "start_time": now,
        },
    ]
    events_by_name = {}
    for e_data in event_definitions:
        existing = db.scalars(select(DisasterEvent).where(DisasterEvent.name == e_data["name"])).first()
        if not existing:
            event = DisasterEvent(
                name=e_data["name"],
                disaster_type=e_data["disaster_type"],
                description=e_data["description"],
                severity=e_data["severity"],
                status=e_data["status"],
                start_time=e_data["start_time"],
            )
            db.add(event)
            db.flush()
            events_by_name[e_data["name"]] = event
        else:
            existing.severity = e_data["severity"]
            existing.status = e_data["status"]
            events_by_name[e_data["name"]] = existing
    db.commit()
    return events_by_name


def seed_disaster_zones(db: Session, events: Dict[str, DisasterEvent]) -> Dict[str, DisasterZone]:
    """Seed at least 10 disaster zones across the simulated events idempotently."""
    cbe_event = events["Coimbatore Flood Simulation - DEMO"]
    nil_event = events["Nilgiris Landslide Drill - DEMO"]

    zone_definitions = [
        {
            "disaster_event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-01",
            "zone_name": "RS Puram Lowland Sector (DEMO)",
            "latitude": 11.0088,
            "longitude": 76.9525,
            "population": 3200,
            "population_density": 420.0,
            "building_density": 65.0,
            "risk_score": 85.0,
            "risk_level": RiskLevelEnum.HIGH.value,
            "road_accessibility": 45.0,
            "evacuation_priority": EvacuationPriorityEnum.HIGH.value,
        },
        {
            "disaster_event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-02",
            "zone_name": "Ukkadam Lakefront Basin (DEMO)",
            "latitude": 10.9912,
            "longitude": 76.9610,
            "population": 4500,
            "population_density": 550.0,
            "building_density": 78.0,
            "risk_score": 92.0,
            "risk_level": RiskLevelEnum.CRITICAL.value,
            "road_accessibility": 30.0,
            "evacuation_priority": EvacuationPriorityEnum.CRITICAL.value,
        },
        {
            "disaster_event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-03",
            "zone_name": "Gandhipuram Commercial Corridor (DEMO)",
            "latitude": 11.0183,
            "longitude": 76.9678,
            "population": 2800,
            "population_density": 380.0,
            "building_density": 50.0,
            "risk_score": 68.0,
            "risk_level": RiskLevelEnum.MEDIUM.value,
            "road_accessibility": 70.0,
            "evacuation_priority": EvacuationPriorityEnum.MEDIUM.value,
        },
        {
            "disaster_event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-04",
            "zone_name": "Peelamedu Tech Cluster (DEMO)",
            "latitude": 11.0267,
            "longitude": 77.0090,
            "population": 1900,
            "population_density": 240.0,
            "building_density": 40.0,
            "risk_score": 42.0,
            "risk_level": RiskLevelEnum.LOW.value,
            "road_accessibility": 90.0,
            "evacuation_priority": EvacuationPriorityEnum.LOW.value,
        },
        {
            "disaster_event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-05",
            "zone_name": "Singanallur Lake Perimeter (DEMO)",
            "latitude": 10.9985,
            "longitude": 77.0254,
            "population": 3600,
            "population_density": 480.0,
            "building_density": 60.0,
            "risk_score": 88.0,
            "risk_level": RiskLevelEnum.HIGH.value,
            "road_accessibility": 40.0,
            "evacuation_priority": EvacuationPriorityEnum.HIGH.value,
        },
        {
            "disaster_event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-06",
            "zone_name": "Sundarapuram Drainage Basin (DEMO)",
            "latitude": 10.9524,
            "longitude": 76.9812,
            "population": 2400,
            "population_density": 310.0,
            "building_density": 45.0,
            "risk_score": 55.0,
            "risk_level": RiskLevelEnum.MEDIUM.value,
            "road_accessibility": 75.0,
            "evacuation_priority": EvacuationPriorityEnum.MEDIUM.value,
        },
        {
            "disaster_event_id": nil_event.id,
            "zone_code": "ZONE-NIL-01",
            "zone_name": "Coonoor Gorge Valley Sector (DEMO)",
            "latitude": 11.3530,
            "longitude": 76.7959,
            "population": 1500,
            "population_density": 180.0,
            "building_density": 35.0,
            "risk_score": 95.0,
            "risk_level": RiskLevelEnum.CRITICAL.value,
            "road_accessibility": 20.0,
            "evacuation_priority": EvacuationPriorityEnum.CRITICAL.value,
        },
        {
            "disaster_event_id": nil_event.id,
            "zone_code": "ZONE-NIL-02",
            "zone_name": "Kotagiri Hillside Ridge (DEMO)",
            "latitude": 11.4285,
            "longitude": 76.8660,
            "population": 1200,
            "population_density": 140.0,
            "building_density": 28.0,
            "risk_score": 78.0,
            "risk_level": RiskLevelEnum.HIGH.value,
            "road_accessibility": 50.0,
            "evacuation_priority": EvacuationPriorityEnum.HIGH.value,
        },
        {
            "disaster_event_id": nil_event.id,
            "zone_code": "ZONE-NIL-03",
            "zone_name": "Ooty Lake Basin Sector (DEMO)",
            "latitude": 11.4064,
            "longitude": 76.6932,
            "population": 2900,
            "population_density": 330.0,
            "building_density": 52.0,
            "risk_score": 62.0,
            "risk_level": RiskLevelEnum.MEDIUM.value,
            "road_accessibility": 65.0,
            "evacuation_priority": EvacuationPriorityEnum.MEDIUM.value,
        },
        {
            "disaster_event_id": nil_event.id,
            "zone_code": "ZONE-NIL-04",
            "zone_name": "Wellington Barracks Perimeter (DEMO)",
            "latitude": 11.3688,
            "longitude": 76.7882,
            "population": 1100,
            "population_density": 120.0,
            "building_density": 25.0,
            "risk_score": 35.0,
            "risk_level": RiskLevelEnum.LOW.value,
            "road_accessibility": 85.0,
            "evacuation_priority": EvacuationPriorityEnum.LOW.value,
        },
        {
            "disaster_event_id": nil_event.id,
            "zone_code": "ZONE-NIL-05",
            "zone_name": "Gudalur Escarpment (DEMO)",
            "latitude": 11.5074,
            "longitude": 76.4972,
            "population": 2100,
            "population_density": 260.0,
            "building_density": 40.0,
            "risk_score": 82.0,
            "risk_level": RiskLevelEnum.HIGH.value,
            "road_accessibility": 35.0,
            "evacuation_priority": EvacuationPriorityEnum.HIGH.value,
        },
    ]

    zones_by_code = {}
    for z_data in zone_definitions:
        existing = db.scalars(select(DisasterZone).where(DisasterZone.zone_code == z_data["zone_code"])).first()
        if not existing:
            zone = DisasterZone(**z_data)
            db.add(zone)
            db.flush()
            zones_by_code[z_data["zone_code"]] = zone
        else:
            for k, v in z_data.items():
                setattr(existing, k, v)
            zones_by_code[z_data["zone_code"]] = existing

        # Ensure ZoneRiskHistory entry exists
        zone_obj = zones_by_code[z_data["zone_code"]]
        hist_existing = db.scalars(
            select(ZoneRiskHistory).where(ZoneRiskHistory.zone_id == zone_obj.id)
        ).first()
        if not hist_existing:
            hist = ZoneRiskHistory(
                zone_id=zone_obj.id,
                risk_score=zone_obj.risk_score,
                risk_level=zone_obj.risk_level,
                rainfall=45.0 if "CBE" in z_data["zone_code"] else 65.0,
                water_level=1.8 if "CBE" in z_data["zone_code"] else 0.5,
                wind_speed=24.0,
                road_accessibility=zone_obj.road_accessibility,
            )
            db.add(hist)

    db.commit()
    return zones_by_code


def seed_shelters(db: Session) -> Dict[str, Shelter]:
    """Seed at least 8 shelters idempotently."""
    shelter_definitions = [
        {
            "name": "RS Puram Community Relief Center (DEMO)",
            "address": "West Brook St, RS Puram, Coimbatore",
            "latitude": 11.0112,
            "longitude": 76.9480,
            "total_capacity": 800,
            "current_occupancy": 250,
            "accessibility": ShelterAccessibilityEnum.GENERAL.value,
            "status": ShelterStatusEnum.AVAILABLE.value,
        },
        {
            "name": "Gandhipuram Central Hall (DEMO)",
            "address": "Cross Cut Rd, Gandhipuram, Coimbatore",
            "latitude": 11.0195,
            "longitude": 76.9690,
            "total_capacity": 1200,
            "current_occupancy": 600,
            "accessibility": ShelterAccessibilityEnum.GENERAL.value,
            "status": ShelterStatusEnum.AVAILABLE.value,
        },
        {
            "name": "Peelamedu High School Sanctuary (DEMO)",
            "address": "Avinashi Rd, Peelamedu, Coimbatore",
            "latitude": 11.0280,
            "longitude": 77.0120,
            "total_capacity": 600,
            "current_occupancy": 180,
            "accessibility": ShelterAccessibilityEnum.WHEELCHAIR_ACCESSIBLE.value,
            "status": ShelterStatusEnum.AVAILABLE.value,
        },
        {
            "name": "Ukkadam Indoor Stadium (DEMO)",
            "address": "South Bypass Rd, Ukkadam, Coimbatore",
            "latitude": 10.9880,
            "longitude": 76.9590,
            "total_capacity": 1500,
            "current_occupancy": 1350,
            "accessibility": ShelterAccessibilityEnum.GENERAL.value,
            "status": ShelterStatusEnum.NEAR_CAPACITY.value,
        },
        {
            "name": "Singanallur Poly Clinic Shelter (DEMO)",
            "address": "Trichy Rd, Singanallur, Coimbatore",
            "latitude": 10.9995,
            "longitude": 77.0280,
            "total_capacity": 500,
            "current_occupancy": 120,
            "accessibility": ShelterAccessibilityEnum.MEDICAL_SUPPORT.value,
            "status": ShelterStatusEnum.AVAILABLE.value,
        },
        {
            "name": "Ooty Municipal Shelter Alpha (DEMO)",
            "address": "Commercial Rd, Ooty",
            "latitude": 11.4120,
            "longitude": 76.7010,
            "total_capacity": 700,
            "current_occupancy": 400,
            "accessibility": ShelterAccessibilityEnum.GENERAL.value,
            "status": ShelterStatusEnum.AVAILABLE.value,
        },
        {
            "name": "Coonoor Valley Relief Center (DEMO)",
            "address": "Bedford Rd, Coonoor",
            "latitude": 11.3560,
            "longitude": 76.7980,
            "total_capacity": 450,
            "current_occupancy": 380,
            "accessibility": ShelterAccessibilityEnum.WHEELCHAIR_ACCESSIBLE.value,
            "status": ShelterStatusEnum.NEAR_CAPACITY.value,
        },
        {
            "name": "Kotagiri Emergency Station (DEMO)",
            "address": "Johnstone Square, Kotagiri",
            "latitude": 11.4310,
            "longitude": 76.8680,
            "total_capacity": 350,
            "current_occupancy": 90,
            "accessibility": ShelterAccessibilityEnum.GENERAL.value,
            "status": ShelterStatusEnum.AVAILABLE.value,
        },
    ]

    shelters_by_name = {}
    for s_data in shelter_definitions:
        existing = db.scalars(select(Shelter).where(Shelter.name == s_data["name"])).first()
        if not existing:
            shelter = Shelter(**s_data)
            db.add(shelter)
            db.flush()
            shelters_by_name[s_data["name"]] = shelter
        else:
            for k, v in s_data.items():
                setattr(existing, k, v)
            shelters_by_name[s_data["name"]] = existing

        # Ensure ShelterCapacityHistory entry exists
        shelter_obj = shelters_by_name[s_data["name"]]
        hist_existing = db.scalars(
            select(ShelterCapacityHistory).where(ShelterCapacityHistory.shelter_id == shelter_obj.id)
        ).first()
        if not hist_existing:
            hist = ShelterCapacityHistory(
                shelter_id=shelter_obj.id,
                recorded_capacity=shelter_obj.total_capacity,
                recorded_occupancy=shelter_obj.current_occupancy,
            )
            db.add(hist)

    db.commit()
    return shelters_by_name


def seed_resources(db: Session) -> Dict[str, Resource]:
    """Seed at least 15 resources and inventory records idempotently."""
    resource_definitions = [
        {
            "resource_code": "RES-MED-01",
            "name": "Advanced Trauma First Aid Kit",
            "resource_type": ResourceTypeEnum.MEDICAL_KIT.value,
            "description": "Sterile bandages, tourniquets, antiseptics, and burn dressings (DEMO)",
            "total_quantity": 300,
            "available_quantity": 250,
            "reserved_quantity": 50,
        },
        {
            "resource_code": "RES-MED-02",
            "name": "Emergency IV Fluids & Saline Packs",
            "resource_type": ResourceTypeEnum.MEDICAL_KIT.value,
            "description": "500ml Normal Saline and Ringer Lactate bags (DEMO)",
            "total_quantity": 500,
            "available_quantity": 420,
            "reserved_quantity": 80,
        },
        {
            "resource_code": "RES-MED-03",
            "name": "Portable Defibrillator AED Units",
            "resource_type": ResourceTypeEnum.MEDICAL_KIT.value,
            "description": "Automated external defibrillators for cardiac emergencies (DEMO)",
            "total_quantity": 25,
            "available_quantity": 20,
            "reserved_quantity": 5,
        },
        {
            "resource_code": "RES-WAT-01",
            "name": "Potable Bottled Water 20L Jerrycans",
            "resource_type": ResourceTypeEnum.WATER.value,
            "description": "Food-grade purified drinking water canisters (DEMO)",
            "total_quantity": 2000,
            "available_quantity": 1600,
            "reserved_quantity": 400,
        },
        {
            "resource_code": "RES-WAT-02",
            "name": "High-Flow Water Purification Filters",
            "resource_type": ResourceTypeEnum.WATER.value,
            "description": "Gravity-fed microfiltration ceramic units (DEMO)",
            "total_quantity": 80,
            "available_quantity": 70,
            "reserved_quantity": 10,
        },
        {
            "resource_code": "RES-WAT-03",
            "name": "Mobile Water Storage Bladder 5000L",
            "resource_type": ResourceTypeEnum.WATER.value,
            "description": "Collapsible high-capacity potable water storage bladder (DEMO)",
            "total_quantity": 15,
            "available_quantity": 12,
            "reserved_quantity": 3,
        },
        {
            "resource_code": "RES-FOO-01",
            "name": "Emergency Meal Ready-to-Eat (MRE) Crates",
            "resource_type": ResourceTypeEnum.FOOD.value,
            "description": "High-calorie shelf-stable disaster rations (DEMO)",
            "total_quantity": 1200,
            "available_quantity": 1000,
            "reserved_quantity": 200,
        },
        {
            "resource_code": "RES-FOO-02",
            "name": "Infant Nutrition & Milk Powder Packs",
            "resource_type": ResourceTypeEnum.FOOD.value,
            "description": "Fortified powdered formula for disaster nurseries (DEMO)",
            "total_quantity": 450,
            "available_quantity": 400,
            "reserved_quantity": 50,
        },
        {
            "resource_code": "RES-FOO-03",
            "name": "High-Energy Biscuits & Electrolyte Packs",
            "resource_type": ResourceTypeEnum.FOOD.value,
            "description": "Compact emergency nutrition bars (DEMO)",
            "total_quantity": 3000,
            "available_quantity": 2600,
            "reserved_quantity": 400,
        },
        {
            "resource_code": "RES-AMB-01",
            "name": "Type-C Advanced Life Support Ambulance",
            "resource_type": ResourceTypeEnum.AMBULANCE.value,
            "description": "Equipped with oxygen delivery and monitoring (DEMO)",
            "total_quantity": 10,
            "available_quantity": 8,
            "reserved_quantity": 2,
        },
        {
            "resource_code": "RES-AMB-02",
            "name": "Basic Life Support Patient Transport Unit",
            "resource_type": ResourceTypeEnum.AMBULANCE.value,
            "description": "Rapid patient transit for non-critical casualties (DEMO)",
            "total_quantity": 14,
            "available_quantity": 11,
            "reserved_quantity": 3,
        },
        {
            "resource_code": "RES-FIR-01",
            "name": "Urban Pumper Fire Engine Unit",
            "resource_type": ResourceTypeEnum.FIRE_ENGINE.value,
            "description": "High-pressure chemical and water deluge cannon (DEMO)",
            "total_quantity": 6,
            "available_quantity": 5,
            "reserved_quantity": 1,
        },
        {
            "resource_code": "RES-FIR-02",
            "name": "Wildland Brush Fire Attack Unit",
            "resource_type": ResourceTypeEnum.FIRE_ENGINE.value,
            "description": "4x4 all-terrain water pump and foam unit (DEMO)",
            "total_quantity": 8,
            "available_quantity": 7,
            "reserved_quantity": 1,
        },
        {
            "resource_code": "RES-RTM-01",
            "name": "Heavy Urban Search & Rescue Squad",
            "resource_type": ResourceTypeEnum.RESCUE_TEAM.value,
            "description": "Trained for structural collapse and confined space rescue (DEMO)",
            "total_quantity": 8,
            "available_quantity": 6,
            "reserved_quantity": 2,
        },
        {
            "resource_code": "RES-RTM-02",
            "name": "Swift Water & Inundation Rescue Unit",
            "resource_type": ResourceTypeEnum.RESCUE_TEAM.value,
            "description": "Equipped with zodiac inflatables and high-buoyancy gear (DEMO)",
            "total_quantity": 12,
            "available_quantity": 10,
            "reserved_quantity": 2,
        },
        {
            "resource_code": "RES-VEH-01",
            "name": "All-Terrain Amphibious Rescue Transport",
            "resource_type": ResourceTypeEnum.EMERGENCY_VEHICLE.value,
            "description": "Tracks and dual-propeller amphibious crawler (DEMO)",
            "total_quantity": 5,
            "available_quantity": 4,
            "reserved_quantity": 1,
        },
    ]

    resources_by_code = {}
    for r_data in resource_definitions:
        existing = db.scalars(select(Resource).where(Resource.resource_code == r_data["resource_code"])).first()
        if not existing:
            resource = Resource(
                resource_code=r_data["resource_code"],
                name=r_data["name"],
                resource_type=r_data["resource_type"],
                description=r_data["description"],
            )
            db.add(resource)
            db.flush()
            resources_by_code[r_data["resource_code"]] = resource
        else:
            existing.name = r_data["name"]
            existing.resource_type = r_data["resource_type"]
            existing.description = r_data["description"]
            resources_by_code[r_data["resource_code"]] = existing

        # Ensure ResourceInventory entry exists
        res_obj = resources_by_code[r_data["resource_code"]]
        inv_existing = db.scalars(
            select(ResourceInventory).where(ResourceInventory.resource_id == res_obj.id)
        ).first()
        if not inv_existing:
            inv = ResourceInventory(
                resource_id=res_obj.id,
                location_name="Central Logistics Depot",
                latitude=11.0168,
                longitude=76.9558,
                total_quantity=r_data["total_quantity"],
                available_quantity=r_data["available_quantity"],
                reserved_quantity=r_data["reserved_quantity"],
                status=InventoryStatusEnum.AVAILABLE.value,
            )
            db.add(inv)
        else:
            inv_existing.total_quantity = r_data["total_quantity"]
            inv_existing.available_quantity = r_data["available_quantity"]
            inv_existing.reserved_quantity = r_data["reserved_quantity"]

    db.commit()
    return resources_by_code


def seed_rescue_teams_and_vehicles(db: Session) -> Dict[str, RescueTeam]:
    """Seed at least 5 rescue teams and 10 vehicles idempotently."""
    team_definitions = [
        {
            "team_code": "TEAM-ALPHA",
            "team_name": "Kovai Quick Response Unit (DEMO)",
            "team_size": 8,
            "specialization": "URBAN_SEARCH_AND_RESCUE",
            "current_latitude": 11.0080,
            "current_longitude": 76.9500,
            "status": TeamStatusEnum.AVAILABLE.value,
        },
        {
            "team_code": "TEAM-BRAVO",
            "team_name": "Nilgiris Mountain Rescue Taskforce (DEMO)",
            "team_size": 6,
            "specialization": "TECHNICAL_ROPE_RESCUE",
            "current_latitude": 11.3500,
            "current_longitude": 76.7900,
            "status": TeamStatusEnum.AVAILABLE.value,
        },
        {
            "team_code": "TEAM-CHARLIE",
            "team_name": "Noyyal Flood Evacuation Crew (DEMO)",
            "team_size": 10,
            "specialization": "WATER_RESCUE",
            "current_latitude": 10.9900,
            "current_longitude": 76.9600,
            "status": TeamStatusEnum.DEPLOYED.value,
        },
        {
            "team_code": "TEAM-DELTA",
            "team_name": "Emergency Medical Field Corps (DEMO)",
            "team_size": 6,
            "specialization": "MEDICAL_EVAC",
            "current_latitude": 11.0250,
            "current_longitude": 77.0100,
            "status": TeamStatusEnum.AVAILABLE.value,
        },
        {
            "team_code": "TEAM-ECHO",
            "team_name": "Hazardous Plume & Debris Squad (DEMO)",
            "team_size": 5,
            "specialization": "HAZMAT_CONTAINMENT",
            "current_latitude": 11.0150,
            "current_longitude": 76.9700,
            "status": TeamStatusEnum.AVAILABLE.value,
        },
    ]

    teams_by_code = {}
    for t_data in team_definitions:
        existing = db.scalars(select(RescueTeam).where(RescueTeam.team_code == t_data["team_code"])).first()
        if not existing:
            team = RescueTeam(**t_data)
            db.add(team)
            db.flush()
            teams_by_code[t_data["team_code"]] = team
        else:
            for k, v in t_data.items():
                setattr(existing, k, v)
            teams_by_code[t_data["team_code"]] = existing

    # Seed vehicles
    vehicle_definitions = [
        {"vehicle_code": "VEH-AMB-01", "vehicle_type": VehicleTypeEnum.AMBULANCE.value, "capacity": 4, "lat": 11.0085, "lng": 76.9505, "status": VehicleStatusEnum.AVAILABLE.value, "team": "TEAM-DELTA"},
        {"vehicle_code": "VEH-AMB-02", "vehicle_type": VehicleTypeEnum.AMBULANCE.value, "capacity": 4, "lat": 11.0255, "lng": 77.0105, "status": VehicleStatusEnum.AVAILABLE.value, "team": "TEAM-DELTA"},
        {"vehicle_code": "VEH-VAN-01", "vehicle_type": VehicleTypeEnum.RESCUE_VAN.value, "capacity": 8, "lat": 11.0080, "lng": 76.9500, "status": VehicleStatusEnum.AVAILABLE.value, "team": "TEAM-ALPHA"},
        {"vehicle_code": "VEH-VAN-02", "vehicle_type": VehicleTypeEnum.RESCUE_VAN.value, "capacity": 8, "lat": 11.3500, "lng": 76.7900, "status": VehicleStatusEnum.AVAILABLE.value, "team": "TEAM-BRAVO"},
        {"vehicle_code": "VEH-FIRE-01", "vehicle_type": VehicleTypeEnum.FIRE_ENGINE.value, "capacity": 6, "lat": 11.0150, "lng": 76.9700, "status": VehicleStatusEnum.AVAILABLE.value, "team": "TEAM-ECHO"},
        {"vehicle_code": "VEH-FIRE-02", "vehicle_type": VehicleTypeEnum.FIRE_ENGINE.value, "capacity": 6, "lat": 11.0010, "lng": 76.9650, "status": VehicleStatusEnum.AVAILABLE.value, "team": None},
        {"vehicle_code": "VEH-TRUCK-01", "vehicle_type": VehicleTypeEnum.SUPPLY_TRUCK.value, "capacity": 20, "lat": 11.0170, "lng": 76.9560, "status": VehicleStatusEnum.AVAILABLE.value, "team": None},
        {"vehicle_code": "VEH-TRUCK-02", "vehicle_type": VehicleTypeEnum.SUPPLY_TRUCK.value, "capacity": 20, "lat": 11.0175, "lng": 76.9565, "status": VehicleStatusEnum.AVAILABLE.value, "team": None},
        {"vehicle_code": "VEH-EMG-01", "vehicle_type": VehicleTypeEnum.EMERGENCY_VEHICLE.value, "capacity": 6, "lat": 10.9905, "lng": 76.9605, "status": VehicleStatusEnum.DEPLOYED.value, "team": "TEAM-CHARLIE"},
        {"vehicle_code": "VEH-EMG-02", "vehicle_type": VehicleTypeEnum.EMERGENCY_VEHICLE.value, "capacity": 6, "lat": 11.3505, "lng": 76.7905, "status": VehicleStatusEnum.AVAILABLE.value, "team": "TEAM-BRAVO"},
    ]

    for v_data in vehicle_definitions:
        existing = db.scalars(select(Vehicle).where(Vehicle.vehicle_code == v_data["vehicle_code"])).first()
        team_id = teams_by_code[v_data["team"]].id if v_data["team"] else None
        if not existing:
            vehicle = Vehicle(
                vehicle_code=v_data["vehicle_code"],
                vehicle_type=v_data["vehicle_type"],
                capacity=v_data["capacity"],
                current_latitude=v_data["lat"],
                current_longitude=v_data["lng"],
                status=v_data["status"],
                rescue_team_id=team_id,
            )
            db.add(vehicle)
        else:
            existing.vehicle_type = v_data["vehicle_type"]
            existing.capacity = v_data["capacity"]
            existing.current_latitude = v_data["lat"]
            existing.current_longitude = v_data["lng"]
            existing.status = v_data["status"]
            existing.rescue_team_id = team_id

    db.commit()
    return teams_by_code


def seed_routes_and_assignments(
    db: Session,
    events: Dict[str, DisasterEvent],
    zones: Dict[str, DisasterZone],
    shelters: Dict[str, Shelter],
) -> None:
    """Seed evacuation routes and operational assignments idempotently."""
    cbe_event = events["Coimbatore Flood Simulation - DEMO"]
    nil_event = events["Nilgiris Landslide Drill - DEMO"]

    routes_data = [
        {
            "event_id": cbe_event.id,
            "source_code": "ZONE-CBE-01",
            "shelter_name": "RS Puram Community Relief Center (DEMO)",
            "distance_km": 1.2,
            "time_minutes": 10.0,
            "safety_score": 85.0,
            "risk_score": 15.0,
            "congestion": 25.0,
            "status": RouteStatusEnum.SAFE.value,
        },
        {
            "event_id": cbe_event.id,
            "source_code": "ZONE-CBE-02",
            "shelter_name": "Ukkadam Indoor Stadium (DEMO)",
            "distance_km": 2.5,
            "time_minutes": 22.0,
            "safety_score": 55.0,
            "risk_score": 45.0,
            "congestion": 60.0,
            "status": RouteStatusEnum.CAUTION.value,
        },
        {
            "event_id": cbe_event.id,
            "source_code": "ZONE-CBE-03",
            "shelter_name": "Gandhipuram Central Hall (DEMO)",
            "distance_km": 0.8,
            "time_minutes": 8.0,
            "safety_score": 92.0,
            "risk_score": 8.0,
            "congestion": 15.0,
            "status": RouteStatusEnum.SAFE.value,
        },
        {
            "event_id": nil_event.id,
            "source_code": "ZONE-NIL-01",
            "shelter_name": "Coonoor Valley Relief Center (DEMO)",
            "distance_km": 3.8,
            "time_minutes": 35.0,
            "safety_score": 40.0,
            "risk_score": 60.0,
            "congestion": 70.0,
            "status": RouteStatusEnum.CAUTION.value,
        },
        {
            "event_id": nil_event.id,
            "source_code": "ZONE-NIL-02",
            "shelter_name": "Kotagiri Emergency Station (DEMO)",
            "distance_km": 1.5,
            "time_minutes": 14.0,
            "safety_score": 88.0,
            "risk_score": 12.0,
            "congestion": 10.0,
            "status": RouteStatusEnum.SAFE.value,
        },
    ]

    for r in routes_data:
        z = zones[r["source_code"]]
        s = shelters[r["shelter_name"]]
        existing = db.scalars(
            select(EvacuationRoute).where(
                EvacuationRoute.disaster_event_id == r["event_id"],
                EvacuationRoute.source_zone_id == z.id,
                EvacuationRoute.destination_shelter_id == s.id,
            )
        ).first()
        if not existing:
            route = EvacuationRoute(
                disaster_event_id=r["event_id"],
                source_zone_id=z.id,
                destination_shelter_id=s.id,
                distance_km=r["distance_km"],
                estimated_time_minutes=r["time_minutes"],
                safety_score=r["safety_score"],
                risk_score=r["risk_score"],
                congestion_score=r["congestion"],
                route_status=r["status"],
            )
            db.add(route)
            db.flush()
            
            # Add demo evacuation assignment
            evac_assign = EvacuationAssignment(
                disaster_zone_id=z.id,
                shelter_id=s.id,
                evacuation_route_id=route.id,
                assigned_population=min(z.population, 500),
                priority="HIGH",
                estimated_time_minutes=r["time_minutes"],
                status=AssignmentStatusEnum.IN_PROGRESS.value,
            )
            db.add(evac_assign)

    # Seed demo ResourceAssignment
    inv = db.scalars(select(ResourceInventory)).first()
    if inv:
        z_cbe = zones["ZONE-CBE-01"]
        existing_res_assign = db.scalars(
            select(ResourceAssignment).where(
                ResourceAssignment.disaster_zone_id == z_cbe.id,
                ResourceAssignment.resource_inventory_id == inv.id,
            )
        ).first()
        if not existing_res_assign:
            res_assign = ResourceAssignment(
                disaster_zone_id=z_cbe.id,
                resource_inventory_id=inv.id,
                assigned_quantity=20,
                priority="CRITICAL",
                estimated_arrival_minutes=15.0,
                status=ResourceAssignmentStatusEnum.DISPATCHED.value,
            )
            db.add(res_assign)

    db.commit()


def seed_simulations_and_alerts(
    db: Session,
    users: Dict[str, User],
    events: Dict[str, DisasterEvent],
    zones: Dict[str, DisasterZone],
) -> None:
    """Seed simulation scenarios, simulation results, alerts, and audit logs idempotently."""
    admin_user = users["admin"]
    cbe_event = events["Coimbatore Flood Simulation - DEMO"]
    nil_event = events["Nilgiris Landslide Drill - DEMO"]

    # Simulation Scenario
    scenario_name = "Monsoon Urban Surge Peak Drill - DEMO"
    existing_scenario = db.scalars(
        select(SimulationScenario).where(SimulationScenario.name == scenario_name)
    ).first()
    if not existing_scenario:
        scenario = SimulationScenario(
            name=scenario_name,
            disaster_type=DisasterTypeEnum.FLOOD.value,
            description="Simulated mathematical modeling for maximum inundation discharge.",
            random_seed=42,
            parameters_json={"rainfall_intensity_mm_hr": 75, "surge_duration_hours": 12, "soil_saturation_pct": 85},
            status=ScenarioStatusEnum.COMPLETED.value,
            created_by=admin_user.id,
        )
        db.add(scenario)
        db.flush()

        result = SimulationResult(
            scenario_id=scenario.id,
            affected_population=18400,
            population_at_risk=8100,
            average_risk_score=78.5,
            estimated_evacuation_time=135.0,
            resource_shortage_count=2,
            shelter_utilization=72.4,
            result_json={"is_simulated": True, "model_type": "hydrodynamic_surge_v1"},
        )
        db.add(result)

    # Alerts
    alerts_data = [
        {
            "event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-02",
            "alert_type": "PERIMETER_BREACH",
            "severity": AlertSeverityEnum.CRITICAL.value,
            "title": "CRITICAL: Ukkadam Basin Surge Warning (DEMO)",
            "message": "Water levels projected to breach primary embankment within 45 minutes. Immediate evacuation recommended.",
        },
        {
            "event_id": nil_event.id,
            "zone_code": "ZONE-NIL-01",
            "alert_type": "GEOTECHNICAL_WARNING",
            "severity": AlertSeverityEnum.WARNING.value,
            "title": "WARNING: Coonoor Valley Slope Displacement (DEMO)",
            "message": "Soil moisture sensors indicate high pore pressure. Hillside roads placed on restricted traffic.",
        },
        {
            "event_id": cbe_event.id,
            "zone_code": "ZONE-CBE-01",
            "alert_type": "DISPATCH_NOTIFICATION",
            "severity": AlertSeverityEnum.INFO.value,
            "title": "INFO: Mobile Medical Convoy En Route (DEMO)",
            "message": "Team Delta ambulance unit dispatched to RS Puram Relief Center.",
        },
    ]

    for a_data in alerts_data:
        existing_alert = db.scalars(
            select(Alert).where(Alert.title == a_data["title"])
        ).first()
        if not existing_alert:
            z = zones.get(a_data["zone_code"])
            alert = Alert(
                disaster_event_id=a_data["event_id"],
                zone_id=z.id if z else None,
                alert_type=a_data["alert_type"],
                severity=a_data["severity"],
                title=a_data["title"],
                message=a_data["message"],
                is_acknowledged=False,
            )
            db.add(alert)

    # Audit Logs with strict sanitization test
    audit_data = [
        {
            "user_id": admin_user.id,
            "action": "SYSTEM_STARTUP",
            "entity_type": "SYSTEM",
            "entity_id": "MAIN",
            "payload": {"status": "INITIALIZED", "simulation_mode": True},
        },
        {
            "user_id": admin_user.id,
            "action": "DISASTER_EVENT_ACTIVATED",
            "entity_type": "DISASTER_EVENT",
            "entity_id": str(cbe_event.id),
            "payload": {"event_name": cbe_event.name, "severity": cbe_event.severity},
        },
        {
            "user_id": admin_user.id,
            "action": "USER_AUTHENTICATED",
            "entity_type": "USER",
            "entity_id": str(admin_user.id),
            "payload": sanitize_audit_payload({
                "username": admin_user.username,
                "password": "[CONFIDENTIAL_PLAINTEXT_ATTEMPT]",
                "auth_method": "JWT",
            }),
        },
    ]

    for entry in audit_data:
        existing_audit = db.scalars(
            select(AuditLog).where(
                AuditLog.action == entry["action"],
                AuditLog.entity_type == entry["entity_type"],
                AuditLog.entity_id == entry["entity_id"],
            )
        ).first()
        if not existing_audit:
            audit = AuditLog(
                user_id=entry["user_id"],
                action=entry["action"],
                entity_type=entry["entity_type"],
                entity_id=entry["entity_id"],
                new_value=entry["payload"],
                ip_address="127.0.0.1",
            )
            db.add(audit)

    db.commit()


def seed_all(db: Session) -> Dict[str, int]:
    """
    Executes complete deterministic database seeding across all 18 tables.
    Completely idempotent: safe to execute multiple times.
    Returns counts of verified records per category.
    """
    logger.info("Beginning deterministic database seed...")

    roles = seed_roles(db)
    users = seed_users(db, roles)
    events = seed_disaster_events(db)
    zones = seed_disaster_zones(db, events)
    shelters = seed_shelters(db)
    resources = seed_resources(db)
    rescue_teams = seed_rescue_teams_and_vehicles(db)
    seed_routes_and_assignments(db, events, zones, shelters)
    seed_simulations_and_alerts(db, users, events, zones)

    counts = {
        "roles": len(roles),
        "users": len(users),
        "disaster_events": len(events),
        "disaster_zones": len(zones),
        "shelters": len(shelters),
        "resources": len(resources),
        "rescue_teams": len(rescue_teams),
        "vehicles": db.scalar(select(Vehicle).with_only_columns(Vehicle.id)).count() if hasattr(select(Vehicle).with_only_columns(Vehicle.id), 'count') else len(db.scalars(select(Vehicle)).all()),
        "evacuation_routes": len(db.scalars(select(EvacuationRoute)).all()),
        "alerts": len(db.scalars(select(Alert)).all()),
        "audit_logs": len(db.scalars(select(AuditLog)).all()),
    }
    logger.info(f"Seed completed successfully: {counts}")
    return counts
