# backend/app.py
"""
Grocery AI Planner - Main FastAPI Application
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from core.database import engine, get_db
from core.models import Base
from core.config import get_settings
from api.routes import auth, users, stores, meal_plans, scraping, health
from telemetry import get_telemetry_config, is_telemetry_available

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global telemetry configuration
telemetry_config = get_telemetry_config()


async def startup_health_checks():
    """Perform comprehensive startup health checks."""
    logger.info("🔍 Starting application health checks...")
    
    # Test database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Test Redis connection (for Celery)
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        sys.exit(1)
    
    # Test LLM connection (if configured)
    try:
        from core.llm_client import create_llm_client
        llm_client = create_llm_client(
            api_url=settings.llm_api_url,
            default_model=settings.default_model,
            telemetry_config=telemetry_config
        )
        health_result = llm_client.health_check()
        if health_result["status"] == "healthy":
            logger.info("✅ LLM client connection successful")
        else:
            logger.warning(f"⚠️ LLM client health check warning: {health_result}")
    except Exception as e:
        logger.warning(f"⚠️ LLM client connection failed: {e}")
        logger.warning("Application will continue but AI features may be limited")

    logger.info("🎉 Health checks completed successfully")


def setup_telemetry(app: FastAPI):
    """Configure telemetry and monitoring."""
    if telemetry_config.enabled and is_telemetry_available():
        try:
            # Instrument FastAPI
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            FastAPIInstrumentor.instrument_app(app)
            logger.info("✅ FastAPI instrumented with OpenTelemetry")
            
            # Start metrics server
            provider = telemetry_config.provider
            if hasattr(provider, 'start_metrics_server'):
                provider.start_metrics_server()
                logger.info(f"✅ Metrics server started on port {settings.telemetry_metrics_port}")
            
        except Exception as e:
            logger.warning(f"⚠️ Telemetry setup failed: {e}")
    else:
        logger.info("📊 Telemetry disabled")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager."""
    logger.info("🚀 Starting Grocery AI Planner API")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Run health checks
    await startup_health_checks()
    
    # Setup telemetry
    setup_telemetry(app)
    
    logger.info("🎉 Application startup complete")
    yield
    
    logger.info("🛑 Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="Grocery AI Planner API",
    description="AI-powered meal planning with real-time grocery deal optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(stores.router, prefix="/api/v1/stores", tags=["stores"])
app.include_router(meal_plans.router, prefix="/api/v1/meal-plans", tags=["meal-plans"])
app.include_router(scraping.router, prefix="/api/v1/scraping", tags=["scraping"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Grocery AI Planner API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/docs": "Interactive API documentation",
            "/api/v1/health": "Health check endpoints",
            "/api/v1/auth": "User authentication",
            "/api/v1/users": "User management", 
            "/api/v1/stores": "Store discovery and management",
            "/api/v1/meal-plans": "AI meal plan generation",
            "/api/v1/scraping": "Grocery deal scraping"
        },
        "telemetry": {
            "enabled": telemetry_config.enabled,
            "metrics_port": settings.telemetry_metrics_port if telemetry_config.enabled else None
        }
    }


@app.get("/metrics-info")
async def metrics_info():
    """Metrics endpoint information."""
    if telemetry_config.enabled and is_telemetry_available():
        return {
            "message": f"Metrics available at http://localhost:{settings.telemetry_metrics_port}/metrics",
            "prometheus_port": settings.telemetry_metrics_port,
            "grafana_url": f"http://localhost:3000",
            "telemetry_enabled": True
        }
    else:
        return {
            "message": "Metrics not available - telemetry disabled or OpenTelemetry not installed",
            "telemetry_enabled": False
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )