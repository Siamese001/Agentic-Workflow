"""
L3 Orchestration package initialization for Outreach Engine.

Provides orchestration components including:
- L5+ Autonomous Outreach Orchestrator with Canon Validator patterns
- Campaign management with convergence loops
- Archetype-aware message generation

Updated: 2025-12-17 - Added L5+ autonomy components
"""

import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Module metadata
__version__: str = "2.0.0"
__author__: str = "Agentic Workflow"
__description__: str = "L5+ Autonomous Outreach Orchestration"

# L5+ Autonomous Orchestrator (Canon Validator parity)
from apps_lic.L3_orchestration.l5_autonomous_orchestrator import (
    L5OutreachOrchestrator,
    OutreachCycleState,
    OutreachExecutionPhase,
    OutreachSnapshot,
    create_l5_outreach_orchestrator,
)

# Core exports
__all__: List[str] = [
    # Module metadata
    "__version__",
    "__author__",
    "__description__",
    # L5+ Autonomous Orchestrator
    "L5OutreachOrchestrator",
    "create_l5_outreach_orchestrator",
    "OutreachExecutionPhase",
    "OutreachCycleState",
    "OutreachSnapshot",
    # Utility functions
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
        "name": "L3 Orchestration",
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

def create_instance(
    config: Optional[Dict[str, Union[str, int, bool]]] = None
) -> Dict[str, Union[str, int, bool]]:
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

    logger.info(f"Created L3 Orchestration instance with config: {final_config}")
    return final_config
