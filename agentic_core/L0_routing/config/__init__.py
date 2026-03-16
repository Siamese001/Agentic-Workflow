"""L0 Routing Config Package."""

from agentic_core.L0_routing.config.path_constants import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    DASHBOARD_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    L0_MAINTENANCE_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_APPROVED_FOLDERS,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    LAYER_ROOTS,
    OPS_SCRIPTS_DIR,
    PROJECT_ROOT_MARKERS,
    ROOT_ALLOWED_PATTERNS,
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
    RUNTIME_STATE_JSON,
    SCRIPTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
    TESTS_DIR,
    VARIABLE_DEPTH_SUBFOLDERS,
    get_validated_project_root,
)
from agentic_core.L0_routing.config.structure_blueprint_data import (
    APP_DOMAIN_PREFIXES,
    AST_PLACEMENT_SIGNALS,
    CANONICAL_LOCATION_PRIORITY,
    COMPOUND_SUFFIX_CONFLICTS,
    DUPLICATE_DETECTION_EXEMPT,
    EPHEMERAL_PATTERN_EXEMPTIONS,
    FILETYPE_TO_FOLDER,
    FOLDER_PURITY_RULES,
    FORBIDDEN_EPHEMERAL_PATTERNS,
    FORENSIC_DISCOVERY_INTEGRITY_HASH,
    FORENSIC_DISCOVERY_SCRIPT,
    GLOBAL_INTERFACES_FOLDER,
    INTERFACE_FILENAME_PATTERN,
    L5_SUBPROCESS_ALLOWLIST,
    L6_HYBRID_ALLOWLIST,
    LAYER_KEYWORD_AFFINITY,
    LAYER_PREFIX_PATTERN,
    SCRIPTS_FORBIDDEN_PATTERNS,
    SUFFIX_TO_FOLDER,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L0")
_emit_routes_through("p1", "__init__", "L0")
_emit_escalates_to_human("p1", "__init__", "L0")
_emit_reads_policy_state("p1", "__init__", "L0")

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

__all__ = [
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "AGENTIC_CORE_DIR",
    "APP_DOMAIN_PREFIXES",
    "APPS_LIC_DIR",
    "APPS_RG_DIR",
    "APPS_SHARED_DIR",
    "ARCHIVES_DIR",
    "AST_PLACEMENT_SIGNALS",
    "CANONICAL_LOCATION_PRIORITY",
    "COMPOUND_SUFFIX_CONFLICTS",
    "DASHBOARD_DIR",
    "DISCOVERY_EXCLUDED_TERRITORIES",
    "DUPLICATE_DETECTION_EXEMPT",
    "EPHEMERAL_PATTERN_EXEMPTIONS",
    "FILETYPE_TO_FOLDER",
    "FOLDER_PURITY_RULES",
    "FORBIDDEN_EPHEMERAL_PATTERNS",
    "FORENSIC_DISCOVERY_INTEGRITY_HASH",
    "FORENSIC_DISCOVERY_SCRIPT",
    "GLOBAL_EXCLUDED_DIRS",
    "GLOBAL_INTERFACES_FOLDER",
    "INTERFACE_FILENAME_PATTERN",
    "L0_MAINTENANCE_DIR",
    "L0_ROUTING_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_APPROVED_FOLDERS",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L5_SUBPROCESS_ALLOWLIST",
    "L6_HYBRID_ALLOWLIST",
    "L6_OBSERVABILITY_DIR",
    "LAYER_KEYWORD_AFFINITY",
    "LAYER_PREFIX_PATTERN",
    "LAYER_ROOTS",
    "OPS_SCRIPTS_DIR",
    "PROJECT_ROOT_MARKERS",
    "ROOT_ALLOWED_PATTERNS",
    "ROOT_PROTECTED_FILES",
    "ROOT_WHITELIST",
    "RUNTIME_STATE_JSON",
    "SCRIPTS_DIR",
    "SCRIPTS_FORBIDDEN_PATTERNS",
    "SOVEREIGN_EXCLUDED_FOLDERS",
    "SOVEREIGN_TERRITORIES",
    "SUFFIX_TO_FOLDER",
    "TESTS_DIR",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "get_validated_project_root",
]
