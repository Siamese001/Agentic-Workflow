"""
Dashboard SSOT Definitions
==========================
SINGLE SOURCE OF TRUTH for all dashboard metric calculations.

⚠️  AUTO-GENERATED FROM agentic_core/L6_observability/dashboards/dashboard_ssot.yaml
⚠️  DO NOT EDIT CONSTANTS MANUALLY - Edit the YAML file instead
⚠️  Run: python agentic_core/L0_maintenance/scripts/generate_dashboard_ssot_util.py

ALL dashboard-related scripts MUST import from this file:
- scripts/full_agent_discovery.py
- scripts/regenerate_dashboard_data.py
- scripts/test_dashboard_end_to_end.py

DO NOT define metric calculations elsewhere. This eliminates "split brain" issues.

Last Generated: 2026-01-20 14:46:21
"""


# ============================================================================
# DASHBOARD COLUMN NAMES (display names in dashboard HTML)
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

COL_TERRITORY = "Territory"
COL_TOTAL = "Total"
COL_COMPLIANT = "Compliant"
COL_HEAL_CAP = "Heal Cap %"
COL_INVOCATION = "Invocation %"
COL_TEST = "Test %"
COL_HARDENED = "MCP Hardened %"
COL_COMPLEXITY_HEALTH = "Complexity Health %"
COL_HEALTH = "Health"
COL_TYPED = "Typed %"
COL_DOCUMENTED = "Documented %"
COL_SCHEMA_STRICTNESS = "schema Strictness %"
COL_CANONICAL_INHERITANCE = "Canonical Inheritance %"
COL_CODE_QUALITY = "Code Quality Score"
COL_AVG_CC = "Avg CC"
COL_OBSERVABLE = "Observable %"


# ============================================================================
# METRIC FIELD NAMES (canonical names used in agent_discovery_full.json)
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

FIELD_CLASS_NAME = "class_name"
FIELD_PATH = "path"
FIELD_LAYER = "layer"
FIELD_TERRITORY = "territory"
FIELD_CATEGORY = "category"
FIELD_HAS_HEALING = "has_healing"
FIELD_HAS_TESTS = "has_tests"
FIELD_HAS_TOOLS = "has_tools"
FIELD_HAS_MEMORY = "has_memory"
FIELD_MCP_HARDENED = "mcp_hardened"
FIELD_INVOCATION = "invocation"
FIELD_TYPED_PCT = "typed_pct"
FIELD_DOCUMENTED_PCT = "documented_pct"
FIELD_SCHEMA_STRICTNESS = "schema_strictness"
FIELD_PROPER_BASE_CLASS = "proper_base_class"
FIELD_CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
FIELD_INHERITANCE = "inheritance"
FIELD_BASE_CLASSES = "base_classes"


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
    assert (
        abs(
            sum(
                [
                    WEIGHT_HEALTH_HEAL_CAP,
                    WEIGHT_HEALTH_INVOCATION,
                    WEIGHT_HEALTH_TEST,
                    WEIGHT_HEALTH_OBSERVABLE,
                    WEIGHT_HEALTH_COMPLEXITY,
                ],
            )
            - 1.0,
        )
        < 0.001
    )
    assert (
        abs(sum([WEIGHT_HEALTH_L0_TEST, WEIGHT_HEALTH_L0_HARDENED, WEIGHT_HEALTH_L0_COMPLEXITY]) - 1.0)
        < 0.001
    )
    assert (
        abs(
            sum(
                [
                    WEIGHT_CODE_QUALITY_TYPED,
                    WEIGHT_CODE_QUALITY_DOCUMENTED,
                    WEIGHT_CODE_QUALITY_SCHEMA_STRICTNESS,
                    WEIGHT_CODE_QUALITY_CANONICAL_INHERITANCE,
                ],
            )
            - 1.0,
        )
        < 0.001
    )
except AssertionError:
    print("❌ CRITICAL: SSOT Weight mismatch detected in dashboard_ssot.yaml")
    raise


# ============================================================================
# PLACEHOLDERS
# ============================================================================
# Auto-generated from dashboard_ssot.yaml - DO NOT EDIT MANUALLY

PLACEHOLDER_OBSERVABLE_PCT = 50.0  # Observable Pct awaiting implementation


# ============================================================================
# LAYER DEFINITIONS
# ============================================================================

LAYER_ORDER = ["Base", "L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps"]

# L0 is infrastructure layer - healing metrics are N/A
L0_HEALING_NA = True

# MCP-hardened base classes
MCP_HARDENED_BASES = {
    "SovereignBaseAgent",
    "L0MaintenanceBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
    "MCPHardenedMixin",
}

# Healer base classes
HEALER_BASES = {
    "HealerMixin",
    "SovereignBaseAgent",
    "L0MaintenanceBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
}


# ============================================================================
# METRIC CALCULATION FUNCTIONS (SSOT)
# ============================================================================
# These functions are preserved from the original file.
# Add calculation functions here.


def calc_heal_cap_pct(agents: list[dict], is_l0: bool = False) -> float:
    """Calculate Heal Capability % for a set of agents."""
    if is_l0:
        return 0.0
    if not agents:
        return 0.0
    count = sum(1 for a in agents if a.get(FIELD_HAS_HEALING, False))
    return round(count / len(agents) * 100, 1)


# Add other calculation functions as needed...
