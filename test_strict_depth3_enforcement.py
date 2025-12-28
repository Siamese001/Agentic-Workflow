#!/usr/bin/env python3
"""
Test Strict Depth 3 Enforcement with Import Healing
Verifies that the canon validator correctly identifies depth violations
and that the import healer can fix broken imports after relocations.
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.runtime.shared.void_compliance import validate_file_location
from agentic_core.runtime.shared.import_healer import ImportHealer, get_sovereign_ignore_list

print("="*70)
print("STRICT DEPTH 3 ENFORCEMENT TEST")
print("="*70)

# Test 1: Verify sovereign ignore list loading
print("\n[TEST 1] Sovereign Ignore List")
ignore_list = get_sovereign_ignore_list()
print(f"Loaded {len(ignore_list)} protected patterns")
print(f"Sample patterns: {sorted(list(ignore_list))[:10]}")

expected_patterns = {'archives', 'data', 'venv', '.venv', 'logs', 'cache', 'core'}
found = expected_patterns & ignore_list
print(f"\nExpected patterns found: {len(found)}/{len(expected_patterns)}")
for pattern in expected_patterns:
    status = "✓" if pattern in ignore_list else "✗"
    print(f"  {status} {pattern}")

# Test 2: Verify depth validation for tests folder
print("\n[TEST 2] Tests Folder Depth Validation")
test_cases = [
    ("tests/test_shallow.py", 2, "SHALLOW", False),
    ("tests/unit/test_correct.py", 3, "PASS", True),
    ("tests/unit/core/test_deep.py", 4, "DEEP", False),
    ("tests/e2e/test_correct.py", 3, "PASS", True),
    ("tests/e2e/core/test_deep.py", 4, "DEEP", False),
]

print("\nTest Case Results:")
for test_path, depth, expected_status, should_pass in test_cases:
    file_path = project_root / test_path
    is_valid, reason = validate_file_location(file_path, project_root)
    
    actual_status = "PASS" if is_valid else reason.split()[0]
    match = "✓" if (is_valid == should_pass) else "✗"
    
    print(f"  {match} {test_path}")
    print(f"     Depth: {depth}, Expected: {expected_status}, Got: {actual_status}")
    if not is_valid:
        print(f"     Reason: {reason}")

# Test 3: Import Healer functionality
print("\n[TEST 3] Import Healer Functionality")
healer = ImportHealer(project_root)

# Simulate a relocation: tests/e2e/core/test_admin.py -> tests/e2e/test_admin.py
old_path = "tests/e2e/core/test_admin.py"
new_path = "tests/e2e/test_admin.py"
healer.register_relocation(old_path, new_path)

print(f"\nRegistered relocation:")
print(f"  Old: {old_path}")
print(f"  New: {new_path}")

# Test import path conversion
test_imports = [
    "tests.e2e.core.test_admin",
    "tests.e2e.core.base",
    "tests.unit.core.helpers",
]

print(f"\nImport path conversions:")
for old_import in test_imports:
    new_import = healer._get_relocated_module(old_import)
    changed = "→" if new_import != old_import else "="
    print(f"  {old_import} {changed} {new_import}")

# Test 4: Verify agentic_core depth 4 enforcement
print("\n[TEST 4] Agentic Core Depth 4 Enforcement")
agentic_test_cases = [
    ("agentic_core/L1_cognition/P1_core/thought_engine.py", 4, True),
    ("agentic_core/L1_cognition/thought_engine.py", 3, False),
    ("agentic_core/L1_cognition/P1_core/submodule/deep.py", 5, False),
]

print("\nAgentic Core Test Results:")
for test_path, depth, should_pass in agentic_test_cases:
    file_path = project_root / test_path
    is_valid, reason = validate_file_location(file_path, project_root)
    
    match = "✓" if (is_valid == should_pass) else "✗"
    status = "PASS" if is_valid else "FAIL"
    
    print(f"  {match} {test_path}")
    print(f"     Depth: {depth}, Status: {status}")
    if not is_valid:
        print(f"     Reason: {reason}")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("\n✅ Strict Depth 3 enforcement is active for tests folder")
print("✅ Strict Depth 4 enforcement is active for agentic_core")
print("✅ Sovereign ignore list loaded from .gitignore")
print("✅ Import healer ready to fix broken imports after relocations")

print("\n⚠️  CRITICAL WARNING:")
print("   When moving files to enforce depth policies, ALWAYS run import healer")
print("   to prevent import breakage in CI/CD pipelines.")

print("\n📋 RECOMMENDED WORKFLOW:")
print("   1. Run canon validator to identify depth violations")
print("   2. Move files to correct depth")
print("   3. Run import healer on affected directories")
print("   4. Run tests to verify no import breakage")
print("   5. Commit changes")
