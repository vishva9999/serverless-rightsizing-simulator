"""
Scenario Repository — Data Access Layer for Scenarios.

Decouples storage logic from FastAPI controllers and services.
Supports multi-tenant organization filtering.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.database import get_connection


class ScenarioRepository:
    """Repository handling CRUD operations for Scenarios in SQLite."""

    @staticmethod
    def list_all(organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        if organization_id:
            cursor.execute("SELECT * FROM scenarios WHERE organization_id = ? ORDER BY created_at DESC;", (organization_id,))
        else:
            cursor.execute("SELECT * FROM scenarios ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(scenario_id: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        if organization_id:
            cursor.execute("SELECT * FROM scenarios WHERE id = ? AND organization_id = ?;", (scenario_id, organization_id))
        else:
            cursor.execute("SELECT * FROM scenarios WHERE id = ?;", (scenario_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(data: Dict[str, Any], organization_id: Optional[str] = None) -> Dict[str, Any]:
        scenario_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        org_id = organization_id or data.get("organization_id", "default-org")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO scenarios (
            id, name, description, workload_type, request_volume,
            baseline_memory_mb, baseline_latency_ms, cpu_utilization,
            current_price, latency_target_ms, availability_target_percent,
            organization_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            scenario_id,
            data["name"],
            data.get("description", ""),
            data["workload_type"],
            data["request_volume"],
            data["baseline_memory_mb"],
            data["baseline_latency_ms"],
            data["cpu_utilization"],
            data["current_price"],
            data["latency_target_ms"],
            data["availability_target_percent"],
            org_id,
            now,
            now
        ))
        conn.commit()
        conn.close()

        return ScenarioRepository.get_by_id(scenario_id)

    @staticmethod
    def update(scenario_id: str, data: Dict[str, Any], organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        existing = ScenarioRepository.get_by_id(scenario_id, organization_id)
        if not existing:
            return None

        now = datetime.now().isoformat()
        updated_name = data.get("name", existing["name"])
        updated_desc = data.get("description", existing["description"])
        updated_workload = data.get("workload_type", existing["workload_type"])
        updated_req_vol = data.get("request_volume", existing["request_volume"])
        updated_mem = data.get("baseline_memory_mb", existing["baseline_memory_mb"])
        updated_lat = data.get("baseline_latency_ms", existing["baseline_latency_ms"])
        updated_cpu = data.get("cpu_utilization", existing["cpu_utilization"])
        updated_price = data.get("current_price", existing["current_price"])
        updated_lat_target = data.get("latency_target_ms", existing["latency_target_ms"])
        updated_avail_target = data.get("availability_target_percent", existing["availability_target_percent"])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE scenarios SET
            name = ?,
            description = ?,
            workload_type = ?,
            request_volume = ?,
            baseline_memory_mb = ?,
            baseline_latency_ms = ?,
            cpu_utilization = ?,
            current_price = ?,
            latency_target_ms = ?,
            availability_target_percent = ?,
            updated_at = ?
        WHERE id = ?;
        """, (
            updated_name,
            updated_desc,
            updated_workload,
            updated_req_vol,
            updated_mem,
            updated_lat,
            updated_cpu,
            updated_price,
            updated_lat_target,
            updated_avail_target,
            now,
            scenario_id
        ))
        conn.commit()
        conn.close()

        return ScenarioRepository.get_by_id(scenario_id)

    @staticmethod
    def delete(scenario_id: str, organization_id: Optional[str] = None) -> bool:
        existing = ScenarioRepository.get_by_id(scenario_id, organization_id)
        if not existing:
            return False

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scenarios WHERE id = ?;", (scenario_id,))
        conn.commit()
        conn.close()
        return True
