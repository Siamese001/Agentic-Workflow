#!/usr/bin/env python3
"""
Simple validator for tests folder only - enforces depth 3 structure.
"""
import os
import sys
from pathlib import Path

# Find project root
project_root = Path(__file__).parent
tests_folder = project_root / "tests"

print("="*70)
print("TESTS FOLDER VALIDATION - DEPTH 3 ENFORCEMENT")
print("="*70)
print(f"\nProject Root: {project_root}")
print(f"Tests Folder: {tests_folder}")

if not tests_folder.exists():
    print(f"\n[ERROR] Tests folder not found at {tests_folder}")
    sys.exit(1)

# Collect all Python files
python_files = []
for root, dirs, files in os.walk(tests_folder):
    # Skip hidden and cache directories
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    for file in files:
        if file.endswith('.py'):
            python_files.append(Path(root) / file)

print(f"\n[SCAN] Found {len(python_files)} Python files in tests folder")

# Validate depth structure
violations = []
valid_files = []

for py_file in python_files:
    try:
        rel_path = py_file.relative_to(project_root)
        # Depth = number of parent directories + 1 (for the file itself)
        # From project root:
        # tests/unit/file.py = depth 3 ✓
        # tests/unit/module/file.py = depth 4 ✗
        depth = len(rel_path.parts)
        
        if depth != 3:
            violations.append((py_file, depth, rel_path))
        else:
            valid_files.append((py_file, rel_path))
    except ValueError:
        print(f"[WARNING] File outside project root: {py_file}")

# Report results
print("\n" + "="*70)
print("VALIDATION RESULTS")
print("="*70)

print(f"\n✓ Valid files (depth 3): {len(valid_files)}")
for py_file, rel_path in valid_files[:10]:
    print(f"  • {rel_path}")
if len(valid_files) > 10:
    print(f"  ... and {len(valid_files) - 10} more")

print(f"\n✗ Violations (depth != 3): {len(violations)}")
for py_file, depth, rel_path in violations:
    expected = 3
    status = "SHALLOW" if depth < expected else "DEEP"
    print(f"  • [{status}] {rel_path}")
    print(f"    Depth: {depth} (expected: {expected})")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total files scanned: {len(python_files)}")
print(f"Valid (depth 3): {len(valid_files)}")
print(f"Violations: {len(violations)}")

if violations:
    print("\n[ACTION REQUIRED] Fix depth violations:")
    print("  - SHALLOW files (depth < 3): Move into proper subdirectory structure")
    print("  - DEEP files (depth > 3): Flatten or consolidate directory structure")
    sys.exit(1)
else:
    print("\n[SUCCESS] All test files conform to depth 3 structure!")
    sys.exit(0)
