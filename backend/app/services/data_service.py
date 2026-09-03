"""
Data Service — loads and processes the synthetic serverless metrics CSV.

Responsibilities:
  1. Load the CSV file from the configured path
  2. Validate that all required columns are present
  3. Detect and report missing values
  4. Compute basic summary statistics

NOTE: All data processed here is SYNTHETIC and generated for simulation
purposes only. It does not represent real AWS billing or performance data.
"""

import os
import pandas as pd
import numpy as np
from app.utils.config import settings
from app.models.response_models import MetricsSummary, DatasetInfo

# Columns that must exist in the CSV for the service to work correctly
REQUIRED_COLUMNS = [
    "timestamp",
    "cpu_utilization",
    "memory_mb",
    "latency_ms",
    "request_volume",
    "instance_price",
    "availability",
]


def _resolve_data_path() -> str:
    """
    Resolve the CSV path relative to this file's location so the backend
    works regardless of which directory uvicorn is launched from.
    """
    # Walk up from this file: app/services/ -> app/ -> backend/ -> project root
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    configured = settings.data_file_path

    # If the path is already absolute, use it directly
    if os.path.isabs(configured):
        return configured

    # Otherwise resolve relative to the backend directory
    return os.path.normpath(os.path.join(backend_dir, configured))


def load_dataframe() -> pd.DataFrame:
    """Load the metrics CSV and return a validated DataFrame."""
    path = _resolve_data_path()

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Metrics CSV not found at: {path}. "
            "Run data/generate_data.py to create it."
        )

    df = pd.read_csv(path, parse_dates=["timestamp"])

    # Validate that all required columns are present
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"CSV is missing required columns: {missing_cols}. "
            f"Found columns: {df.columns.tolist()}"
        )

    return df


def get_metrics_summary() -> MetricsSummary:
    """
    Load the CSV and compute summary statistics.
    Returns a MetricsSummary Pydantic model ready to be serialized as JSON.
    """
    df = load_dataframe()

    # Count missing (NaN) values per column for data quality reporting
    missing_values = {
        col: int(df[col].isna().sum())
        for col in REQUIRED_COLUMNS
    }

    # Build dataset info block
    dataset_info = DatasetInfo(
        total_records=len(df),
        date_range_start=df["timestamp"].min().isoformat() if not df["timestamp"].isna().all() else None,
        date_range_end=df["timestamp"].max().isoformat() if not df["timestamp"].isna().all() else None,
        missing_values=missing_values,
    )

    # Compute aggregated statistics
    summary = MetricsSummary(
        average_cpu_utilization=round(float(df["cpu_utilization"].mean()), 2),
        average_memory_mb=round(float(df["memory_mb"].mean()), 2),
        average_latency_ms=round(float(df["latency_ms"].mean()), 2),
        total_request_volume=int(df["request_volume"].sum()),
        average_availability=round(float(df["availability"].mean()), 4),
        total_estimated_cost=round(float(df["instance_price"].sum()), 6),
        average_request_volume_per_interval=round(float(df["request_volume"].mean()), 2),
        dataset_info=dataset_info,
        note=(
            "SYNTHETIC DATA: These statistics are derived from artificially "
            "generated data for demonstration and simulation purposes only. "
            "They do not represent real AWS infrastructure costs or performance."
        ),
    )

    return summary
