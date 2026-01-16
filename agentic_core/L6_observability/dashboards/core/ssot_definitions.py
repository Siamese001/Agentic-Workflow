"""
Dashboard SSOT Definitions
==========================
SINGLE SOURCE OF TRUTH for all dashboard metric calculations.

⚠️  AUTO-GENERATED FROM scripts/config/dashboard_ssot.yaml
⚠️  DO NOT EDIT CONSTANTS MANUALLY - Edit the YAML file instead
⚠️  Run: python scripts/generate_dashboard_ssot.py

ALL dashboard-related scripts MUST import from this file:
- scripts/full_agent_discovery.py
- scripts/regenerate_dashboard_data.py
- scripts/test_dashboard_end_to_end.py

DO NOT define metric calculations elsewhere. This eliminates "split brain" issues.

Last Generated: 2026-01-16 18:25:30
"""
from typing import Dict, Any, List, Set


# ============================================================================
# DASHBOARD COLUMN NAMES (display names in dashboard HTML)
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

COL_TERRITORY = 'Territory'
COL_TOTAL = 'Total'
COL_COMPLIANT = 'Compliant'
COL_HEAL_CAP = 'Heal Cap %'
COL_INVOCATION = 'Invocation %'
COL_TEST = 'Test %'
COL_HARDENED = 'MCP Hardened %'
COL_COMPLEXITY_HEALTH = 'Complexity Health %'
COL_HEALTH = 'Health'
COL_TYPED = 'Typed %'
COL_DOCUMENTED = 'Documented %'
COL_SCHEMA_STRICTNESS = 'Schema Strictness %'
COL_CANONICAL_INHERITANCE = 'Canonical Inheritance %'
COL_CODE_QUALITY = 'Code Quality Score'
COL_AVG_CC = 'Avg CC'
COL_OBSERVABLE = 'Observable %'


# ============================================================================
# METRIC FIELD NAMES (canonical names used in agent_discovery_full.json)
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

FIELD_CLASS_NAME = 'class_name'
FIELD_PATH = 'path'
FIELD_LAYER = 'layer'
FIELD_TERRITORY = 'territory'
FIELD_CATEGORY = 'category'
FIELD_HAS_HEALING = 'has_healing'
FIELD_HAS_TESTS = 'has_tests'
FIELD_HAS_TOOLS = 'has_tools'
FIELD_HAS_MEMORY = 'has_memory'
FIELD_MCP_HARDENED = 'mcp_hardened'
FIELD_INVOCATION = 'invocation'
FIELD_TYPED_PCT = 'typed_pct'
FIELD_DOCUMENTED_PCT = 'documented_pct'
FIELD_SCHEMA_STRICTNESS = 'schema_strictness'
FIELD_PROPER_BASE_CLASS = 'proper_base_class'
FIELD_CYCLOMATIC_COMPLEXITY = 'cyclomatic_complexity'
FIELD_INHERITANCE = 'inheritance'
FIELD_BASE_CLASSES = 'base_classes'


# ============================================================================
# METRIC THRESHOLDS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

THRESHOLD_MCP_HARDENED_TARGET = 100.0
THRESHOLD_HEAL_CAP_TARGET = 100.0
THRESHOLD_TEST_COVERAGE_MIN = 50.0
THRESHOLD_HEALTH_SCORE_MIN = 60.0
THRESHOLD_COMPLEXITY_HEALTH_MIN = 30.0
THRESHOLD_TEST_COVERAGE_TARGET = 80.0
THRESHOLD_TYPED_TARGET = 100.0
THRESHOLD_DOCUMENTED_TARGET = 100.0
THRESHOLD_SCHEMA_STRICTNESS_TARGET = 100.0
THRESHOLD_OUTLIER_THRESHOLD_DEFAULT = 50.0
THRESHOLD_OUTLIER_THRESHOLD_CRITICAL = 0.0
THRESHOLD_COMPLEXITY_HEALTH_MAX = 60.0
THRESHOLD_AVG_CC_WARNING = 15.0
THRESHOLD_AVG_CC_CRITICAL = 25.0
THRESHOLD_COVERAGE_WARNING = 70.0
THRESHOLD_COVERAGE_CRITICAL = 40.0
THRESHOLD_QUALITY_TARGET = 90.0


