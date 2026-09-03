"""
S3 Artifact Storage Service — Phase 4 S3 Cloud Artifact Export.

Uploads full simulation execution results to S3 when STORAGE_MODE=aws.
If STORAGE_MODE=local, S3 operations are bypassed silently.
"""

import json
import logging
from typing import Optional, Dict, Any
from app.utils.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service handling S3 simulation JSON artifact exports."""

    @staticmethod
    def upload_simulation_artifact(
        scenario_id: str,
        history_id: str,
        simulation_result: Dict[str, Any]
    ) -> Optional[str]:
        """
        Uploads simulation result JSON to S3 bucket if STORAGE_MODE=aws.
        S3 key structure: simulations/{scenario_id}/{history_id}.json
        """
        if settings.storage_mode.lower() != "aws":
            return None

        object_key = f"simulations/{scenario_id}/{history_id}.json"

        try:
            import boto3
            s3_client = boto3.client("s3", region_name=settings.aws_region)
            json_data = json.dumps(simulation_result, indent=2)

            s3_client.put_object(
                Bucket=settings.s3_bucket,
                Key=object_key,
                Body=json_data,
                ContentType="application/json"
            )
            logger.info(f"Uploaded simulation artifact to s3://{settings.s3_bucket}/{object_key}")
            return object_key
        except Exception as e:
            logger.warning(f"S3 artifact upload skipped or failed: {str(e)}")
            return None
