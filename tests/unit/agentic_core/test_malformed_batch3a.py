#!/usr/bin/env python3
"""
Test Suite: Batch 3A Orphan Moves (L1-L3)

Verifies that Batch 3A agents have integrated their orphans correctly.
Note: Some "orphans" are intentionally module-level (lazy loaders, signal handlers,
convenience functions) and should NOT be moved into classes.
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


def test_batch3a_orphan_moves():
    """Verify Batch 3A agents have integrated their orphans."""
    print("\n" + "=" * 70)
    print("Batch 3A Orphan Moves Tests")
    print("=" * 70)

    # These are the actual orphans that need to be class methods
    targets = [
        (
            "agentic_core/L3_orchestration/fission_logic/SubAtomicAgent.py",
            ["heal_repository"],
            "SubAtomicAgent",
        ),
        (
            "agentic_core/L3_orchestration/workflow_engines/DagExecutorAgent.py",
            ["__init__", "execute"],
            "DagExecutorAgent",
        ),
        (
            "agentic_core/L3_orchestration/workflow_engines/WorkflowOrchestratorAgent.py",
            ["__init__", "execute"],
            "LicWorkflowOrchestratorAgent",
        ),
    ]

    for rel_path, required_methods, class_name in targets:
        full_path = PROJECT_ROOT / rel_path
        agent_name = Path(rel_path).stem

        print(f"\n--- {agent_name} ---")

        if not full_path.exists():
            test_fail(f"{agent_name}", f"File not found: {rel_path}")
            continue

        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # 1. Check for orphans (top-level functions)
        for method in required_methods:
            orphans = [i + 1 for i, l in enumerate(lines) if l.startswith(f"def {method}(")]
            if len(orphans) > 0:
                test_fail(
                    f"{agent_name}-{method}-ORPHAN",
                    f"Top-level '{method}' still exists at lines: {orphans}",
                )
            else:
                test_pass(f"{agent_name}-{method}-ORPHAN", f"No top-level '{method}' found")

        # 2. Syntax validation
        try:
            ast.parse(content)
            test_pass(f"{agent_name}-SYNTAX", "Valid Python syntax")
        except SyntaxError as e:
            test_fail(f"{agent_name}-SYNTAX", f"Syntax error: {e}")
            continue

        # 3. Check class has required methods
        try:
            tree = ast.parse(content)
            class_methods = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_methods.add(item.name)

            for method in required_methods:
                if method in class_methods:
                    test_pass(f"{agent_name}-{method}-METHOD", f"Class has '{method}' method")
                else:
                    test_fail(f"{agent_name}-{method}-METHOD", f"Class missing '{method}' method")
        except Exception as e:
            test_fail(f"{agent_name}-METHODS", f"Error checking methods: {e}")


def main():
    print("\n" + "=" * 70)
    print("BATCH 3A ORPHAN MOVES TEST SUITE")
    print("=" * 70)

    test_batch3a_orphan_moves()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - BATCH 3A COMPLETE")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
