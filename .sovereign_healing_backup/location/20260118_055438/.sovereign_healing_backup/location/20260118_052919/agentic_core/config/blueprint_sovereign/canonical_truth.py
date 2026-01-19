"""
CANONICAL TRUTH: Sovereign Single Source of Truth
==================================================

This module is the BEDROCK FOUNDATION for all derived logic in the codebase.

CRITICAL CONSTRAINTS:
- ZERO internal project imports (no agentic_core.* imports)
- Only stdlib imports allowed (pathlib, re, typing)
- Can be imported from anywhere without circular dependencies
- All functions are pure and deterministic

PURPOSE:
Resolves SSOT violations by providing canonical implementations for:
1. Health score calculation (Violation 4)
2. Layer inference from paths (Violation 2)
3. Future: Agent categorization, territory mapping, etc.

USAGE:
    from agentic_core.L5_safety.validators.canonical_truth_1 import (
        calculate_health_score,
        get_canonical_layer
    )
"""

import re
from pathlib import Path
from typing import Dict, Union, Optional


# ============================================================================
# HEALTH SCORE CALCULATION (SSOT for Violation 4)
# ============================================================================

# Weighted formula for health score calculation
# Total must sum to 1.0 (100%)
HEALTH_WEIGHTS: Dict[str, float] = {
    "heal_capability": 0.30,   # 30% - Ability to self-heal
    "invocation": 0.10,        # 10% - Invocation status
    "test_coverage": 0.25,     # 25% - Test coverage
    "observability": 0.20,     # 20% - Observability metrics
    "complexity": 0.15         # 15% - Complexity health
}

# Validation: Ensure weights sum to 1.0
assert abs(sum(HEALTH_WEIGHTS.values()) - 1.0) < 0.0001, "Health weights must sum to 1.0"


def calculate_health_score(
    heal_cap: float,
    invoc: float,
    test_cov: float,
    obs: float,
    comp_health: float
) -> float:
    """
    Sovereign SSOT for health score calculation.
    
    This is the ONLY place where health scores should be calculated.
    All consumers (dashboard, tests, validators) MUST use this function.
    
    Args:
        heal_cap: Heal capability percentage (0.0 to 100.0)
        invoc: Invocation percentage (0.0 to 100.0)
        test_cov: Test coverage percentage (0.0 to 100.0)
        obs: Observability percentage (0.0 to 100.0)
        comp_health: Complexity health percentage (0.0 to 100.0)
    
    Returns:
        Weighted health score rounded to 4 decimal places for precision
    
    Formula:
        health = (heal_cap * 0.30) + (invoc * 0.10) + (test_cov * 0.25) +
                 (obs * 0.20) + (comp_health * 0.15)
    
    Example:
        >>> calculate_health_score(100.0, 100.0, 100.0, 100.0, 100.0)
        100.0
        >>> calculate_health_score(90.0, 80.0, 70.0, 85.0, 60.0)
        79.75
    """
    # Validate inputs are in valid range
    for name, value in [
        ("heal_cap", heal_cap),
        ("invoc", invoc),
        ("test_cov", test_cov),
        ("obs", obs),
        ("comp_health", comp_health)
    ]:
        if not (0.0 <= value <= 100.0):
            raise ValueError(f"{name} must be between 0.0 and 100.0, got {value}")
    
    # Calculate weighted sum
    raw_score = (
        heal_cap * HEALTH_WEIGHTS["heal_capability"] +
        invoc * HEALTH_WEIGHTS["invocation"] +
        test_cov * HEALTH_WEIGHTS["test_coverage"] +
        obs * HEALTH_WEIGHTS["observability"] +
        comp_health * HEALTH_WEIGHTS["complexity"]
    )
    
    # Round to 4 decimal places to prevent floating point mismatches
    return round(raw_score, 4)


# ============================================================================
# LAYER INFERENCE (SSOT for Violation 2)
# ============================================================================

# Layer markers in paths (priority order)
LAYER_MARKERS: Dict[str, str] = {
    "L0_maintenance": "L0",
    "L1_cognition": "L1",
    "L2_execution": "L2",
    "L3_orchestration": "L3",
    "L4_state": "L4",
    "L5_safety": "L5",
    "L6_observability": "L6",
    "apps_rg": "Apps",
    "apps_lic": "Apps",
    "apps_shared": "Apps",
    "utils": "utils",
    "tests": "tests"
}


