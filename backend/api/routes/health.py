# backend/api/routes/health.py
"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from core.database import get_db
from core.config import get_settings
from telemetry import get_telemetry_info

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check."""
    settings = get_settings()
    
    # Test database
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
        db_error = None
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
    
    # Test Redis
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        redis_status = "healthy"
        redis_error = None
    except Exception as e:
        redis_status = "unhealthy"
        redis_error = str(e)
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "components": {
            "database": {
                "status": db_status,
                "error": db_error
            },
            "redis": {
                "status": redis_status, 
                "error": redis_error
            }
        },
        "telemetry": get_telemetry_info()
    }


@router.get("/health/simple")
async def simple_health():
    """Simple health check for load balancers."""
    return {"status": "ok", "timestamp": "2024-01-01T00:00:00Z"}