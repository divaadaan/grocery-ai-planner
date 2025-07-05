"""
Application configuration using Docker secrets and environment variables.
Secrets for sensitive data, environment variables for non-sensitive config.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import BaseSettings, Field
from .secrets import SecretsManager


class Settings(BaseSettings):
    """Application settings with Docker secrets for sensitive data."""

    # Application (non-sensitive)
    app_name: str = "Grocery AI Planner"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # LLM Configuration (non-sensitive model name)
    default_model: str = Field(default="qwen2.5-coder:14b", env="DEFAULT_MODEL")

    # Telemetry (non-sensitive)
    telemetry_enabled: bool = Field(default=True, env="TELEMETRY_ENABLED")
    telemetry_metrics_port: int = Field(default=8001, env="TELEMETRY_METRICS_PORT")
    telemetry_console_export: bool = Field(default=False, env="TELEMETRY_CONSOLE_EXPORT")

    # Email Configuration (non-sensitive settings)
    mail_from: Optional[str] = Field(default=None, env="MAIL_FROM")
    mail_port: int = Field(default=587, env="MAIL_PORT")
    mail_server: Optional[str] = Field(default=None, env="MAIL_SERVER")
    mail_starttls: bool = Field(default=True, env="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(default=False, env="MAIL_SSL_TLS")

    # Scraping Configuration (non-sensitive)
    max_scrape_workers: int = Field(default=3, env="MAX_SCRAPE_WORKERS")
    scrape_delay_min: int = Field(default=1, env="SCRAPE_DELAY_MIN")
    scrape_delay_max: int = Field(default=3, env="SCRAPE_DELAY_MAX")
    user_agent: str = Field(default="GroceryAI-Bot/1.0", env="USER_AGENT")

    # New Scraping System Configuration (non-sensitive)
    flipp_rate_limit_delay: float = Field(default=0.5, env="FLIPP_RATE_LIMIT_DELAY")
    scraping_timeout: int = Field(default=30, env="SCRAPING_TIMEOUT")
    selenium_headless: bool = Field(default=True, env="SELENIUM_HEADLESS")
    max_scraping_retries: int = Field(default=3, env="MAX_SCRAPING_RETRIES")
    enable_flipp_api: bool = Field(default=True, env="ENABLE_FLIPP_API")
    enable_selenium_fallback: bool = Field(default=True, env="ENABLE_SELENIUM_FALLBACK")
    enable_pdf_fallback: bool = Field(default=False, env="ENABLE_PDF_FALLBACK")
    enable_vision_fallback: bool = Field(default=False, env="ENABLE_VISION_FALLBACK")

    # Job Configuration (non-sensitive)
    celery_result_expires: int = Field(default=3600, env="CELERY_RESULT_EXPIRES")
    max_retries: int = Field(default=3, env="MAX_RETRIES")

    # CORS (non-sensitive)
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )

    # Sensitive data from Docker secrets
    @property
    def database_url(self) -> str:
        """Get database URL from Docker secret."""
        return SecretsManager.get_secret("database_url")

    @property
    def redis_url(self) -> str:
        """Get Redis URL from Docker secret."""
        return SecretsManager.get_secret("redis_url")

    @property
    def secret_key(self) -> str:
        """Get application secret key from Docker secret."""
        return SecretsManager.get_secret("secret_key")

    @property
    def llm_api_url(self) -> str:
        """Get LLM API URL from Docker secret."""
        return SecretsManager.get_secret("llm_api_url")

    @property
    def google_maps_api_key(self) -> Optional[str]:
        """Get Google Maps API key from Docker secret."""
        return SecretsManager.get_optional_secret("google_maps_api_key")

    @property
    def mail_password(self) -> Optional[str]:
        """Get mail password from Docker secret."""
        return SecretsManager.get_optional_secret("mail_password")

    @property
    def mail_username(self) -> Optional[str]:
        """Get mail username from Docker secret."""
        return SecretsManager.get_optional_secret("mail_username")

    class Config:
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Helper functions remain the same but use properties
def get_database_url() -> str:
    """Get database URL."""
    return get_settings().database_url


def get_redis_url() -> str:
    """Get Redis URL."""
    return get_settings().redis_url


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