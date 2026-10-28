import sys
from pathlib import Path

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.database import SessionLocal, engine
from app.core.logging import logger
from app.services.seed_service import seed_all


def run_seed():
    """CLI runner to seed the disaster command center database."""
    print("=" * 70)
    print("Disaster Command Center - Deterministic Demo Data Seeder")
    print(f"Target Database: {engine.url}")
    print("=" * 70)

    db = SessionLocal()
    try:
        counts = seed_all(db)
        print("\nSeed completed successfully! Record summary:")
        for table, count in counts.items():
            print(f" - {table}: {count}")
        print("=" * 70)
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        print(f"\nERROR: Seeding failed with exception: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
