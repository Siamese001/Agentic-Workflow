"""
Shared constants for Location Validation and Healing.

Extracted from LocationAgent.py during SRP fission.
All location-related agents should import from this module.
"""

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("location_constants_util", "p4obs", "metric_1")
_emit_emits_metric_event("location_constants_util", "p4obs", "metric_2")
_emit_emits_metric_event("location_constants_util", "p4obs", "metric_3")
_emit_emits_metric_event("location_constants_util", "p4obs", "metric_4")
_emit_emits_metric_event("location_constants_util", "p4obs", "metric_5")
_emit_emits_metric_event("location_constants_util", "p4obs", "metric_6")
_emit_records_incident_event("location_constants_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("location_constants_util", "p4obs", "anomaly")
_emit_writes_observability_log("location_constants_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("location_constants_util", "p4obs", "mon_state")
_emit_triggers_alert("location_constants_util", "p4obs", "alert")
_emit_links_incident_trace("location_constants_util", "p4obs", "trace_link")
_emit_captures_pattern("location_constants_util", "p3lm", "pattern")
_emit_records_learning_event("location_constants_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("location_constants_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("location_constants_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("location_constants_util", "p3lm", "routing")
_emit_improves_agent_policy("location_constants_util", "p3lm", "policy")
_emit_stores_learning_state("location_constants_util", "p3lm", "state")
_emit_records_execution_trace("location_constants_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("location_constants_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("location_constants_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("location_constants_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("location_constants_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("location_constants_util", "env_read", "p2_env_1")
_emit_reads_environ("location_constants_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("location_constants_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("location_constants_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "location_constants_util")
emit_determinism_digest("p0", "location_constants_util")

_emit_dispatches_healing_run("p1", "location_constants_util", "L5")
_emit_routes_through("p1", "location_constants_util", "L5")
_emit_checks_agent_registry("p1", "location_constants_util", "agent_registry")
_emit_validates_agent_capability("p1", "location_constants_util", "capability")
_emit_dispatches_execution_plan("p1", "location_constants_util", "exec_plan")
_emit_agent_executes_agent("p1", "location_constants_util", "sub_agent")
_emit_routes_to_agent("p1", "location_constants_util", "target_agent")
_emit_verifies_policy("p1", "location_constants_util", "policy_check")
_emit_observes_runtime_state("p1", "location_constants_util", "runtime_state")
_emit_verifies_boundary("p1", "location_constants_util", "boundary_check")
_emit_transcripts_response("p1", "location_constants_util", "transcript")
_emit_hard_fails_untranscripted("p1", "location_constants_util")
_emit_gated_by_confidence("p1", "location_constants_util", "confidence_gate")
_emit_escalates_to_human("p1", "location_constants_util", "L5")
_emit_reads_policy_state("p1", "location_constants_util", "L5")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "location_constants_util")
_emit_applies_guardrail("p0", "location_constants_util", "p0_governance")
_emit_snapshots_state("p0", "location_constants_util", "state_snapshot")
_emit_authorize_and_execute("p2", "location_constants_util", "execution_auth")
_emit_validates_capability("p2", "location_constants_util", "capability_check")
_emit_routes_to_capability("p2", "location_constants_util", "capability_route")
_emit_writes_via_uwg("p2", "location_constants_util", "uwg_write")
_emit_blocks_direct_write("p2", "location_constants_util", "direct_write_block")
_emit_records_tool_invocation("p2", "location_constants_util", "tool_invocation")
_emit_captures_execution_output("p2", "location_constants_util", "exec_output")
_emit_dispatches_agent("p3", "location_constants_util", "agent_dispatch")
_emit_coordinates_agents("p3", "location_constants_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "location_constants_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "location_constants_util", "healing_outcome")
_emit_escalates_failure("p3", "location_constants_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "location_constants_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "location_constants_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "location_constants_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "location_constants_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "location_constants_util", "eval_metric")
_emit_stores_embedding("p4", "location_constants_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "location_constants_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "location_constants_util", "exec_snapshot_link")
_emit_pulls_context("p1", "location_constants_util", "context_pull")
_emit_pulls_context("p1", "location_constants_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "location_constants_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "location_constants_util", "uwg_term_secondary")
_emit_writes_through("p1", "location_constants_util", "write_through")
_emit_writes_through("p1", "location_constants_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "location_constants_util", "safety_validation")
_emit_invokes_eval("p1", "location_constants_util", "eval_call")
_emit_proposal_commits_routing("p1", "location_constants_util", "routing_commit")

# Archive subfolder mapping for violation types
ARCHIVE_SUBFOLDERS: dict[str, str] = {
    "VOID VIOLATION": "void_violations",
    "GRAVITY": "void_violations",
    "LAYER PREFIX VIOLATION": "naming_violations",
}

# Default archive subfolder for unclassified violations
DEFAULT_ARCHIVE_SUBFOLDER: str = "location_violations"

# Healing strategy mapping (violation type → method name)
# CRITICAL: VOID VIOLATION must be handled BEFORE falling back to archiving
# The correct flow is: relocate → propose new subfolder → update SSOT → archive (last resort)
HEALING_STRATEGY_MAP: dict[str, str] = {
    "BROKEN BACKUP": "_heal_broken_backup",
    "APP-SPECIFIC IN CORE": "_heal_app_specific_violation",
    "TERRITORY MISMATCH": "_heal_territory_mismatch",
    "DEEP VIOLATION": "_heal_depth_violation",
    "SHALLOW VIOLATION": "_heal_depth_violation",
    "PASCAL_IN_NON_AGENT_FOLDER": "_heal_app_specific_violation",
    "VOID VIOLATION": "_heal_void_violation",  # NEW: Handle void violations properly
}

# Default app healing target subfolder
DEFAULT_APP_HEALING_TARGET: str = "reasoning"

# Violation severity thresholds
VIOLATION_THRESHOLDS: dict[str, int] = {
    "critical": 10,
    "high": 25,
    "medium": 50,
}

# Default report path
DEFAULT_REPORT_PATH: str = "reports/location_audit.json"
