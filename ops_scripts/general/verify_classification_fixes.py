"""
Verify FileClassificationAgent fixes for classification priority and naming stutter.
Tests the three target files to ensure correct classification.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.core.FileClassificationAgent import FileClassificationAgent


def verify_classifications():
    """Verify that the classification fixes work correctly."""

    agent = FileClassificationAgent(project_root=project_root, dry_run=True, validate_only=True)

    test_files = [
        (
            "DecompositionOrchestratorAgent.py",
            project_root
            / "agentic_core"
            / "L3_orchestration"
            / "workflow_engines"
            / "DecompositionOrchestratorAgent.py",
            ["ORCHESTRATOR", "AGENT"],
        ),
        (
            "DagEngineAgent.py",
            project_root / "agentic_core" / "L3_orchestration" / "workflow_engines" / "DagEngineAgent.py",
            ["AGENT", "CLASS"],
        ),
        (
            "CodeHealerAgent.py",
            project_root / "agentic_core" / "L5_safety" / "policy_engine" / "CodeHealerAgent.py",
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
