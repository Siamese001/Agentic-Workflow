#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite: L4 Structure Validation

Tests the L4 SSOT definitions in structure_blueprint.py:
1. L4_SUBFOLDER_MAP structure and completeness
2. L4_APPROVED_FOLDERS validation
3. Folder depth validation for L4-approved folders
4. Integration with existing CORE_SUBFOLDER_MAP

Run: python scripts/test_l4_structure_validation.py
"""
import sys
import os
if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from typing import Tuple, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_1_l4_subfolder_map_exists() -> Tuple[bool, str]:
    """Test 1: Verify L4_SUBFOLDER_MAP exists in structure_blueprint."""
    try:
        from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

        if not L4_SUBFOLDER_MAP:
            return False, "L4_SUBFOLDER_MAP is empty"

        return True, f"L4_SUBFOLDER_MAP exists with {len(L4_SUBFOLDER_MAP)} entries"
    except ImportError as e:
        return False, f"Import failed: {e}"


def test_2_l4_approved_folders_exists() -> Tuple[bool, str]:
    """Test 2: Verify L4_APPROVED_FOLDERS exists."""
    try:
        from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

        if not L4_APPROVED_FOLDERS:
            return False, "L4_APPROVED_FOLDERS is empty"

        return True, f"L4_APPROVED_FOLDERS exists with {len(L4_APPROVED_FOLDERS)} entries"
    except ImportError as e:
        return False, f"Import failed: {e}"


def test_3_l4_map_has_required_folders() -> Tuple[bool, str]:
    """Test 3: Verify L4_SUBFOLDER_MAP has all required high-complexity folders."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    required_folders = [
        'dashboards',        # L6_observability/dashboards
        'scripts',           # L0_maintenance/scripts
        'workflow_engines',  # L3_orchestration/workflow_engines
        'thought_engine',    # L1_cognition/thought_engine
        'guardrails',        # L5_safety/guardrails
        'ToolRegistry',      # L2_execution/ToolRegistry
        'core_extensions',   # utils/core_extensions
    ]

    missing = [f for f in required_folders if f not in L4_SUBFOLDER_MAP]

    if missing:
        return False, f"Missing required folders: {missing}"

    return True, f"All {len(required_folders)} required folders present"


def test_4_l4_approved_folders_match_map() -> Tuple[bool, str]:
    """Test 4: Verify L4_APPROVED_FOLDERS matches L4_SUBFOLDER_MAP keys."""
    from agentic_core.L5_safety.validators.structure_blueprint import (
        L4_SUBFOLDER_MAP, L4_APPROVED_FOLDERS
    )

    # Extract folder names from approved paths
    approved_names = set()
    for path in L4_APPROVED_FOLDERS:
        folder_name = path.split('/')[-1]
        approved_names.add(folder_name)

    map_names = set(L4_SUBFOLDER_MAP.keys())

    # Check if all map keys are in approved folders
    missing_in_approved = map_names - approved_names
    if missing_in_approved:
        return False, f"Folders in map but not approved: {missing_in_approved}"

    return True, f"All {len(map_names)} L4 folders are approved"


def test_5_dashboards_has_js_subfolders() -> Tuple[bool, str]:
    """Test 5: Verify dashboards L4 map includes JS subfolders."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    dashboards = L4_SUBFOLDER_MAP.get('dashboards', {})

    if 'js' not in dashboards:
        return False, "dashboards missing 'js' subfolder definition"

    js_subfolders = dashboards['js']
    expected = ['components', 'controllers', 'renderers', 'utils', 'constants']

    missing = [f for f in expected if f not in js_subfolders]
    if missing:
        return False, f"JS missing subfolders: {missing}"

    return True, f"dashboards/js has {len(js_subfolders)} subfolders defined"


def test_6_scripts_has_healing_subfolder() -> Tuple[bool, str]:
    """Test 6: Verify scripts L4 map includes healing subfolder."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    scripts = L4_SUBFOLDER_MAP.get('scripts', {})

    required_subfolders = ['healing', 'validation', 'utilities', 'workflows', 'runtime']
    missing = [f for f in required_subfolders if f not in scripts]

    if missing:
        return False, f"scripts missing subfolders: {missing}"

    return True, f"scripts has {len(scripts)} L4 subfolders defined"


