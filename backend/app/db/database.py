"""
SQLite Database Layer for Phase 3, 4, 5, and 6.
Provides local persistence for Organizations, Users, Scenarios, and Simulation History.

Uses Python's built-in sqlite3. Decoupled behind Repository patterns.
"""

import sqlite3
import os
from datetime import datetime

# DB file location (stored inside backend directory by default, or overridden by DB_PATH)
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "simulator.db")


def get_db_path() -> str:
    return os.environ.get("DB_PATH", DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Enables dict-like column access
    return conn


def init_db():
    """Creates tables if they do not exist and applies schema migrations."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Organizations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Seed Default Organization
    now = datetime.now().isoformat()
    cursor.execute("SELECT COUNT(*) FROM organizations WHERE id = 'default-org';")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO organizations (id, name, description, created_at, updated_at)
        VALUES ('default-org', 'Default Organization', 'Default System Workgroup', ?, ?);
        """, (now, now))

    # 2. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        organization_id TEXT NOT NULL,
        role TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (organization_id) REFERENCES organizations(id)
    );
    """)

    # 3. Scenarios Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        workload_type TEXT NOT NULL,
        request_volume INTEGER NOT NULL,
        baseline_memory_mb REAL NOT NULL,
        baseline_latency_ms REAL NOT NULL,
        cpu_utilization REAL NOT NULL,
        current_price REAL NOT NULL,
        latency_target_ms REAL NOT NULL,
        availability_target_percent REAL NOT NULL,
        organization_id TEXT DEFAULT 'default-org',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Check if organization_id column exists in scenarios table (migration check)
    cursor.execute("PRAGMA table_info(scenarios);")
    columns = [col[1] for col in cursor.fetchall()]
    if "organization_id" not in columns:
        cursor.execute("ALTER TABLE scenarios ADD COLUMN organization_id TEXT DEFAULT 'default-org';")

    # 4. Simulation History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_history (
        id TEXT PRIMARY KEY,
        scenario_id TEXT NOT NULL,
        scenario_name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        recommended_memory_mb REAL,
        recommended_cost REAL,
        recommended_latency_ms REAL,
        recommended_availability_percent REAL,
        savings_percent REAL,
        status TEXT NOT NULL,
        full_simulation_json TEXT NOT NULL,
        organization_id TEXT DEFAULT 'default-org'
    );
    """)

    cursor.execute("PRAGMA table_info(simulation_history);")
    columns_hist = [col[1] for col in cursor.fetchall()]
    if "organization_id" not in columns_hist:
        cursor.execute("ALTER TABLE simulation_history ADD COLUMN organization_id TEXT DEFAULT 'default-org';")

    conn.commit()

    # 5. Seed Default Scenario Presets if scenarios table is empty
    cursor.execute("SELECT COUNT(*) FROM scenarios;")
    count = cursor.fetchone()[0]

    if count == 0:
        presets = [
            (
                "preset-low-traffic",
                "Low Traffic",
                "Off-peak nighttime execution with low volume and loose targets",
                "Low Traffic",
                100000,
                1024.0,
                110.0,
                20.0,
                0.00001667,
                250.0,
                99.5,
                "default-org",
                now,
                now
            ),
            (
                "preset-normal-traffic",
                "Normal Traffic",
                "Standard daily business workload with typical CPU load",
                "Normal Traffic",
                2000000,
                1024.0,
                150.0,
                65.0,
                0.00001667,
                200.0,
                99.9,
                "default-org",
                now,
                now
            ),
            (
                "preset-high-traffic",
                "High Traffic",
                "Peak business hours traffic spike with strict performance targets",
                "High Traffic",
                8000000,
                1024.0,
                220.0,
                90.0,
                0.00001667,
                180.0,
                99.9,
                "default-org",
                now,
                now
            )
        ]

        cursor.executemany("""
        INSERT INTO scenarios (
            id, name, description, workload_type, request_volume,
            baseline_memory_mb, baseline_latency_ms, cpu_utilization,
            current_price, latency_target_ms, availability_target_percent,
            organization_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, presets)

        conn.commit()

    conn.close()
