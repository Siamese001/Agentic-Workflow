#!/usr/bin/env python3
"""
SSOT: Territory Name Definitions
=================================

Single Source of Truth for all territory names used in agent discovery and dashboard.

CRITICAL: All territory names MUST be defined here and used consistently across:
- full_agent_discovery.py (agent categorization)
- regenerate_dashboard_data.py (dashboard generation)
- All test files (validation)

DO NOT hardcode territory names anywhere else.
"""

# ============================================================================
# CANONICAL TERRITORY NAMES
# ============================================================================

# Base/Root Territory
TERRITORY_SOVEREIGN_BASE = "Sovereign Base Agent"

# Layer Base Agent Territories
TERRITORY_L0_BASE = "L0 Maintenance/Base Agent"
TERRITORY_L1_BASE = "L1 Cognition/Base Agent"
TERRITORY_L2_BASE = "L2 Execution/Base Agent"
TERRITORY_L3_BASE = "L3 Orchestration/Base Agent"
TERRITORY_L4_BASE = "L4 State/Base Agent"
TERRITORY_L5_BASE = "L5 Safety/Base Agent"
TERRITORY_L6_BASE = "L6_Observability/Base Agent"

# L0 Maintenance Territories
TERRITORY_L0_CORE = "L0 Maintenance/Core"
TERRITORY_L0_INFRASTRUCTURE = "L0 Maintenance/Infrastructure"

# L1 Cognition Territories
TERRITORY_L1_CORE = "L1 Cognition/Core"
TERRITORY_L1_SPECIALIZED = "L1 Cognition/Specialized"

# L2 Execution Territories
TERRITORY_L2_CORE = "L2 Execution/Core"
TERRITORY_L2_SPECIALIZED = "L2 Execution/Specialized"

# L3 Orchestration Territories
TERRITORY_L3_CORE = "L3 Orchestration/Core"
TERRITORY_L3_INFRASTRUCTURE = "L3 Orchestration/Infrastructure"
TERRITORY_L3_SPECIALIZED = "L3 Orchestration/Specialized"

# L4 State Territories
TERRITORY_L4_CORE = "L4 State/Core"
TERRITORY_L4_INFRASTRUCTURE = "L4 State/Infrastructure"
TERRITORY_L4_SPECIALIZED = "L4 State/Specialized"

# L5 Safety Territories
TERRITORY_L5_VALIDATORS = "L5 Safety/Validators"
TERRITORY_L5_GUARDRAILS = "L5 Safety/Guardrails"
TERRITORY_L5_RED_TEAMING = "L5 Safety/Red Teaming"
TERRITORY_L5_GRAVITY = "L5 Safety/Gravity"

# L6 Observability Territories
TERRITORY_L6_METRICS = "L6_Observability/Metrics"
TERRITORY_L6_TELEMETRY = "L6_Observability/Telemetry"
TERRITORY_L6_TRACING = "L6_Observability/Tracing"
TERRITORY_L6_COMPLIANCE = "L6_Observability/Compliance"

# Apps Territories
TERRITORY_APPS_LIC = "Apps Lic"
TERRITORY_APPS_RG = "Apps Rg"
TERRITORY_APPS_SHARED = "Apps Shared"

# Utils Territory
TERRITORY_UTILS = "Utils"

# ============================================================================
# TERRITORY MAPPING FUNCTIONS
# ============================================================================

def get_base_agent_territory(layer: str) -> str:
    """
    Get the canonical territory name for a base agent in a given layer.
    
    Args:
        layer: Layer name (e.g., 'L0', 'L1', 'Base')
    
    Returns:
        Canonical territory name for the base agent
    """
    base_territories = {
        'Base': TERRITORY_SOVEREIGN_BASE,
        'L0': TERRITORY_L0_BASE,
        'L1': TERRITORY_L1_BASE,
        'L2': TERRITORY_L2_BASE,
        'L3': TERRITORY_L3_BASE,
        'L4': TERRITORY_L4_BASE,
        'L5': TERRITORY_L5_BASE,
        'L6': TERRITORY_L6_BASE,
    }
    return base_territories.get(layer, f"{layer}/Base Agent")


