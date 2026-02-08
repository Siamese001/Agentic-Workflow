"""
Structure Blueprint Package - Refactored for Performance

This package splits the monolithic structure_blueprint_config.py into:
- ssot.py: HOT module (minimal, fast import)
- territories.py: COLD module (heavy territory definitions)
- classification.py: COLD module (pattern matching, lazy regex)
- semantics.py: COLD module (semantic analysis registries)
- derived.py: COLD module (derived registries, compilation)

All public exports are re-exported here for backward compatibility.
"""

from __future__ import annotations

# HOT imports - always loaded (minimal)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    # Path constants
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    BLUEPRINT_SOVEREIGN_DIR,
    COVERAGE_HTML_DIR,
    DASHBOARD_DIR,
    DOCS_REPORTS_PLANS,
    KNOWN_GOOD_HASHES,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    # Allowlists (path-based)
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
    L6_OBSERVABILITY_DIR,
    # Layer validation
    LAYER_ROOTS,
    LEAF_DOMAINS_NO_LCD,
    OPS_SCRIPTS_DIR,
    PROJECT_ROOT_MARKERS,
    PROMPT_GOVERNANCE_DIR,
    REPORTS_DIR,
    REQUIRED_LCD_SUBFOLDERS,
    RUNTIME_DIR,
    RUNTIME_STATE_JSON,
    SCHEMAS_DIR,
    SCRIPTS_FORBIDDEN_PATTERNS,
    STANDARD_LAYER_STRUCTURE,
    TESTS_AUTOGEN_DIR,
    TESTS_DIR,
    TESTS_E2E_DIR,
    TESTS_INTEGRATION_DIR,
    TESTS_UNIT_DIR,
    UTILS_DIR,
    # Variable depth
    VARIABLE_DEPTH_SUBFOLDERS,
    get_apps_lic_subfolder_map,
    get_apps_rg_subfolder_map,
    get_apps_shared_subfolder_map,
    get_core_subfolder_map,
    # Lazy loaders
    get_sovereign_territories,
    get_subfolder_metadata,
    get_validated_project_root,
    is_allowed_subfolder,
    is_layer_root,
    safe_path_join,
    validate_no_nested_lcd,
    validate_path_within_project,
)


