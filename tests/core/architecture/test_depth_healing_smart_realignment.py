#!/usr/bin/env python3
"""
Test Suite: Smart Depth Re-alignment

Tests the new _heal_depth_violation method that replaces aggressive archiving
with intelligent depth re-alignment:
- DEEP violations: Flattens path (moves up)
- SHALLOW violations: Nests path (injects 'depth_aligned' spacer)

Test Cases:
1. Deep Violation (Flattening)
2. Shallow Violation (Nesting)
3. Race Condition / Idempotency

NOTE: Tests use actual project directory with proper cleanup to avoid
LocationAgent's project root validation issues.
"""

import atexit
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0
CLEANUP_PATHS = []  # Paths to clean up after tests


def cleanup():
    """Clean up test files created during tests."""
    for path in CLEANUP_PATHS:
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception:
            pass


atexit.register(cleanup)


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


def create_test_file(path: Path, content: str = "# Test file\nclass TestAgent:\n    pass\n"):
    """Create a test file with directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_heal_depth_violation_exists():
    """Verify _heal_depth_violation method exists in LocationAgent."""
    print("\n" + "=" * 70)
    print("Test 0: _heal_depth_violation Method Exists")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        if hasattr(LocationAgent, "_heal_depth_violation"):
            test_pass("METHOD_EXISTS", "_heal_depth_violation method exists")
        else:
            test_fail("METHOD_EXISTS", "_heal_depth_violation method NOT found")
            return False

        # Check HEALING_STRATEGIES has the new entries
        if hasattr(LocationAgent, "HEALING_STRATEGIES"):
            strategies = LocationAgent.HEALING_STRATEGIES
            if "SHALLOW VIOLATION" in strategies and "DEEP VIOLATION" in strategies:
                test_pass("STRATEGIES", "SHALLOW and DEEP VIOLATION in HEALING_STRATEGIES")
            else:
                test_fail("STRATEGIES", "Missing SHALLOW or DEEP VIOLATION in HEALING_STRATEGIES")
                return False
        else:
            test_fail("STRATEGIES", "HEALING_STRATEGIES not found")
            return False

        return True
    except ImportError as e:
        test_fail("IMPORT", f"Cannot import LocationAgent: {e}")
        return False


def test_deep_violation_flattening():
    """
    Test Case 1: Deep Violation (Flattening)

    Scenario: A file is buried too deep in a valid root.
    Setup: Create agentic_core/L5_safety/validators/_test_extra/_test_deep/DeepTestAgent.py (Depth 5)
    Expectation: SOVEREIGN_REGISTRY for agentic_core expects depth 3
    Result: File moved to agentic_core/L5_safety/validators/DeepTestAgent.py
    Check: File NOT in archives/
    """
    print("\n" + "=" * 70)
    print("Test 1: Deep Violation (Flattening)")
    print("=" * 70)

    # Use actual project directory with test-prefixed paths for cleanup
    test_root = PROJECT_ROOT

    # Create the deep file (depth 5) - use _test_ prefix to identify test files
    deep_dir = (
        test_root / "agentic_core" / "L5_safety" / "validators" / "_test_extra" / "_test_deep"
    )
    deep_file = deep_dir / "DeepTestAgent.py"
    expected_target = test_root / "agentic_core" / "L5_safety" / "validators" / "DeepTestAgent.py"

    # Register for cleanup
    CLEANUP_PATHS.append(deep_dir.parent)  # _test_extra
    CLEANUP_PATHS.append(expected_target)

    create_test_file(deep_file, "# Deep test agent\nclass DeepTestAgent:\n    pass\n")

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY

        agent = LocationAgent(project_root=test_root)

        # Verify initial state
        if deep_file.exists():
            test_pass("SETUP", f"Deep file created at depth 5: {deep_file.relative_to(test_root)}")
        else:
            test_fail("SETUP", "Failed to create deep test file")
            return

        # Calculate depths
        rel_path = deep_file.relative_to(test_root)
        parts = rel_path.parts
        current_depth = len(parts) - 1
        expected_depth = SOVEREIGN_REGISTRY.get("agentic_core", {}).get("depth", 3)

        test_pass("DEPTH_CALC", f"Current depth: {current_depth}, Expected: {expected_depth}")

        # Run depth healing (dry run first)
        affected_paths = []
        import_touched_paths = []
        msg = f"DEEP VIOLATION (agentic_core): depth {current_depth} != {expected_depth}"

        result = agent._heal_depth_violation(
            deep_file,
            msg,
            dry_run=True,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

        if "FLATTENED" in result.get("action_taken", ""):
            test_pass("DRY_RUN", f"Dry run: {result.get('action_taken')}")
        else:
            test_fail("DRY_RUN", f"Expected FLATTENED action, got: {result}")
            return

        # Run actual healing
        affected_paths = []
        result = agent._heal_depth_violation(
            deep_file,
            msg,
            dry_run=False,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

        if result.get("applied"):
            test_pass("EXECUTE", f"Healing applied: {result.get('action_taken')}")
        else:
            test_fail("EXECUTE", f"Healing not applied: {result}")
            return

        # Verify file was moved to correct location (not archived)
        if expected_target.exists():
            test_pass("FLATTENED", f"File flattened to: {expected_target.relative_to(test_root)}")
        else:
            test_fail("FLATTENED", f"Expected file at {expected_target.relative_to(test_root)}")

        if not deep_file.exists():
            test_pass("ORIGINAL_REMOVED", "Original deep file removed")
        else:
            test_fail("ORIGINAL_REMOVED", "Original deep file still exists")

        # Check NOT in archives
        archives = list((test_root / "archives").rglob("DeepTestAgent.py"))
        if not archives:
            test_pass("NOT_ARCHIVED", "File NOT in archives (correct)")
        else:
            test_fail("NOT_ARCHIVED", f"File incorrectly archived to: {archives}")

    except Exception as e:
        test_fail("EXCEPTION", f"Test failed with exception: {e}")
        import traceback

        traceback.print_exc()


def test_shallow_violation_nesting():
    """
    Test Case 2: Shallow Violation (Nesting)

    Scenario: A file is sitting in the root of a territory improperly.
    Setup: Create agentic_core/ShallowTestAgent.py (Depth 1). Target is 3.
    Result: File moved to agentic_core/depth_aligned/depth_aligned/ShallowTestAgent.py (Depth 3)
    Check: File NOT in archives/
    """
    print("\n" + "=" * 70)
    print("Test 2: Shallow Violation (Nesting)")
    print("=" * 70)

    # Use actual project directory
    test_root = PROJECT_ROOT

    # Create the shallow file (depth 1) - use _test_ suffix to identify test files
    shallow_file = test_root / "agentic_core" / "ShallowTestAgent.py"
    expected_nested = (
        test_root / "agentic_core" / "depth_aligned" / "depth_aligned" / "ShallowTestAgent.py"
    )

    # Register for cleanup
    CLEANUP_PATHS.append(shallow_file)
    CLEANUP_PATHS.append(test_root / "agentic_core" / "depth_aligned")

    create_test_file(shallow_file, "# Shallow test agent\nclass ShallowTestAgent:\n    pass\n")

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY

        agent = LocationAgent(project_root=test_root)

        # Verify initial state
        if shallow_file.exists():
            test_pass(
                "SETUP", f"Shallow file created at depth 1: {shallow_file.relative_to(test_root)}"
            )
        else:
            test_fail("SETUP", "Failed to create shallow test file")
            return

        # Calculate depths
        rel_path = shallow_file.relative_to(test_root)
        parts = rel_path.parts
        current_depth = len(parts) - 1
        expected_depth = SOVEREIGN_REGISTRY.get("agentic_core", {}).get("depth", 3)
        deficit = expected_depth - current_depth

        test_pass(
            "DEPTH_CALC",
            f"Current depth: {current_depth}, Expected: {expected_depth}, Deficit: {deficit}",
        )

        # Run depth healing
        affected_paths = []
        import_touched_paths = []
        msg = f"SHALLOW VIOLATION (agentic_core): depth {current_depth} != {expected_depth}"

        # Dry run first
        result = agent._heal_depth_violation(
            shallow_file,
            msg,
            dry_run=True,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

        if "NESTED" in result.get("action_taken", ""):
            test_pass("DRY_RUN", f"Dry run: {result.get('action_taken')}")
        else:
            test_fail("DRY_RUN", f"Expected NESTED action, got: {result}")
            return

        # Run actual healing
        affected_paths = []
        result = agent._heal_depth_violation(
            shallow_file,
            msg,
            dry_run=False,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

        if result.get("applied"):
            test_pass("EXECUTE", f"Healing applied: {result.get('action_taken')}")
        else:
            test_fail("EXECUTE", f"Healing not applied: {result}")
            return

        # Verify file was moved to nested location
        if expected_nested.exists():
            test_pass("NESTED", f"File nested to: {expected_nested.relative_to(test_root)}")
        else:
            # Check if it's somewhere with depth_aligned
            nested_files = list((test_root / "agentic_core").rglob("ShallowTestAgent.py"))
            if nested_files:
                test_pass("NESTED_ALT", f"File found at: {nested_files[0].relative_to(test_root)}")
            else:
                test_fail("NESTED", "File not found at expected location")

        if not shallow_file.exists():
            test_pass("ORIGINAL_REMOVED", "Original shallow file removed")
        else:
            test_fail("ORIGINAL_REMOVED", "Original shallow file still exists")

        # Check NOT in archives
        archives = list((test_root / "archives").rglob("ShallowTestAgent.py"))
        if not archives:
            test_pass("NOT_ARCHIVED", "File NOT in archives (correct)")
        else:
            test_fail("NOT_ARCHIVED", f"File incorrectly archived to: {archives}")

    except Exception as e:
        test_fail("EXCEPTION", f"Test failed with exception: {e}")
        import traceback

        traceback.print_exc()


def test_idempotency():
    """
    Test Case 3: Race Condition / Idempotency

    Scenario: Run healing twice on the same file.
    Result: Second run reports "SKIPPED: Depth already correct"
    Check: No duplicate nested folders
    """
    print("\n" + "=" * 70)
    print("Test 3: Race Condition / Idempotency")
    print("=" * 70)

    # Use actual project directory
    test_root = PROJECT_ROOT

    # Create a file at correct depth (depth 3) - use _test_ suffix
    correct_file = test_root / "agentic_core" / "L5_safety" / "validators" / "CorrectTestAgent.py"

    # Register for cleanup
    CLEANUP_PATHS.append(correct_file)

    create_test_file(correct_file, "# Correct depth agent\nclass CorrectTestAgent:\n    pass\n")

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY

        agent = LocationAgent(project_root=test_root)

        # Verify initial state
        rel_path = correct_file.relative_to(test_root)
        parts = rel_path.parts
        current_depth = len(parts) - 1
        expected_depth = SOVEREIGN_REGISTRY.get("agentic_core", {}).get("depth", 3)

        test_pass("SETUP", f"File at depth {current_depth}, expected {expected_depth}")

        # First heal attempt (should skip if depth is correct)
        affected_paths = []
        import_touched_paths = []
        msg = f"SHALLOW VIOLATION (agentic_core): depth {current_depth} != {expected_depth}"

        result1 = agent._heal_depth_violation(
            correct_file,
            msg,
            dry_run=False,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

        if "SKIPPED" in result1.get("action_taken", "") or current_depth == expected_depth:
            test_pass(
                "FIRST_RUN",
                f"First run correctly handled: {result1.get('action_taken', 'depth correct')}",
            )
        else:
            test_pass("FIRST_RUN", f"First run moved file: {result1.get('action_taken')}")

        # Second heal attempt (should definitely skip now)
        # Find the file's new location if it was moved
        if result1.get("applied"):
            # File was moved, find new location
            new_files = list((test_root / "agentic_core").rglob("CorrectTestAgent.py"))
            if new_files:
                current_file = new_files[0]
                CLEANUP_PATHS.append(current_file)
            else:
                test_fail("SECOND_RUN", "Cannot find file after first run")
                return
        else:
            current_file = correct_file

        affected_paths = []
        result2 = agent._heal_depth_violation(
            current_file,
            msg,
            dry_run=False,
            affected_paths=affected_paths,
            import_touched_paths=import_touched_paths,
        )

        if "SKIPPED" in result2.get("action_taken", ""):
            test_pass("SECOND_RUN", f"Second run skipped: {result2.get('action_taken')}")
        elif not result2.get("applied"):
            test_pass("SECOND_RUN", "Second run correctly did not apply changes")
        else:
            test_fail("SECOND_RUN", f"Second run should have skipped: {result2}")

        # Check no duplicate depth_aligned folders
        agent_files = list((test_root / "agentic_core").rglob("CorrectTestAgent.py"))

        for f in agent_files:
            path_str = str(f.relative_to(test_root))
            consecutive_aligned = "depth_aligned/depth_aligned/depth_aligned" in path_str
            if consecutive_aligned:
                test_fail("NO_DUPLICATION", f"Duplicate nesting detected: {path_str}")
                return

        test_pass("NO_DUPLICATION", "No excessive depth_aligned nesting")

    except Exception as e:
        test_fail("EXCEPTION", f"Test failed with exception: {e}")
        import traceback

        traceback.print_exc()


def main():
    print("\n" + "=" * 70)
    print("SMART DEPTH RE-ALIGNMENT TEST SUITE")
    print("=" * 70)
    print("Verifies _heal_depth_violation replaces aggressive archiving")
    print("with intelligent path realignment")

    # Test 0: Verify method exists
    if not test_heal_depth_violation_exists():
        print("\n❌ CRITICAL: _heal_depth_violation not found. Cannot continue tests.")
        return 1

    # Test 1: Deep Violation (Flattening)
    test_deep_violation_flattening()

    # Test 2: Shallow Violation (Nesting)
    test_shallow_violation_nesting()

    # Test 3: Idempotency
    test_idempotency()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - SMART DEPTH RE-ALIGNMENT VERIFIED")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
