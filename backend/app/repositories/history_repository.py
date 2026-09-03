"""
History Repository — Data Access Layer for Simulation History & Comparisons.

Decouples history persistence from FastAPI controllers and services.
Supports multi-tenant organization filtering.
"""

import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.database import get_connection


class HistoryRepository:
    """Repository handling CRUD and comparison operations for Simulation History in SQLite."""

    @staticmethod
    def create(
        scenario_id: str,
        scenario_name: str,
        simulation_response: Dict[str, Any],
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        history_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        org_id = organization_id or "default-org"

        rec = simulation_response.get("recommendation")

        if rec:
            rec_mem = rec.get("memory_mb")
            rec_cost = rec.get("estimated_monthly_cost")
            rec_lat = rec.get("estimated_latency_ms")
            rec_avail = rec.get("estimated_availability")
            savings = rec.get("cost_savings_percentage")

            # Status label logic: "Near Optimal" if baseline memory matches recommendation
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

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO simulation_history (
            id, scenario_id, scenario_name, created_at,
            recommended_memory_mb, recommended_cost, recommended_latency_ms,
            recommended_availability_percent, savings_percent, status,
            full_simulation_json, organization_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            history_id,
            scenario_id,
            scenario_name,
            now,
            rec_mem,
            rec_cost,
            rec_lat,
            rec_avail,
            savings,
            status_label,
            full_json,
            org_id
        ))
        conn.commit()
        conn.close()

        return HistoryRepository.get_by_id(history_id, org_id)

    @staticmethod
    def list_all(scenario_id: Optional[str] = None, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT id, scenario_id, scenario_name, created_at, recommended_memory_mb, recommended_cost, recommended_latency_ms, recommended_availability_percent, savings_percent, status FROM simulation_history WHERE 1=1"
        params = []

        if organization_id:
            query += " AND organization_id = ?"
            params.append(organization_id)

        if scenario_id:
            query += " AND scenario_id = ?"
            params.append(scenario_id)

        query += " ORDER BY created_at DESC;"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(history_id: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()

        if organization_id:
            cursor.execute("SELECT * FROM simulation_history WHERE id = ? AND organization_id = ?;", (history_id, organization_id))
        else:
            cursor.execute("SELECT * FROM simulation_history WHERE id = ?;", (history_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        result = dict(row)
        if "full_simulation_json" in result and result["full_simulation_json"]:
            try:
                result["simulation_detail"] = json.loads(result["full_simulation_json"])
            except Exception:
                result["simulation_detail"] = None

        return result

    @staticmethod
    def delete(history_id: str, organization_id: Optional[str] = None) -> bool:
        existing = HistoryRepository.get_by_id(history_id, organization_id)
        if not existing:
            return False

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM simulation_history WHERE id = ?;", (history_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def compare(id1: str, id2: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        run1 = HistoryRepository.get_by_id(id1, organization_id)
        run2 = HistoryRepository.get_by_id(id2, organization_id)

        if not run1 or not run2:
            return None

        cost_diff = None
        if run1["recommended_cost"] is not None and run2["recommended_cost"] is not None:
            cost_diff = round(run2["recommended_cost"] - run1["recommended_cost"], 4)

        latency_diff = None
        if run1["recommended_latency_ms"] is not None and run2["recommended_latency_ms"] is not None:
            latency_diff = round(run2["recommended_latency_ms"] - run1["recommended_latency_ms"], 2)

        return {
            "run_1": {
                "id": run1["id"],
                "scenario_id": run1["scenario_id"],
                "scenario_name": run1["scenario_name"],
                "created_at": run1["created_at"],
                "recommended_memory_mb": run1["recommended_memory_mb"],
                "recommended_cost": run1["recommended_cost"],
                "recommended_latency_ms": run1["recommended_latency_ms"],
                "recommended_availability_percent": run1["recommended_availability_percent"],
                "savings_percent": run1["savings_percent"],
                "status": run1["status"]
            },
            "run_2": {
                "id": run2["id"],
                "scenario_id": run2["scenario_id"],
                "scenario_name": run2["scenario_name"],
                "created_at": run2["created_at"],
                "recommended_memory_mb": run2["recommended_memory_mb"],
                "recommended_cost": run2["recommended_cost"],
                "recommended_latency_ms": run2["recommended_latency_ms"],
                "recommended_availability_percent": run2["recommended_availability_percent"],
                "savings_percent": run2["savings_percent"],
                "status": run2["status"]
            },
            "comparison_summary": {
                "cost_difference": cost_diff,
                "latency_difference_ms": latency_diff,
                "same_recommendation": run1["recommended_memory_mb"] == run2["recommended_memory_mb"]
            }
        }
