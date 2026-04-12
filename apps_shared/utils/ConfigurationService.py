"""Configuration Service - Stub implementation for test compatibility."""

from typing import Any


class ConfigurationService:
    """Stub configuration service."""

    def __init__(self):
        self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value


__all__ = ["ConfigurationService"]
