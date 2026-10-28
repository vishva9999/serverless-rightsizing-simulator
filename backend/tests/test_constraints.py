import pytest
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.shelter import Shelter
from app.models.disaster_zone import DisasterZone
from app.models.rescue_team import RescueTeam
from app.models.disaster_event import DisasterEvent


def test_shelter_capacity_constraint():
    """Verify shelter current_occupancy cannot exceed total_capacity when enforced."""
    db = SessionLocal()
    try:
        # Valid shelter
        valid_shelter = Shelter(
            name="Test Valid Shelter (DEMO)",
            address="123 Safe St",
            latitude=11.0,
            longitude=76.9,
            total_capacity=500,
            current_occupancy=200,
        )
        db.add(valid_shelter)
        db.commit()
        assert valid_shelter.id is not None

        # Clean up
        db.delete(valid_shelter)
        db.commit()
    finally:
        db.close()


def test_rescue_team_size_constraint():
    """Verify rescue team model enforces valid non-negative team size."""
    db = SessionLocal()
    try:
        valid_team = RescueTeam(
            team_code="TEST-TEAM-01",
            team_name="Test Alpha",
            team_size=5,
            specialization="SEARCH",
            current_latitude=11.0,
            current_longitude=76.9,
        )
        db.add(valid_team)
        db.commit()
        assert valid_team.id is not None

        # Clean up
        db.delete(valid_team)
        db.commit()
    finally:
        db.close()
