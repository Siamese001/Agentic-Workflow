#!/usr/bin/env python3
"""
Fix remaining depth violations in schemas and other folders
"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.runtime.shared_runtime.import_healer import ImportHealer

project_root = Path(__file__).parent
agentic_core = project_root / "agentic_core"

print("="*70)
print("FIXING REMAINING DEPTH VIOLATIONS")
print("="*70)

# Remaining schema files at depth 3 (need to move to models/)
schema_files = [
    "context_passport.py",
    "golden_state.py",
    "injection.py",
    "messaging.py",
    "metacognition.py",
    "profiles.py",
    "reasoning.py",
    "runtime_micro.py",
    "runtime_shared.py",
    "sovereign_envelope.py",
    "validation_models.py",
]

# Find files at root depth 1
root_files = []
for item in agentic_core.iterdir():
    if item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
        root_files.append(item.name)

# Find observability_from_L6 folder
obs_from_l6 = agentic_core / "observability_from_L6"

healer = ImportHealer(project_root)
moved_count = 0

print(f"\nFound {len(schema_files)} schema files to move to models/")
print(f"Found {len(root_files)} files at agentic_core root")
if obs_from_l6.exists():
    print(f"Found observability_from_L6 folder to merge")

response = input("\nProceed with fixes? (yes/no): ")
if response.lower() != 'yes':
    print("Aborted")
    sys.exit(0)

# Move schema files to models/
print("\n" + "="*70)
print("MOVING SCHEMA FILES TO models/")
print("="*70)

schemas_dir = agentic_core / "schemas"
models_dir = schemas_dir / "models"
models_dir.mkdir(parents=True, exist_ok=True)

for filename in schema_files:
    old_path = schemas_dir / filename
    new_path = models_dir / filename
    
    if not old_path.exists():
        print(f"[!] Not found: {filename}")
        continue
    
    try:
        # Register for import healing
        old_path_str = str(old_path.relative_to(project_root)).replace('\\', '/')
        new_path_str = str(new_path.relative_to(project_root)).replace('\\', '/')
        healer.register_relocation(old_path_str, new_path_str)
        
        # Move file
        shutil.move(str(old_path), str(new_path))
        moved_count += 1
        print(f"[✓] Moved: {filename}")
        
    except Exception as e:
        print(f"[!] Failed to move {filename}: {e}")

# Move root files to appropriate locations
print("\n" + "="*70)
print("MOVING ROOT FILES")
print("="*70)

for filename in root_files:
    old_path = agentic_core / filename
    
    # Determine target based on filename
    if "mission" in filename.lower() or "control" in filename.lower():
        target_dir = agentic_core / "L3_orchestration" / "workflow_engines"
    elif "config" in filename.lower():
        target_dir = agentic_core / "config" / "environments"
    else:
        target_dir = agentic_core / "L0_maintenance" / "scripts"
    
    target_dir.mkdir(parents=True, exist_ok=True)
    new_path = target_dir / filename
    
    try:
        # Register for import healing
        old_path_str = str(old_path.relative_to(project_root)).replace('\\', '/')
        new_path_str = str(new_path.relative_to(project_root)).replace('\\', '/')
        healer.register_relocation(old_path_str, new_path_str)
        
        # Move file
        shutil.move(str(old_path), str(new_path))
        moved_count += 1
        print(f"[✓] Moved: {filename} → {target_dir.name}/")
        
    except Exception as e:
        print(f"[!] Failed to move {filename}: {e}")

# Merge observability_from_L6 into observability
if obs_from_l6.exists():
    print("\n" + "="*70)
    print("MERGING observability_from_L6 INTO observability")
    print("="*70)
    
    obs_dir = agentic_core / "observability"
    
    # Move all contents
    for item in obs_from_l6.rglob("*"):
        if item.is_file() and not item.name.startswith('.'):
            rel_path = item.relative_to(obs_from_l6)
            target = obs_dir / rel_path
            
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(target))
                print(f"[✓] Merged: {item.name}")
                moved_count += 1
            except Exception as e:
                print(f"[!] Failed to merge {item.name}: {e}")
    
    # Remove empty folder
    try:
        shutil.rmtree(obs_from_l6)
        print(f"[✓] Removed: observability_from_L6/")
    except Exception as e:
        print(f"[!] Failed to remove observability_from_L6: {e}")

# Fix imports
if moved_count > 0:
    print(f"\n{'='*70}")
    print("FIXING IMPORTS")
    print(f"{'='*70}")
    
    results = healer.heal_all_imports_in_directory(agentic_core)
    if results:
        print(f"[✓] Fixed imports in {len(results)} files")
    else:
        print("[!] No imports needed fixing")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Files moved: {moved_count}")
print("\nRe-run validation to verify:")
print("  python run_agentic_core_validation.py")
