"""
Shared layer gravity constants and validation.

SSOT for layer hierarchy and gravity rules.
Used by: StructuralValidatorAgent, GravityLeakRepairAgent, ArchitectureGovernorAgent

Extracted from:
- StructuralValidatorAgent.LAYER_ORDER, GRAVITY_RULES
- GravityLeakRepairAgent.LAYER_ORDER
- ArchitectureGovernorAgent (implicit usage)

All implementations were identical - this consolidates them.
"""

from __future__ import annotations

from pathlib import Path

# Layer hierarchy - lower index = higher authority (can be imported by higher layers)
# L0 is the "lowest" layer and can only import from itself
# L6 is the "highest" layer and can import from all lower layers
LAYER_ORDER: dict[str, int] = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
}

# Gravity rules: L(N) can only import from L(0..N)
# This prevents "upward imports" where lower layers depend on higher layers
GRAVITY_RULES: dict[str, set[str]] = {
    "L0": {"L0"},
    "L1": {"L0", "L1"},
    "L2": {"L0", "L1", "L2"},
    "L3": {"L0", "L1", "L2", "L3"},
    "L4": {"L0", "L1", "L2", "L3", "L4"},
    "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
    "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
}


def extract_layer_from_path(path: Path | str) -> str | None:
    """
    Extract layer identifier from file path.

    Args:
        path: File path (Path object or string)

    Returns:
        Layer identifier (e.g., "L5") or None if not in a layer

    Example:
        >>> extract_layer_from_path("agentic_core/L5_safety/validators/GovernanceAgent.py")
        'L5'
        >>> extract_layer_from_path("apps_rg/engines/tool.py")
        None
    """
    path_str = str(path)
    for layer in LAYER_ORDER.keys():
        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
            return layer
    return None


def extract_layer_from_module(module: str) -> str | None:
    """
    Extract layer identifier from module path.

    Args:
        module: Module path (e.g., "agentic_core.L3_orchestration.workflow_engines")

    Returns:
        Layer identifier (e.g., "L3") or None if not in a layer

    Example:
        >>> extract_layer_from_module("agentic_core.L3_orchestration.workflow_engines")
        'L3'
        >>> extract_layer_from_module("apps_shared.common_utils")
        None
    """
    for layer in LAYER_ORDER.keys():
        if f".{layer}_" in module or module.startswith(f"{layer}_") or f"_{layer}_" in module:
            return layer
    return None


def is_gravity_violation(source_layer: str, target_layer: str) -> bool:
    """
    Check if importing target_layer from source_layer violates gravity.

    Gravity violation occurs when a lower layer imports from a higher layer.

    Args:
        source_layer: Layer of the importing file (e.g., "L3")
        target_layer: Layer being imported (e.g., "L5")

    Returns:
        True if this is a gravity violation (upward import)

    Example:
        >>> is_gravity_violation("L3", "L5")  # L3 importing L5
        True
        >>> is_gravity_violation("L5", "L3")  # L5 importing L3
        False
        >>> is_gravity_violation("L3", "L3")  # Same layer
        False
    """
    allowed = GRAVITY_RULES.get(source_layer, set())
    return target_layer not in allowed


def get_allowed_layers(source_layer: str) -> set[str]:
    """
    Get the set of layers that a source layer is allowed to import from.

    Args:
        source_layer: Layer of the importing file

    Returns:
        Set of allowed layer identifiers

    Example:
        >>> get_allowed_layers("L3")
        {'L0', 'L1', 'L2', 'L3'}
    """
    return GRAVITY_RULES.get(source_layer, set())


def get_layer_order(layer: str) -> int:
    """
    Get the numeric order of a layer (lower = more foundational).

    Args:
        layer: Layer identifier (e.g., "L3")

    Returns:
        Numeric order (0-6) or -1 if not a valid layer

    Example:
        >>> get_layer_order("L3")
        3
        >>> get_layer_order("invalid")
        -1
    """
    return LAYER_ORDER.get(layer, -1)