def test_7_workflow_engines_has_dag_subfolder() -> Tuple[bool, str]:
    """Test 7: Verify workflow_engines L4 map includes DAG subfolder."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    workflow_engines = L4_SUBFOLDER_MAP.get('workflow_engines', {})

    required_subfolders = ['core', 'dag', 'rl', 'mission', 'mcp']
    missing = [f for f in required_subfolders if f not in workflow_engines]

    if missing:
        return False, f"workflow_engines missing subfolders: {missing}"

    return True, f"workflow_engines has {len(workflow_engines)} L4 subfolders defined"


def test_8_guardrails_has_security_subfolder() -> Tuple[bool, str]:
    """Test 8: Verify guardrails L4 map includes security subfolder."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    guardrails = L4_SUBFOLDER_MAP.get('guardrails', {})

    required_subfolders = ['security', 'quality', 'structural', 'constitutional', 'detection']
    missing = [f for f in required_subfolders if f not in guardrails]

    if missing:
        return False, f"guardrails missing subfolders: {missing}"

    return True, f"guardrails has {len(guardrails)} L4 subfolders defined"


def test_9_l4_approved_folders_are_valid_paths() -> Tuple[bool, str]:
    """Test 9: Verify L4_APPROVED_FOLDERS contains valid path patterns."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

    invalid_paths = []
    for path in L4_APPROVED_FOLDERS:
        # Should start with agentic_core
        if not path.startswith('agentic_core/'):
            invalid_paths.append(f"{path} (doesn't start with agentic_core/)")
            continue

        # Should have at least 3 parts (agentic_core/layer/folder)
        parts = path.split('/')
        if len(parts) < 3:
            invalid_paths.append(f"{path} (too few path parts)")

    if invalid_paths:
        return False, f"Invalid paths: {invalid_paths}"

    return True, f"All {len(L4_APPROVED_FOLDERS)} paths are valid"


def test_10_l4_folders_exist_on_disk() -> Tuple[bool, str]:
    """Test 10: Verify L4-approved folders actually exist on disk."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

    missing_folders = []
    existing_folders = []

    for folder_path in L4_APPROVED_FOLDERS:
        full_path = project_root / folder_path
        if full_path.exists():
            existing_folders.append(folder_path)
        else:
            missing_folders.append(folder_path)

    if missing_folders:
        return False, f"Missing folders: {missing_folders}"

    return True, f"All {len(existing_folders)} L4 folders exist on disk"


def test_11_l4_map_values_are_dicts() -> Tuple[bool, str]:
    """Test 11: Verify L4_SUBFOLDER_MAP values are dictionaries."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    invalid_entries = []
    for folder, subfolders in L4_SUBFOLDER_MAP.items():
        if not isinstance(subfolders, dict):
            invalid_entries.append(f"{folder}: {type(subfolders)}")

    if invalid_entries:
        return False, f"Invalid value types: {invalid_entries}"

    return True, f"All {len(L4_SUBFOLDER_MAP)} entries have dict values"


def test_12_l4_subfolder_values_are_lists() -> Tuple[bool, str]:
    """Test 12: Verify L4 subfolder values are lists."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    invalid_entries = []
    for folder, subfolders in L4_SUBFOLDER_MAP.items():
        for subfolder, l5_folders in subfolders.items():
            if not isinstance(l5_folders, list):
                invalid_entries.append(f"{folder}/{subfolder}: {type(l5_folders)}")

    if invalid_entries:
        return False, f"Invalid subfolder types: {invalid_entries}"

    return True, "All L4 subfolder values are lists"


def test_13_core_subfolder_map_unchanged() -> Tuple[bool, str]:
    """Test 13: Verify CORE_SUBFOLDER_MAP still works correctly."""
    from agentic_core.L5_safety.validators.structure_blueprint import CORE_SUBFOLDER_MAP

    # Check key layers exist
    required_layers = ['L0_maintenance', 'L1_cognition', 'L2_execution',
                       'L3_orchestration', 'L4_state', 'L5_safety', 'L6_observability']

    missing = [l for l in required_layers if l not in CORE_SUBFOLDER_MAP]

    if missing:
        return False, f"Missing layers in CORE_SUBFOLDER_MAP: {missing}"

    return True, f"CORE_SUBFOLDER_MAP has all {len(required_layers)} layers"