# ============================================================================
# HEALTH SCORE FORMULA WEIGHTS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

WEIGHT_HEALTH_HEAL_CAP = 0.3
WEIGHT_HEALTH_INVOCATION = 0.1
WEIGHT_HEALTH_TEST = 0.25
WEIGHT_HEALTH_OBSERVABLE = 0.2
WEIGHT_HEALTH_COMPLEXITY = 0.15

# L0-specific weights (infrastructure layer)
WEIGHT_HEALTH_L0_TEST = 0.4
WEIGHT_HEALTH_L0_HARDENED = 0.3
WEIGHT_HEALTH_L0_COMPLEXITY = 0.3


# ============================================================================
# CODE QUALITY FORMULA WEIGHTS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

WEIGHT_CODE_QUALITY_TYPED = 0.25
WEIGHT_CODE_QUALITY_DOCUMENTED = 0.25
WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS = 0.25
WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE = 0.25

# ============================================================================
# SSOT INTEGRITY CONSTRAINTS
# ============================================================================
try:
    assert abs(sum([WEIGHT_HEALTH_HEAL_CAP, WEIGHT_HEALTH_INVOCATION, WEIGHT_HEALTH_TEST, WEIGHT_HEALTH_OBSERVABLE, WEIGHT_HEALTH_COMPLEXITY]) - 1.0) < 0.001
    assert abs(sum([WEIGHT_HEALTH_L0_TEST, WEIGHT_HEALTH_L0_HARDENED, WEIGHT_HEALTH_L0_COMPLEXITY]) - 1.0) < 0.001
    assert abs(sum([WEIGHT_CODE_QUALITY_TYPED, WEIGHT_CODE_QUALITY_DOCUMENTED, WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS, WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE]) - 1.0) < 0.001
except AssertionError as e:
    print(f'❌ CRITICAL: SSOT Weight mismatch detected in dashboard_ssot.yaml')
    raise


# ============================================================================
# PLACEHOLDERS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

PLACEHOLDER_OBSERVABLE_PCT = 50.0  # Observable Pct awaiting implementation


# ============================================================================
# LAYER DEFINITIONS
# ============================================================================

LAYER_ORDER = ['Base', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'Apps']

# L0 is infrastructure layer - healing metrics are N/A
L0_HEALING_NA = True

# MCP-hardened base classes
MCP_HARDENED_BASES = {
    'SovereignBaseAgent', 'L0MaintenanceBaseAgent', 'L1CognitionBaseAgent',
    'L2ExecutionBaseAgent', 'L3OrchestrationBaseAgent', 'L4StateBaseAgent',
    'L5SafetyBaseAgent', 'L6ObservabilityBaseAgent', 'MCPHardenedMixin'
}

# Healer base classes
HEALER_BASES = {
    'HealerMixin', 'SovereignBaseAgent', 'L0MaintenanceBaseAgent',
    'L1CognitionBaseAgent', 'L2ExecutionBaseAgent', 'L3OrchestrationBaseAgent',
    'L4StateBaseAgent', 'L5SafetyBaseAgent', 'L6ObservabilityBaseAgent'
}


# ============================================================================
# METRIC CALCULATION FUNCTIONS (SSOT)
# ============================================================================

def calc_heal_cap_pct(agents: List[Dict], is_l0: bool = False) -> float:
    """
    Calculate Heal Capability % for a set of agents.
    
    Definition: Percentage of agents that have healing capability through:
    1. Direct implementation (heal, apply_fix, heal_violation, heal_repository)
    2. Inheritance from HealerMixin or layer base classes
    
    Args:
        agents: List of agent dictionaries from discovery
        is_l0: If True, return "N/A" equivalent (L0 is infrastructure layer)
    
    Returns:
        Percentage (0-100) or 0.0 if L0
    """
    if is_l0:
        return 0.0  # Will be displayed as "N/A" in dashboard
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False))
    return round(count / len(agents) * 100, 1)


