"""
Territories Loader Module — YAML-based territory construction.

This module provides the implementation for building territory definitions
from YAML files (territories.yaml, layers.yaml, ast_signals.yaml).

Replaces the deprecated build_sovereign_territories() function from _constants.py.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
    load_ast_signals,
    load_territories,
)


def build_territories_from_yaml() -> dict[str, dict]:
    """Build complete territory definitions from YAML files.

    This function:
    1. Loads base territories from territories.yaml
    2. Merges AST signals from ast_signals.yaml
    3. Returns complete territory definitions

    Returns:
        Dictionary mapping territory names to their complete definitions.
    """
    # Load base territories from YAML
    base_territories = load_territories()
    territories = base_territories.get("territories", {})

    # Load AST signals
    ast_signals_data = load_ast_signals()
    ast_signals = ast_signals_data["ast_signals"]

    # Apply AST signals to agentic_core territory
    if "agentic_core" in territories:
        territories["agentic_core"]["ast_signals"] = ast_signals

    return territories


def get_all_territories_yaml() -> dict[str, dict]:
    """Get all territory definitions.

    Returns:
        Dictionary mapping territory_name -> territory definition.
    """
    return build_territories_from_yaml()


def get_territory_yaml(name: str) -> dict | None:
    """Get a specific territory by name.

    Args:
        name: Territory name (e.g., "agentic_core", "docs", "apps_shared")

    Returns:
        Territory definition dict, or None if not found.
    """
    territories = build_territories_from_yaml()
    return territories.get(name)


__all__ = [
    "build_territories_from_yaml",
    "get_all_territories_yaml",
    "get_territory_yaml",
]
