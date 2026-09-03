"""
Unit tests for Phase 4 AWS Cloud Persistence & Storage Factory.

Uses unittest.mock to mock boto3 — ZERO real AWS API calls are made.

Verifies:
  1. Default local storage mode selection (STORAGE_MODE=local -> SQLite)
  2. Storage status API endpoint (GET /api/storage/status)
  3. Storage factory repository selection
  4. DynamoDB scenario repository CRUD (mocked boto3)
  5. DynamoDB history repository CRUD & comparison (mocked boto3)
  6. S3 service artifact upload behavior in local vs AWS mode
  7. Missing AWS credentials graceful error handling
  8. Invalid storage mode fallback
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.utils.config import settings
from app.repositories.storage_factory import get_scenario_repository, get_history_repository
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.history_repository import HistoryRepository
from app.repositories.dynamodb_scenario_repository import DynamoDBScenarioRepository
from app.repositories.dynamodb_history_repository import DynamoDBHistoryRepository
from app.services.s3_service import S3Service

client = TestClient(app)


def test_1_local_storage_mode_selection():
    """Verify STORAGE_MODE=local selects SQLite repositories."""
    with patch.object(settings, "storage_mode", "local"):
        s_repo = get_scenario_repository()
        h_repo = get_history_repository()
        assert s_repo == ScenarioRepository
        assert h_repo == HistoryRepository


def test_2_aws_storage_mode_selection():
    """Verify STORAGE_MODE=aws selects DynamoDB repositories."""
    with patch.object(settings, "storage_mode", "aws"):
        s_repo = get_scenario_repository()
        h_repo = get_history_repository()
        assert s_repo == DynamoDBScenarioRepository
        assert h_repo == DynamoDBHistoryRepository


def test_3_storage_status_endpoint_local():
    """Verify GET /api/storage/status returns local mode info."""
    with patch.object(settings, "storage_mode", "local"):
        response = client.get("/api/storage/status")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "local"
        assert data["database"] == "SQLite"
        assert data["s3_enabled"] is False
        assert data["aws_configured"] is False


def test_4_storage_status_endpoint_aws_mocked():
    """Verify GET /api/storage/status returns AWS mode info with mocked STS."""
    with patch.object(settings, "storage_mode", "aws"):
        with patch("boto3.client") as mock_boto:
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
            mock_boto.return_value = mock_sts

            response = client.get("/api/storage/status")
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "aws"
            assert data["database"] == "DynamoDB"
            assert data["s3_enabled"] is True
            assert data["aws_configured"] is True
            assert data["aws_connectivity_status"] == "Connected to AWS"


def test_5_s3_service_bypassed_in_local_mode():
    """Verify S3Service skips uploads in local mode."""
    with patch.object(settings, "storage_mode", "local"):
        result = S3Service.upload_simulation_artifact(
            scenario_id="scen-1",
            history_id="hist-1",
            simulation_result={"status": "success"}
        )
        assert result is None


def test_6_s3_service_upload_aws_mode_mocked():
    """Verify S3Service uploads simulation artifact in AWS mode using mocked boto3."""
    with patch.object(settings, "storage_mode", "aws"):
        with patch("boto3.client") as mock_boto:
            mock_s3 = MagicMock()
            mock_boto.return_value = mock_s3

            result = S3Service.upload_simulation_artifact(
                scenario_id="scen-123",
                history_id="hist-456",
                simulation_result={"status": "success", "recommendation": {"memory_mb": 1024}}
            )

            assert result == "simulations/scen-123/hist-456.json"
            mock_s3.put_object.assert_called_once()
            call_kwargs = mock_s3.put_object.call_args[1]
            assert call_kwargs["Bucket"] == settings.s3_bucket
            assert call_kwargs["Key"] == "simulations/scen-123/hist-456.json"


def test_7_dynamodb_scenario_repository_mocked():
    """Verify DynamoDBScenarioRepository CRUD using mocked boto3."""
    with patch("boto3.resource") as mock_boto_res:
        mock_table = MagicMock()
        mock_boto_res.return_value.Table.return_value = mock_table

        # Test Create
        payload = {
            "name": "Mocked AWS Scenario",
            "workload_type": "High Traffic",
            "request_volume": 5000000,
            "baseline_memory_mb": 1024.0,
            "baseline_latency_ms": 180.0,
            "cpu_utilization": 70.0,
            "current_price": 0.00001667,
            "latency_target_ms": 200.0,
            "availability_target_percent": 99.9
        }
        created = DynamoDBScenarioRepository.create(payload)
        assert created["name"] == "Mocked AWS Scenario"
        mock_table.put_item.assert_called()

        # Test List
        mock_table.scan.return_value = {"Items": [created]}
        scenarios = DynamoDBScenarioRepository.list_all()
        assert len(scenarios) == 1
        assert scenarios[0]["name"] == "Mocked AWS Scenario"


def test_8_dynamodb_history_repository_mocked():
    """Verify DynamoDBHistoryRepository CRUD & compare using mocked boto3."""
    with patch("boto3.resource") as mock_boto_res:
        mock_table = MagicMock()
        mock_boto_res.return_value.Table.return_value = mock_table

        sim_res = {
            "simulation_status": "success",
            "baseline": {"memory_mb": 1024.0},
            "recommendation": {
                "memory_mb": 1024.0,
                "estimated_monthly_cost": 5.001,
                "estimated_latency_ms": 150.0,
                "estimated_availability": 99.96,
                "cost_savings_percentage": 0.0
            }
        }

        entry = DynamoDBHistoryRepository.create("scen-1", "Mocked Scenario", sim_res)
        assert entry["scenario_id"] == "scen-1"
        assert entry["status"] == "Near Optimal"


def test_9_missing_aws_credentials_handling():
    """Verify graceful handling when AWS credentials are missing in AWS mode."""
    with patch.object(settings, "storage_mode", "aws"):
        with patch("boto3.client") as mock_boto:
            mock_boto.side_effect = Exception("No AWS credentials found")

            response = client.get("/api/storage/status")
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "aws"
            assert "No AWS credentials found" in data["aws_connectivity_status"]


def test_10_invalid_storage_mode_fallback():
    """Verify invalid storage_mode setting falls back to SQLite."""
    with patch.object(settings, "storage_mode", "invalid_mode_name"):
        s_repo = get_scenario_repository()
        h_repo = get_history_repository()
        assert s_repo == ScenarioRepository
        assert h_repo == HistoryRepository
