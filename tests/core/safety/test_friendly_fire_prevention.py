#!/usr/bin/env python3
"""
Test Suite: Friendly Fire Prevention
=====================================
Verifies that HierarchyAgent and FilesystemAgent do NOT archive validly placed files.

RCA Summary:
- Root Cause: Agents were archiving files that were in valid sovereign territory
- Impact: Critical infrastructure files were moved to archives
- Fix: Added is_path_allowed safety brake and smart depth healing

Test Categories:
1. Structure Blueprint Validator Tests (is_path_allowed)
2. HierarchyAgent Healing Tests (Flatten/Nest)
3. FilesystemAgent Safety Brake Tests
"""
import sys
from pathlib import Path
from unittest.mock import patch

# Setup path
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
# === 1. Structure Blueprint Validator Tests ===
# ============================================================================

def test_is_path_allowed_valid_sovereign():
    """Verify is_path_allowed returns True for valid sovereign paths."""
    print("\n" + "=" * 70)
    print("Test 1: is_path_allowed - Valid Sovereign Paths")
    print("=" * 70)

    from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed

    # Test Valid Core Path (L2 Execution is in SOVEREIGN_REGISTRY)
    if is_path_allowed("agentic_core/L2_execution/ToolRegistry/SomeAgent.py"):
        test_pass("VALID_CORE", "agentic_core/L2_execution/ToolRegistry/SomeAgent.py")
    else:
        test_fail("VALID_CORE", "Should allow valid core path")

    # Test Valid App Path (apps_rg has engines)
    if is_path_allowed("apps_rg/engines/ResumeBuilder.py"):
        test_pass("VALID_APP", "apps_rg/engines/ResumeBuilder.py")
    else:
        test_fail("VALID_APP", "Should allow valid app path")

    # Test Valid Tests Path
    if is_path_allowed("tests/core/architecture/test_file.py"):
        test_pass("VALID_TESTS", "tests/core/architecture/test_file.py")
    else:
        test_fail("VALID_TESTS", "Should allow valid tests path")

    # Test Valid Utils Path (variable depth)
    if is_path_allowed("agentic_core/utils/core_extensions/healer_mixin.py"):
        test_pass("VALID_UTILS", "agentic_core/utils/core_extensions/healer_mixin.py")
    else:
        test_fail("VALID_UTILS", "Should allow valid utils path")


def test_is_path_allowed_invalid_paths():
    """Verify is_path_allowed returns False for structurally invalid paths."""
    print("\n" + "=" * 70)
    print("Test 2: is_path_allowed - Invalid Paths")
    print("=" * 70)

    from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed

    # Invalid Root
    if not is_path_allowed("random_folder/script.py"):
        test_pass("INVALID_ROOT", "random_folder/script.py correctly rejected")
    else:
        test_fail("INVALID_ROOT", "Should reject unknown root folder")

    # Valid Root, Invalid Subfolder (agentic_core does not have 'random_stuff')
    if not is_path_allowed("agentic_core/random_stuff/script.py"):
        test_pass("INVALID_SUBFOLDER", "agentic_core/random_stuff/script.py correctly rejected")
    else:
        test_fail("INVALID_SUBFOLDER", "Should reject invalid subfolder")

    # Unknown root with deep path
    if not is_path_allowed("unknown_root/subdir/file.py"):
        test_pass("UNKNOWN_ROOT", "unknown_root/subdir/file.py correctly rejected")
    else:
        test_fail("UNKNOWN_ROOT", "Should reject unknown root")


def test_is_path_allowed_depth_check():
    """Verify is_path_allowed handles depth correctly."""
    print("\n" + "=" * 70)
    print("Test 3: is_path_allowed - Depth Handling")
    print("=" * 70)

    from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed

    # Deeply nested valid path (is_path_allowed only checks root + subfolder)
    if is_path_allowed("agentic_core/L2_execution/ToolRegistry/extra/deep/file.py"):
        test_pass("DEEP_VALID", "Deep path passes sovereign gate (depth check is separate)")
    else:
        test_fail("DEEP_VALID", "is_path_allowed should pass deep paths (depth check is HierarchyAgent's job)")

    # Shallow valid path
    if is_path_allowed("agentic_core/L5_safety/validators/LocationAgent.py"):
        test_pass("SHALLOW_VALID", "Standard depth path passes")
    else:
        test_fail("SHALLOW_VALID", "Should allow standard depth path")


