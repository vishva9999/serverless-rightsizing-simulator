from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    # Base application metadata
    APP_NAME: str = "AI Disaster Evacuation & Resource Allocation Command Center"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # Simulation Notice: All data is synthetic / simulated
    IS_SIMULATION_MODE: bool = True
    EMERGENCY_SERVICES_INTEGRATED: bool = False

    # Security
    SECRET_KEY: str = "dev-secret-key-32-chars-long-safety-token-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql://command_admin:command_secure_password@localhost:5432/disaster_command_db"
    USE_SQLITE_FALLBACK: bool = True
    SQLITE_FALLBACK_URL: str = "sqlite:///./disaster_command_local.db"

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # WebSocket
    WS_PING_INTERVAL_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
