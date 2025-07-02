# backend/core/config.py
"""
Application configuration using Pydantic settings.
"""

import os
from functools import lru_cache
from typing import Optional, List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Grocery AI Planner"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # Database
    database_url: str = Field(env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(env="REDIS_URL")
    
    # LLM Configuration
    llm_api_url: str = Field(env="LLM_API_URL")
    default_model: str = Field(default="qwen2.5-coder:14b", env="DEFAULT_MODEL")
    
    # Telemetry
    telemetry_enabled: bool = Field(default=True, env="TELEMETRY_ENABLED")
    telemetry_metrics_port: int = Field(default=8001, env="TELEMETRY_METRICS_PORT")
    telemetry_console_export: bool = Field(default=False, env="TELEMETRY_CONSOLE_EXPORT")
    
    # External APIs
    google_maps_api_key: Optional[str] = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    
    # Email Configuration
    mail_username: Optional[str] = Field(default=None, env="MAIL_USERNAME")
    mail_password: Optional[str] = Field(default=None, env="MAIL_PASSWORD")
    mail_from: Optional[str] = Field(default=None, env="MAIL_FROM")
    mail_port: int = Field(default=587, env="MAIL_PORT")
    mail_server: Optional[str] = Field(default=None, env="MAIL_SERVER")
    mail_starttls: bool = Field(default=True, env="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(default=False, env="MAIL_SSL_TLS")
    
    # Scraping Configuration
    max_scrape_workers: int = Field(default=3, env="MAX_SCRAPE_WORKERS")
    scrape_delay_min: int = Field(default=1, env="SCRAPE_DELAY_MIN")
    scrape_delay_max: int = Field(default=3, env="SCRAPE_DELAY_MAX")
    user_agent: str = Field(default="GroceryAI-Bot/1.0", env="USER_AGENT")
    
    # New Scraping System Configuration
    flipp_rate_limit_delay: float = Field(default=0.5, env="FLIPP_RATE_LIMIT_DELAY")
    scraping_timeout: int = Field(default=30, env="SCRAPING_TIMEOUT")
    selenium_headless: bool = Field(default=True, env="SELENIUM_HEADLESS")
    max_scraping_retries: int = Field(default=3, env="MAX_SCRAPING_RETRIES")
    enable_flipp_api: bool = Field(default=True, env="ENABLE_FLIPP_API")
    enable_selenium_fallback: bool = Field(default=True, env="ENABLE_SELENIUM_FALLBACK")
    enable_pdf_fallback: bool = Field(default=False, env="ENABLE_PDF_FALLBACK")
    enable_vision_fallback: bool = Field(default=False, env="ENABLE_VISION_FALLBACK")
    
    # Job Configuration
    celery_result_expires: int = Field(default=3600, env="CELERY_RESULT_EXPIRES")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Database configuration
def get_database_url() -> str:
    """Get database URL with fallback."""
    settings = get_settings()
    return settings.database_url


# Redis configuration  
def get_redis_url() -> str:
    """Get Redis URL with fallback."""
    settings = get_settings()
    return settings.redis_url


# Celery configuration
def get_celery_config() -> dict:
    """Get Celery configuration."""
    settings = get_settings()
    return {
        'broker_url': settings.redis_url,
        'result_backend': settings.redis_url,
        'result_expires': settings.celery_result_expires,
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'worker_prefetch_multiplier': 1,
        'task_acks_late': True,
        'task_reject_on_worker_lost': True,
    }


# Scraping configuration
def get_scraping_config() -> dict:
    """Get scraping system configuration."""
    settings = get_settings()
    return {
        'flipp_api': {
            'rate_limit_delay': settings.flipp_rate_limit_delay,
            'timeout': settings.scraping_timeout,
            'enabled': settings.enable_flipp_api,
            'user_agent': settings.user_agent
        },
        'selenium': {
            'headless': settings.selenium_headless,
            'timeout': settings.scraping_timeout,
            'enabled': settings.enable_selenium_fallback,
            'user_agent': settings.user_agent
        },
        'pdf_ocr': {
            'enabled': settings.enable_pdf_fallback,
            'timeout': settings.scraping_timeout
        },
        'vision_ai': {
            'enabled': settings.enable_vision_fallback,
            'timeout': settings.scraping_timeout
        },
        'general': {
            'max_retries': settings.max_scraping_retries,
            'timeout': settings.scraping_timeout
        }
    }