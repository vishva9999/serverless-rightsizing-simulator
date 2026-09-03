"""
FastAPI application entry point.

This is the main file that:
  - Creates the FastAPI app instance
  - Configures CORS for React frontend communication
  - Initializes local SQLite persistence database (if in local mode)
  - Registers all API routers (health, info, metrics, simulate, scenarios, history, storage, sensitivity, auth, organizations, users)
  - Serves OpenAPI docs at /docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.config import settings
from app.api import health, info, metrics, simulate, scenarios, history, storage, sensitivity, auth, organizations, users
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize SQLite database tables & default scenario presets if in local mode
    if settings.storage_mode.lower() == "local":
        init_db()
    yield


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=(
        "Backend API for the Serverless Cost & Performance Rightsizing Simulator. "
        "Phase 6: Local JWT Authentication, Multi-Tenant Organizations & RBAC Permissions."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router Registration ---
app.include_router(health.router)
app.include_router(info.router)
app.include_router(metrics.router)
app.include_router(simulate.router)
app.include_router(scenarios.router)
app.include_router(history.router)
app.include_router(storage.router)
app.include_router(sensitivity.router)
app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(users.router)


# --- Root Redirect ---
@app.get("/", tags=["Root"])
def root():
    """Root endpoint — confirms the API is live and points to docs."""
    return {
        "message": f"Welcome to {settings.project_name} API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health",
        "storage_status": "/api/storage/status"
    }
