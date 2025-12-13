"""
Check Rules package initialization.

Provides core functionality and exports for the Check Rules module.
"""


import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Module metadata
__version__: str = "1.0.0"
__author__: str = "Agentic Workflow"
__description__: str = "Core Check Rules functionality"

# Core exports
__all__: List[str] = [
    "__version__",
    "__author__",
    "__description__",
    "get_module_info",
    "validate_config",
    "create_instance"
]

def get_module_info() -> Dict[str, Union[str, List[str]]]:
    """
    Get comprehensive module information.

    Returns:
        Dictionary containing module metadata and capabilities
    """
    return {
        "name": "Check Rules",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "exports": __all__
    }

def validate_config(config: Dict[str, Union[str, int, bool]]) -> bool:
    """
    Validate module configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    required_keys = ["enabled", "mode"]
    return all(key in config for key in required_keys)

def create_instance(config: Optional[Dict[str,
    """Docstring."""
    Union[str,
    int,
    bool]]] = None) -> Dict[str,
    Union[str,
    int,
    bool]]:
    """
    Create a configured module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Instance configuration dictionary
    """
    default_config = {"enabled": True, "mode": "production"}
    final_config = {**default_config, **(config or {})}

    if not validate_config(final_config):
        raise ValueError("Invalid configuration provided")

    logger.info(f"Created Check Rules instance with config: {final_config}")
    return final_config
