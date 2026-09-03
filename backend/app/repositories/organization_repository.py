"""
Organization Repository — Data Access Layer for Organizations.
Encapsulates SQLite operations for Organization management.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.database import get_connection


class OrganizationRepository:
    """Repository handling CRUD operations for Organizations in SQLite."""

    @staticmethod
    def get_by_id(org_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organizations WHERE id = ?;", (org_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_name(name: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organizations WHERE LOWER(name) = LOWER(?);", (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name: str, description: str = "") -> Dict[str, Any]:
        org_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO organizations (id, name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?);
        """, (org_id, name, description, now, now))
        conn.commit()
        conn.close()

        return OrganizationRepository.get_by_id(org_id)

    @staticmethod
    def update(org_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        existing = OrganizationRepository.get_by_id(org_id)
        if not existing:
            return None

        now = datetime.now().isoformat()
        new_name = name if name is not None else existing["name"]
        new_desc = description if description is not None else existing["description"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE organizations SET name = ?, description = ?, updated_at = ? WHERE id = ?;
        """, (new_name, new_desc, now, org_id))
        conn.commit()
        conn.close()

        return OrganizationRepository.get_by_id(org_id)

    @staticmethod
    def get_member_count(org_id: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE organization_id = ?;", (org_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
