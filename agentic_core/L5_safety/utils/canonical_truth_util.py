"""
CANONICAL TRUTH: Sovereign Single Source of Truth Utilities
=========================================================

This module provides pure utility functions for SSOT calculations.

CRITICAL CONSTRAINTS:
- ZERO internal project imports (no agentic_core.* imports)
- Only stdlib imports allowed (pathlib, re, typing)
- Can be imported from anywhere without circular dependencies
- All functions are pure and deterministic

PURPOSE:
Resolves SSOT violations by providing canonical implementations for:
1. Health score calculation (Violation 4)
2. Layer inference from paths (Violation 2)
3. Agent categorization, territory mapping, etc.

USAGE:
    from agentic_core.utils.canonical_truth_validator import (
        calculate_health_score,
        get_canonical_layer
    )
"""

import re
from pathlib import Path
from typing import Any

# ============================================================================
# HEALTH SCORE CALCULATION (SSOT for Violation 4)
# ============================================================================


def calculate_health_score(
    violations: list[dict[str, Any]],
    weights: dict[str, float] | None = None,
) -> float:
    """
    Calculate a normalized health score (0-100) from violation data.

    Args:
        violations: List of violation dictionaries with 'severity' and 'count' keys
        weights: Optional weights for different severity levels

    Returns:
        Health score from 0 (worst) to 100 (best)
    """
    if not violations:
        return 100.0

    # Default weights if not provided
    default_weights = {"critical": 10.0, "high": 5.0, "medium": 2.0, "low": 1.0}
    weights = weights or default_weights

    total_penalty = 0.0
    max_possible_penalty = 0.0

    for violation in violations:
        severity = violation.get("severity", "medium").lower()
        count = violation.get("count", 1)

        penalty = weights.get(severity, 2.0) * count
        total_penalty += penalty

        # Assume max possible is all violations being critical
        max_possible_penalty += default_weights["critical"] * count

    if max_possible_penalty == 0:
        return 100.0

    # Convert penalty to health score (inverse relationship)
    health_score = max(0, 100 - (total_penalty / max_possible_penalty * 100))
    return round(health_score, 2)


# ============================================================================
# LAYER INFERENCE (SSOT for Violation 2)
# ============================================================================


def get_canonical_layer(file_path: str | Path) -> str:
    """
    Infer the canonical layer from a file path.

    Args:
        file_path: Path to the file

    Returns:
        Canonical layer string (L0-L6, Apps, Utils, Tests, or 'unknown')
    """
    path_str = str(file_path)

    # Direct layer mappings
    layer_patterns = {
        r"/L0_maintenance/": "L0",
        r"/L1_cognition/": "L1",
        r"/L2_execution/": "L2",
        r"/L3_orchestration/": "L3",
        r"/L4_state/": "L4",
        r"/L5_safety/": "L5",
        r"/L6_observability/": "L6",
        r"/apps_": "Apps",
        r"/apps_shared/": "Apps",
        r"/agentic_core/utils/": "Utils",
        r"/tests/": "Tests",
        r"/test_": "Tests",
    }

    for pattern, layer in layer_patterns.items():
        if re.search(pattern, path_str):
            return layer

    return "unknown"


# ============================================================================
# HEALTH COMPONENTS VALIDATION
# ============================================================================


def validate_health_components(components: dict[str, Any]) -> dict[str, Any]:
    """
    Validate health components and return validation results.

    Args:
        components: Dictionary of health components to validate

    Returns:
        Validation results with valid/invalid components
    """
    results = {"valid": [], "invalid": [], "missing_required": [], "overall_valid": True}

    required_components = ["violations", "weights", "thresholds"]

    # Check required components
    for component in required_components:
        if component not in components:
            results["missing_required"].append(component)
            results["overall_valid"] = False

    # Validate violations structure
    if "violations" in components:
        violations = components["violations"]
        if isinstance(violations, list):
            results["valid"].append("violations")
        else:
            results["invalid"].append("violations")
            results["overall_valid"] = False

    # Validate weights structure
    if "weights" in components:
        weights = components["weights"]
        if isinstance(weights, dict) and all(
            isinstance(k, str) and isinstance(v, int | float) for k, v in weights.items()
        ):
            results["valid"].append("weights")
        else:
            results["invalid"].append("weights")
            results["overall_valid"] = False

    return results


def get_health_weights() -> dict[str, float]:
    """
    Get default health calculation weights.

    Returns:
        Dictionary of weights for different violation severities
    """
    return {"critical": 10.0, "high": 5.0, "medium": 2.0, "low": 1.0, "info": 0.5}


# ============================================================================
# AGENT CATEGORIZATION
# ============================================================================


def categorize_agent(class_name: str, base_classes: list | None = None, docstring: str | None = None) -> str:
    """
    Categorize an agent based on its name, inheritance, and documentation.

    Args:
        class_name: Name of the agent class (e.g., "BaseClassEnforcerAgent")
        base_classes: List of base class names (e.g., ["L5Agent", "MCPHardenedMixin"])
        docstring: Optional docstring content

    Returns:
        Agent category string
    """
    base_classes = base_classes or []

    # Combine class_name + base_classes + docstring into search string
    search_string = class_name + " " + " ".join(base_classes) + " " + (docstring or "")

    # Category patterns
    categories = {
        "Validator": r"validator|check|enforce|validate|audit",
        "Orchestrator": r"orchestrat|workflow|coordination|meta",
        "Guardrail": r"guardrail|safety|security|protect",
        "Memory": r"memory|storage|cache|persist",
        "L1": r"cognition|thought|intent|analysis",
        "L2": r"execution|tool|action|mcp",
        "L3": r"orchestrat|workflow|coordination|meta",
        "L4": r"state|validation|ledger|memory",
        "L5": r"safety|guardrail|validator|audit",
        "L6": r"observability|logging|telemetry|metrics",
        "GenericAgent": r"agent|base|sovereign",
    }

    # Check patterns in order of specificity
    for category, pattern in categories.items():
        if re.search(pattern, search_string, re.IGNORECASE):
            return category

    return "Unknown"


def get_agent_categories() -> list[str]:
    """
    Get list of all valid agent categories.

    Returns:
        List of category strings
    """
    return [
        "Validator",
        "Orchestrator",
        "Guardrail",
        "Memory",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "GenericAgent",
        "Unknown",
    ]
