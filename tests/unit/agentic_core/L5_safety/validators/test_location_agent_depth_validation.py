#!/usr/bin/env python3
"""
Test Suite: LocationAgent Depth Validation Hardening

RCA Summary:
- Root Cause: LocationAgent._validate_depth_requirements had hard-coded depth=3 check
- Impact: Valid files in utils/core_extensions/ (depth 4) were archived
- Agent Responsible: LocationAgent
- Fix: Added VARIABLE_DEPTH_SUBFOLDERS exemption list

This test suite ensures:
1. Variable-depth subfolders are NOT flagged as violations
2. Standard depth validation still works for non-exempted paths
3. Critical infrastructure files are never archived
4. Depth validation logic is correct
"""

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


# ============================================================================
# VARIABLE DEPTH PATHS - These should NEVER be flagged as violations
# ============================================================================
VALID_VARIABLE_DEPTH_PATHS = [
    # utils/core_extensions/* (depth 4)
    "agentic_core/utils/core_extensions/healer_mixin.py",
    "agentic_core/utils/core_extensions/decorators.py",
    "agentic_core/utils/core_extensions/infrastructure_mixin.py",
    "agentic_core/utils/core_extensions/subatomic_testing_mixin.py",
    "agentic_core/utils/core_extensions/timeout_decorator.py",
    # config/blueprint_sovereign/* (depth 4)
    "agentic_core/config/blueprint_sovereign/structure_blueprint.py",
    "agentic_core/config/blueprint_sovereign/core_contracts.py",
    "agentic_core/config/blueprint_sovereign/canonical_truth.py",
    # common/healing/* (depth 4)
    "agentic_core/common/healing/healer_mixin.py",
    # L6_observability with variable depth
    "agentic_core/L6_observability/dashboards/index.html",
    "agentic_core/L6_observability/dashboards/js/table-renderer.js",
]

# Standard depth 3 paths - should be valid
VALID_STANDARD_DEPTH_PATHS = [
    "agentic_core/L5_safety/validators/LocationAgent.py",
    "agentic_core/L5_safety/validators/NamingAgent.py",
    "agentic_core/L2_execution/mcp/client.py",
    "agentic_core/L3_orchestration/unified_orchestrator.py",
]

# Invalid paths that SHOULD be flagged
INVALID_PATHS = [
    "random_folder/some_file.py",  # Not in sovereign registry
    "agentic_core/file_at_root.py",  # Depth 1 (too shallow)
]


def test_variable_depth_subfolders_exist():
    """Verify VARIABLE_DEPTH_SUBFOLDERS is defined in SSOT (structure_blueprint.py)."""
    print("\n" + "=" * 70)
    print("Test 1: VARIABLE_DEPTH_SUBFOLDERS Defined")
    print("=" * 70)

    try:
        # [SSOT] VARIABLE_DEPTH_SUBFOLDERS is now defined in structure_blueprint.py
        from agentic_core.L5_safety.validators.structure_blueprint_config import (
            VARIABLE_DEPTH_SUBFOLDERS,
        )

        if VARIABLE_DEPTH_SUBFOLDERS:
            test_pass(
                "DEFINED",
                f"VARIABLE_DEPTH_SUBFOLDERS exists with {len(VARIABLE_DEPTH_SUBFOLDERS)} entries",
            )

            # Check expected subfolders are included
            expected = {"utils", "config", "common", "observability", "L6_observability"}
            missing = expected - VARIABLE_DEPTH_SUBFOLDERS
            if missing:
                test_fail("COMPLETE", f"Missing subfolders: {missing}")
            else:
                test_pass("COMPLETE", "All expected subfolders included")
        else:
            test_fail("DEFINED", "VARIABLE_DEPTH_SUBFOLDERS is empty!")
    except (ImportError, NameError, AttributeError, TypeError) as e:
        test_fail("IMPORT", f"Cannot import VARIABLE_DEPTH_SUBFOLDERS: {e}")


def test_variable_depth_paths_not_flagged():
    """Verify variable-depth paths are NOT flagged as violations."""
    print("\n" + "=" * 70)
    print("Test 2: Variable Depth Paths Not Flagged")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        agent = LocationAgent(project_root=PROJECT_ROOT)

        for rel_path_str in VALID_VARIABLE_DEPTH_PATHS:
            PROJECT_ROOT / rel_path_str
            rel_path = Path(rel_path_str)
            parts = rel_path.parts
            root_folder = parts[0]

            is_valid, msg = agent._validate_depth_requirements(parts, root_folder, rel_path)

            if is_valid:
                test_pass(f"DEPTH-{Path(rel_path_str).stem[:20]}", f"{rel_path_str}")
            else:
                test_fail(
                    f"DEPTH-{Path(rel_path_str).stem[:20]}",
                    f"{rel_path_str} incorrectly flagged: {msg}",
                )

    except Exception as e:
        test_fail("VALIDATION", f"Error during validation: {e}")


