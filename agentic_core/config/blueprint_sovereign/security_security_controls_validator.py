from __future__ import annotations

"""
Security Controls package initialization.

Provides core functionality and exports for the Security Controls module.
"""
import logging
from typing import Any

Logger: Any = logging.getLogger(__name__)
__version__: str = "1.0.0"
__author__: str = "Agentic Workflow"
__description__: str = "Core Security Controls functionality"
__all__: list[str] = [
    "__version__",
    "__author__",
    "__description__",
    "get_module_info",
    "validate_config",
    "create_instance",
]


def get_module_info() -> dict[str, str | list[str]]:
    """
    Get comprehensive module information.

    Returns:
        Dictionary containing module metadata and capabilities
    """
    return {
        "name": "Security Controls",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "exports": __all__,
    }


def validate_config(config: dict[str, str | int | bool]) -> bool:
    """
    Validate module configuration.

    Args:
        config: configuration dictionary to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    required_keys: Any = ["enabled", "mode"]
    return all(key in config for key in required_keys)


def create_instance(
    config: dict[str, str | int | bool] | None = None,
) -> dict[str, str | int | bool]:
    """
    Create a configured module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Instance configuration dictionary
    """
    default_config: Any = {"enabled": True, "mode": "production"}
    final_config: Any = {**default_config, **(config or {})}
    if not validate_config(final_config):
        raise ValueError("Invalid configuration provided")
    LOGGER.info(f"Created Security Controls instance with config: {final_config}")
    return final_config
