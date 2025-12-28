#!/usr/bin/env python3
"""
Automated test restructuring script - moves files from tests/core/ to proper depth 3 structure.
"""
import os
import shutil
from pathlib import Path

project_root = Path(__file__).parent
tests_folder = project_root / "tests"
core_folder = tests_folder / "core"

# Mapping of file prefixes to their proper locations
# Format: (prefix, test_type, module)
file_mappings = [
    # Unit tests for agentic_core
    ("unit_agentic_core_", "unit", "agentic_core"),
    
    # Unit tests for apps
    ("unit_apps_lic_", "unit", "apps_lic"),
    ("unit_apps_rg_", "unit", "apps_rg"),
    ("unit_apps_shared_", "unit", "apps_shared"),
    
    # Unit tests for other modules
    ("unit_config_", "unit", "config"),
    ("unit_data_", "unit", "data"),
    ("unit_engine_", "unit", "engine"),
    ("unit_observability_", "unit", "observability"),
    ("unit_prompt_governance_", "unit", "prompt_governance"),
    ("unit_runtime_", "unit", "runtime"),
    ("unit_schemas_", "unit", "schemas"),
    ("unit_scripts_", "unit", "scripts"),
    ("unit_shared_", "unit", "shared"),
    
    # Generic unit tests
    ("unit_test_", "unit", "core"),
    ("unit_", "unit", "core"),
    
    # Integration tests
    ("integration_", "integration", "core"),
    ("dry_run_", "integration", "core"),
    ("test_l5_", "integration", "core"),
    ("test_pinecone_", "integration", "core"),
    ("test_sovereign_", "integration", "core"),
    
    # E2E tests
    ("e2e_", "e2e", "core"),
    
    # Other test files
    ("test_", "unit", "core"),
    ("validate_", "unit", "core"),
    ("_test_", "unit", "core"),
]

print("="*70)
print("TEST STRUCTURE RESTRUCTURING")
print("="*70)

if not core_folder.exists():
    print(f"\n[INFO] No tests/core/ folder found - structure may already be correct")
    exit(0)

# Collect all files to move
files_to_move = []
for file in core_folder.rglob("*.py"):
    if file.is_file():
        files_to_move.append(file)

print(f"\n[SCAN] Found {len(files_to_move)} files in tests/core/")

# Categorize and move files
moved_count = 0
skipped_count = 0

for file in files_to_move:
    filename = file.name
    
    # Determine target location
    target_type = None
    target_module = None
    
    for prefix, test_type, module in file_mappings:
        if filename.startswith(prefix):
            target_type = test_type
            target_module = module
            # Remove prefix from filename for cleaner names
            if prefix.startswith("unit_") and not prefix == "unit_":
                # Remove unit_<module>_ prefix
                new_filename = filename.replace(prefix, "test_", 1)
            else:
                new_filename = filename
            break
    
    if not target_type:
        # Default: unit/core
        target_type = "unit"
        target_module = "core"
        new_filename = filename
    
    # Create target directory
    target_dir = tests_folder / target_type / target_module
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Target file path
    target_file = target_dir / new_filename
    
    # Check if target already exists
    if target_file.exists():
        print(f"[SKIP] {filename} -> {target_type}/{target_module}/ (already exists)")
        skipped_count += 1
        continue
    
    # Move file
    try:
        shutil.move(str(file), str(target_file))
        print(f"[MOVE] {filename} -> {target_type}/{target_module}/{new_filename}")
        moved_count += 1
    except Exception as e:
        print(f"[ERROR] Failed to move {filename}: {e}")

# Clean up empty directories
def remove_empty_dirs(path):
    """Recursively remove empty directories."""
    if not path.is_dir():
        return
    
    # Remove empty subdirectories first
    for subdir in path.iterdir():
        if subdir.is_dir():
            remove_empty_dirs(subdir)
    
    # Remove this directory if it's empty
    try:
        if not any(path.iterdir()):
            path.rmdir()
            print(f"[CLEANUP] Removed empty directory: {path.relative_to(tests_folder)}")
    except:
        pass

if core_folder.exists():
    remove_empty_dirs(core_folder)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Files moved: {moved_count}")
print(f"Files skipped: {skipped_count}")
print(f"\n[SUCCESS] Test structure restructuring complete!")
