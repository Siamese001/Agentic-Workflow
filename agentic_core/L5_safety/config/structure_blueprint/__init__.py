"""
Structure Blueprint Package - Modular SSOT (2026-02-08).

This package is the Single Source of Truth for all structural configuration.
The monolithic structure_blueprint_config.py is a backward-compatible shim
that re-exports everything from this package.

Modules:
  ssot.py           - Core constants, path utilities, whitelists, flat enforcement
  territories.py    - SOVEREIGN_TERRITORIES definition
  classification.py - Suffix patterns, folder purity, naming rules
  semantics.py      - AST signals, keyword affinity, agent/placement registries
  artifacts.py      - File patterns, artifact routing, subfolder metadata
  derived.py        - Derived registries (computed from territories)
  governance.py     - Healing, mission, gravity, MCP operational config
"""

from __future__ import annotations

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.L5_safety.config.structure_blueprint._constants import (
    AGENT_RESILIENCE_CONFIG,
    DOWNSTREAM_ROOTS,
    GRAVITY_CONFIG,
    GRAVITY_SURGERY_ENABLED,
    HEALING_CONFIG,
    LAYER_OVERRIDES,
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    UPSTREAM_SOVEREIGN_ROOTS,
    SubfolderDefinition,
    TerritoryDefinition,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    ALLOW_ROOT_PY_TERRITORIES,
    ALLOWED_DUPLICATE_FILENAMES,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    AUTONOMOUS_AGENT_WHITELIST,
    BLUEPRINT_SOVEREIGN_DIR,
    CODE_TERRITORIES,
    COVERAGE_HTML_DIR,
    DASHBOARD_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    DOCS_REPORTS_PLANS,
    ENFORCED_TERRITORIES,
    FLAT_DIRECTORIES,
    FORBIDDEN_FOLDER_PATTERN,
    FORBIDDEN_PATTERNS,
    FORBIDDEN_ROOT_FOLDERS,
    FORENSIC_DISCOVERY_INTEGRITY_HASH,
    FORENSIC_DISCOVERY_SCRIPT,
    GLOBAL_EXCLUDED_DIRS,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
    L6_OBSERVABILITY_DIR,
    LAYER_PREFIX_EXEMPT_TERRITORIES,
    LAYER_ROOTS,
    LEAF_DOMAINS_NO_LCD,
    NAMING_EXEMPT_DIRS,
    NAMING_EXEMPT_FILES,
    OPS_SCRIPTS_DIR,
    PROJECT_ROOT_MARKERS,
    PROJECT_ROOT_WHITELIST,
    PROMPT_GOVERNANCE_DIR,
    PYTHON_STDLIB_MODULES,
    REPORTS_DIR,
    REQUIRED_LCD_SUBFOLDERS,
    ROOT_ALLOWED_PATTERNS,
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
    RUNTIME_DIR,
    RUNTIME_STATE_JSON,
    SCHEMAS_DIR,
    SCOPE_SUMMARY_EXCLUSIONS,
    SCRIPTS_FORBIDDEN_PATTERNS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    STANDARD_LAYER_STRUCTURE,
    TEST_CANONICAL_LOCATION_MAP,
    TEST_MIRROR_BASE,
    TEST_MIRROR_ROOTS,
    TESTS_AUTOGEN_DIR,
    TESTS_DIR,
    TESTS_E2E_DIR,
    TESTS_INTEGRATION_DIR,
    TESTS_ROOT_FILE_WHITELIST,
    TESTS_UNIT_DIR,
    UTILS_DIR,
    VALIDATED_FILE_EXTENSIONS,
    VARIABLE_DEPTH_SUBFOLDERS,
    VOLATILE_TERRITORIES,
    get_apps_lic_subfolder_map,
    get_apps_rg_subfolder_map,
    get_apps_shared_subfolder_map,
    get_canonical_test_path,
    get_core_subfolder_map,
    get_sovereign_territories,
    get_subfolder_metadata,
    get_validated_project_root,
    ignore_dirs,
    is_allowed_subfolder,
    is_l4_approved,
    is_layer_root,
    is_path_allowed,
    protected_folders,
    safe_path_join,
    safe_prefixed_filename,
    sovereign_ignored_folders,
    validate_flat_directory,
    validate_no_duplicate_prefix,
    validate_no_nested_lcd,
    validate_path_within_project,
)
from agentic_core.L5_safety.config.structure_blueprint.territories import (
    get_all_territories,
    get_territory_metadata,
    is_valid_root_folder,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L5")
_emit_routes_through("p1", "__init__", "L5")
_emit_checks_agent_registry("p1", "__init__", "agent_registry")
_emit_validates_agent_capability("p1", "__init__", "capability")
_emit_dispatches_execution_plan("p1", "__init__", "exec_plan")
_emit_agent_executes_agent("p1", "__init__", "sub_agent")
_emit_routes_to_agent("p1", "__init__", "target_agent")
_emit_verifies_policy("p1", "__init__", "policy_check")
_emit_observes_runtime_state("p1", "__init__", "runtime_state")
_emit_verifies_boundary("p1", "__init__", "boundary_check")
_emit_transcripts_response("p1", "__init__", "transcript")
_emit_hard_fails_untranscripted("p1", "__init__")
_emit_gated_by_confidence("p1", "__init__", "confidence_gate")
_emit_escalates_to_human("p1", "__init__", "L5")
_emit_reads_policy_state("p1", "__init__", "L5")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")
_emit_authorize_and_execute("p2", "__init__", "execution_auth")
_emit_validates_capability("p2", "__init__", "capability_check")
_emit_routes_to_capability("p2", "__init__", "capability_route")
_emit_writes_via_uwg("p2", "__init__", "uwg_write")
_emit_blocks_direct_write("p2", "__init__", "direct_write_block")
_emit_records_tool_invocation("p2", "__init__", "tool_invocation")
_emit_captures_execution_output("p2", "__init__", "exec_output")
_emit_dispatches_agent("p3", "__init__", "agent_dispatch")
_emit_coordinates_agents("p3", "__init__", "agent_coordination")
_emit_records_workflow_lineage("p3", "__init__", "workflow_lineage")
_emit_records_healing_outcome("p3", "__init__", "healing_outcome")
_emit_escalates_failure("p3", "__init__", "failure_escalation")
_emit_orchestrates_workflow("p3", "__init__", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "__init__", "healing_dispatch")
_emit_invokes_evaluation("p3", "__init__", "evaluation_signal")
_emit_records_telemetry_event("p4", "__init__", "telemetry_event")
_emit_captures_evaluation_metric("p4", "__init__", "eval_metric")
_emit_stores_embedding("p4", "__init__", "embedding_store")
_emit_updates_meta_learning_state("p4", "__init__", "meta_learning")
_emit_links_execution_to_snapshot("p4", "__init__", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("__init__", "p4obs", "metric_1")
_emit_emits_metric_event("__init__", "p4obs", "metric_2")
_emit_emits_metric_event("__init__", "p4obs", "metric_3")
_emit_emits_metric_event("__init__", "p4obs", "metric_4")
_emit_emits_metric_event("__init__", "p4obs", "metric_5")
_emit_emits_metric_event("__init__", "p4obs", "metric_6")
_emit_records_incident_event("__init__", "p4obs", "incident")
_emit_captures_runtime_anomaly("__init__", "p4obs", "anomaly")
_emit_writes_observability_log("__init__", "p4obs", "obs_log")
_emit_updates_monitoring_state("__init__", "p4obs", "mon_state")
_emit_triggers_alert("__init__", "p4obs", "alert")
_emit_links_incident_trace("__init__", "p4obs", "trace_link")
_emit_captures_pattern("__init__", "p3lm", "pattern")
_emit_records_learning_event("__init__", "p3lm", "learning_event")
_emit_writes_learning_snapshot("__init__", "p3lm", "snapshot")
_emit_feeds_meta_learning("__init__", "p3lm", "meta_feed")
_emit_updates_routing_strategy("__init__", "p3lm", "routing")
_emit_improves_agent_policy("__init__", "p3lm", "policy")
_emit_stores_learning_state("__init__", "p3lm", "state")
_emit_records_execution_trace("__init__", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("__init__", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("__init__", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("__init__", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("__init__", "L4_STATE", "p2_trace_5")
_emit_reads_environ("__init__", "env_read", "p2_env_1")
_emit_reads_environ("__init__", "env_read", "p2_env_2")
_emit_reads_runtime_state("__init__", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("__init__", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "__init__", "context_pull")
_emit_pulls_context("p1", "__init__", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "__init__", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "__init__", "uwg_term_2")
_emit_writes_through("p1", "__init__", "write_through")
_emit_writes_through("p1", "__init__", "write_through_2")
_emit_validated_by_safety_plane("p1", "__init__", "safety_validation")
_emit_invokes_eval("p1", "__init__", "eval_call")
_emit_proposal_commits_routing("p1", "__init__", "routing_commit")


def __getattr__(name: str):
    """Lazy load cold module exports on first access."""
    if name in {
        "CANONICAL_LOCATION_PRIORITY",
        "CLASSIFICATION_SUFFIX_PATTERNS",
        "COMPOUND_SUFFIX_CONFLICTS",
        "DOMAIN_CONTENT_SIGNALS",
        "DUPLICATE_DETECTION_EXEMPT",
        "FILETYPE_TO_FOLDER",
        "FOLDER_PURITY_DISALLOWED",
        "FOLDER_PURITY_RULES",
        "INFRASTRUCTURE_PROFILES",
        "FOLDER_ALIASES",
        "NO_ROOT_FILES_FOLDERS",
        "APPROVED_SUBFOLDERS",
        "FORBIDDEN_COMPOUND_PATTERNS",
        "GLOBAL_INTERFACES_FOLDER",
        "INTERFACE_FILENAME_PATTERN",
        "KNOWN_ARCHITECTURAL_SUFFIXES",
        "L5_ENFORCEMENT_ALLOWED_SUFFIXES",
        "LAYER_PREFIX_PATTERN",
        "NON_PYTHON_FOLDER_ROUTES",
        "SERVICE_CLASS_INDICATORS",
        "SUFFIX_TO_FOLDER",
        "get_classification_suffix_patterns_compiled",
        "get_compound_suffix_patterns_compiled",
        "get_folder_purity_disallowed_compiled",
        "get_folder_purity_patterns_compiled",
        "get_forbidden_compound_patterns_compiled",
    }:
        from agentic_core.L5_safety.config.structure_blueprint import classification

        return getattr(classification, name)
    if name in {
        "AGENT_REGISTRY",
        "APP_DOMAIN_PREFIXES",
        "APP_LIC_AST_TERMS",
        "APP_LIC_STRING_TERMS",
        "APP_LIC_VARIABLE_TERMS",
        "APP_RG_AST_TERMS",
        "APP_RG_STRING_TERMS",
        "APP_RG_VARIABLE_TERMS",
        "AST_DOMAIN_HIT_THRESHOLD",
        "AST_PLACEMENT_SIGNALS",
        "CORE_TERRITORY_KEYWORDS",
        "DEFAULT_APP_HEALING_TARGET",
        "DEFAULT_CORE_HEALING_TERRITORY",
        "EXERCISER_REGISTRY",
        "FORBIDDEN_APP_MODULES",
        "L2_TO_L1_MAP",
        "LAYER_FORBIDDEN_IMPORTS",
        "LAYER_KEYWORD_AFFINITY",
        "LEGACY_AST_SIGNALS",
        "MIN_ALIGNMENT_SCORE",
        "NAMING_CONVENTIONS",
        "PLACEMENT_CONFIDENCE",
        "POLYGLOT_DOMAIN_SIGNALS",
        "SEMANTIC_L2_REGISTRY",
        "STRING_HIT_WEIGHT",
        "TERRITORY_MISMATCH_THRESHOLD",
        "TEST_TYPE_SIGNALS",
        "VARIABLE_HIT_WEIGHT",
        "VIOLATION_SEVERITY",
        "semantic_l2_registry",
    }:
        from agentic_core.L5_safety.config.structure_blueprint import semantics

        return getattr(semantics, name)
    if name in {
        "APP_SPECIFIC_PATTERNS",
        "APP_SPECIFIC_PATTERN_STRINGS",
        "APP_SPECIFIC_PREFIXES",
        "APP_SPECIFIC_TARGET_SUBFOLDER",
        "ARTIFACT_ROUTING_MAP",
        "DATA_SUBFOLDER_METADATA",
        "DOCS_SUBFOLDER_METADATA",
        "EPHEMERAL_PATTERN_EXEMPTIONS",
        "FORBIDDEN_BACKUP_PATTERNS",
        "FORBIDDEN_BACKUP_PATTERN_STRINGS",
        "FORBIDDEN_EPHEMERAL_PATTERNS",
        "FORBIDDEN_FILENAME_PATTERNS",
        "FORBIDDEN_LAYER_PREFIXES",
        "PROJECT_ROOT_METADATA",
        "PROJECT_ROOT_SUBFOLDERS",
        "STUTTERING_PREFIX_MAP",
        "check_forbidden_signals",
        "get_app_specific_patterns_compiled",
        "get_correct_app_folder",
        "get_correct_app_path",
        "get_ephemeral_exemption_patterns_compiled",
        "get_forbidden_backup_patterns_compiled",
        "get_forbidden_ephemeral_patterns_compiled",
        "has_forbidden_layer_prefix",
        "is_app_specific_file",
        "is_broken_backup_file",
        "validate_artifact_routing",
    }:
        from agentic_core.L5_safety.config.structure_blueprint import artifacts

        return getattr(artifacts, name)
    if name in {
        "APPS_LIC_SUBFOLDER_MAP",
        "APPS_RG_SUBFOLDER_MAP",
        "APPS_SHARED_SUBFOLDER_MAP",
        "CORE_SUBFOLDER_MAP",
        "DEPTH_RULES",
        "L4_APPROVED_FOLDERS",
        "L4_SUBFOLDER_MAP",
        "SCRIPTS_PLACEMENT_RULES",
        "SUBFOLDER_METADATA",
        "TESTS_L2_SUBFOLDER_MAP",
        "TESTS_SUBFOLDER_MAP",
        "agentic_core_registry",
        "verify_derived_registries",
    }:
        from agentic_core.L5_safety.config.structure_blueprint import derived

        return getattr(derived, name)
    if name == "SOVEREIGN_TERRITORIES":
        # Wave 3: SOVEREIGN_TERRITORIES now accessed via territories API
        from agentic_core.L5_safety.config.structure_blueprint.territories import get_all_territories

        return get_all_territories()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AGENTIC_CORE_DIR",
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "FORENSIC_DISCOVERY_INTEGRITY_HASH",
    "FORENSIC_DISCOVERY_SCRIPT",
    "AGENT_REGISTRY",
    "AGENT_RESILIENCE_CONFIG",
    "ALLOW_ROOT_PY_TERRITORIES",
    "ALLOWED_DUPLICATE_FILENAMES",
    "APPS_LIC_DIR",
    "APPS_LIC_SUBFOLDER_MAP",
    "APPS_RG_DIR",
    "APPS_RG_SUBFOLDER_MAP",
    "APPS_SHARED_DIR",
    "APPS_SHARED_SUBFOLDER_MAP",
    "APP_DOMAIN_PREFIXES",
    "APP_LIC_AST_TERMS",
    "APP_LIC_STRING_TERMS",
    "APP_LIC_VARIABLE_TERMS",
    "APP_RG_AST_TERMS",
    "APP_RG_STRING_TERMS",
    "APP_RG_VARIABLE_TERMS",
    "APP_SPECIFIC_PATTERNS",
    "APP_SPECIFIC_PATTERN_STRINGS",
    "APP_SPECIFIC_PREFIXES",
    "APP_SPECIFIC_TARGET_SUBFOLDER",
    "ARCHIVES_DIR",
    "ARTIFACT_ROUTING_MAP",
    "AST_DOMAIN_HIT_THRESHOLD",
    "AST_PLACEMENT_SIGNALS",
    "AUTONOMOUS_AGENT_WHITELIST",
    "BLUEPRINT_SOVEREIGN_DIR",
    "CANONICAL_LOCATION_PRIORITY",
    "CLASSIFICATION_SUFFIX_PATTERNS",
    "COMPOUND_SUFFIX_CONFLICTS",
    "CORE_SUBFOLDER_MAP",
    "CORE_TERRITORY_KEYWORDS",
    "COVERAGE_HTML_DIR",
    "DASHBOARD_DIR",
    "DATA_SUBFOLDER_METADATA",
    "DEFAULT_APP_HEALING_TARGET",
    "DEFAULT_CORE_HEALING_TERRITORY",
    "DEPTH_RULES",
    "DISCOVERY_EXCLUDED_TERRITORIES",
    "DOCS_REPORTS_PLANS",
    "DOCS_SUBFOLDER_METADATA",
    "DOMAIN_CONTENT_SIGNALS",
    "DOWNSTREAM_ROOTS",
    "DUPLICATE_DETECTION_EXEMPT",
    "EPHEMERAL_PATTERN_EXEMPTIONS",
    "EXERCISER_REGISTRY",
    "FILETYPE_TO_FOLDER",
    "FLAT_DIRECTORIES",
    "FOLDER_PURITY_DISALLOWED",
    "FOLDER_PURITY_RULES",
    "INFRASTRUCTURE_PROFILES",
    "FOLDER_ALIASES",
    "NO_ROOT_FILES_FOLDERS",
    "APPROVED_SUBFOLDERS",
    "FORBIDDEN_APP_MODULES",
    "FORBIDDEN_BACKUP_PATTERNS",
    "FORBIDDEN_BACKUP_PATTERN_STRINGS",
    "FORBIDDEN_COMPOUND_PATTERNS",
    "FORBIDDEN_EPHEMERAL_PATTERNS",
    "FORBIDDEN_FILENAME_PATTERNS",
    "FORBIDDEN_FOLDER_PATTERN",
    "FORBIDDEN_LAYER_PREFIXES",
    "FORBIDDEN_PATTERNS",
    "FORBIDDEN_ROOT_FOLDERS",
    "GLOBAL_EXCLUDED_DIRS",
    "GLOBAL_INTERFACES_FOLDER",
    "GRAVITY_CONFIG",
    "get_all_territories",
    "get_territory_metadata",
    "GRAVITY_SURGERY_ENABLED",
    "HEALING_CONFIG",
    "INTERFACE_FILENAME_PATTERN",
    "KNOWN_ARCHITECTURAL_SUFFIXES",
    "L0_MAINTENANCE_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L2_TO_L1_MAP",
    "L3_ORCHESTRATION_DIR",
    "L4_STATE_DIR",
    "L5_ENFORCEMENT_ALLOWED_SUFFIXES",
    "L5_SAFETY_DIR",
    "L5_SUBPROCESS_ALLOWLIST",
    "L6_HYBRID_ALLOWLIST",
    "L6_OBSERVABILITY_DIR",
    "LAYER_FORBIDDEN_IMPORTS",
    "LAYER_KEYWORD_AFFINITY",
    "LAYER_PREFIX_PATTERN",
    "LAYER_ROOTS",
    "LEAF_DOMAINS_NO_LCD",
    "LEGACY_AST_SIGNALS",
    "CODE_TERRITORIES",
    "ENFORCED_TERRITORIES",
    "VOLATILE_TERRITORIES",
    "MCP_CAPABILITIES",
    "MIN_ALIGNMENT_SCORE",
    "MISSION_CONFIG",
    "NAMING_CONVENTIONS",
    "NAMING_EXEMPT_DIRS",
    "NAMING_EXEMPT_FILES",
    "NON_PYTHON_FOLDER_ROUTES",
    "OPS_SCRIPTS_DIR",
    "PLACEMENT_CONFIDENCE",
    "POLYGLOT_DOMAIN_SIGNALS",
    "PROJECT_ROOT_MARKERS",
    "PROJECT_ROOT_METADATA",
    "PROJECT_ROOT_SUBFOLDERS",
    "PROJECT_ROOT_WHITELIST",
    "PROMPT_GOVERNANCE_DIR",
    "PYTHON_STDLIB_MODULES",
    "REPORTS_DIR",
    "REQUIRED_LCD_SUBFOLDERS",
    "ROOT_ALLOWED_PATTERNS",
    "ROOT_PROTECTED_FILES",
    "ROOT_WHITELIST",
    "RUNTIME_DIR",
    "RUNTIME_STATE_JSON",
    "SCHEMAS_DIR",
    "SCOPE_SUMMARY_EXCLUSIONS",
    "SCRIPTS_FORBIDDEN_PATTERNS",
    "SEMANTIC_L2_REGISTRY",
    "SERVICE_CLASS_INDICATORS",
    "SOVEREIGN_EXCLUDED_FOLDERS",
    "SOVEREIGN_TERRITORIES",
    "STANDARD_LAYER_STRUCTURE",
    "STRING_HIT_WEIGHT",
    "STUTTERING_PREFIX_MAP",
    "SUBFOLDER_METADATA",
    "SUFFIX_TO_FOLDER",
    "TERRITORY_MISMATCH_THRESHOLD",
    "TEST_CANONICAL_LOCATION_MAP",
    "TEST_MIRROR_BASE",
    "TEST_MIRROR_ROOTS",
    "TESTS_AUTOGEN_DIR",
    "get_canonical_test_path",
    "TESTS_DIR",
    "TESTS_E2E_DIR",
    "TESTS_INTEGRATION_DIR",
    "TESTS_L2_SUBFOLDER_MAP",
    "TESTS_ROOT_FILE_WHITELIST",
    "TESTS_SUBFOLDER_MAP",
    "TESTS_UNIT_DIR",
    "TEST_TYPE_SIGNALS",
    "UPSTREAM_SOVEREIGN_ROOTS",
    "UTILS_DIR",
    "VALIDATED_FILE_EXTENSIONS",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "VARIABLE_HIT_WEIGHT",
    "VIOLATION_SEVERITY",
    "check_forbidden_signals",
    "get_correct_app_folder",
    "get_correct_app_path",
    "get_ephemeral_exemption_patterns_compiled",
    "get_folder_purity_patterns_compiled",
    "get_forbidden_backup_patterns_compiled",
    "get_forbidden_compound_patterns_compiled",
    "get_forbidden_ephemeral_patterns_compiled",
    "get_validated_project_root",
    "has_forbidden_layer_prefix",
    "ignore_dirs",
    "is_allowed_subfolder",
    "is_app_specific_file",
    "is_broken_backup_file",
    "is_l4_approved",
    "is_layer_root",
    "is_path_allowed",
    "protected_folders",
    "safe_path_join",
    "safe_prefixed_filename",
    "semantic_l2_registry",
    "sovereign_ignored_folders",
    "validate_artifact_routing",
    "validate_flat_directory",
    "validate_no_duplicate_prefix",
    "validate_no_nested_lcd",
    "validate_path_within_project",
]