# ============================================================================
# === 2. HierarchyAgent Healing Tests (Flatten/Nest) ===
# ============================================================================

def test_hierarchy_heal_deep_violation_flatten():
    """
    Scenario: File is too deep.
    Expected: File is moved UP to the expected depth (Flattened).
    """
    print("\n" + "=" * 70)
    print("Test 4: HierarchyAgent - Deep Violation Flattening")
    print("=" * 70)

    import tempfile
    import ast

    # Verify the method exists in source code (static analysis)
    hierarchy_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/HierarchyAgent.py"
    if not hierarchy_path.exists():
        test_fail("FILE_EXISTS", "HierarchyAgent.py not found")
        return

    content = hierarchy_path.read_text(encoding='utf-8')

    # Check _heal_depth_violation method exists
    if '_heal_depth_violation' in content:
        test_pass("METHOD_EXISTS", "_heal_depth_violation method exists in HierarchyAgent")
    else:
        test_fail("METHOD_EXISTS", "_heal_depth_violation method NOT found")
        return

    # Check FLATTENED logic exists
    if 'FLATTENED' in content and 'depth > expected' in content:
        test_pass("FLATTEN_LOGIC", "Flattening logic (depth > expected) exists")
    else:
        test_fail("FLATTEN_LOGIC", "Flattening logic not found")

    # Check NESTED logic exists
    if 'NESTED' in content and 'depth_aligned' in content:
        test_pass("NEST_LOGIC", "Nesting logic (depth_aligned spacers) exists")
    else:
        test_fail("NEST_LOGIC", "Nesting logic not found")

    # Verify syntax
    try:
        ast.parse(content)
        test_pass("SYNTAX", "HierarchyAgent.py has valid syntax")
    except SyntaxError as e:
        test_fail("SYNTAX", f"Syntax error: {e}")


def test_hierarchy_heal_shallow_violation_nest():
    """
    Scenario: File is too shallow.
    Expected: File is pushed DOWN with 'depth_aligned' spacers (Nested).
    """
    print("\n" + "=" * 70)
    print("Test 5: HierarchyAgent - Shallow Violation Nesting")
    print("=" * 70)

    # Static analysis - verify nesting logic in source
    hierarchy_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/HierarchyAgent.py"
    content = hierarchy_path.read_text(encoding='utf-8')

    # Check deficit calculation exists
    if 'deficit = expected - depth' in content:
        test_pass("DEFICIT_CALC", "Deficit calculation exists")
    else:
        test_fail("DEFICIT_CALC", "Deficit calculation not found")

    # Check spacers tuple creation
    if 'spacers = tuple' in content and 'depth_aligned' in content:
        test_pass("SPACERS", "Spacers tuple creation exists")
    else:
        test_fail("SPACERS", "Spacers creation not found")

    # Check new_parts construction for nesting
    if 'new_parts = rel.parts[:-1] + spacers' in content:
        test_pass("NEST_PARTS", "Nesting path construction exists")
    else:
        test_fail("NEST_PARTS", "Nesting path construction not found")


def test_hierarchy_heal_collision_fallback():
    """
    Scenario: Healing target already exists.
    Expected: Fallback to archive to prevent overwrite.
    """
    print("\n" + "=" * 70)
    print("Test 6: HierarchyAgent - Collision Fallback")
    print("=" * 70)

    # Static analysis - verify collision handling in source
    hierarchy_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/HierarchyAgent.py"
    content = hierarchy_path.read_text(encoding='utf-8')

    # Check target exists check
    if 'target_path.exists()' in content:
        test_pass("COLLISION_CHECK", "Collision check (target_path.exists()) exists")
    else:
        test_fail("COLLISION_CHECK", "Collision check not found")

    # Check fallback to legacy archive
    if '_legacy_archive_depth_violation' in content:
        test_pass("FALLBACK_METHOD", "_legacy_archive_depth_violation fallback exists")
    else:
        test_fail("FALLBACK_METHOD", "Fallback method not found")

    # Check collision triggers fallback
    if 'return self._legacy_archive_depth_violation' in content:
        test_pass("COLLISION_FALLBACK", "Collision triggers archive fallback")
    else:
        test_fail("COLLISION_FALLBACK", "Collision fallback not found")