def calc_invocation_pct(agents: List[Dict], is_l0: bool = False) -> float:
    """
    Calculate Heal Invocation % for a set of agents.
    
    Definition: Percentage of agents that call super().heal_repository()
    in their heal_repository() method (ensures healing propagates through MRO).
    
    Args:
        agents: List of agent dictionaries from discovery
        is_l0: If True, return "N/A" equivalent (L0 is infrastructure layer)
    
    Returns:
        Percentage (0-100) or 0.0 if L0
    """
    if is_l0:
        return 0.0  # Will be displayed as "N/A" in dashboard
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_INVOCATION) == 'Yes')
    return round(count / len(agents) * 100, 1)


def calc_test_pct(agents: List[Dict]) -> float:
    """
    Calculate Test Coverage % for a set of agents.
    
    Definition: Percentage of agents that have associated test files.
    Uses 'has_tests' boolean field from discovery.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Percentage (0-100)
    """
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_HAS_TESTS, False))
    return round(count / len(agents) * 100, 1)


def calc_hardened_pct(agents: List[Dict]) -> float:
    """
    Calculate MCP Hardened % for a set of agents.
    
    Definition: Percentage of agents with MCPHardenedMixin for tool boundary security.
    Detection is MRO-aware: agents inheriting from hardened bases are considered hardened.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Percentage (0-100)
    """
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_MCP_HARDENED, False))
    return round(count / len(agents) * 100, 1)


def calc_typed_pct(agents: List[Dict]) -> float:
    """
    Calculate average Typed % for a set of agents.
    
    Definition: Average percentage of code with type hints across all agents.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Percentage (0-100)
    """
    if not agents:
        return 0.0
    total = sum(a.get(FIELD_TYPED_PCT, 0) for a in agents)
    return round(total / len(agents), 1)


def calc_documented_pct(agents: List[Dict]) -> float:
    """
    Calculate average Documented % for a set of agents.
    
    Definition: Average percentage of code with docstrings across all agents.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Percentage (0-100)
    """
    if not agents:
        return 0.0
    total = sum(a.get(FIELD_DOCUMENTED_PCT, 0) for a in agents)
    return round(total / len(agents), 1)


def calc_schema_strictness_pct(agents: List[Dict]) -> float:
    """
    Calculate average Schema Strictness % for a set of agents.
    
    Definition: Average schema strictness score across all agents.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Percentage (0-100)
    """
    if not agents:
        return 0.0
    total = sum(a.get(FIELD_SCHEMA_STRICTNESS, 0) for a in agents)
    return round(total / len(agents), 1)


def calc_canonical_inheritance_pct(agents: List[Dict]) -> float:
    """
    Calculate Canonical Inheritance % for a set of agents.
    
    Definition: Percentage of agents inheriting from proper layer base class.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Percentage (0-100)
    """
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_PROPER_BASE_CLASS, False))
    return round(count / len(agents) * 100, 1)


def calc_avg_cc(agents: List[Dict]) -> float:
    """
    Calculate average Cyclomatic Complexity for a set of agents.
    
    Args:
        agents: List of agent dictionaries from discovery
    
    Returns:
        Average CC value
    """
    if not agents:
        return 0.0
    total = sum(a.get(FIELD_CYCLOMATIC_COMPLEXITY, 0) for a in agents)
    return round(total / len(agents), 1)


def calc_complexity_health(avg_cc: float) -> float:
    """
    Calculate Complexity Health score from average CC.
    
    Definition: 100 - (CC * 2), capped at 0 minimum.
    Lower CC = higher health.
    
    Args:
        avg_cc: Average cyclomatic complexity
    
    Returns:
        Complexity health score (0-100)
    """
    return round(max(0, 100 - avg_cc * 2), 1)


