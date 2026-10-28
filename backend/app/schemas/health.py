from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DatabaseHealth(BaseModel):
    connected: bool
    engine: str
    is_fallback: bool
    message: str


class HealthResponse(BaseModel):
    status: str = Field(default="ok", json_schema_extra={"example": "ok"})
    app_name: str
    environment: str
    timestamp: datetime
    uptime_seconds: float
    database: DatabaseHealth
    is_simulated: bool = Field(default=True, description="Strictly simulated platform flag")
    emergency_services_integrated: bool = Field(default=False, description="Explicit confirmation of no real emergency dispatch integration")
    simulation_disclaimer: str = Field(
        default="SIMULATED PLATFORM ONLY. Not connected to real-world 911, civil defense, or emergency services."
    )


class VersionResponse(BaseModel):
    app_name: str
    version: str = "1.0.0-phase1"
    api_version: str = "v1"
    environment: str
    is_simulated: bool = True
    build_target: str = "command_center_shell"
