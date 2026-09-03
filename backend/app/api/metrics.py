"""
Metrics endpoints.
Provides summary statistics derived from the synthetic serverless metrics dataset.
"""

from fastapi import APIRouter, HTTPException
from app.models.response_models import MetricsSummary
from app.services.data_service import get_metrics_summary

router = APIRouter(prefix="/api/metrics")


@router.get("/summary", response_model=MetricsSummary, tags=["Metrics"])
def metrics_summary():
    """
    Returns aggregated statistics from the synthetic metrics CSV dataset.

    Statistics include:
    - Average CPU utilization (%)
    - Average memory usage (MB)
    - Average latency (ms)
    - Total request volume
    - Average availability (%)
    - Total estimated cost (USD)
    - Dataset info (record count, date range, missing values)

    Note: All data is synthetic and generated for simulation purposes only.
    """
    try:
        return get_metrics_summary()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process metrics data: {str(e)}",
        )
