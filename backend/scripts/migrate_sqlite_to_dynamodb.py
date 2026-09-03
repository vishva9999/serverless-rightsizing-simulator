"""
Data Migration Utility — SQLite to Amazon DynamoDB Migration Script.

Reads existing workload scenarios and simulation history records from the local
SQLite database (simulator.db) and populates the configured Amazon DynamoDB tables.

Usage:
  py scripts/migrate_sqlite_to_dynamodb.py
"""

import sys
import os

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import init_db
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.history_repository import HistoryRepository
from app.repositories.dynamodb_scenario_repository import DynamoDBScenarioRepository
from app.repositories.dynamodb_history_repository import DynamoDBHistoryRepository


def run_migration():
    print("=" * 60)
    print("  Serverless Rightsizing Simulator — SQLite to DynamoDB Migration")
    print("=" * 60)

    # 1. Initialize SQLite database connection
    init_db()

    # 2. Read scenarios from SQLite
    sqlite_scenarios = ScenarioRepository.list_all()
    print(f"\nScenarios found in SQLite: {len(sqlite_scenarios)}")

    migrated_scenarios = 0
    for scenario in sqlite_scenarios:
        try:
            DynamoDBScenarioRepository.create(scenario)
            migrated_scenarios += 1
        except Exception as e:
            print(f"  ❌ Failed to migrate scenario '{scenario.get('name')}': {str(e)}")

    print(f"Scenarios migrated to DynamoDB: {migrated_scenarios}")

    # 3. Read history records from SQLite
    sqlite_history = HistoryRepository.list_all()
    print(f"\nHistory records found in SQLite: {len(sqlite_history)}")

    migrated_history = 0
    for hist in sqlite_history:
        try:
            full_item = HistoryRepository.get_by_id(hist["id"])
            sim_detail = full_item.get("simulation_detail") if full_item else {}

            DynamoDBHistoryRepository.create(
                scenario_id=hist["scenario_id"],
                scenario_name=hist["scenario_name"],
                simulation_response=sim_detail or {}
            )
            migrated_history += 1
        except Exception as e:
            print(f"  ❌ Failed to migrate history record '{hist.get('id')}': {str(e)}")

    print(f"History records migrated to DynamoDB: {migrated_history}")

    print("\n" + "=" * 60)
    print("  Migration Summary Statistics:")
    print(f"  Scenarios found: {len(sqlite_scenarios)}")
    print(f"  Scenarios migrated: {migrated_scenarios}")
    print(f"  History records found: {len(sqlite_history)}")
    print(f"  History records migrated: {migrated_history}")
    print("=" * 60)


if __name__ == "__main__":
    run_migration()
