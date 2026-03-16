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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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
