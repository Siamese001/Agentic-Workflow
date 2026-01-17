// ============================================================================
// DASHBOARD CONSTANTS
// ============================================================================
// ⚠️  AUTO-GENERATED FROM scripts/config/dashboard_ssot.yaml
// ⚠️  DO NOT EDIT MANUALLY - Edit the YAML file instead
// ⚠️  Run: python scripts/generate_dashboard_ssot.py
//
// Last Generated: 2026-01-17 08:00:53
// ============================================================================

// ============================================================================
// COLUMN NAMES
// ============================================================================
// Display names for dashboard table columns

window.COLUMNS = {
    TERRITORY: "Territory",
    TOTAL: "Total",
    COMPLIANT: "Compliant",
    HEAL_CAP: "Heal Cap %",
    INVOCATION: "Invocation %",
    TEST: "Test %",
    HARDENED: "MCP Hardened %",
    COMPLEXITY_HEALTH: "Complexity Health %",
    HEALTH: "Health",
    TYPED: "Typed %",
    DOCUMENTED: "Documented %",
    SCHEMA_STRICTNESS: "Schema Strictness %",
    CANONICAL_INHERITANCE: "Canonical Inheritance %",
    CODE_QUALITY: "Code Quality Score",
    AVG_CC: "Avg CC",
    OBSERVABLE: "Observable %",
};

// ============================================================================
// FIELD NAMES
// ============================================================================
// Field names from agent_discovery_full.json

window.FIELDS = {
    CLASS_NAME: "class_name",
    PATH: "path",
    LAYER: "layer",
    TERRITORY: "territory",
    CATEGORY: "category",
    HAS_HEALING: "has_healing",
    HAS_TESTS: "has_tests",
    HAS_TOOLS: "has_tools",
    HAS_MEMORY: "has_memory",
    MCP_HARDENED: "mcp_hardened",
    INVOCATION: "invocation",
    TYPED_PCT: "typed_pct",
    DOCUMENTED_PCT: "documented_pct",
    SCHEMA_STRICTNESS: "schema_strictness",
    PROPER_BASE_CLASS: "proper_base_class",
    CYCLOMATIC_COMPLEXITY: "cyclomatic_complexity",
    INHERITANCE: "inheritance",
    BASE_CLASSES: "base_classes",
};

// ============================================================================
// METRIC THRESHOLDS
// ============================================================================
// Standard thresholds for validation and outlier detection

window.THRESHOLDS = {
    MCP_HARDENED_TARGET: 100.0,
    HEAL_CAP_TARGET: 100.0,
    TEST_COVERAGE_MIN: 50.0,
    HEALTH_SCORE_MIN: 60.0,
    COMPLEXITY_HEALTH_MIN: 30.0,
    TEST_COVERAGE_TARGET: 80.0,
    TYPED_TARGET: 100.0,
    DOCUMENTED_TARGET: 100.0,
    SCHEMA_STRICTNESS_TARGET: 100.0,
    OUTLIER_THRESHOLD_DEFAULT: 50.0,
    OUTLIER_THRESHOLD_CRITICAL: 0.0,
    COMPLEXITY_HEALTH_MAX: 60.0,
    AVG_CC_WARNING: 15.0,
    AVG_CC_CRITICAL: 25.0,
    COVERAGE_WARNING: 70.0,
    COVERAGE_CRITICAL: 40.0,
    QUALITY_TARGET: 90.0,
};

// ============================================================================
// JAVASCRIPT METRIC KEYS
// ============================================================================
// CamelCase keys used in agentData objects

window.METRIC_KEYS = {
    HEALCAP: "healCap",
    INVOCATION: "invocation",
    HARDENED: "hardened",
    TEST: "test",
    COMPLEXITYHEALTH: "complexityHealth",
    HEALTH: "health",
    TYPED: "typed",
    DOCUMENTED: "documented",
    SCHEMASTRICTNESS: "schemaStrictness",
    PROPERBASE: "properBase",
    CODEQUALITY: "codeQuality",
};

// ============================================================================
// HEALTH SCORE WEIGHTS
// ============================================================================

window.HEALTH_WEIGHTS = {
    HEAL_CAP: 0.3,
    INVOCATION: 0.1,
    TEST: 0.25,
    OBSERVABLE: 0.2,
    COMPLEXITY: 0.15,
};

window.HEALTH_WEIGHTS_L0 = {
    TEST: 0.4,
    HARDENED: 0.3,
    COMPLEXITY: 0.3,
};

// ============================================================================
// CODE QUALITY WEIGHTS
// ============================================================================

window.CODE_QUALITY_WEIGHTS = {
    TYPED: 0.25,
    DOCUMENTED: 0.25,
    SCHEMA_STRICTNESS: 0.25,
    CANONICAL_INHERITANCE: 0.25,
};

// ============================================================================
// PLACEHOLDERS
// ============================================================================

window.PLACEHOLDERS = {
    OBSERVABLE_PCT: 50.0,
};
