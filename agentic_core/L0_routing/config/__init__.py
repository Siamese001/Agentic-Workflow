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
    REPORTS_DIR,
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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L0")
_emit_routes_through("p1", "__init__", "L0")
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
_emit_escalates_to_human("p1", "__init__", "L0")
_emit_reads_policy_state("p1", "__init__", "L0")
_emit_pulls_context("p1", "__init__", "context_pull")
_emit_pulls_context("p1", "__init__", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "__init__", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "__init__", "uwg_term_secondary")
_emit_writes_through("p1", "__init__", "write_through")
_emit_writes_through("p1", "__init__", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "__init__", "safety_validation")
_emit_invokes_eval("p1", "__init__", "eval_call")
_emit_proposal_commits_routing("p1", "__init__", "routing_commit")

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
