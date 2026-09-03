"""
Configuration utility for the Serverless Rightsizing Simulator backend.
Reads settings from environment variables or .env file using pydantic-settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    project_name: str = "Serverless Cost & Performance Rightsizing Simulator"
    version: str = "0.1.0"
    environment: str = "development"

    # Path to the synthetic CSV dataset (relative to backend/ working directory)
    data_file_path: str = "../data/sample_serverless_metrics.csv"

    # CORS allowed origin for the React dev server / CloudFront distribution
    cors_origin: str = "http://localhost:5173"

    # --- Phase 4 AWS & Storage Settings ---
    # storage_mode: 'local' (SQLite) or 'aws' (DynamoDB + S3)
    storage_mode: str = "local"
    aws_region: str = "ap-south-1"
    scenarios_table: str = "serverless-rightsizing-scenarios"
    history_table: str = "serverless-rightsizing-history"
    s3_bucket: str = "serverless-rightsizing-artifacts"

    # --- Phase 6 & 7 Auth & RBAC Settings ---
    # auth_mode: 'local' (JWT/SQLite) or 'cognito' (AWS Cognito User Pool)
    auth_mode: str = "local"
    jwt_secret_key: str = "change-me-in-development-secret-key-32bytes"
    jwt_expire_minutes: int = 60

    # Amazon Cognito settings (used when auth_mode='cognito')
    cognito_user_pool_id: Optional[str] = None
    cognito_client_id: Optional[str] = None
    cognito_region: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Single shared settings instance used throughout the application
settings = Settings()
