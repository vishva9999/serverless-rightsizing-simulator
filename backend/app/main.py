from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from app.core.database import Base, engine, check_db_connection
from app.api.v1.router import api_v1_router
from app.api.v1.endpoints import health, version
from app.websocket.manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("=" * 70)
    logger.info(f"Initializing {settings.APP_NAME}")
    logger.info(f"Environment: {settings.APP_ENV} | Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Simulation Mode: {settings.IS_SIMULATION_MODE} (Real Dispatch: {settings.EMERGENCY_SERVICES_INTEGRATED})")
    
    # Initialize database tables if connected
    db_status = check_db_connection()
    logger.info(f"Database status: {db_status}")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Core database schema initialized successfully")
    except Exception as e:
        logger.warning(f"Could not automatically create database tables on startup: {e}")
        
    logger.info("Command Center Backend startup complete")
    logger.info("=" * 70)

    yield

    # Shutdown sequence
    logger.info("Shutting down Command Center Backend")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Decision-support and disaster simulation platform command center backend. "
        "NOTICE: All incident feeds, GIS overlays, and resource dispatches are mathematically "
        "simulated for research and operational drills. No integration with real emergency services."
    ),
    version="1.0.0-phase1",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# CORS middleware
origins = settings.BACKEND_CORS_ORIGINS if isinstance(settings.BACKEND_CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root level /api aliases as requested: GET /api/health and GET /api/version
app.include_router(health.router, prefix="/api", tags=["Health & Status"])
app.include_router(version.router, prefix="/api", tags=["Version"])

# Versioned router /api/v1/...
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


# WebSocket endpoint for real-time telemetry stream
@app.websocket("/ws")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial handshake message confirming simulation mode
        await websocket.send_json({
            "event": "CONNECTED",
            "message": "Connected to Disaster Command Center Telemetry Stream",
            "is_simulated": True,
            "emergency_services_integrated": False,
        })
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat / telemetry request
            await websocket.send_json({
                "event": "PONG",
                "received": data,
                "is_simulated": True,
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket communication exception: {e}")
        ws_manager.disconnect(websocket)
