#!/usr/bin/env python3
"""
Flatten tests structure from depth 4 to depth 3.
Move files from tests/<type>/<module>/ to tests/<type>/
"""
import os
import shutil
from pathlib import Path

project_root = Path(__file__).parent
tests_folder = project_root / "tests"

print("="*70)
print("FLATTENING TEST STRUCTURE TO DEPTH 3")
print("="*70)

# Find all Python files at depth 4
files_to_move = []
for root, dirs, files in os.walk(tests_folder):
    for file in files:
        if file.endswith('.py'):
            file_path = Path(root) / file
            try:
                rel_path = file_path.relative_to(tests_folder)
                depth = len(rel_path.parts)
                if depth == 3:  # tests/<type>/<module>/file.py
                    files_to_move.append((file_path, rel_path))
            except ValueError:
                pass

print(f"\n[SCAN] Found {len(files_to_move)} files at depth 4 (need to flatten to depth 3)")

moved_count = 0
for file_path, rel_path in files_to_move:
    # Get the test type (unit, integration, e2e, etc.)
    test_type = rel_path.parts[0]
    module = rel_path.parts[1]
    filename = rel_path.parts[2]
    
    # Create new filename with module prefix if needed
    if module != "core":
        new_filename = f"{module}_{filename}"
    else:
        new_filename = filename
    
    # Target location: tests/<type>/
    target_dir = tests_folder / test_type
    target_file = target_dir / new_filename
    
    # Skip if target already exists
    if target_file.exists():
        print(f"[SKIP] {rel_path} (target exists)")
        continue
    
    # Move file
    try:
        shutil.move(str(file_path), str(target_file))
        print(f"[MOVE] {rel_path} -> {test_type}/{new_filename}")
        moved_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to move {rel_path}: {e}")

# Clean up empty directories
def remove_empty_dirs(path):
    if not path.is_dir():
        return
    for subdir in path.iterdir():
        if subdir.is_dir():
            remove_empty_dirs(subdir)
    try:
        if not any(path.iterdir()):
            path.rmdir()
            print(f"[CLEANUP] Removed empty: {path.relative_to(tests_folder)}")
    except:
        pass

for test_type in ['unit', 'integration', 'e2e', 'fixtures', 'performance', 'security']:
    type_dir = tests_folder / test_type
    if type_dir.exists():
        remove_empty_dirs(type_dir)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Files moved: {moved_count}")
print(f"\n[SUCCESS] Test structure flattened to depth 3!")