def calc_health_score(
    heal_cap_pct: float,
    invocation_pct: float,
    test_pct: float,
    observable_pct: float,
    complexity_health: float,
    is_l0: bool = False
) -> float:
    """
    Calculate overall Health score for a territory using SSOT weights.
    
    Definition (standard):
        Health = (Heal Cap * WEIGHT_HEALTH_HEAL_CAP) + (Invocation * WEIGHT_HEALTH_INVOCATION) + 
                 (Test * WEIGHT_HEALTH_TEST) + (Observable * WEIGHT_HEALTH_OBSERVABLE) + 
                 (Complexity Health * WEIGHT_HEALTH_COMPLEXITY)
    
    Definition (L0 - infrastructure layer):
        Health = (Test * WEIGHT_HEALTH_L0_TEST) + (Hardened * WEIGHT_HEALTH_L0_HARDENED) + 
                 (Complexity Health * WEIGHT_HEALTH_L0_COMPLEXITY)
        Note: L0 excludes healing metrics as they are N/A
    
    Args:
        heal_cap_pct: Heal Capability %
        invocation_pct: Heal Invocation %
        test_pct: Test Coverage %
        observable_pct: Observability % (placeholder at 50 currently)
        complexity_health: Complexity Health score
        is_l0: If True, use L0-specific formula
    
    Returns:
        Health score (0-100)
    """
    if is_l0:
        # L0 health excludes healing metrics, uses L0-specific SSOT weights
        return round(
            test_pct * WEIGHT_HEALTH_L0_TEST +
            THRESHOLD_MCP_HARDENED_TARGET * WEIGHT_HEALTH_L0_HARDENED +
            complexity_health * WEIGHT_HEALTH_L0_COMPLEXITY,
            1
        )
    return round(
        heal_cap_pct * WEIGHT_HEALTH_HEAL_CAP +
        invocation_pct * WEIGHT_HEALTH_INVOCATION +
        test_pct * WEIGHT_HEALTH_TEST +
        observable_pct * WEIGHT_HEALTH_OBSERVABLE +
        complexity_health * WEIGHT_HEALTH_COMPLEXITY,
        1
    )


def calc_code_quality_score(
    typed_pct: float,
    documented_pct: float,
    schema_pct: float,
    canonical_pct: float
) -> float:
    """
    Calculate Code Quality Score using SSOT weights.
    
    Definition: Weighted composite of code quality metrics.
        Quality = (Typed * WEIGHT_CODE_QUALITY_TYPED) + (Documented * WEIGHT_CODE_QUALITY_DOCUMENTED) + 
                  (Schema * WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS) + (Canonical * WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE)
    
    Args:
        typed_pct: Typed %
        documented_pct: Documented %
        schema_pct: Schema Strictness %
        canonical_pct: Canonical Inheritance %
    
    Returns:
        Code quality score (0-100)
    """
    return round(
        typed_pct * WEIGHT_CODE_QUALITY_TYPED +
        documented_pct * WEIGHT_CODE_QUALITY_DOCUMENTED +
        schema_pct * WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS +
        canonical_pct * WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE,
        1
    )


def is_l0_territory(territory: str) -> bool:
    """Check if a territory is L0 (infrastructure layer)."""
    return 'L0' in territory


def get_heal_cap_display(pct: float, is_l0: bool) -> Any:
    """Get display value for Heal Cap % (returns 'N/A' for L0)."""
    if is_l0:
        return "N/A"
    return pct


def get_invocation_display(pct: float, is_l0: bool) -> Any:
    """Get display value for Invocation % (returns 'N/A' for L0)."""
    if is_l0:
        return "N/A"
    return pct


# ============================================================================
# TERRITORY SORTING (SovereignBaseAgent at top)
# ============================================================================

def get_territory_sort_key(territory: str) -> tuple:
    """
    Get sort key for territory ordering.
    
    Order:
    1. Base/Root (SovereignBaseAgent) - ALWAYS FIRST
    2. L0 Maintenance
    3. L1 Cognition
    4. L2 Execution
    5. L3 Orchestration
    6. L4 State
    7. L5 Safety
    8. L6 Observability
    9. Apps (alphabetically)
    
    Args:
        territory: Territory name
    
    Returns:
        Tuple for sorting (layer_order, suborder, name)
    """
    # Base/Root always first
    if territory in ('Base/Root', 'Base/Base Class'):
        return (0, 0, territory)
    
    # Layer-based ordering
    for i, layer in enumerate(LAYER_ORDER):
        if territory.startswith(layer):
            # Within layer: Base Agent first, then alphabetical
            if 'Base Agent' in territory or 'Base Class' in territory:
                return (i + 1, 0, territory)
            elif 'Core' in territory:
                return (i + 1, 1, territory)
            else:
                return (i + 1, 2, territory)
    
    # Apps at the end
    if 'Apps' in territory:
        return (100, 0, territory)
    
    # Unknown territories last
    return (999, 0, territory)


def sort_territories(territories: List[str]) -> List[str]:
    """Sort territories with Base/Root first."""
    return sorted(territories, key=get_territory_sort_key)