# Lazy property accessors for backward compatibility
# These trigger loading of cold modules on first access
def __getattr__(name: str):
    """Lazy load cold module exports on first access."""
    # Territories
    if name == "SOVEREIGN_TERRITORIES":
        return get_sovereign_territories()
    if name == "CORE_SUBFOLDER_MAP":
        return get_core_subfolder_map()
    if name == "SUBFOLDER_METADATA":
        return get_subfolder_metadata()
    if name == "APPS_RG_SUBFOLDER_MAP":
        return get_apps_rg_subfolder_map()
    if name == "APPS_LIC_SUBFOLDER_MAP":
        return get_apps_lic_subfolder_map()
    if name == "APPS_SHARED_SUBFOLDER_MAP":
        return get_apps_shared_subfolder_map()
    if name == "agentic_core_registry":
        return get_core_subfolder_map()

    # Classification patterns (lazy)
    if name in (
        "CLASSIFICATION_SUFFIX_PATTERNS",
        "COMPOUND_SUFFIX_CONFLICTS",
        "FOLDER_PURITY_RULES",
        "SUFFIX_TO_FOLDER",
        "FILETYPE_TO_FOLDER",
        "KNOWN_ARCHITECTURAL_SUFFIXES",
        "FORBIDDEN_COMPOUND_PATTERNS",
        "L5_ENFORCEMENT_ALLOWED_SUFFIXES",
        "LAYER_PREFIX_PATTERN",
        "INTERFACE_FILENAME_PATTERN",
        "GLOBAL_INTERFACES_FOLDER",
        "CANONICAL_LOCATION_PRIORITY",
        "DUPLICATE_DETECTION_EXEMPT",
        "NON_PYTHON_FOLDER_ROUTES",
        "DOMAIN_CONTENT_SIGNALS",
        "SERVICE_CLASS_INDICATORS",
    ):
        from agentic_core.L5_safety.config.structure_blueprint import classification

        return getattr(classification, name)

    # Semantics (lazy)
    if name in (
        "NAMING_CONVENTIONS",
        "LAYER_KEYWORD_AFFINITY",
        "APP_RG_AST_TERMS",
        "APP_LIC_AST_TERMS",
        "APP_RG_VARIABLE_TERMS",
        "APP_LIC_VARIABLE_TERMS",
        "APP_RG_STRING_TERMS",
        "APP_LIC_STRING_TERMS",
        "VARIABLE_HIT_WEIGHT",
        "STRING_HIT_WEIGHT",
        "AST_DOMAIN_HIT_THRESHOLD",
        "FORBIDDEN_APP_MODULES",
        "POLYGLOT_DOMAIN_SIGNALS",
        "CORE_TERRITORY_KEYWORDS",
        "LAYER_FORBIDDEN_IMPORTS",
        "TERRITORY_MISMATCH_THRESHOLD",
        "MIN_ALIGNMENT_SCORE",
        "DEFAULT_APP_HEALING_TARGET",
        "DEFAULT_CORE_HEALING_TERRITORY",
        "VIOLATION_SEVERITY",
        "APP_DOMAIN_PREFIXES",
    ):
        from agentic_core.L5_safety.config.structure_blueprint import semantics

        return getattr(semantics, name)

    # Artifacts (lazy)
    if name in (
        "APP_SPECIFIC_PATTERNS",
        "FORBIDDEN_BACKUP_PATTERNS",
        "FORBIDDEN_FILENAME_PATTERNS",
        "FORBIDDEN_EPHEMERAL_PATTERNS",
        "EPHEMERAL_PATTERN_EXEMPTIONS",
        "APP_SPECIFIC_PREFIXES",
        "STUTTERING_PREFIX_MAP",
        "APP_SPECIFIC_TARGET_SUBFOLDER",
        "FORBIDDEN_LAYER_PREFIXES",
        "get_app_specific_patterns_compiled",
        "get_forbidden_backup_patterns_compiled",
    ):
        from agentic_core.L5_safety.config.structure_blueprint import artifacts

        return getattr(artifacts, name)

    # Derived registries (lazy)
    if name in (
        "L4_SUBFOLDER_MAP",
        "L4_APPROVED_FOLDERS",
        "SCRIPTS_PLACEMENT_RULES",
        "TESTS_L2_SUBFOLDER_MAP",
        "TESTS_SUBFOLDER_MAP",
        "verify_derived_registries",
    ):
        from agentic_core.L5_safety.config.structure_blueprint import derived

        return getattr(derived, name)

    # Territories module (lazy)
    if name in (
        "SubfolderDefinition",
        "TerritoryDefinition",
        "build_sovereign_territories",
    ):
        from agentic_core.L5_safety.config.structure_blueprint import territories

        return getattr(territories, name)

    # Helper functions (lazy)
    if name in (
        "get_correct_app_folder",
        "get_correct_app_path",
        "is_app_specific_file",
        "has_forbidden_layer_prefix",
        "is_broken_backup_file",
    ):
        from agentic_core.L5_safety.config.structure_blueprint import artifacts

        return getattr(artifacts, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # HOT exports (always available)
    "LAYER_ROOTS",
    "REQUIRED_LCD_SUBFOLDERS",
    "LEAF_DOMAINS_NO_LCD",
    "STANDARD_LAYER_STRUCTURE",
    "is_layer_root",
    "is_allowed_subfolder",
    "validate_no_nested_lcd",
    "L5_SUBPROCESS_ALLOWLIST",
    "L6_HYBRID_ALLOWLIST",
    "SCRIPTS_FORBIDDEN_PATTERNS",
    "AGENTIC_CORE_DIR",
    "APPS_RG_DIR",
    "APPS_LIC_DIR",
    "APPS_SHARED_DIR",
    "OPS_SCRIPTS_DIR",
    "TESTS_DIR",
    "L0_MAINTENANCE_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L6_OBSERVABILITY_DIR",
    "DASHBOARD_DIR",
    "BLUEPRINT_SOVEREIGN_DIR",
    "SCHEMAS_DIR",
    "PROMPT_GOVERNANCE_DIR",
    "UTILS_DIR",
    "RUNTIME_DIR",
    "TESTS_UNIT_DIR",
    "TESTS_INTEGRATION_DIR",
    "TESTS_E2E_DIR",
    "TESTS_AUTOGEN_DIR",
    "REPORTS_DIR",
    "ARCHIVES_DIR",
    "COVERAGE_HTML_DIR",
    "DOCS_REPORTS_PLANS",
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "RUNTIME_STATE_JSON",
    "KNOWN_GOOD_HASHES",
    "PROJECT_ROOT_MARKERS",
    "get_validated_project_root",
    "validate_path_within_project",
    "safe_path_join",
    "VARIABLE_DEPTH_SUBFOLDERS",
    # COLD exports (lazy loaded)
    "SOVEREIGN_TERRITORIES",
    "CORE_SUBFOLDER_MAP",
    "SUBFOLDER_METADATA",
    "APPS_RG_SUBFOLDER_MAP",
    "APPS_LIC_SUBFOLDER_MAP",
    "APPS_SHARED_SUBFOLDER_MAP",
    "agentic_core_registry",
    "SubfolderDefinition",
    "TerritoryDefinition",
    "build_sovereign_territories",
    "CLASSIFICATION_SUFFIX_PATTERNS",
    "COMPOUND_SUFFIX_CONFLICTS",
    "FOLDER_PURITY_RULES",
    "SUFFIX_TO_FOLDER",
    "FILETYPE_TO_FOLDER",
    "NAMING_CONVENTIONS",
    "LAYER_KEYWORD_AFFINITY",
    "APP_RG_AST_TERMS",
    "APP_LIC_AST_TERMS",
    "APP_SPECIFIC_PATTERNS",
    "FORBIDDEN_BACKUP_PATTERNS",
    "L4_SUBFOLDER_MAP",
    "L4_APPROVED_FOLDERS",
    "verify_derived_registries",
    "get_correct_app_folder",
    "get_correct_app_path",
    "is_app_specific_file",
    "has_forbidden_layer_prefix",
    "is_broken_backup_file",
]