def test_14_l4_folders_have_high_file_count() -> Tuple[bool, str]:
    """Test 14: Verify L4-approved folders actually have high file counts."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

    low_count_folders = []
    high_count_folders = []

    for folder_path in L4_APPROVED_FOLDERS:
        full_path = project_root / folder_path
        if not full_path.exists():
            continue

        # Count Python files
        # Absolute Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    py_files = list(get_python_files(full_path))
        py_count = len([f for f in py_files if '__pycache__' not in str(f)])

        if py_count < 10:
            low_count_folders.append(f"{folder_path}: {py_count} files")
        else:
            high_count_folders.append(f"{folder_path}: {py_count} files")

    # Allow some folders to have low counts (they may be newly organized)
    if len(low_count_folders) > len(high_count_folders):
        return False, f"Too many low-count folders: {low_count_folders}"

    return True, f"{len(high_count_folders)} folders have high file counts"


def test_15_no_duplicate_l4_definitions() -> Tuple[bool, str]:
    """Test 15: Verify no duplicate subfolder definitions in L4_SUBFOLDER_MAP."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    all_subfolders = []
    duplicates = []

    for folder, subfolders in L4_SUBFOLDER_MAP.items():
        for subfolder in subfolders.keys():
            key = f"{folder}/{subfolder}"
            if key in all_subfolders:
                duplicates.append(key)
            all_subfolders.append(key)

    if duplicates:
        return False, f"Duplicate definitions: {duplicates}"

    return True, f"No duplicates in {len(all_subfolders)} subfolder definitions"


def test_16_l4_approved_folders_is_set() -> Tuple[bool, str]:
    """Test 16: Verify L4_APPROVED_FOLDERS is a set (for O(1) lookup)."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

    if not isinstance(L4_APPROVED_FOLDERS, set):
        return False, f"L4_APPROVED_FOLDERS is {type(L4_APPROVED_FOLDERS)}, should be set"

    return True, "L4_APPROVED_FOLDERS is a set for O(1) lookup"


def test_17_thought_engine_has_reasoning_subfolder() -> Tuple[bool, str]:
    """Test 17: Verify thought_engine L4 map includes reasoning subfolder."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    thought_engine = L4_SUBFOLDER_MAP.get('thought_engine', {})

    required_subfolders = ['reasoning', 'planning', 'memory', 'analysis']
    missing = [f for f in required_subfolders if f not in thought_engine]

    if missing:
        return False, f"thought_engine missing subfolders: {missing}"

    return True, f"thought_engine has {len(thought_engine)} L4 subfolders defined"


def test_18_tool_registry_has_core_subfolder() -> Tuple[bool, str]:
    """Test 18: Verify ToolRegistry L4 map includes core subfolder."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    tool_registry = L4_SUBFOLDER_MAP.get('ToolRegistry', {})

    required_subfolders = ['core', 'tools', 'handlers']
    missing = [f for f in required_subfolders if f not in tool_registry]

    if missing:
        return False, f"ToolRegistry missing subfolders: {missing}"

    return True, f"ToolRegistry has {len(tool_registry)} L4 subfolders defined"


# ============================================================================
# HELPER FUNCTION: Check if folder is L4 approved
# ============================================================================

def is_l4_approved(folder_path: str) -> bool:
    """Check if a folder path is approved for L4 depth."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

    # Normalize path
    normalized = folder_path.replace('\\', '/')

    # Check exact match
    if normalized in L4_APPROVED_FOLDERS:
        return True

    # Check if it's a subfolder of an approved folder
    for approved in L4_APPROVED_FOLDERS:
        if normalized.startswith(approved + '/'):
            return True

    return False


