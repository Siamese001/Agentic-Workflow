#!/usr/bin/env python3
"""
Test Suite: Batch 1 Malformed Agents Structural Integrity

Verifies that Batch 1 agents have no top-level heal_repository functions
and that the class methods are properly wired.
"""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


def test_batch1_structural_integrity():
    """Verify Batch 1 agents have no top-level heal_repository."""
    print("\n" + "=" * 70)
    print("Batch 1 Structural Integrity Tests")
    print("=" * 70)

    targets = [
        "agentic_core/L2_execution/ToolRegistry/DeadCodeDetectorAgent.py",
        "agentic_core/L2_execution/ToolRegistry/DriftDetectorAgent.py",
        "agentic_core/L3_orchestration/workflow_engines/CoordinateObservabilityOperationsAgent.py",
        "agentic_core/L5_safety/guardrails/TestCoverageGuardianAgent.py",
        "agentic_core/L5_safety/guardrails/MultiProviderRouterAgent.py",
        "agentic_core/L3_orchestration/workflow_engines/SovereignRagOrchestratorAgent.py",
    ]

    for rel_path in targets:
        full_path = PROJECT_ROOT / rel_path
        agent_name = Path(rel_path).stem

        if not full_path.exists():
            test_fail(f"{agent_name}", f"File not found: {rel_path}")
            continue

        # 1. Static Analysis - check for top-level heal_repository
        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check for top-level definition (def heal_repository at start of line)
        top_level_defs = [i + 1 for i, l in enumerate(lines) if l.startswith("def heal_repository")]

        if len(top_level_defs) > 0:
            test_fail(
                f"{agent_name}-ORPHAN",
                f"Still has top-level heal_repository at lines: {top_level_defs}",
            )
        else:
            test_pass(f"{agent_name}-ORPHAN", "No top-level heal_repository found")

        # 2. Syntax validation
        try:
            ast.parse(content)
            test_pass(f"{agent_name}-SYNTAX", "Valid Python syntax")
        except SyntaxError as e:
            test_fail(f"{agent_name}-SYNTAX", f"Syntax error: {e}")

        # 3. Check class has heal_repository method
        has_class_method = False
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "heal_repository":
                            has_class_method = True
                            break
        except:
            pass

        if has_class_method:
            test_pass(f"{agent_name}-METHOD", "Class has heal_repository method")
        else:
            test_fail(f"{agent_name}-METHOD", "Class missing heal_repository method")


def main():
    print("\n" + "=" * 70)
    print("BATCH 1 MALFORMED AGENTS TEST SUITE")
    print("=" * 70)

    test_batch1_structural_integrity()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - BATCH 1 COMPLETE")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