def sort_dashboard_data(dashboard_data: List[Dict]) -> List[Dict]:
    """
    Sort dashboard data with correct ordering.
    
    Order:
    1. Base/Root (SovereignBaseAgent) FIRST - the root of all agents
    2. L0 through L6 layers in order
    3. Apps territories
    4. TOTAL row LAST (for summary)
    """
    total_row = None
    territory_rows = []
    
    for row in dashboard_data:
        if row.get('Territory') == 'TOTAL':
            total_row = row
        else:
            territory_rows.append(row)
    
    # Sort territories with Base/Root first
    territory_rows.sort(key=lambda r: get_territory_sort_key(r.get('Territory', '')))
    
    # TOTAL at end
    if total_row:
        territory_rows.append(total_row)
    
    return territory_rows


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_agent_has_required_fields(agent: Dict) -> List[str]:
    """Validate an agent dictionary has all required fields."""
    required = [
        'path', 'class_name', 'layer', FIELD_HAS_HEALING, FIELD_INVOCATION,
        FIELD_HAS_TESTS, FIELD_MCP_HARDENED, FIELD_TYPED_PCT, 
        FIELD_DOCUMENTED_PCT, FIELD_SCHEMA_STRICTNESS, FIELD_PROPER_BASE_CLASS
    ]
    missing = [f for f in required if f not in agent]
    return missing


def get_canonical_health_score(metrics_dict: Dict[str, Any], is_l0: bool = False) -> float:
    """
    Calculate health score using SSOT weights and field constants.
    
    This is the canonical implementation that should be used everywhere
    health scores are calculated. It uses SSOT weights from the YAML config.
    
    Args:
        metrics_dict: Dictionary with agent metrics (uses FIELD_* constants as keys)
        is_l0: If True, uses L0-specific formula (no healing metrics)
    
    Returns:
        Health score (0-100)
    """
    if is_l0:
        # L0 health excludes healing metrics
        return round(
            safe_numeric(metrics_dict.get(FIELD_HAS_TESTS, 0)) * WEIGHT_HEALTH_L0_TEST +
            safe_numeric(metrics_dict.get(FIELD_MCP_HARDENED, 0)) * WEIGHT_HEALTH_L0_HARDENED +
            safe_numeric(metrics_dict.get(FIELD_CYCLOMATIC_COMPLEXITY, 0)) * WEIGHT_HEALTH_L0_COMPLEXITY,
            2
        )
    
    # Standard health formula
    return round(
        safe_numeric(metrics_dict.get(FIELD_HAS_HEALING, 0)) * WEIGHT_HEALTH_HEAL_CAP +
        safe_numeric(metrics_dict.get(FIELD_INVOCATION, 0)) * WEIGHT_HEALTH_INVOCATION +
        safe_numeric(metrics_dict.get(FIELD_HAS_TESTS, 0)) * WEIGHT_HEALTH_TEST +
        PLACEHOLDER_OBSERVABLE_PCT * WEIGHT_HEALTH_OBSERVABLE +
        safe_numeric(metrics_dict.get(FIELD_CYCLOMATIC_COMPLEXITY, 0)) * WEIGHT_HEALTH_COMPLEXITY,
        2
    )


def get_canonical_code_quality_score(metrics_dict: Dict[str, Any]) -> float:
    """
    Calculate code quality score using SSOT weights and field constants.
    
    This is the canonical implementation that should be used everywhere
    code quality scores are calculated.
    
    Args:
        metrics_dict: Dictionary with agent metrics (uses FIELD_* constants as keys)
    
    Returns:
        Code quality score (0-100)
    """
    return round(
        safe_numeric(metrics_dict.get(FIELD_TYPED_PCT, 0)) * WEIGHT_CODE_QUALITY_TYPED +
        safe_numeric(metrics_dict.get(FIELD_DOCUMENTED_PCT, 0)) * WEIGHT_CODE_QUALITY_DOCUMENTED +
        safe_numeric(metrics_dict.get(FIELD_SCHEMA_STRICTNESS, 0)) * WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS +
        safe_numeric(metrics_dict.get(FIELD_PROPER_BASE_CLASS, 0)) * WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE,
        2
    )


def safe_numeric(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float, handling None and 'N/A'."""
    if value is None or value == "N/A":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
