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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
