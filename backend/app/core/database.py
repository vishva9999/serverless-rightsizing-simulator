from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from app.core.config import settings
from app.core.logging import logger
from app.models.base import Base


def _init_engine():
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        return create_engine(settings.DATABASE_URL, connect_args=connect_args)
    
    try:
        pg_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args=connect_args,
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return pg_engine
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK:
            logger.warning(f"Could not connect to PostgreSQL ({e}). Using SQLite fallback: {settings.SQLITE_FALLBACK_URL}")
            return create_engine(settings.SQLITE_FALLBACK_URL, connect_args={"check_same_thread": False})
        logger.warning(f"Could not initialize database engine: {e}")
        return pg_engine


engine = _init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> Dict[str, Any]:
    """
    Actively verifies connectivity to the configured database.
    Returns status dictionary with connection latency and engine type.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            return {
                "connected": result == 1,
                "engine": engine.dialect.name,
                "is_fallback": "sqlite" in str(engine.url),
                "message": "Database operational",
            }
    except (OperationalError, SQLAlchemyError, Exception) as e:
        logger.warning(f"Database health check failed: {e}")
        return {
            "connected": False,
            "engine": engine.dialect.name if hasattr(engine, "dialect") else "unknown",
            "is_fallback": "sqlite" in str(engine.url),
            "message": f"Database unreachable: {type(e).__name__}",
        }

