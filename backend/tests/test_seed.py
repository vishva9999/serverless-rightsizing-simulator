import pytest
from app.core.database import SessionLocal
from app.services.seed_service import seed_all


def test_seed_records_and_idempotency():
    """Verify seed_all generates required record minimums and is fully idempotent."""
    db = SessionLocal()
    try:
        # First execution
        counts_first = seed_all(db)

        assert counts_first["roles"] >= 6
        assert counts_first["users"] >= 5
        assert counts_first["disaster_events"] >= 2
        assert counts_first["disaster_zones"] >= 10
        assert counts_first["shelters"] >= 8
        assert counts_first["resources"] >= 15
        assert counts_first["rescue_teams"] >= 5
        assert counts_first["vehicles"] >= 10
        assert counts_first["evacuation_routes"] >= 5
        assert counts_first["alerts"] >= 3
        assert counts_first["audit_logs"] >= 3

        # Second execution to test idempotency
        counts_second = seed_all(db)

        assert counts_first == counts_second, f"Idempotency violated: {counts_first} != {counts_second}"
    finally:
        db.close()