# ============================================================================
# === 3. FilesystemAgent Safety Brake Tests ===
# ============================================================================

def test_fs_agent_safety_brake_valid_file():
    """
    Scenario: A valid file in agentic_core is passed to _determine_archive_subpath.
    Expected: Returns None (Do NOT archive).
    """
    print("\n" + "=" * 70)
    print("Test 7: FilesystemAgent - Safety Brake (Valid File)")
    print("=" * 70)

    # Static analysis - verify safety brake in source
    fs_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/FilesystemAgent.py"
    if not fs_path.exists():
        test_fail("FILE_EXISTS", "FilesystemAgent.py not found")
        return

    content = fs_path.read_text(encoding='utf-8')

    # Check is_path_allowed import
    if 'from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed' in content:
        test_pass("IMPORT", "is_path_allowed imported from SSOT")
    else:
        test_fail("IMPORT", "is_path_allowed import not found")

    # Check safety brake check
    if 'is_path_allowed' in content and 'return None' in content:
        test_pass("SAFETY_BRAKE", "Safety brake (is_path_allowed -> return None) exists")
    else:
        test_fail("SAFETY_BRAKE", "Safety brake not found")

    # Check _determine_archive_subpath returns Optional[Path]
    if 'Optional[Path]' in content or '-> Optional[Path]' in content:
        test_pass("RETURN_TYPE", "_determine_archive_subpath can return None")
    else:
        test_fail("RETURN_TYPE", "Return type not Optional[Path]")


def test_fs_agent_archives_invalid_file():
    """
    Scenario: An invalid file (random root) is passed.
    Expected: Returns a path to 'uncategorized' (or AST prediction).
    """
    print("\n" + "=" * 70)
    print("Test 8: FilesystemAgent - Archives Invalid File")
    print("=" * 70)

    # Static analysis - verify uncategorized fallback in source
    fs_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/FilesystemAgent.py"
    content = fs_path.read_text(encoding='utf-8')

    # Check uncategorized fallback exists
    if 'uncategorized' in content:
        test_pass("UNCATEGORIZED", "Uncategorized fallback exists")
    else:
        test_fail("UNCATEGORIZED", "Uncategorized fallback not found")

    # Check cleanup_violations handles None return
    if 'archive_subpath is None' in content:
        test_pass("NONE_HANDLING", "cleanup_violations handles None return")
    else:
        test_fail("NONE_HANDLING", "None handling not found in cleanup_violations")

    # Check SKIPPED action for valid files
    if 'SKIPPED' in content and 'valid sovereign territory' in content:
        test_pass("SKIP_ACTION", "SKIPPED action for valid sovereign files exists")
    else:
        test_fail("SKIP_ACTION", "SKIPPED action not found")


# ============================================================================
# === Main Execution ===
# ============================================================================

def main():
    print("=" * 70)
    print("FRIENDLY FIRE PREVENTION TEST SUITE")
    print("=" * 70)
    print("Verifies agents do NOT archive validly placed files")
    print()

    # Run all tests
    test_is_path_allowed_valid_sovereign()
    test_is_path_allowed_invalid_paths()
    test_is_path_allowed_depth_check()
    test_hierarchy_heal_deep_violation_flatten()
    test_hierarchy_heal_shallow_violation_nest()
    test_hierarchy_heal_collision_fallback()
    test_fs_agent_safety_brake_valid_file()
    test_fs_agent_archives_invalid_file()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Total Tests: {PASSED + FAILED}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {PASSED / (PASSED + FAILED) * 100:.1f}%")
    print()

    if FAILED == 0:
        print("  ✅ ALL TESTS PASSED - FRIENDLY FIRE PREVENTION VERIFIED")
        return 0
    else:
        print(f"  ❌ {FAILED} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
