"""
Comprehensive exceptions config for autonomy metrics.

Defines expected targets per metric and territory pattern.
- "N/A": Metric is irrelevant (displayed as "—" or "N/A", colored neutral).
- Numeric: Specific target percentage (e.g., 80).
- Patterns: Regex matches against Territory strings (e.g., "L0_.*").
"""
import re
from typing import Dict, Any, Union, Optional

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Default targets for high-autonomy layers (L1-L5)
DEFAULT_TARGETS = {
    "heal_capability": 100,
    "invocation": 100,
    "mcp_hardened": 100,
    TESTS_DIR: 95,
    "observability": 95,
    "complexity_max": 10,   # Lower is better
    "typing": 95,
    "documentation": 90,
}

TARGETS: Dict[str, Dict[str, Union[int, str]]] = {
    "default": DEFAULT_TARGETS,

    # --- L0 Maintenance (Passive/Bootstrapping) ---
    # Low invocation is normal; they only run during startup or specific failures.
    "L0_.*": {
        "heal_capability": 60,      # Simple scripts may not need full healing
        "invocation": 20,           # Rare execution path
        "observability": 70,        # Minimal runtime events
        "mcp_hardened": "N/A",      # Often no external tools
        TESTS_DIR: 80,
    },

    # --- Infrastructure (Utilities/Wrappers) ---
    # Wrappers around DBs/APIs; heavy on complexity, light on autonomous decision making.
    ".*infrastructure": {
        "invocation": 70,
        TESTS_DIR: 85,
        "mcp_hardened": "conditional_tools", # Special flag handled in logic
        "complexity_max": 20,       # Validation logic often requires nesting
    },

    # --- Base Classes (Abstract) ---
    # Cannot run directly; invocation/observability N/A.
    # Matches any territory ending exactly with "Base Class" (case-insensitive).
    # Covers L1-L5 uniformly without hard-coding layers.
    "Base Class": {
        "invocation": "N/A",
        "observability": "N/A",
        TESTS_DIR: 70,                # Interface tests only
        "mcp_hardened": "N/A",
    },

    # --- L5 Safety (High Criticality) ---
    # Complexity allowed for rigorous validation chains.
    "L5_.*": {
        "complexity_max": 20,
    },
}

def get_target(territory: str, metric: str, extra_context: Optional[Dict[str, Any]] = None) -> Union[int, str]:
    """
    Resolve target metric for a specific territory.
    
    Patterns are checked in order of specificity:
    1. More specific patterns (e.g., ".*infrastructure") checked first
    2. Less specific patterns (e.g., "L0_.*") checked last
    3. First match wins, so order matters

    Args:
        territory: The territory name (e.g., "L0 Maintenance/Infrastructure")
        metric: The metric key (e.g., "invocation", "mcp_hardened")
        extra_context: Optional dict (e.g., {"has_tools": False}) for dynamic decisions.
    """
    extra_context = extra_context or {}
    
    # Check patterns in order of specificity (more specific first)
    # Infrastructure and Base Class are more specific than L0/L5 layer patterns
    pattern_order = [
        ".*infrastructure",
        "Base Class",
        "L5_.*",
        "L0_.*",
    ]
    
    for pattern in pattern_order:
        if pattern not in TARGETS:
            continue
        overrides = TARGETS[pattern]
        # Normalize pattern for loose matching (underscore -> space optional)
        if pattern == "Base Class":
            regex = r"Base Class$"
        else:
            regex = pattern.replace('.*', '.*').replace('_', '[ _]')
        if re.search(regex, territory, re.IGNORECASE):
            val = overrides.get(metric)
            if val == "conditional_tools":
                return 100 if extra_context.get("has_tools") else "N/A"
            if val is not None:
                return val
                
    return DEFAULT_TARGETS.get(metric, 100)
