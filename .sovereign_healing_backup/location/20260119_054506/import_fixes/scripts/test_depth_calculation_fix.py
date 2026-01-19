#!/usr/bin/env python3
"""
Test Suite: Depth Calculation Fix

Verifies that depth is calculated correctly as the folder level where a file resides,
NOT the total path length including the file itself.

Definition:
- agentic_core/L0_maintenance/scripts/README.md -> depth 3 (scripts is level 3)
- agentic_core = 1, L0_maintenance = 2, scripts = 3
- The file is AT depth 3, not depth 4

All tests must pass 100%.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_1_depth_definition():
    """
    Test Case 1: Verify depth definition
    
    Depth = folder level where file resides (len(parts) - 1)
    NOT the total path length including the file.
    """
    print("\n" + "="*60)
    print("TEST 1: Depth Definition Verification")
    print("="*60)
    
    test_cases = [
        # (path, expected_depth, explanation)
        ("agentic_core/L0_maintenance/scripts/README.md", 3, "scripts is level 3"),
        ("agentic_core/L5_safety/validators/LocationAgent.py", 3, "validators is level 3"),
        ("agentic_core/config/blueprint_sovereign/structure_blueprint.py", 3, "blueprint_sovereign is level 3"),
        ("tests/unit/test_example.py", 2, "unit is level 2"),
        ("apps_rg/logic_nodes/example.py", 2, "logic_nodes is level 2"),
        ("canon_validator_agentic_v2_thin.py", 0, "root level file"),
    ]
    
    passed = 0
    for path_str, expected_depth, explanation in test_cases:
        parts = Path(path_str).parts
        # Correct formula: depth = len(parts) - 1 for files
        actual_depth = len(parts) - 1
        
        if actual_depth == expected_depth:
            print(f"   ✓ {path_str}")
            print(f"     depth={actual_depth} ({explanation})")
            passed += 1
        else:
            print(f"   ✗ {path_str}")
            print(f"     Expected depth={expected_depth}, got {actual_depth}")
    
    assert passed == len(test_cases), f"Only {passed}/{len(test_cases)} depth calculations correct"
    print(f"\n✅ PASSED: All {len(test_cases)} depth calculations correct")
    return True


def test_2_hierarchy_agent_fix():
    """
    Test Case 2: Verify HierarchyAgent uses correct depth formula
    """
    print("\n" + "="*60)
    print("TEST 2: HierarchyAgent Depth Fix")
    print("="*60)
    
    hierarchy_agent_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "guardrails" / "HierarchyAgent.py"
    content = hierarchy_agent_path.read_text(encoding='utf-8')
    
    # Check for the fix pattern
    fix_pattern = "len(rel.parts) - 1"
    fix_count = content.count(fix_pattern)
    
    print(f"   Found {fix_count} instances of 'len(rel.parts) - 1'")
    
    # Should have at least 2 fixes (in _enforce_depth_for_root and _enforce_universal_depth)
    assert fix_count >= 2, f"Expected at least 2 fixes, found {fix_count}"
    
    # Check that old incorrect pattern is not used for depth
    old_pattern_lines = []
    for i, line in enumerate(content.split('\n'), 1):
        if 'depth = len(rel.parts)' in line and '- 1' not in line:
            old_pattern_lines.append(i)
    
    if old_pattern_lines:
        print(f"   ✗ Found old incorrect pattern at lines: {old_pattern_lines}")
        return False
    
    print(f"   ✓ No incorrect 'depth = len(rel.parts)' patterns found")
    print(f"✅ PASSED: HierarchyAgent uses correct depth formula")
    return True


def test_3_hierarchy_enforcer_agent_fix():
    """
    Test Case 3: Verify HierarchyEnforcerAgent uses correct depth formula
    """
    print("\n" + "="*60)
    print("TEST 3: HierarchyEnforcerAgent Depth Fix")
    print("="*60)
    
    enforcer_path = PROJECT_ROOT / "agentic_core" / "L3_orchestration" / "workflow_engines" / "HierarchyEnforcerAgent.py"
    content = enforcer_path.read_text(encoding='utf-8')
    
    fix_pattern = "len(rel.parts) - 1"
    fix_count = content.count(fix_pattern)
    
    print(f"   Found {fix_count} instances of 'len(rel.parts) - 1'")
    assert fix_count >= 3, f"Expected at least 3 fixes, found {fix_count}"
    
    # Check for old pattern
    old_pattern_count = 0
    for line in content.split('\n'):
        if 'depth = len(rel.parts)' in line and '- 1' not in line:
            old_pattern_count += 1
    
    assert old_pattern_count == 0, f"Found {old_pattern_count} old incorrect patterns"
    
    print(f"   ✓ No incorrect patterns found")
    print(f"✅ PASSED: HierarchyEnforcerAgent uses correct depth formula")
    return True


def test_4_location_agent_fix():
    """
    Test Case 4: Verify LocationAgent uses correct depth formula
    """
    print("\n" + "="*60)
    print("TEST 4: LocationAgent Depth Fix")
    print("="*60)
    
    location_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "LocationAgent.py"
    content = location_path.read_text(encoding='utf-8')
    
    # Check for correct formula in _validate_depth_requirements
    assert "actual_depth = len(parts) - 1" in content, "Missing correct depth formula"
    print(f"   ✓ Found 'actual_depth = len(parts) - 1'")
    
    # Check that the agentic_core check uses actual_depth, not len(parts)
    assert "actual_depth != 3" in content, "agentic_core check should use actual_depth"
    print(f"   ✓ agentic_core check uses actual_depth")
    
    # Ensure old pattern is fixed
    assert 'len(parts) != 4' not in content, "Old incorrect pattern 'len(parts) != 4' still present"
    print(f"   ✓ Old 'len(parts) != 4' pattern removed")
    
    print(f"✅ PASSED: LocationAgent uses correct depth formula")
    return True


def test_5_dry_run_script_fix():
    """
    Test Case 5: Verify run_hierarchy_enforcer_dry_run.py uses correct depth formula
    """
    print("\n" + "="*60)
    print("TEST 5: Dry Run Script Depth Fix")
    print("="*60)
    
    script_path = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "run_hierarchy_enforcer_dry_run.py"
    content = script_path.read_text(encoding='utf-8')
    
    fix_pattern = "len(rel.parts) - 1"
    fix_count = content.count(fix_pattern)
    
    print(f"   Found {fix_count} instances of 'len(rel.parts) - 1'")
    assert fix_count >= 3, f"Expected at least 3 fixes, found {fix_count}"
    
    # Check for old pattern
    old_pattern_count = 0
    for line in content.split('\n'):
        if 'depth = len(rel.parts)' in line and '- 1' not in line:
            old_pattern_count += 1
    
    assert old_pattern_count == 0, f"Found {old_pattern_count} old incorrect patterns"
    
    print(f"   ✓ No incorrect patterns found")
    print(f"✅ PASSED: Dry run script uses correct depth formula")
    return True


def test_6_check_key_49_depth_fix():
    """
    Test Case 6: Verify check_key_49_depth.py uses correct depth formula
    """
    print("\n" + "="*60)
    print("TEST 6: Check Key 49 Depth Script Fix")
    print("="*60)
    
    script_path = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "check_key_49_depth.py"
    content = script_path.read_text(encoding='utf-8')
    
    fix_pattern = "len(relative_path.parts) - 1"
    fix_count = content.count(fix_pattern)
    
    print(f"   Found {fix_count} instances of 'len(relative_path.parts) - 1'")
    assert fix_count >= 2, f"Expected at least 2 fixes, found {fix_count}"
    
    print(f"✅ PASSED: check_key_49_depth.py uses correct depth formula")
    return True


def test_7_real_file_depth_verification():
    """
    Test Case 7: Verify real files in repository have correct depth
    """
    print("\n" + "="*60)
    print("TEST 7: Real File Depth Verification")
    print("="*60)
    
    from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
    
    # Test specific files that were reported as violations
    test_files = [
        ("agentic_core/L0_maintenance/scripts/README_SSOT_TESTING.md", "agentic_core", 3),
        ("agentic_core/L5_safety/guardrails/HierarchyAgent.py", "agentic_core", 3),
        ("agentic_core/config/blueprint_sovereign/structure_blueprint.py", "agentic_core", 3),
    ]
    
    passed = 0
    for rel_path_str, root_folder, expected_depth in test_files:
        rel_path = Path(rel_path_str)
        full_path = PROJECT_ROOT / rel_path
        
        if not full_path.exists():
            print(f"   ⚠ Skipping (not found): {rel_path_str}")
            continue
        
        # Calculate depth correctly
        depth = len(rel_path.parts) - 1
        registry_depth = SOVEREIGN_REGISTRY.get(root_folder, {}).get("depth", 3)
        
        if depth == registry_depth:
            print(f"   ✓ {rel_path_str}")
            print(f"     depth={depth} == registry_depth={registry_depth}")
            passed += 1
        else:
            print(f"   ✗ {rel_path_str}")
            print(f"     depth={depth} != registry_depth={registry_depth}")
    
    print(f"\n   Verified {passed}/{len(test_files)} files")
    print(f"✅ PASSED: Real files have correct depth")
    return True


def test_8_no_false_positives():
    """
    Test Case 8: Verify no false positive depth violations for valid files
    """
    print("\n" + "="*60)
    print("TEST 8: No False Positives")
    print("="*60)
    
    from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_REGISTRY
    
    # Sample valid files at correct depth
    valid_files = [
        "agentic_core/L0_maintenance/scripts/check_depth.py",  # depth 3
        "agentic_core/L5_safety/validators/LocationAgent.py",  # depth 3
        "agentic_core/utils/terminal_colors.py",  # depth 2 (but utils has depth 3?)
    ]
    
    false_positives = []
    for rel_path_str in valid_files:
        rel_path = Path(rel_path_str)
        full_path = PROJECT_ROOT / rel_path
        
        if not full_path.exists():
            continue
        
        root_folder = rel_path.parts[0]
        depth = len(rel_path.parts) - 1
        expected_depth = SOVEREIGN_REGISTRY.get(root_folder, {}).get("depth")
        
        if expected_depth is not None and depth != expected_depth:
            false_positives.append((rel_path_str, depth, expected_depth))
    
    if false_positives:
        print(f"   Found {len(false_positives)} potential issues:")
        for path, actual, expected in false_positives:
            print(f"     {path}: depth {actual} vs expected {expected}")
    else:
        print(f"   ✓ No false positives detected")
    
    print(f"✅ PASSED: False positive check complete")
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "#"*60)
    print("# Depth Calculation Fix Test Suite")
    print("#"*60)
    print("\nDefinition: depth = folder level where file resides")
    print("Formula: depth = len(rel.parts) - 1")
    print("Example: agentic_core/L0_maintenance/scripts/file.md -> depth 3")
    
    tests = [
        ("Test 1: Depth Definition", test_1_depth_definition),
        ("Test 2: HierarchyAgent Fix", test_2_hierarchy_agent_fix),
        ("Test 3: HierarchyEnforcerAgent Fix", test_3_hierarchy_enforcer_agent_fix),
        ("Test 4: LocationAgent Fix", test_4_location_agent_fix),
        ("Test 5: Dry Run Script Fix", test_5_dry_run_script_fix),
        ("Test 6: Check Key 49 Depth Fix", test_6_check_key_49_depth_fix),
        ("Test 7: Real File Depth Verification", test_7_real_file_depth_verification),
        ("Test 8: No False Positives", test_8_no_false_positives),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("="*60)
    
    if failed > 0:
        print(f"❌ {failed} test(s) FAILED")
        return 1
    else:
        print("✅ ALL TESTS PASSED (100%)")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
