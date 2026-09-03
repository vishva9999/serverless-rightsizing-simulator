"""
User Repository — Data Access Layer for User Profiles & Credentials.
Encapsulates SQLite CRUD operations for User accounts.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.db.database import get_connection


class UserRepository:
    """Repository handling CRUD operations for Users in SQLite."""

    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?);", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def list_by_organization(organization_id: str) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, organization_id, role, is_active, created_at, updated_at FROM users WHERE organization_id = ? ORDER BY created_at ASC;", (organization_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def create(
        email: str,
        password_hash: str,
        full_name: str,
        organization_id: str,
        role: str = "analyst",
        is_active: bool = True
    ) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (
            id, email, password_hash, full_name, organization_id, role, is_active, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            user_id,
            email.lower().strip(),
            password_hash,
            full_name.strip(),
            organization_id,
            role.lower(),
            1 if is_active else 0,
            now,
            now
        ))
        conn.commit()
        conn.close()

        res = UserRepository.get_by_id(user_id)
        if res:
            res.pop("password_hash", None)
        return res

    @staticmethod
    def update_role(user_id: str, new_role: str, organization_id: str) -> Optional[Dict[str, Any]]:
        existing = UserRepository.get_by_id(user_id)
        if not existing or existing["organization_id"] != organization_id:
            return None

        now = datetime.now().isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET role = ?, updated_at = ? WHERE id = ? AND organization_id = ?;
        """, (new_role.lower(), now, user_id, organization_id))
        conn.commit()
        conn.close()

        res = UserRepository.get_by_id(user_id)
        if res:
            res.pop("password_hash", None)
        return res

    @staticmethod
    def update_status(user_id: str, is_active: bool, organization_id: str) -> Optional[Dict[str, Any]]:
        existing = UserRepository.get_by_id(user_id)
        if not existing or existing["organization_id"] != organization_id:
            return None

        now = datetime.now().isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET is_active = ?, updated_at = ? WHERE id = ? AND organization_id = ?;
        """, (1 if is_active else 0, now, user_id, organization_id))
        conn.commit()
        conn.close()

        res = UserRepository.get_by_id(user_id)
        if res:
            res.pop("password_hash", None)
        return res

    @staticmethod
    def count_active_admins_in_org(organization_id: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT COUNT(*) FROM users WHERE organization_id = ? AND role = 'admin' AND is_active = 1;
        """, (organization_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
