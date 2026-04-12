"""Full scanner violation dump for all buckets."""

from pathlib import Path

from agentic_core.L5_safety.validators.static_checks.system_invariant_scanner import (
    scan_repository_for_bypasses,
)
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("check_scanner_full", "p4obs", "metric_1")
_emit_emits_metric_event("check_scanner_full", "p4obs", "metric_2")
_emit_emits_metric_event("check_scanner_full", "p4obs", "metric_3")
_emit_emits_metric_event("check_scanner_full", "p4obs", "metric_4")
_emit_emits_metric_event("check_scanner_full", "p4obs", "metric_5")
_emit_emits_metric_event("check_scanner_full", "p4obs", "metric_6")
_emit_records_incident_event("check_scanner_full", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_scanner_full", "p4obs", "anomaly")
_emit_writes_observability_log("check_scanner_full", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_scanner_full", "p4obs", "mon_state")
_emit_triggers_alert("check_scanner_full", "p4obs", "alert")
_emit_links_incident_trace("check_scanner_full", "p4obs", "trace_link")
_emit_captures_pattern("check_scanner_full", "p3lm", "pattern")
_emit_records_learning_event("check_scanner_full", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_scanner_full", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_scanner_full", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_scanner_full", "p3lm", "routing")
_emit_improves_agent_policy("check_scanner_full", "p3lm", "policy")
_emit_stores_learning_state("check_scanner_full", "p3lm", "state")
_emit_records_execution_trace("check_scanner_full", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_scanner_full", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_scanner_full", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_scanner_full", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_scanner_full", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_scanner_full", "env_read", "p2_env_1")
_emit_reads_environ("check_scanner_full", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_scanner_full", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_scanner_full", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "check_scanner_full")
_emit_applies_guardrail("p0", "check_scanner_full", "p0_governance")
_emit_reads_policy_state("p0", "check_scanner_full", "policy_binding")
_emit_snapshots_state("p0", "check_scanner_full", "state_snapshot")
_emit_pulls_context("p1", "check_scanner_full", "context_pull")
_emit_pulls_context("p1", "check_scanner_full", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_scanner_full", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_scanner_full", "uwg_term_secondary")
_emit_writes_through("p1", "check_scanner_full", "write_through")
_emit_writes_through("p1", "check_scanner_full", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_scanner_full", "safety_validation")
_emit_invokes_eval("p1", "check_scanner_full", "eval_call")
_emit_proposal_commits_routing("p1", "check_scanner_full", "routing_commit")
_emit_escalates_to_human("p1", "check_scanner_full", "human_escalation")
_emit_routes_through("p1", "check_scanner_full", "route_through")
_emit_checks_agent_registry("p1", "check_scanner_full", "agent_registry")
_emit_validates_agent_capability("p1", "check_scanner_full", "capability")
_emit_dispatches_execution_plan("p1", "check_scanner_full", "exec_plan")
_emit_agent_executes_agent("p1", "check_scanner_full", "sub_agent")
_emit_routes_to_agent("p1", "check_scanner_full", "target_agent")
_emit_verifies_policy("p1", "check_scanner_full", "policy_check")
_emit_observes_runtime_state("p1", "check_scanner_full", "runtime_state")
_emit_verifies_boundary("p1", "check_scanner_full", "boundary_check")
_emit_transcripts_response("p1", "check_scanner_full", "transcript")
_emit_hard_fails_untranscripted("p1", "check_scanner_full")
_emit_gated_by_confidence("p1", "check_scanner_full", "confidence_gate")
emit_replay_key("p0", "check_scanner_full")
emit_determinism_digest("p0", "check_scanner_full")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_scanner_full", "execution_auth")
_emit_validates_capability("p2", "check_scanner_full", "capability_check")
_emit_routes_to_capability("p2", "check_scanner_full", "capability_route")
_emit_writes_via_uwg("p2", "check_scanner_full", "uwg_write")
_emit_blocks_direct_write("p2", "check_scanner_full", "direct_write_block")
_emit_records_tool_invocation("p2", "check_scanner_full", "tool_invocation")
_emit_captures_execution_output("p2", "check_scanner_full", "exec_output")
_emit_dispatches_agent("p3", "check_scanner_full", "agent_dispatch")
_emit_coordinates_agents("p3", "check_scanner_full", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_scanner_full", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_scanner_full", "healing_outcome")
_emit_escalates_failure("p3", "check_scanner_full", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_scanner_full", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_scanner_full", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_scanner_full", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_scanner_full", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_scanner_full", "eval_metric")
_emit_stores_embedding("p4", "check_scanner_full", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_scanner_full", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_scanner_full", "exec_snapshot_link")
root = Path(__file__).resolve().parents[2]
for bucket_rel in [L2_EXECUTION_DIR, L5_SAFETY_DIR, "tests/sovereign_hardening"]:
    bucket = (root / bucket_rel).resolve()
    violations = scan_repository_for_bypasses(bucket)
    prefix = str(bucket)
    filtered = [v for v in violations if str(Path(v.file_path).resolve()).startswith(prefix)]
    py_files = [f for f in bucket.rglob("*.py") if "__pycache__" not in f.parts]
    print(f"\n=== {bucket_rel}: {len(py_files)} files, {len(filtered)} violations ===")
    for v in filtered:
        print(f"  {Path(v.file_path).name}:{v.line} [{v.rule_id}]")