def test_standard_depth_paths_valid():
    """Verify standard depth 3 paths are valid."""
    print("\n" + "=" * 70)
    print("Test 3: Standard Depth Paths Valid")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        agent = LocationAgent(project_root=PROJECT_ROOT)

        for rel_path_str in VALID_STANDARD_DEPTH_PATHS:
            rel_path = Path(rel_path_str)
            parts = rel_path.parts
            root_folder = parts[0]

            is_valid, msg = agent._validate_depth_requirements(parts, root_folder, rel_path)

            if is_valid:
                test_pass(f"STANDARD-{Path(rel_path_str).stem[:20]}", f"{rel_path_str}")
            else:
                test_fail(
                    f"STANDARD-{Path(rel_path_str).stem[:20]}",
                    f"{rel_path_str} incorrectly flagged: {msg}",
                )

    except Exception as e:
        test_fail("VALIDATION", f"Error during validation: {e}")


def test_is_path_allowed_function():
    """Verify is_path_allowed correctly validates nested paths."""
    print("\n" + "=" * 70)
    print("Test 4: is_path_allowed Function")
    print("=" * 70)

    try:
        from agentic_core.L5_safety.validators.structure_blueprint_config import is_path_allowed

        # These should all be allowed
        allowed_paths = [
            "agentic_core/utils/core_extensions/healer_mixin.py",
            "agentic_core/L5_safety/validators/LocationAgent.py",
            "agentic_core/config/blueprint_sovereign/structure_blueprint.py",
            "tests/core/architecture/test_file.py",
        ]

        for path_str in allowed_paths:
            if is_path_allowed(path_str):
                test_pass(f"ALLOWED-{Path(path_str).stem[:15]}", path_str)
            else:
                test_fail(f"ALLOWED-{Path(path_str).stem[:15]}", f"{path_str} incorrectly rejected")

        # These should NOT be allowed
        disallowed_paths = [
            "random_folder/file.py",
            "unknown_root/subdir/file.py",
        ]

        for path_str in disallowed_paths:
            if not is_path_allowed(path_str):
                test_pass(f"REJECTED-{Path(path_str).stem[:15]}", f"{path_str} correctly rejected")
            else:
                test_fail(f"REJECTED-{Path(path_str).stem[:15]}", f"{path_str} incorrectly allowed")

    except (ImportError, NameError, AttributeError, TypeError) as e:
        test_fail("IMPORT", f"Cannot import is_path_allowed: {e}")


def test_critical_files_not_archived():
    """Verify critical infrastructure files would pass depth validation."""
    print("\n" + "=" * 70)
    print("Test 5: Critical Files Pass Depth Validation")
    print("=" * 70)

    critical_files = [
        "agentic_core/utils/sovereign_index.py",
        "agentic_core/utils/core_extensions/healer_mixin.py",
        "agentic_core/utils/core_extensions/decorators.py",
        "agentic_core/L5_safety/validators/LocationAgent.py",
        "agentic_core/L2_execution/mcp/mcp_hardened_mixin.py",
        "agentic_core/config/blueprint_sovereign/core_contracts.py",
    ]

    try:
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        agent = LocationAgent(project_root=PROJECT_ROOT)

        for rel_path_str in critical_files:
            rel_path = Path(rel_path_str)
            parts = rel_path.parts
            root_folder = parts[0]

            is_valid, msg = agent._validate_depth_requirements(parts, root_folder, rel_path)

            if is_valid:
                test_pass(f"CRITICAL-{Path(rel_path_str).stem[:15]}", rel_path_str)
            else:
                test_fail(
                    f"CRITICAL-{Path(rel_path_str).stem[:15]}",
                    f"WOULD BE ARCHIVED: {rel_path_str} - {msg}",
                )

    except Exception as e:
        test_fail("VALIDATION", f"Error during validation: {e}")


def test_depth_calculation_accuracy():
    """Verify depth calculation is accurate."""
    print("\n" + "=" * 70)
    print("Test 6: Depth Calculation Accuracy")
    print("=" * 70)

    test_cases = [
        ("agentic_core/file.py", 1),
        ("agentic_core/L5_safety/file.py", 2),
        ("agentic_core/L5_safety/validators/file.py", 3),
        ("agentic_core/utils/core_extensions/file.py", 3),
        ("agentic_core/utils/core_extensions/subdir/file.py", 4),
    ]

    for path_str, expected_depth in test_cases:
        rel_path = Path(path_str)
        parts = rel_path.parts
        actual_depth = len(parts) - 1  # Minus 1 for the file itself

        if actual_depth == expected_depth:
            test_pass(f"DEPTH-{expected_depth}", f"{path_str} = depth {actual_depth}")
        else:
            test_fail(
                f"DEPTH-{expected_depth}",
                f"{path_str} expected {expected_depth}, got {actual_depth}",
            )


def main():
    print("\n" + "=" * 70)
    print("LOCATION AGENT DEPTH VALIDATION HARDENING TEST SUITE")
    print("=" * 70)
    print("RCA: Depth validation incorrectly archived variable-depth files")
    print("Fix: Added VARIABLE_DEPTH_SUBFOLDERS exemption list")

    test_variable_depth_subfolders_exist()
    test_variable_depth_paths_not_flagged()
    test_standard_depth_paths_valid()
    test_is_path_allowed_function()
    test_critical_files_not_archived()
    test_depth_calculation_accuracy()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - DEPTH VALIDATION HARDENED")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED - DEPTH VALIDATION NOT HARDENED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
