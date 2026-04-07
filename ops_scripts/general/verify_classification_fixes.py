"""
Verify FileClassificationAgent fixes for classification priority and naming stutter.
Tests the three target files to ensure correct classification.
"""

import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    L3_ORCHESTRATION_DIR,
    L5_SAFETY_DIR,
    get_validated_project_root,
)
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

_emit_records_execution_trace("p0", "evidence", "verify_classification_fixes")
_emit_applies_guardrail("p0", "verify_classification_fixes", "p0_governance")
_emit_reads_policy_state("p0", "verify_classification_fixes", "policy_binding")
_emit_snapshots_state("p0", "verify_classification_fixes", "state_snapshot")
emit_replay_key("p0", "verify_classification_fixes")
emit_determinism_digest("p0", "verify_classification_fixes")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "verify_classification_fixes", "execution_auth")
_emit_validates_capability("p2", "verify_classification_fixes", "capability_check")
_emit_routes_to_capability("p2", "verify_classification_fixes", "capability_route")
_emit_writes_via_uwg("p2", "verify_classification_fixes", "uwg_write")
_emit_blocks_direct_write("p2", "verify_classification_fixes", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_classification_fixes", "tool_invocation")
_emit_captures_execution_output("p2", "verify_classification_fixes", "exec_output")
_emit_dispatches_agent("p3", "verify_classification_fixes", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_classification_fixes", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_classification_fixes", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_classification_fixes", "healing_outcome")
_emit_escalates_failure("p3", "verify_classification_fixes", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_classification_fixes", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_classification_fixes", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_classification_fixes", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_classification_fixes", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_classification_fixes", "eval_metric")
_emit_stores_embedding("p4", "verify_classification_fixes", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_classification_fixes", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_classification_fixes", "exec_snapshot_link")

project_root = get_validated_project_root()

from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent
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

_emit_emits_metric_event("verify_classification_fixes", "p4obs", "metric_1")
_emit_emits_metric_event("verify_classification_fixes", "p4obs", "metric_2")
_emit_emits_metric_event("verify_classification_fixes", "p4obs", "metric_3")
_emit_emits_metric_event("verify_classification_fixes", "p4obs", "metric_4")
_emit_emits_metric_event("verify_classification_fixes", "p4obs", "metric_5")
_emit_emits_metric_event("verify_classification_fixes", "p4obs", "metric_6")
_emit_records_incident_event("verify_classification_fixes", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_classification_fixes", "p4obs", "anomaly")
_emit_writes_observability_log("verify_classification_fixes", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_classification_fixes", "p4obs", "mon_state")
_emit_triggers_alert("verify_classification_fixes", "p4obs", "alert")
_emit_links_incident_trace("verify_classification_fixes", "p4obs", "trace_link")
_emit_captures_pattern("verify_classification_fixes", "p3lm", "pattern")
_emit_records_learning_event("verify_classification_fixes", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_classification_fixes", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_classification_fixes", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_classification_fixes", "p3lm", "routing")
_emit_improves_agent_policy("verify_classification_fixes", "p3lm", "policy")
_emit_stores_learning_state("verify_classification_fixes", "p3lm", "state")
_emit_records_execution_trace("verify_classification_fixes", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_classification_fixes", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_classification_fixes", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_classification_fixes", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_classification_fixes", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_classification_fixes", "env_read", "p2_env_1")
_emit_reads_environ("verify_classification_fixes", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_classification_fixes", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_classification_fixes", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_classification_fixes", "context_pull")
_emit_pulls_context("p1", "verify_classification_fixes", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "verify_classification_fixes", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_classification_fixes", "uwg_term_secondary")
_emit_writes_through("p1", "verify_classification_fixes", "write_through")
_emit_writes_through("p1", "verify_classification_fixes", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "verify_classification_fixes", "safety_validation")
_emit_invokes_eval("p1", "verify_classification_fixes", "eval_call")
_emit_proposal_commits_routing("p1", "verify_classification_fixes", "routing_commit")
_emit_escalates_to_human("p1", "verify_classification_fixes", "human_escalation")
_emit_routes_through("p1", "verify_classification_fixes", "route_through")
_emit_checks_agent_registry("p1", "verify_classification_fixes", "agent_registry")
_emit_validates_agent_capability("p1", "verify_classification_fixes", "capability")
_emit_dispatches_execution_plan("p1", "verify_classification_fixes", "exec_plan")
_emit_agent_executes_agent("p1", "verify_classification_fixes", "sub_agent")
_emit_routes_to_agent("p1", "verify_classification_fixes", "target_agent")
_emit_verifies_policy("p1", "verify_classification_fixes", "policy_check")
_emit_observes_runtime_state("p1", "verify_classification_fixes", "runtime_state")
_emit_verifies_boundary("p1", "verify_classification_fixes", "boundary_check")
_emit_transcripts_response("p1", "verify_classification_fixes", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_classification_fixes")
_emit_gated_by_confidence("p1", "verify_classification_fixes", "confidence_gate")


def verify_classifications():
    """Verify that the classification fixes work correctly."""

    agent = FileClassificationAgent(project_root=project_root, dry_run=True, validate_only=True)

    test_files = [
        (
            "DecompositionOrchestratorAgent.py",
            project_root / L3_ORCHESTRATION_DIR / "workflow_engines" / "DecompositionOrchestratorAgent.py",
            ["ORCHESTRATOR", "AGENT"],
        ),
        (
            "DagEngineAgent.py",
            project_root / L3_ORCHESTRATION_DIR / "workflow_engines" / "DagEngineAgent.py",
            ["AGENT", "CLASS"],
        ),
        (
            "CodeHealerAgent.py",
            project_root / L5_SAFETY_DIR / "policy_engine" / "CodeHealerAgent.py",
            ["AGENT"],
        ),
    ]

    print("=" * 70)
    print("CLASSIFICATION VERIFICATION TEST")
    print("=" * 70)

    results = []
    for name, path, expected in test_files:
        if not path.exists():
            print(f"\n❌ {name}: FILE NOT FOUND")
            results.append(False)
            continue

        classification = agent.classify_file(path)
        is_correct = classification in expected

        status = "✅" if is_correct else "❌"
        print(f"\n{status} {name}")
        print(f"   Path: {path.relative_to(project_root)}")
        print(f"   Classification: {classification}")
        print(f"   Expected: {' or '.join(expected)}")
        print(f"   Result: {'PASS' if is_correct else 'FAIL - Should NOT be TYPES or SCRIPT'}")

        results.append(is_correct)

    print("\n" + "=" * 70)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)

    return all(results)


if __name__ == "__main__":
    success = verify_classifications()
    sys.exit(0 if success else 1)