def test_19_is_l4_approved_helper_works() -> Tuple[bool, str]:
    """Test 19: Verify is_l4_approved helper function works."""
    # Test approved folder
    if not is_l4_approved('agentic_core/L6_observability/dashboards'):
        return False, "Failed to recognize approved folder"

    # Test subfolder of approved folder
    if not is_l4_approved('agentic_core/L6_observability/dashboards/js'):
        return False, "Failed to recognize subfolder of approved folder"

    # Test non-approved folder
    if is_l4_approved('agentic_core/L6_observability/metrics'):
        return False, "Incorrectly approved non-L4 folder"

    return True, "is_l4_approved helper works correctly"


def test_20_core_extensions_has_mixins_subfolder() -> Tuple[bool, str]:
    """Test 20: Verify core_extensions L4 map includes mixins subfolder."""
    from agentic_core.L5_safety.validators.structure_blueprint import L4_SUBFOLDER_MAP

    core_extensions = L4_SUBFOLDER_MAP.get('core_extensions', {})

    required_subfolders = ['mixins', 'decorators', 'validators', 'helpers']
    missing = [f for f in required_subfolders if f not in core_extensions]

    if missing:
        return False, f"core_extensions missing subfolders: {missing}"

    return True, f"core_extensions has {len(core_extensions)} L4 subfolders defined"


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and return results."""
    tests = [
        ("Test 1: L4_SUBFOLDER_MAP exists", test_1_l4_subfolder_map_exists),
        ("Test 2: L4_APPROVED_FOLDERS exists", test_2_l4_approved_folders_exists),
        ("Test 3: L4 map has required folders", test_3_l4_map_has_required_folders),
        ("Test 4: L4 approved folders match map", test_4_l4_approved_folders_match_map),
        ("Test 5: Dashboards has JS subfolders", test_5_dashboards_has_js_subfolders),
        ("Test 6: Scripts has healing subfolder", test_6_scripts_has_healing_subfolder),
        ("Test 7: Workflow engines has DAG subfolder", test_7_workflow_engines_has_dag_subfolder),
        ("Test 8: Guardrails has security subfolder", test_8_guardrails_has_security_subfolder),
        ("Test 9: L4 approved folders are valid paths", test_9_l4_approved_folders_are_valid_paths),
        ("Test 10: L4 folders exist on disk", test_10_l4_folders_exist_on_disk),
        ("Test 11: L4 map values are dicts", test_11_l4_map_values_are_dicts),
        ("Test 12: L4 subfolder values are lists", test_12_l4_subfolder_values_are_lists),
        ("Test 13: CORE_SUBFOLDER_MAP unchanged", test_13_core_subfolder_map_unchanged),
        ("Test 14: L4 folders have high file count", test_14_l4_folders_have_high_file_count),
        ("Test 15: No duplicate L4 definitions", test_15_no_duplicate_l4_definitions),
        ("Test 16: L4_APPROVED_FOLDERS is set", test_16_l4_approved_folders_is_set),
        ("Test 17: Thought engine has reasoning subfolder", test_17_thought_engine_has_reasoning_subfolder),
        ("Test 18: ToolRegistry has core subfolder", test_18_tool_registry_has_core_subfolder),
        ("Test 19: is_l4_approved helper works", test_19_is_l4_approved_helper_works),
        ("Test 20: Core extensions has mixins subfolder", test_20_core_extensions_has_mixins_subfolder),
    ]

    results = {
        "passed": 0,
        "failed": 0,
        "total": len(tests),
        "details": [],
    }

    print("\n" + "=" * 70)
    print("L4 STRUCTURE VALIDATION TEST SUITE")
    print("Testing L4 SSOT definitions in structure_blueprint.py")
    print("=" * 70)

    for name, test_func in tests:
        try:
            passed, message = test_func()
            icon = "✅" if passed else "❌"

            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "name": name,
                "passed": passed,
                "message": message,
            })

            print(f"\n{icon} {name}")
            print(f"   {message}")

        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "name": name,
                "passed": False,
                "message": f"ERROR: {e}",
            })
            print(f"\n❌ {name}")
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {results['passed']}/{results['total']} PASSED")
    print("=" * 70)

    if results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in results["details"]:
            if not detail["passed"]:
                print(f"   - {detail['name']}: {detail['message']}")

    return results


if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if results["failed"] == 0 else 1)
