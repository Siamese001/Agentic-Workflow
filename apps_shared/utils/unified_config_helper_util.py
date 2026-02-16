"""
Unified Configuration Helper - Phase 1.2

Provides configuration loading and validation for UnifiedAgent instances.
Integrates with the existing config_loader system while adding:
- Schema validation for agent categories
- Default configuration merging
- Configuration migration utilities
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from apps_shared.config.config_loader_config import (
    ConfigLoadResult,
    get_config_loader,
    load_agent_config,
)

logger = logging.getLogger(__name__)

# Default configurations for each agent category
CATEGORY_DEFAULTS: dict[str, dict[str, Any]] = {
    "validator": {
        "validation_rules": {},
        "forbidden_content": [],
        "required_content": [],
        "thresholds": {"min_score": 0.3, "max_issues": 10},
        "patterns": {},
        "stop_words": ["the", "and", "for", "with", "that", "this"],
    },
    "orchestrator": {
        "workflow_steps": [],
        "signal_handlers": {},
        "retry_config": {
            "max_retries": 3,
            "retry_delay_seconds": 1,
            "exponential_backoff": True,
        },
        "timeout_config": {"step_timeout_seconds": 30, "total_timeout_seconds": 300},
    },
    "healer": {
        "healing_rules": {},
        "auto_fix": False,
        "dry_run_default": True,
        "backup_before_fix": True,
    },
    "generic": {
        "execution_mode": "standard",
        "logging_level": "INFO",
    },
    "executor": {
        "execution_timeout": 60,
        "retry_on_failure": True,
        "max_retries": 3,
    },
    "monitor": {
        "monitoring_interval": 60,
        "alert_thresholds": {},
        "metrics_to_track": [],
    },
    "analyzer": {
        "validation_rules": {},
        "forbidden_content": [],
        "required_content": [],
        "thresholds": {"min_score": 0.3, "max_issues": 10},
        "analysis_depth": "standard",
        "output_format": "json",
    },
    "governor": {
        "validation_rules": {},
        "forbidden_content": [],
        "required_content": [],
        "thresholds": {"min_score": 0.3, "max_issues": 10},
        "governance_rules": {},
        "enforcement_mode": "warn",
    },
}


def get_category_defaults(category: str) -> dict[str, Any]:
    """
    Get default configuration for a specific agent category.

    Args:
        category: Agent category name (e.g., "validator", "orchestrator")

    Returns:
        Default configuration dictionary for the category
    """
    return CATEGORY_DEFAULTS.get(category.lower(), {}).copy()


def merge_with_defaults(config: dict[str, Any], category: str) -> dict[str, Any]:
    """
    Merge provided configuration with category defaults.

    Args:
        config: User-provided configuration
        category: Agent category name

    Returns:
        Merged configuration with defaults filled in
    """
    defaults = get_category_defaults(category)
    return deep_merge(defaults, config)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries, with override taking precedence.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_unified_config(
    agent_name: str,
    category: str,
    config_file: str | None = None,
) -> dict[str, Any]:
    """
    Load configuration for a UnifiedAgent instance.

    Loads configuration from file and merges with category defaults.

    Args:
        agent_name: Name of the agent (e.g., "ats_compatibility")
        category: Agent category (e.g., "validator")
        config_file: Optional specific config file

    Returns:
        Merged configuration dictionary
    """
    # Get category defaults
    defaults = get_category_defaults(category)

    try:
        # Try to load from file
        config = load_agent_config(agent_name, config_file, fallback_config=defaults)
        # Merge with defaults to ensure all required fields exist
        return merge_with_defaults(config, category)
    except RuntimeError:
        # If file not found, use defaults
        logger.debug(f"No config file for {agent_name}, using {category} defaults")
        return defaults


def validate_unified_config(config: dict[str, Any], category: str) -> ConfigLoadResult:
    """
    Validate configuration against category schema.

    Args:
        config: Configuration to validate
        category: Agent category

    Returns:
        ConfigLoadResult with validation status
    """
    errors = []
    defaults = get_category_defaults(category)

    # Check for required fields based on category
    required_fields = _get_required_fields(category)
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Validate field types
    for key, value in config.items():
        if key in defaults:
            expected_type = type(defaults[key])
            if not isinstance(value, expected_type):
                errors.append(
                    f"Field {key} should be {expected_type.__name__}, got {type(value).__name__}",
                )

    return ConfigLoadResult(
        success=len(errors) == 0,
        config=config,
        errors=errors,
        source="validation",
    )


def _get_required_fields(category: str) -> list[str]:
    """Get required fields for a category."""
    required_map = {
        "validator": ["validation_rules"],
        "orchestrator": ["workflow_steps"],
        "healer": [],
        "generic": [],
        "executor": [],
        "monitor": [],
        "analyzer": ["validation_rules"],
        "governor": ["validation_rules"],
    }
    return required_map.get(category.lower(), [])


class UnifiedConfigLoader:
    """
    Configuration loader specifically for UnifiedAgent instances.

    Wraps the standard ConfigLoader with category-aware defaults
    and validation.
    """

    def __init__(self, config_root: Path | None = None):
        """Initialize unified config loader."""
        self._loader = get_config_loader(config_root)
        self._cache: dict[str, dict[str, Any]] = {}

    def load(
        self,
        agent_name: str,
        category: str,
        config_file: str | None = None,
        force_reload: bool = False,
    ) -> dict[str, Any]:
        """
        Load configuration for an agent.

        Args:
            agent_name: Name of the agent
            category: Agent category
            config_file: Optional specific config file
            force_reload: Force reload from disk

        Returns:
            Configuration dictionary
        """
        cache_key = f"{agent_name}:{category}"

        if not force_reload and cache_key in self._cache:
            return self._cache[cache_key]

        config = load_unified_config(agent_name, category, config_file)
        self._cache[cache_key] = config

        return config

    def validate(self, agent_name: str, category: str) -> ConfigLoadResult:
        """
        Validate configuration for an agent.

        Args:
            agent_name: Name of the agent
            category: Agent category

        Returns:
            ConfigLoadResult with validation status
        """
        config = self.load(agent_name, category)
        return validate_unified_config(config, category)

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()


# Global unified config loader instance
_unified_loader: UnifiedConfigLoader | None = None


def get_unified_config_loader(
    config_root: Path | None = None,
) -> UnifiedConfigLoader:
    """Get global unified config loader instance."""
    global _unified_loader
    if _unified_loader is None:
        _unified_loader = UnifiedConfigLoader(config_root)
    return _unified_loader


__all__ = [
    "CATEGORY_DEFAULTS",
    "get_category_defaults",
    "merge_with_defaults",
    "deep_merge",
    "load_unified_config",
    "validate_unified_config",
    "UnifiedConfigLoader",
    "get_unified_config_loader",
]
