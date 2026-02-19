"""
Health check endpoints for monitoring.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from redis import Redis

from app.database import SessionLocal
from app.config import settings
from app.logging_config import get_logger

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health/live")
def liveness():
    """
    Liveness probe - is the service alive?
    
    Returns 200 if the application is running.
    Used by Kubernetes/Docker to know if container should be restarted.
    """
    return {"status": "alive"}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    """
    Readiness probe - is the service ready to accept traffic?
    
    Checks:
    - Database connectivity
    - Redis connectivity
    
    Returns 200 if all dependencies are healthy, 503 otherwise.
    Used by load balancers to know if traffic should be routed here.
    """
    checks = {
        "database": check_database(db),
        "redis": check_redis(),
    }
    
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "version": settings.app_version
        }
    )


@router.get("/health/startup")
def startup(db: Session = Depends(get_db)):
    """
    Startup probe - has the service finished starting up?
    
    Same as readiness but can have different timeout configuration.
    """
    return readiness(db)


def check_database(db: Session) -> bool:
    """
    Check database connectivity.
    
    Returns:
        True if database is accessible, False otherwise
    """
    try:
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))
        return False


def check_redis() -> bool:
    """
    Check Redis connectivity.
    
    Returns:
        True if Redis is accessible, False otherwise
    """
    try:
        redis_client = Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        redis_client.ping()
        return True
    except Exception as e:
        logger.error("health_check_redis_failed", error=str(e))
        return False
