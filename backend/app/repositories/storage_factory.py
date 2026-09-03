"""
Storage Repository Factory — Phase 4 Storage Selector Pattern.

Selects either SQLite repositories (STORAGE_MODE=local) or DynamoDB repositories (STORAGE_MODE=aws).
"""

from app.utils.config import settings
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.history_repository import HistoryRepository


def get_scenario_repository():
    """
    Returns scenario repository class based on STORAGE_MODE setting.
    STORAGE_MODE=local -> ScenarioRepository (SQLite)
    STORAGE_MODE=aws   -> DynamoDBScenarioRepository (DynamoDB)
    """
    if settings.storage_mode.lower() == "aws":
        from app.repositories.dynamodb_scenario_repository import DynamoDBScenarioRepository
        return DynamoDBScenarioRepository
    return ScenarioRepository


def get_history_repository():
    """
    Returns history repository class based on STORAGE_MODE setting.
    STORAGE_MODE=local -> HistoryRepository (SQLite)
    STORAGE_MODE=aws   -> DynamoDBHistoryRepository (DynamoDB)
    """
    if settings.storage_mode.lower() == "aws":
        from app.repositories.dynamodb_history_repository import DynamoDBHistoryRepository
        return DynamoDBHistoryRepository
    return HistoryRepository
