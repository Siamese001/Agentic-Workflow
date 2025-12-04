"""Configuration helpers for the v10.7 runtime."""

from __future__ import annotations

import logging
from typing import Dict

from mcp import get_schema

logger = logging.getLogger("core_v10_7")


class ConfigV10_7:
    """Configuration loader for v10.7"""
    
    def __init__(self, config_path: str = "master_config_v10_7.json"):
        self._config = get_schema(config_path)

        # Validate schema version
        expected_schema = "master_config_v10.7"
        loaded_schema = self._config.get("schema_version")
        if loaded_schema != expected_schema:
            raise ValueError(f"Config schema mismatch. Expected {expected_schema}, got {loaded_schema}")

        redis_cfg = self._config.setdefault("redis_config", {})
        redis_cfg.setdefault("required", True)
        redis_cfg.setdefault("persistent", False)

        logger.info(f"Loaded {loaded_schema} configuration")
    
    def __getattr__(self, name):
        """Dynamic attribute access for nested config"""
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        section = self._config.get(name)
        if section is None:
            snake_name = name.replace('-', '_')
            section = self._config.get(snake_name)
            if section is None:
                raise AttributeError(f"Config section '{name}' or '{snake_name}' not found")

        return ConfigSection(section)

class ConfigSection:
    """Wrapper for nested config sections"""

    def __init__(self, data: Dict):
        self._data = data

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        value = self._data.get(name)
        if value is None:
            snake_name = name.replace('-', '_')
            value = self._data.get(snake_name)
            if value is None:
                raise AttributeError(f"Config key '{name}' or '{snake_name}' not found")

        if isinstance(value, dict):
            return ConfigSection(value)
        return value

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        key = name if name in self._data else name.replace('-', '_')
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __contains__(self, key):
        return key in self._data


__all__ = ["ConfigV10_7", "ConfigSection"]

