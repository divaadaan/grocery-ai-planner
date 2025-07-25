# backend/telemetry/__init__.py
"""
Telemetry package for conditional monitoring support.
Adapted for Grocery AI Planner.
"""

import os
from typing import Optional

try:
    from .interface import (
        TelemetryConfig,
        create_telemetry_provider,
        SpanStatus
    )
except ImportError:
    # Fallback minimal implementations if interface.py has issues
    class SpanStatus:
        OK = "ok"
        ERROR = "error"

    class TelemetryConfig:
        def __init__(self, enabled=False):
            self.enabled = enabled
            self.tracer = None
            self.llm_request_counter = None
            self.llm_response_time = None
            self.llm_token_counter = None
            self.agent_request_counter = None
            self.agent_response_time = None
            self.scraping_counter = None
            self.meal_plan_counter = None

    def create_telemetry_provider(enabled=False):
        return None


def is_telemetry_available() -> bool:
    """Check if OpenTelemetry dependencies are available."""
    try:
        import opentelemetry
        return True
    except ImportError:
        return False


def get_telemetry_config(
        enabled: Optional[bool] = None,
        console_export: Optional[bool] = None,
        metrics_port: Optional[int] = None
) -> TelemetryConfig:
    """Get telemetry configuration with environment variable support."""
    # Determine if telemetry should be enabled
    if enabled is None:
        enabled = os.getenv("TELEMETRY_ENABLED", "false").lower() == "true"

    # If OpenTelemetry isn't available, force disabled regardless of config
    if enabled and not is_telemetry_available():
        import logging
        logging.warning(
            "Telemetry requested but OpenTelemetry not available. "
            "Forcing telemetry disabled for lite build."
        )
        enabled = False

    return TelemetryConfig(enabled=enabled)


def get_telemetry_info() -> dict:
    """Get information about telemetry availability and configuration."""
    return {
        "enabled": os.getenv("TELEMETRY_ENABLED", "false").lower() == "true",
        "available": is_telemetry_available(),
        "config_source": "environment" if os.getenv("TELEMETRY_ENABLED") else "default"
    }


# Try to import advanced features
try:
    from .opentelemetry_provider import setup_telemetry
    quick_setup = setup_telemetry  # Alias for compatibility
except ImportError:
    setup_telemetry = None
    quick_setup = None

__all__ = [
    'TelemetryConfig',
    'get_telemetry_config',
    'is_telemetry_available',
    'SpanStatus',
    'get_telemetry_info'
]

if quick_setup:
    __all__.append('quick_setup')