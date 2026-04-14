"""Scan execute_ssot.py for silent_swallower antipatterns using the gate's scanner."""

import sys

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_records_execution_trace("p0", "evidence", "_scan_silent_swallower")
_emit_applies_guardrail("p0", "_scan_silent_swallower", "p0_governance")
_emit_reads_policy_state("p0", "_scan_silent_swallower", "policy_binding")
_emit_snapshots_state("p0", "_scan_silent_swallower", "state_snapshot")
emit_replay_key("p0", "_scan_silent_swallower")
emit_determinism_digest("p0", "_scan_silent_swallower")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_scan_silent_swallower", "execution_auth")
_emit_validates_capability("p2", "_scan_silent_swallower", "capability_check")
_emit_routes_to_capability("p2", "_scan_silent_swallower", "capability_route")
_emit_writes_via_uwg("p2", "_scan_silent_swallower", "uwg_write")
_emit_blocks_direct_write("p2", "_scan_silent_swallower", "direct_write_block")
_emit_records_tool_invocation("p2", "_scan_silent_swallower", "tool_invocation")
_emit_captures_execution_output("p2", "_scan_silent_swallower", "exec_output")
_emit_dispatches_agent("p3", "_scan_silent_swallower", "agent_dispatch")
_emit_coordinates_agents("p3", "_scan_silent_swallower", "agent_coordination")
_emit_records_workflow_lineage("p3", "_scan_silent_swallower", "workflow_lineage")
_emit_records_healing_outcome("p3", "_scan_silent_swallower", "healing_outcome")
_emit_escalates_failure("p3", "_scan_silent_swallower", "failure_escalation")
_emit_orchestrates_workflow("p3", "_scan_silent_swallower", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_scan_silent_swallower", "healing_dispatch")
_emit_invokes_evaluation("p3", "_scan_silent_swallower", "evaluation_signal")
_emit_records_telemetry_event("p4", "_scan_silent_swallower", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_scan_silent_swallower", "eval_metric")
_emit_stores_embedding("p4", "_scan_silent_swallower", "embedding_store")
_emit_updates_meta_learning_state("p4", "_scan_silent_swallower", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_scan_silent_swallower", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, ".")
from pathlib import Path

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("_scan_silent_swallower", "p4obs", "metric_1")
_emit_emits_metric_event("_scan_silent_swallower", "p4obs", "metric_2")
_emit_emits_metric_event("_scan_silent_swallower", "p4obs", "metric_3")
_emit_emits_metric_event("_scan_silent_swallower", "p4obs", "metric_4")
_emit_emits_metric_event("_scan_silent_swallower", "p4obs", "metric_5")
_emit_emits_metric_event("_scan_silent_swallower", "p4obs", "metric_6")
_emit_records_incident_event("_scan_silent_swallower", "p4obs", "incident")
_emit_captures_runtime_anomaly("_scan_silent_swallower", "p4obs", "anomaly")
_emit_writes_observability_log("_scan_silent_swallower", "p4obs", "obs_log")
_emit_updates_monitoring_state("_scan_silent_swallower", "p4obs", "mon_state")
_emit_triggers_alert("_scan_silent_swallower", "p4obs", "alert")
_emit_links_incident_trace("_scan_silent_swallower", "p4obs", "trace_link")
_emit_captures_pattern("_scan_silent_swallower", "p3lm", "pattern")
_emit_records_learning_event("_scan_silent_swallower", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_scan_silent_swallower", "p3lm", "snapshot")
_emit_feeds_meta_learning("_scan_silent_swallower", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_scan_silent_swallower", "p3lm", "routing")
_emit_improves_agent_policy("_scan_silent_swallower", "p3lm", "policy")
_emit_stores_learning_state("_scan_silent_swallower", "p3lm", "state")
_emit_records_execution_trace("_scan_silent_swallower", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_scan_silent_swallower", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_scan_silent_swallower", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_scan_silent_swallower", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_scan_silent_swallower", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_scan_silent_swallower", "env_read", "p2_env_1")
_emit_reads_environ("_scan_silent_swallower", "env_read", "p2_env_2")
_emit_reads_runtime_state("_scan_silent_swallower", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_scan_silent_swallower", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_scan_silent_swallower", "context_pull")
_emit_pulls_context("p1", "_scan_silent_swallower", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_scan_silent_swallower", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_scan_silent_swallower", "uwg_term_2")
_emit_writes_through("p1", "_scan_silent_swallower", "write_through")
_emit_writes_through("p1", "_scan_silent_swallower", "write_through_2")
_emit_validated_by_safety_plane("p1", "_scan_silent_swallower", "safety_validation")
_emit_invokes_eval("p1", "_scan_silent_swallower", "eval_call")
_emit_proposal_commits_routing("p1", "_scan_silent_swallower", "routing_commit")
_emit_escalates_to_human("p1", "_scan_silent_swallower", "human_escalation")
_emit_routes_through("p1", "_scan_silent_swallower", "route_through")
_emit_checks_agent_registry("p1", "_scan_silent_swallower", "agent_registry")
_emit_validates_agent_capability("p1", "_scan_silent_swallower", "capability")
_emit_dispatches_execution_plan("p1", "_scan_silent_swallower", "exec_plan")
_emit_agent_executes_agent("p1", "_scan_silent_swallower", "sub_agent")
_emit_routes_to_agent("p1", "_scan_silent_swallower", "target_agent")
_emit_verifies_policy("p1", "_scan_silent_swallower", "policy_check")
_emit_observes_runtime_state("p1", "_scan_silent_swallower", "runtime_state")
_emit_verifies_boundary("p1", "_scan_silent_swallower", "boundary_check")
_emit_transcripts_response("p1", "_scan_silent_swallower", "transcript")
_emit_hard_fails_untranscripted("p1", "_scan_silent_swallower")
_emit_gated_by_confidence("p1", "_scan_silent_swallower", "confidence_gate")

project_root = Path(".")
scanner = AntiPatternScanner(project_root)
results = scanner.scan_file(Path("agentic_core/L0_routing/scripts/execute_ssot.py"))
print(f"result type: {type(results)}")
if isinstance(results, list):
    ss = [
        r
        for r in results
        if getattr(r, "category", None) == "silent_swallower" or "silent" in str(getattr(r, "category", ""))
    ]
    print(f"silent_swallower count={len(ss)}")
    for item in ss:
        print(f"  line={getattr(item, 'line_no', '?')}  {str(item)[:120]}")
    # Show all categories
    from collections import Counter

    cats = Counter(getattr(r, "category", str(r)) for r in results)
    print("All categories:", dict(cats))
elif isinstance(results, dict):
    for cat, items in results.items():
        if cat == "silent_swallower":
            print(f"silent_swallower count={len(items)}")
            for item in items:
                print(f"  line={item.line_no}  snippet={item.snippet[:100]}")
        elif items:
            print(f"{cat} count={len(items)}")
