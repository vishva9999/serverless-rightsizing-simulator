"""
DynamoDB Scenario Repository — Phase 4 AWS Cloud Repository.

Implements Scenario CRUD using Amazon DynamoDB via boto3.
Compatible interface with SQLite ScenarioRepository.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from app.utils.config import settings


def _float_to_decimal(val: Any) -> Any:
    """Helper to convert floats to Decimal for DynamoDB storage."""
    if isinstance(val, float):
        return Decimal(str(val))
    if isinstance(val, dict):
        return {k: _float_to_decimal(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_float_to_decimal(v) for v in val]
    return val


def _decimal_to_float(val: Any) -> Any:
    """Helper to convert Decimal back to float for JSON/API responses."""
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, dict):
        return {k: _decimal_to_float(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_decimal_to_float(v) for v in val]
    return val


class DynamoDBScenarioRepository:
    """Repository handling CRUD operations for Scenarios in Amazon DynamoDB."""

    @staticmethod
    def _get_table():
        import boto3
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        return dynamodb.Table(settings.scenarios_table)

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        table = DynamoDBScenarioRepository._get_table()
        response = table.scan()
        items = response.get("Items", [])
        scenarios = [_decimal_to_float(item) for item in items]
        scenarios.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return scenarios

    @staticmethod
    def get_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
        table = DynamoDBScenarioRepository._get_table()
        response = table.get_item(Key={"scenario_id": scenario_id})
        item = response.get("Item")
        if not item:
            # Fallback check for 'id' key if created via generic dict
            response = table.get_item(Key={"id": scenario_id})
            item = response.get("Item")
        if not item:
            return None
        res = _decimal_to_float(item)
        if "id" not in res:
            res["id"] = res.get("scenario_id", scenario_id)
        return res

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        scenario_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        item = {
            "id": scenario_id,
            "scenario_id": scenario_id,
            "name": data["name"],
            "description": data.get("description", ""),
            "workload_type": data["workload_type"],
            "request_volume": data["request_volume"],
            "baseline_memory_mb": data["baseline_memory_mb"],
            "baseline_latency_ms": data["baseline_latency_ms"],
            "cpu_utilization": data["cpu_utilization"],
            "current_price": data["current_price"],
            "latency_target_ms": data["latency_target_ms"],
            "availability_target_percent": data["availability_target_percent"],
            "created_at": now,
            "updated_at": now
        }

        table = DynamoDBScenarioRepository._get_table()
        table.put_item(Item=_float_to_decimal(item))
        return item

    @staticmethod
    def update(scenario_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = DynamoDBScenarioRepository.get_by_id(scenario_id)
        if not existing:
            return None

        now = datetime.now().isoformat()
        updated_item = {**existing, **data, "updated_at": now, "id": scenario_id, "scenario_id": scenario_id}

        table = DynamoDBScenarioRepository._get_table()
        table.put_item(Item=_float_to_decimal(updated_item))
        return updated_item

    @staticmethod
    def delete(scenario_id: str) -> bool:
        existing = DynamoDBScenarioRepository.get_by_id(scenario_id)
        if not existing:
            return False

        table = DynamoDBScenarioRepository._get_table()
        table.delete_item(Key={"scenario_id": scenario_id})
        return True
