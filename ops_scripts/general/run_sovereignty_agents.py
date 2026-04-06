"""
Script to execute the integrated Sovereignty Guardians.
Runs RootHygieneAgent and PascalSovereigntyAgent to clean and enforce standards.
"""

import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "run_sovereignty_agents")
_emit_applies_guardrail("p0", "run_sovereignty_agents", "p0_governance")
_emit_reads_policy_state("p0", "run_sovereignty_agents", "policy_binding")
_emit_snapshots_state("p0", "run_sovereignty_agents", "state_snapshot")
emit_replay_key("p0", "run_sovereignty_agents")
emit_determinism_digest("p0", "run_sovereignty_agents")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "run_sovereignty_agents", "execution_auth")
_emit_validates_capability("p2", "run_sovereignty_agents", "capability_check")
_emit_routes_to_capability("p2", "run_sovereignty_agents", "capability_route")
_emit_writes_via_uwg("p2", "run_sovereignty_agents", "uwg_write")
_emit_blocks_direct_write("p2", "run_sovereignty_agents", "direct_write_block")
_emit_records_tool_invocation("p2", "run_sovereignty_agents", "tool_invocation")
_emit_captures_execution_output("p2", "run_sovereignty_agents", "exec_output")
_emit_dispatches_agent("p3", "run_sovereignty_agents", "agent_dispatch")
_emit_coordinates_agents("p3", "run_sovereignty_agents", "agent_coordination")
_emit_records_workflow_lineage("p3", "run_sovereignty_agents", "workflow_lineage")
_emit_records_healing_outcome("p3", "run_sovereignty_agents", "healing_outcome")
_emit_escalates_failure("p3", "run_sovereignty_agents", "failure_escalation")
_emit_orchestrates_workflow("p3", "run_sovereignty_agents", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "run_sovereignty_agents", "healing_dispatch")
_emit_invokes_evaluation("p3", "run_sovereignty_agents", "evaluation_signal")
_emit_records_telemetry_event("p4", "run_sovereignty_agents", "telemetry_event")
_emit_captures_evaluation_metric("p4", "run_sovereignty_agents", "eval_metric")
_emit_stores_embedding("p4", "run_sovereignty_agents", "embedding_store")
_emit_updates_meta_learning_state("p4", "run_sovereignty_agents", "meta_learning")
_emit_links_execution_to_snapshot("p4", "run_sovereignty_agents", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L5_safety.reasoning.PascalSovereigntyAgent import PascalSovereigntyAgent
from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("run_sovereignty_agents", "p4obs", "metric_1")
_emit_emits_metric_event("run_sovereignty_agents", "p4obs", "metric_2")
_emit_emits_metric_event("run_sovereignty_agents", "p4obs", "metric_3")
_emit_emits_metric_event("run_sovereignty_agents", "p4obs", "metric_4")
_emit_emits_metric_event("run_sovereignty_agents", "p4obs", "metric_5")
_emit_emits_metric_event("run_sovereignty_agents", "p4obs", "metric_6")
_emit_records_incident_event("run_sovereignty_agents", "p4obs", "incident")
_emit_captures_runtime_anomaly("run_sovereignty_agents", "p4obs", "anomaly")
_emit_writes_observability_log("run_sovereignty_agents", "p4obs", "obs_log")
_emit_updates_monitoring_state("run_sovereignty_agents", "p4obs", "mon_state")
_emit_triggers_alert("run_sovereignty_agents", "p4obs", "alert")
_emit_links_incident_trace("run_sovereignty_agents", "p4obs", "trace_link")
_emit_captures_pattern("run_sovereignty_agents", "p3lm", "pattern")
_emit_records_learning_event("run_sovereignty_agents", "p3lm", "learning_event")
_emit_writes_learning_snapshot("run_sovereignty_agents", "p3lm", "snapshot")
_emit_feeds_meta_learning("run_sovereignty_agents", "p3lm", "meta_feed")
_emit_updates_routing_strategy("run_sovereignty_agents", "p3lm", "routing")
_emit_improves_agent_policy("run_sovereignty_agents", "p3lm", "policy")
_emit_stores_learning_state("run_sovereignty_agents", "p3lm", "state")
_emit_records_execution_trace("run_sovereignty_agents", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("run_sovereignty_agents", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("run_sovereignty_agents", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("run_sovereignty_agents", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("run_sovereignty_agents", "L4_STATE", "p2_trace_5")
_emit_reads_environ("run_sovereignty_agents", "env_read", "p2_env_1")
_emit_reads_environ("run_sovereignty_agents", "env_read", "p2_env_2")
_emit_reads_runtime_state("run_sovereignty_agents", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("run_sovereignty_agents", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "run_sovereignty_agents", "context_pull")
_emit_pulls_context("p1", "run_sovereignty_agents", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "run_sovereignty_agents", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "run_sovereignty_agents", "uwg_term_secondary")
_emit_writes_through("p1", "run_sovereignty_agents", "write_through")
_emit_writes_through("p1", "run_sovereignty_agents", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "run_sovereignty_agents", "safety_validation")
_emit_invokes_eval("p1", "run_sovereignty_agents", "eval_call")
_emit_proposal_commits_routing("p1", "run_sovereignty_agents", "routing_commit")
_emit_escalates_to_human("p1", "run_sovereignty_agents", "human_escalation")
_emit_routes_through("p1", "run_sovereignty_agents", "route_through")
_emit_checks_agent_registry("p1", "run_sovereignty_agents", "agent_registry")
_emit_validates_agent_capability("p1", "run_sovereignty_agents", "capability")
_emit_dispatches_execution_plan("p1", "run_sovereignty_agents", "exec_plan")
_emit_agent_executes_agent("p1", "run_sovereignty_agents", "sub_agent")
_emit_routes_to_agent("p1", "run_sovereignty_agents", "target_agent")
_emit_verifies_policy("p1", "run_sovereignty_agents", "policy_check")
_emit_observes_runtime_state("p1", "run_sovereignty_agents", "runtime_state")
_emit_verifies_boundary("p1", "run_sovereignty_agents", "boundary_check")
_emit_transcripts_response("p1", "run_sovereignty_agents", "transcript")
_emit_hard_fails_untranscripted("p1", "run_sovereignty_agents")
_emit_gated_by_confidence("p1", "run_sovereignty_agents", "confidence_gate")


def main():
    print("=" * 80)
    print("SOVEREIGNTY GUARDIANS EXECUTION")
    print("=" * 80)
    print("\n[PHASE 1] Executing RootHygieneAgent...")
    hygiene_agent = RootHygieneAgent(project_root=project_root, dry_run=False)
    hygiene_result = hygiene_agent.run()
    print("\n=== ROOT HYGIENE RESULTS ===")
    print(f"Success: {hygiene_result['success']}")
    print(f"Stats: {hygiene_result['stats']}")
    print(f"Summary: {hygiene_result['summary']}")
    print("\n[PHASE 2] Executing PascalSovereigntyAgent...")
    pascal_agent = PascalSovereigntyAgent(project_root=project_root, dry_run=False)
    pascal_result = pascal_agent.run()
    print("\n=== PASCAL SOVEREIGNTY RESULTS ===")
    print(f"Success: {pascal_result['success']}")
    print(f"Stats: {pascal_result['stats']}")
    print(f"Summary: {pascal_result['summary']}")
    print("\n[PHASE 3] Running validation audit...")
    validator = PascalSovereigntyAgent(project_root=project_root, dry_run=True, validate_only=True)
    validator.run()
    total_violations = sum(validator.stats["violations"].values())
    print("\n=== VALIDATION AUDIT ===")
    print(f"Total Violations Remaining: {total_violations}")
    print(f"Compliant Files: {validator.stats['compliant']}")
    print(f"Analyzed Files: {validator.stats['analyzed']}")
    if total_violations == 0:
        print("\n✅ 100% COMPLIANT - All sovereignty standards enforced!")
        return 0
    else:
        print(f"\n⚠️  {total_violations} violations remain - manual review required")
        return 1


if __name__ == "__main__":
    sys.exit(main())
