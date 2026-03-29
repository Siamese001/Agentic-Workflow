"""Services module for shared system services."""
from __future__ import annotations

import logging
from typing import Any


class ConfigurationService:
    """Service for managing system configuration."""
    
    _instance: ConfigurationService | None = None
    _config: dict[str, Any] = {}
    
    def __new__(cls) -> ConfigurationService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.Logger = logging.getLogger(__name__)
        self.data: Any = None
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value


__all__ = ["ConfigurationService"]
