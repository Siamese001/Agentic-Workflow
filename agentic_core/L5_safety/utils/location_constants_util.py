"""
Shared constants for Location Validation and Healing.

Extracted from LocationAgent.py during SRP fission.
All location-related agents should import from this module.
"""

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("location_constants_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("location_constants_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("location_constants_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("location_constants_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("location_constants_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("location_constants_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("location_constants_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("location_constants_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("location_constants_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("location_constants_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("location_constants_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("location_constants_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("location_constants_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("location_constants_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("location_constants_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("location_constants_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("location_constants_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("location_constants_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("location_constants_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("location_constants_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("location_constants_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("location_constants_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("location_constants_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("location_constants_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("location_constants_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("location_constants_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("location_constants_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("location_constants_util", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "location_constants_util")
trace_contract.emit_determinism_digest("p0", "location_constants_util")

trace_contract._emit_dispatches_healing_run("p1", "location_constants_util", "L5")
trace_contract._emit_routes_through("p1", "location_constants_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "location_constants_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "location_constants_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "location_constants_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "location_constants_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "location_constants_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "location_constants_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "location_constants_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "location_constants_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "location_constants_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "location_constants_util")
trace_contract._emit_gated_by_confidence("p1", "location_constants_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "location_constants_util", "L5")
trace_contract._emit_reads_policy_state("p1", "location_constants_util", "L5")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "location_constants_util")
trace_contract._emit_applies_guardrail("p0", "location_constants_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "location_constants_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "location_constants_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "location_constants_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "location_constants_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "location_constants_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "location_constants_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "location_constants_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "location_constants_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "location_constants_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "location_constants_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "location_constants_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "location_constants_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "location_constants_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "location_constants_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "location_constants_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "location_constants_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "location_constants_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "location_constants_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "location_constants_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "location_constants_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "location_constants_util", "exec_snapshot_link")
trace_contract._emit_pulls_context("p1", "location_constants_util", "context_pull")
trace_contract._emit_pulls_context("p1", "location_constants_util", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "location_constants_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "location_constants_util", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "location_constants_util", "write_through")
trace_contract._emit_writes_through("p1", "location_constants_util", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "location_constants_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "location_constants_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "location_constants_util", "routing_commit")

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