def get_territory_from_path(layer: str, path_str: str, is_base_class: bool, class_name: str = '') -> str:
    """
    Determine the canonical territory name based on layer, path, and class type.
    
    Args:
        layer: Layer name (e.g., 'L0', 'L1', 'Base')
        path_str: Lowercase path string (e.g., 'agentic_core/l5_safety/validators')
        is_base_class: Whether this is a base agent class
        class_name: Name of the class (optional, for special cases)
    
    Returns:
        Canonical territory name
    """
    # Special case: SovereignBaseAgent
    if class_name == 'SovereignBaseAgent' or layer == 'Base':
        return TERRITORY_SOVEREIGN_BASE
    
    # Base agents get their layer's base territory
    if is_base_class:
        return get_base_agent_territory(layer)
    
    # Apps territories
    if 'apps_lic' in path_str:
        return TERRITORY_APPS_LIC
    elif 'apps_rg' in path_str:
        return TERRITORY_APPS_RG
    elif 'apps_shared' in path_str:
        return TERRITORY_APPS_SHARED
    
    # Utils territory
    if 'utils' in path_str:
        return TERRITORY_UTILS
    
    # Layer-specific territories
    if layer == 'L5':
        if 'validators' in path_str or 'validator' in path_str:
            return TERRITORY_L5_VALIDATORS
        elif 'red_team' in path_str or 'red_teaming' in path_str:
            return TERRITORY_L5_RED_TEAMING
        elif 'gravity' in path_str:
            return TERRITORY_L5_GRAVITY
        else:
            return TERRITORY_L5_GUARDRAILS
    
    elif layer == 'L4':
        if 'filesystem' in path_str or 'infrastructure' in path_str:
            return TERRITORY_L4_INFRASTRUCTURE
        elif 'adapter' in path_str:
            return TERRITORY_L4_SPECIALIZED
        else:
            return TERRITORY_L4_CORE
    
    elif layer == 'L3':
        if 'infrastructure' in path_str:
            return TERRITORY_L3_INFRASTRUCTURE
        elif 'adapter' in path_str:
            return TERRITORY_L3_SPECIALIZED
        else:
            return TERRITORY_L3_CORE
    
    elif layer == 'L2':
        if 'adapter' in path_str:
            return TERRITORY_L2_SPECIALIZED
        else:
            return TERRITORY_L2_CORE
    
    elif layer == 'L1':
        if 'adapter' in path_str:
            return TERRITORY_L1_SPECIALIZED
        else:
            return TERRITORY_L1_CORE
    
    elif layer == 'L0':
        if 'infrastructure' in path_str:
            return TERRITORY_L0_INFRASTRUCTURE
        else:
            return TERRITORY_L0_CORE
    
    elif layer == 'L6':
        if 'metrics' in path_str:
            return TERRITORY_L6_METRICS
        elif 'telemetry' in path_str:
            return TERRITORY_L6_TELEMETRY
        elif 'tracing' in path_str:
            return TERRITORY_L6_TRACING
        elif 'compliance' in path_str:
            return TERRITORY_L6_COMPLIANCE
        else:
            return TERRITORY_L6_METRICS
    
    # Fallback
    return layer if layer else "Unknown"


# ============================================================================
# CANONICAL TERRITORY ORDER (for dashboard sorting)
# ============================================================================

CANONICAL_TERRITORY_ORDER = [
    # Sovereign Base Agent always first
    TERRITORY_SOVEREIGN_BASE,
    
    # L6 Observability
    TERRITORY_L6_BASE,
    TERRITORY_L6_METRICS,
    TERRITORY_L6_TELEMETRY,
    TERRITORY_L6_TRACING,
    TERRITORY_L6_COMPLIANCE,
    
    # L5 Safety
    TERRITORY_L5_BASE,
    TERRITORY_L5_VALIDATORS,
    TERRITORY_L5_GUARDRAILS,
    TERRITORY_L5_RED_TEAMING,
    TERRITORY_L5_GRAVITY,
    
    # L4 State
    TERRITORY_L4_BASE,
    TERRITORY_L4_CORE,
    TERRITORY_L4_INFRASTRUCTURE,
    TERRITORY_L4_SPECIALIZED,
    
    # L3 Orchestration
    TERRITORY_L3_BASE,
    TERRITORY_L3_CORE,
    TERRITORY_L3_INFRASTRUCTURE,
    TERRITORY_L3_SPECIALIZED,
    
    # L2 Execution
    TERRITORY_L2_BASE,
    TERRITORY_L2_CORE,
    TERRITORY_L2_SPECIALIZED,
    
    # L1 Cognition
    TERRITORY_L1_BASE,
    TERRITORY_L1_CORE,
    TERRITORY_L1_SPECIALIZED,
    
    # L0 Maintenance
    TERRITORY_L0_BASE,
    TERRITORY_L0_CORE,
    TERRITORY_L0_INFRASTRUCTURE,
    
    # Apps
    TERRITORY_APPS_LIC,
    TERRITORY_APPS_RG,
    TERRITORY_APPS_SHARED,
    
    # Utils
    TERRITORY_UTILS,
]


def get_territory_sort_key(territory: str) -> int:
    """
    Get the sort key for a territory (for canonical ordering).
    
    Args:
        territory: Territory name
    
    Returns:
        Sort key (lower = earlier in list)
    """
    try:
        return CANONICAL_TERRITORY_ORDER.index(territory)
    except ValueError:
        # Unknown territories go to the end
        return 9999
