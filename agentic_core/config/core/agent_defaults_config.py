"""
Agent Default Configuration

Phase 2 Landmine Remediation - Magic Configuration Extraction
This module externalizes hardcoded constants and thresholds,
enabling runtime tuning without code changes.

Usage:
    from agentic_core.config.agent_defaults import AgentDefaults

    threshold = AgentDefaults.get("PINECONE_RELEVANCE_THRESHOLD", 0.75)
"""

import os
from typing import Any


class AgentDefaults:
    """
    Centralized configuration for agent default values.

    Values can be overridden via environment variables with the same name.
    All values have sensible defaults that match previous hardcoded behavior.
    """

    # === Vector Search Thresholds ===
    RAG_SIMILARITY_THRESHOLD: float = 0.8
    SEMANTIC_CACHE_THRESHOLD: float = 0.92

    # === Timeout Configuration (seconds) ===
    DEFAULT_API_TIMEOUT: float = 60.0
    TOOL_EXECUTION_TIMEOUT: int = 30
    HEAL_OPERATION_TIMEOUT: int = 120
    SUBPROCESS_TIMEOUT: int = 300

    # === Rate Limiting ===
    DEFAULT_RATE_LIMIT_REQUESTS: int = 100
    DEFAULT_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # === Healing Thresholds ===
    CONFIDENCE_THRESHOLD: float = 0.75
    AUTO_EXECUTE_THRESHOLD: float = 0.75
    SAFETY_THRESHOLD: float = 0.95

    # === Model Configuration ===
    DEFAULT_MODEL: str = "gpt-4"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"

    # === Circuit Breaker ===
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60

    # === Performance Thresholds ===
    PERFORMANCE_DEGRADATION_THRESHOLD: float = 0.5
    COMPLEXITY_THRESHOLD: int = 15
    MAX_CONCURRENT_OPERATIONS: int = 5

    # === Cost Management ===
    DEFAULT_BUDGET_LIMIT: float = 5.0
    BUDGET_WARNING_THRESHOLD: float = 0.8

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with environment variable override.

        Args:
            key: Configuration key (must be a class attribute)
            default: Default value if not found (uses class default if None)

        Returns:
            Configuration value (env var override takes precedence)
        """
        # Check environment variable first
        env_value = os.environ.get(key)
        if env_value is not None:
            # Try to convert to the expected type
            class_default = getattr(cls, key, default)
            if class_default is not None:
                try:
                    if isinstance(class_default, bool):
                        return env_value.lower() in ("1", "true", "yes")
                    elif isinstance(class_default, int):
                        return int(env_value)
                    elif isinstance(class_default, float):
                        return float(env_value)
                    else:
                        return env_value
                except (ValueError, TypeError):
                    pass
            return env_value

        # Fall back to class default
        return getattr(cls, key, default)

    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        value = cls.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        value = cls.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = cls.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes")
        return bool(value)


# Convenience exports
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value with environment variable override."""
    return AgentDefaults.get(key, default)


__all__ = [
    "AgentDefaults",
    "get_config",
]
