"""
System Integration Test Suite for Disaster Command Center.
Validates end-to-end contract between frontend expectations and backend endpoints.
"""
import pytest
import sys
import os

# Include backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
from app.main import app


def test_system_health_and_simulation_contract():
    """Verify that backend strictly adheres to simulation safety flags."""
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    # Safety Assertions
    assert data["is_simulated"] is True
    assert data["emergency_services_integrated"] is False
    assert "SIMULATED PLATFORM ONLY" in data["simulation_disclaimer"]


def test_system_version_contract():
    """Verify semantic versioning and build target metadata."""
    client = TestClient(app)
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0-phase1"
    assert data["api_version"] == "v1"
    assert data["is_simulated"] is True
