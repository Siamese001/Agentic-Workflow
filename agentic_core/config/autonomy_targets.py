"""
Comprehensive exceptions config for autonomy metrics.

Defines expected targets per metric and territory pattern.
- "N/A": Metric is irrelevant (displayed as "—" or "N/A", colored neutral).
- Numeric: Specific target percentage (e.g., 80).
- Patterns: Regex matches against Territory strings (e.g., "L0_.*").
"""
import re
from typing import Dict, Any, Union, Optional

# Default targets for high-autonomy layers (L1-L5)
DEFAULT_TARGETS = {
    "heal_capability": 100,
    "invocation": 100,
    "mcp_hardened": 100,
    "tests": 95,
    "observability": 95,
    "complexity_max": 10,   # Lower is better
    "typing": 95,
    "documentation": 90,
}

TARGETS: Dict[str, Dict[str, Union[int, str]]] = {
    "default": DEFAULT_TARGETS,

    # --- L0 Maintenance (Passive/Bootstrapping) ---
    # MAX INVOCATION TARGET: All agents should aim for 100% invocation
    "L0_.*": {
        "heal_capability": 100,     # Max target
        "invocation": 100,          # MAX TARGET - all agents should invoke healing
        "observability": 100,       # Max target
        "mcp_hardened": 100,        # Max target
        "tests": 100,               # Max target
    },

    # --- Infrastructure (Utilities/Wrappers) ---
    # MAX INVOCATION TARGET: All agents should aim for 100% invocation
    ".*infrastructure": {
        "invocation": 100,          # MAX TARGET
        "tests": 100,               # Max target
        "mcp_hardened": 100,        # Max target
        "complexity_max": 20,       # Validation logic often requires nesting
    },

    # --- Base Classes (Abstract) ---
    # MAX INVOCATION TARGET: Even abstract classes should define heal patterns
    ".*base_class": {
        "invocation": 100,          # MAX TARGET
        "observability": 100,       # Max target
        "tests": 100,               # Max target
        "mcp_hardened": 100,        # Max target
    },

    # --- L5 Safety (High Criticality) ---
    # MAX INVOCATION TARGET
    "L5_.*": {
        "invocation": 100,          # MAX TARGET
        "complexity_max": 20,       # Validation logic often requires nesting
    },
}

def get_target(territory: str, metric: str, extra_context: Optional[Dict[str, Any]] = None) -> Union[int, str]:
    """
    Resolve target metric for a specific territory.

    Args:
        territory: The territory name (e.g., "L0 Maintenance/Infrastructure")
        metric: The metric key (e.g., "invocation", "mcp_hardened")
        extra_context: Optional dict (e.g., {"has_tools": False}) for dynamic decisions.
    """
    extra_context = extra_context or {}
    
    for pattern, overrides in TARGETS.items():
        if pattern == "default":
            continue
        # Normalize pattern for loose matching (underscore -> space optional)
        regex = pattern.replace('.*', '.*').replace('_', '[ _]')
        if re.search(regex, territory, re.IGNORECASE):
            val = overrides.get(metric)
            if val == "conditional_tools":
                return 100 if extra_context.get("has_tools") else "N/A"
            if val is not None:
                return val
                
    return DEFAULT_TARGETS.get(metric, 100)