def get_canonical_layer(file_path: Union[str, Path]) -> str:
    """
    Sovereign SSOT for layer inference from file paths.
    
    This is the ONLY place where layer inference should be performed.
    All consumers (discovery, validators, categorizers) MUST use this function.
    
    Args:
        file_path: Absolute or relative file path (str or Path object)
    
    Returns:
        Layer identifier: 'L0', 'L1', ..., 'L6', 'Apps', 'utils', 'tests', or 'Unknown'
    
    Algorithm:
        1. Normalize path separators (Windows/Linux compatibility)
        2. Check for direct layer markers in path (L0_maintenance, L1_cognition, etc.)
        3. Fallback: Pattern-based detection (e.g., /L5/ in path)
        4. Return 'Unknown' if no match found
    
    Example:
        >>> get_canonical_layer("agentic_core/L5_safety/validators/LocationAgent.py")
        'L5'
        >>> get_canonical_layer("apps_rg/engines/engine.py")
        'Apps'
        >>> get_canonical_layer("C:\\Git\\Agentic-Workflow\\agentic_core\\L3_orchestration\\workflow_engines\\agent.py")
        'L3'
    """
    # Normalize path to forward slashes for cross-platform consistency
    path_str = str(file_path).replace("\\", "/")
    path_lower = path_str.lower()
    
    # Priority 1: Direct layer markers
    for marker, layer in LAYER_MARKERS.items():
        if marker.lower() in path_lower:
            return layer
    
    # Priority 2: Pattern-based detection (e.g., /L5/ or /L5_)
    # Split path and look for L[0-6] patterns
    parts = path_str.split('/')
    for part in parts:
        # Check if part starts with L followed by a digit
        if len(part) >= 2 and part[0] in ('L', 'l') and part[1].isdigit():
            digit = part[1]
            if digit in '0123456':
                return f"L{digit}"
    
    # No match found
    return "Unknown"


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_health_components(
    heal_cap: float,
    invoc: float,
    test_cov: float,
    obs: float,
    comp_health: float
) -> bool:
    """
    Validate that all health components are in valid range [0.0, 100.0].
    
    Args:
        heal_cap: Heal capability percentage
        invoc: Invocation percentage
        test_cov: Test coverage percentage
        obs: Observability percentage
        comp_health: Complexity health percentage
    
    Returns:
        True if all components are valid, False otherwise
    """
    components = [heal_cap, invoc, test_cov, obs, comp_health]
    return all(0.0 <= c <= 100.0 for c in components)


def get_health_weights() -> Dict[str, float]:
    """
    Get the canonical health weights dictionary.
    
    Returns:
        Dictionary mapping component names to their weights
    """
    return HEALTH_WEIGHTS.copy()


# ============================================================================
# AGENT CATEGORIZATION (SSOT for Violation 3)
# ============================================================================

# Category patterns for agent classification
# Priority order matters - first match wins
AGENT_CATEGORY_PATTERNS: Dict[str, list] = {
    "Validator": [r"Validator", r"Validation", r"Enforcer", r"Compliance", r"Check", r"Verify", r"Audit"],
    "Healer": [r"Healer", r"Healing", r"Recovery", r"Repair", r"Fix", r"Reconcile", r"Restore"],
    "Guardian": [r"Guardian", r"Guard", r"Safety", r"Security", r"Protect", r"Defense", r"Sentinel"],
    "Orchestrator": [r"Orchestrator", r"Orchestration", r"Workflow", r"Engine", r"Coordinator", r"Router", r"Conductor", r"Exerciser", r"System"],
    "Analyzer": [r"Analyzer", r"Analysis", r"Detector", r"Detection", r"Hunter", r"Finder"],
    "Governor": [r"Governor", r"Governance", r"Architect", r"Architecture", r"Hierarchy", r"Location", r"Territory"],
    "Monitor": [r"Monitor", r"Monitoring", r"Metric", r"Telemetry", r"Trace", r"Logger", r"Report"],
    "Cognition": [r"Thinker", r"Reasoning", r"Brain", r"Cognitive", r"Thought", r"Intent", r"Planning"],
    "Executor": [r"Executor", r"Execution", r"Tool", r"Action", r"Handler"],
    "State": [r"State", r"Memory", r"Cache", r"Store", r"Ledger", r"Context"],
}


def categorize_agent(
    class_name: str,
    base_classes: Optional[list] = None,
    docstring: Optional[str] = None
) -> str:
    """
    Sovereign SSOT for agent categorization.
    
    This is the ONLY place where agent categorization should be performed.
    All consumers (discovery, dashboard, validators) MUST use this function.
    
    Args:
        class_name: Name of the agent class (e.g., "BaseClassEnforcerAgent")
        base_classes: List of base class names (e.g., ["L5Agent", "MCPHardenedMixin"])
        docstring: Optional docstring for additional context
    
    Returns:
        Category name: 'Validator', 'Healer', 'Guardian', 'Orchestrator', etc.
        Returns 'GenericAgent' if no pattern matches.
    
    Algorithm:
        1. Combine class_name + base_classes + docstring into search string
        2. Check patterns in priority order (first match wins)
        3. Return category or 'GenericAgent' as fallback
    
    Example:
        >>> categorize_agent("BaseClassEnforcerAgent")
        'Validator'
        >>> categorize_agent("TerritoryHealerAgent")
        'Healer'
        >>> categorize_agent("WorkflowEngine", ["L3OrchestrationBaseAgent"])
        'Orchestrator'
    """
    # Build comprehensive search string
    base_classes = base_classes or []
    docstring = docstring or ""
    
    search_string = class_name + " " + " ".join(base_classes) + " " + docstring
    
    # Check patterns in priority order
    for category, patterns in AGENT_CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, search_string, re.IGNORECASE):
                return category
    
    # Fallback for uncategorized agents
    return "GenericAgent"


def get_agent_categories() -> list:
    """
    Get list of all canonical agent categories.
    
    Returns:
        List of category names in priority order
    """
    return list(AGENT_CATEGORY_PATTERNS.keys()) + ["GenericAgent"]


# ============================================================================
# MODULE METADATA
# ============================================================================

__all__ = [
    "calculate_health_score",
    "get_canonical_layer",
    "validate_health_components",
    "get_health_weights",
    "categorize_agent",
    "get_agent_categories",
    "HEALTH_WEIGHTS",
    "LAYER_MARKERS",
    "AGENT_CATEGORY_PATTERNS"
]

__version__ = "1.1.0"
__author__ = "Agentic Workflow Team"
__doc_status__ = "SSOT - Do not duplicate logic from this module"
