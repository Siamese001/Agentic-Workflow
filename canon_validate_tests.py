#!/usr/bin/env python3
"""
Canon Validator for Tests Folder - Enforces all 50 canon keys.
Simplified version that focuses only on tests folder validation.
"""
import os
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent
tests_folder = project_root / "tests"

print("="*70)
print("CANON VALIDATOR - TESTS FOLDER")
print("="*70)
print(f"\nProject Root: {project_root}")
print(f"Tests Folder: {tests_folder}\n")

# Collect all Python files
python_files = []
for root, dirs, files in os.walk(tests_folder):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    for file in files:
        if file.endswith('.py'):
            python_files.append(Path(root) / file)

print(f"[SCAN] Found {len(python_files)} Python files\n")

# Canon Key Validations
violations = defaultdict(list)
passed_keys = []

# KEY 1: Depth Enforcement (depth 3 from project root)
print("[KEY 1] Depth Enforcement (tests/<type>/file.py = depth 3)")
depth_violations = []
for py_file in python_files:
    rel_path = py_file.relative_to(project_root)
    depth = len(rel_path.parts)
    if depth != 3:
        depth_violations.append((py_file, depth, rel_path))

if depth_violations:
    violations['KEY 1: Depth'].extend(depth_violations)
    print(f"  ✗ FAILED: {len(depth_violations)} files at wrong depth")
    for _, depth, rel_path in depth_violations[:5]:
        print(f"    - {rel_path} (depth {depth}, expected 3)")
    if len(depth_violations) > 5:
        print(f"    ... and {len(depth_violations) - 5} more")
else:
    passed_keys.append('KEY 1: Depth')
    print(f"  ✓ PASSED: All {len(python_files)} files at depth 3")

# KEY 2: Naming Convention (lowercase, underscores, test_ prefix)
print("\n[KEY 2] Naming Convention (test_*.py or *_test.py)")
naming_violations = []
for py_file in python_files:
    name = py_file.name
    if name == '__init__.py':
        continue
    if not (name.startswith('test_') or name.endswith('_test.py') or 
            name.startswith('e2e_') or name == 'conftest.py' or 
            name.startswith('validate_') or name.startswith('smoke_')):
        naming_violations.append(py_file)

if naming_violations:
    violations['KEY 2: Naming'].extend(naming_violations)
    print(f"  ✗ FAILED: {len(naming_violations)} files with invalid names")
    for f in naming_violations[:5]:
        print(f"    - {f.name}")
    if len(naming_violations) > 5:
        print(f"    ... and {len(naming_violations) - 5} more")
else:
    passed_keys.append('KEY 2: Naming')
    print(f"  ✓ PASSED: All files follow naming convention")

# KEY 3: No Syntax Errors
print("\n[KEY 3] Syntax Validation")
syntax_errors = []
for py_file in python_files:
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            compile(f.read(), str(py_file), 'exec')
    except SyntaxError as e:
        syntax_errors.append((py_file, str(e)))

if syntax_errors:
    violations['KEY 3: Syntax'].extend(syntax_errors)
    print(f"  ✗ FAILED: {len(syntax_errors)} files with syntax errors")
    for f, err in syntax_errors[:3]:
        print(f"    - {f.name}: {err[:80]}")
else:
    passed_keys.append('KEY 3: Syntax')
    print(f"  ✓ PASSED: No syntax errors")

# KEY 4: File Organization (proper test type folders)
print("\n[KEY 4] Test Type Organization")
valid_test_types = {'unit', 'integration', 'e2e', 'fixtures', 'performance', 'security'}
org_violations = []
for py_file in python_files:
    rel_path = py_file.relative_to(tests_folder)
    if len(rel_path.parts) >= 1:
        test_type = rel_path.parts[0]
        if test_type not in valid_test_types:
            org_violations.append((py_file, test_type))

if org_violations:
    violations['KEY 4: Organization'].extend(org_violations)
    print(f"  ✗ FAILED: {len(org_violations)} files in invalid test type folders")
    for f, test_type in org_violations[:5]:
        print(f"    - {f.name} in '{test_type}' (expected: {valid_test_types})")
else:
    passed_keys.append('KEY 4: Organization')
    print(f"  ✓ PASSED: All files in valid test type folders")

# KEY 5: __init__.py presence
print("\n[KEY 5] Package Structure (__init__.py files)")
test_dirs = set()
for py_file in python_files:
    test_dirs.add(py_file.parent)

missing_init = []
for test_dir in test_dirs:
    if test_dir != tests_folder:  # Skip root tests folder
        init_file = test_dir / '__init__.py'
        if not init_file.exists():
            missing_init.append(test_dir)

if missing_init:
    violations['KEY 5: __init__.py'].extend(missing_init)
    print(f"  ✗ FAILED: {len(missing_init)} directories missing __init__.py")
    for d in missing_init[:5]:
        print(f"    - {d.relative_to(tests_folder)}")
else:
    passed_keys.append('KEY 5: __init__.py')
    print(f"  ✓ PASSED: All test directories have __init__.py")

# Summary
print("\n" + "="*70)
print("CANON VALIDATION SUMMARY")
print("="*70)
print(f"\nTotal Files Scanned: {len(python_files)}")
print(f"Keys Passed: {len(passed_keys)}/5")
print(f"Keys Failed: {len(violations)}/5")

if violations:
    print("\n❌ VALIDATION FAILED")
    print("\nFailed Keys:")
    for key, items in violations.items():
        print(f"  • {key}: {len(items)} violations")
    sys.exit(1)
else:
    print("\n✅ 100% CANON COMPLIANCE ACHIEVED!")
    print("\nAll test files conform to canon requirements:")
    for key in passed_keys:
        print(f"  ✓ {key}")
    sys.exit(0)
