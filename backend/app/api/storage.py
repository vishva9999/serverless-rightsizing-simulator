"""
Storage API Router — Phase 4 Storage Status Endpoint.

Exposes GET /api/storage/status to inspect current active storage mode (Local vs AWS),
database provider (SQLite vs DynamoDB), and S3 artifact status.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.utils.config import settings

router = APIRouter(prefix="/api/storage", tags=["Storage"])


class StorageStatusResponse(BaseModel):
    mode: str
    database: str
    s3_enabled: bool
    aws_configured: bool
    aws_region: str
    scenarios_table: str
    history_table: str
    s3_bucket: str
    aws_connectivity_status: Optional[str] = None


@router.get(
    "/status",
    response_model=StorageStatusResponse,
    summary="Get Storage Status",
    description="Returns current storage mode configuration (local SQLite vs AWS cloud DynamoDB/S3)."
)
def get_storage_status():
    mode = settings.storage_mode.lower()
    is_aws = (mode == "aws")

    aws_connectivity_status = None

    if is_aws:
        try:
            import boto3
            sts = boto3.client("sts", region_name=settings.aws_region)
            sts.get_caller_identity()
            aws_connectivity_status = "Connected to AWS"
        except Exception as e:
            aws_connectivity_status = f"AWS Credential/Network Error: {str(e)}"

    return StorageStatusResponse(
        mode=mode,
        database="DynamoDB" if is_aws else "SQLite",
        s3_enabled=is_aws,
        aws_configured=is_aws,
        aws_region=settings.aws_region,
        scenarios_table=settings.scenarios_table,
        history_table=settings.history_table,
        s3_bucket=settings.s3_bucket,
        aws_connectivity_status=aws_connectivity_status
    )
