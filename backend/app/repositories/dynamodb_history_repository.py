"""
DynamoDB History Repository — Phase 4 AWS Cloud Repository.

Implements Simulation History CRUD and side-by-side run comparison using Amazon DynamoDB via boto3.
Compatible interface with SQLite HistoryRepository.
"""

import uuid
import json
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


class DynamoDBHistoryRepository:
    """Repository handling CRUD and comparison operations for Simulation History in Amazon DynamoDB."""

    @staticmethod
    def _get_table():
        import boto3
        dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
        return dynamodb.Table(settings.history_table)

    @staticmethod
    def create(
        scenario_id: str,
        scenario_name: str,
        simulation_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        history_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        rec = simulation_response.get("recommendation")
        if rec:
            rec_mem = rec.get("memory_mb")
            rec_cost = rec.get("estimated_monthly_cost")
            rec_lat = rec.get("estimated_latency_ms")
            rec_avail = rec.get("estimated_availability")
            savings = rec.get("cost_savings_percentage")

            baseline = simulation_response.get("baseline", {})
            if baseline and baseline.get("memory_mb") == rec_mem:
                status_label = "Near Optimal"
            else:
                status_label = "Recommended"
        else:
            rec_mem = None
            rec_cost = None
            rec_lat = None
            rec_avail = None
            savings = None
            status_label = "No Feasible Configuration"

        full_json = json.dumps(simulation_response)

        item = {
            "id": history_id,
            "history_id": history_id,
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "created_at": now,
            "recommended_memory_mb": rec_mem,
            "recommended_cost": rec_cost,
            "recommended_latency_ms": rec_lat,
            "recommended_availability_percent": rec_avail,
            "savings_percent": savings,
            "status": status_label,
            "full_simulation_json": full_json
        }

        table = DynamoDBHistoryRepository._get_table()
        table.put_item(Item=_float_to_decimal(item))

        res = _decimal_to_float(item)
        res["simulation_detail"] = simulation_response
        return res

    @staticmethod
    def list_all(scenario_id: Optional[str] = None) -> List[Dict[str, Any]]:
        table = DynamoDBHistoryRepository._get_table()

        if scenario_id:
            from boto3.dynamodb.conditions import Key
            try:
                response = table.query(
                    IndexName="scenario_id-index",
                    KeyConditionExpression=Key("scenario_id").eq(scenario_id)
                )
                items = response.get("Items", [])
            except Exception:
                # Fallback to scan if index not present
                response = table.scan()
                items = [item for item in response.get("Items", []) if item.get("scenario_id") == scenario_id]
        else:
            response = table.scan()
            items = response.get("Items", [])

        history_list = []
        for item in items:
            h = _decimal_to_float(item)
            if "id" not in h:
                h["id"] = h.get("history_id", "")
            # Omit large full_simulation_json from list view
            h.pop("full_simulation_json", None)
            history_list.append(h)

        history_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return history_list

    @staticmethod
    def get_by_id(history_id: str) -> Optional[Dict[str, Any]]:
        table = DynamoDBHistoryRepository._get_table()
        response = table.get_item(Key={"history_id": history_id})
        item = response.get("Item")
        if not item:
            response = table.get_item(Key={"id": history_id})
            item = response.get("Item")
        if not item:
            return None

        result = _decimal_to_float(item)
        if "id" not in result:
            result["id"] = result.get("history_id", history_id)

        if "full_simulation_json" in result and result["full_simulation_json"]:
            try:
                result["simulation_detail"] = json.loads(result["full_simulation_json"])
            except Exception:
                result["simulation_detail"] = None

        return result

    @staticmethod
    def delete(history_id: str) -> bool:
        existing = DynamoDBHistoryRepository.get_by_id(history_id)
        if not existing:
            return False

        table = DynamoDBHistoryRepository._get_table()
        table.delete_item(Key={"history_id": history_id})
        return True

    @staticmethod
    def compare(id1: str, id2: str) -> Optional[Dict[str, Any]]:
        run1 = DynamoDBHistoryRepository.get_by_id(id1)
        run2 = DynamoDBHistoryRepository.get_by_id(id2)

        if not run1 or not run2:
            return None

        cost_diff = None
        if run1.get("recommended_cost") is not None and run2.get("recommended_cost") is not None:
            cost_diff = round(run2["recommended_cost"] - run1["recommended_cost"], 4)

        latency_diff = None
        if run1.get("recommended_latency_ms") is not None and run2.get("recommended_latency_ms") is not None:
            latency_diff = round(run2["recommended_latency_ms"] - run1["recommended_latency_ms"], 2)

        return {
            "run_1": {
                "id": run1["id"],
                "scenario_id": run1["scenario_id"],
                "scenario_name": run1["scenario_name"],
                "created_at": run1["created_at"],
                "recommended_memory_mb": run1.get("recommended_memory_mb"),
                "recommended_cost": run1.get("recommended_cost"),
                "recommended_latency_ms": run1.get("recommended_latency_ms"),
                "recommended_availability_percent": run1.get("recommended_availability_percent"),
                "savings_percent": run1.get("savings_percent"),
                "status": run1["status"]
            },
            "run_2": {
                "id": run2["id"],
                "scenario_id": run2["scenario_id"],
                "scenario_name": run2["scenario_name"],
                "created_at": run2["created_at"],
                "recommended_memory_mb": run2.get("recommended_memory_mb"),
                "recommended_cost": run2.get("recommended_cost"),
                "recommended_latency_ms": run2.get("recommended_latency_ms"),
                "recommended_availability_percent": run2.get("recommended_availability_percent"),
                "savings_percent": run2.get("savings_percent"),
                "status": run2["status"]
            },
            "comparison_summary": {
                "cost_difference": cost_diff,
                "latency_difference_ms": latency_diff,
                "same_recommendation": run1.get("recommended_memory_mb") == run2.get("recommended_memory_mb")
            }
        }
