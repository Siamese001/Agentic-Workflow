#!/usr/bin/env python3
"""
Fix location violations by moving files to proper depth 4 locations
"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP
from agentic_core.runtime.shared_runtime.import_healer import ImportHealer

project_root = Path(__file__).parent
agentic_core = project_root / "agentic_core"

print("="*70)
print("FIXING DEPTH VIOLATIONS")
print("="*70)

# Files to fix
depth_violations = [
    # Depth 2 files (should be depth 4)
    ("agentic_core/sovereign_mission_control.py", "agentic_core/L3_orchestration/workflow_engines/sovereign_mission_control.py"),
    
    # Depth 3 files (should be depth 4)
    ("agentic_core/L0_maintenance/reset_sovereign_state.py", "agentic_core/L0_maintenance/scripts/reset_sovereign_state.py"),
    ("agentic_core/L4_state/autonomous_checkpoint_manager.py", "agentic_core/L4_state/validation_context/autonomous_checkpoint_manager.py"),
    ("agentic_core/L4_state/autonomous_state_guardian.py", "agentic_core/L4_state/validation_context/autonomous_state_guardian.py"),
    ("agentic_core/L5_safety/self_updating_safety_engine.py", "agentic_core/L5_safety/guardrails/self_updating_safety_engine.py"),
    ("agentic_core/schemas/base.py", "agentic_core/schemas/models/base.py"),
    ("agentic_core/schemas/consensus.py", "agentic_core/schemas/models/consensus.py"),
    ("agentic_core/schemas/core_contracts.py", "agentic_core/schemas/models/core_contracts.py"),
    
    # Depth 5 files (should be depth 4)
    ("agentic_core/config/blueprint_sovereign/environments/sovereign_config.py", "agentic_core/config/environments/sovereign_config.py"),
    ("agentic_core/L0_maintenance/scripts/maintenance/generate_hooks.py", "agentic_core/L0_maintenance/scripts/generate_hooks.py"),
]

# Unapproved L1 folders to move
l1_violations = [
    ("agentic_core/checkpoints", "agentic_core/L4_state/validation_context/checkpoints"),
    ("agentic_core/L6_observability", "agentic_core/observability"),
]

healer = ImportHealer(project_root)
moved_count = 0
folders_moved = 0

print(f"\nFound {len(depth_violations)} depth violations to fix")
print(f"Found {len(l1_violations)} L1 folder violations to fix")

response = input("\nProceed with fixes? (yes/no): ")
if response.lower() != 'yes':
    print("Aborted")
    sys.exit(0)

# Fix depth violations
print("\n" + "="*70)
print("FIXING DEPTH VIOLATIONS")
print("="*70)

for old_path_str, new_path_str in depth_violations:
    old_path = project_root / old_path_str
    new_path = project_root / new_path_str
    
    if not old_path.exists():
        print(f"[!] Not found: {old_path.name}")
        continue
    
    try:
        # Create parent directory
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Register for import healing
        healer.register_relocation(old_path_str, new_path_str)
        
        # Move file
        shutil.move(str(old_path), str(new_path))
        moved_count += 1
        print(f"[✓] Moved: {old_path.name} → {new_path.parent.name}/")
        
    except Exception as e:
        print(f"[!] Failed to move {old_path.name}: {e}")

# Fix L1 folder violations
print("\n" + "="*70)
print("FIXING L1 FOLDER VIOLATIONS")
print("="*70)

for old_path_str, new_path_str in l1_violations:
    old_path = project_root / old_path_str
    new_path = project_root / new_path_str
    
    if not old_path.exists():
        print(f"[!] Not found: {old_path.name}")
        continue
    
    try:
        # For L6_observability → observability, just rename
        if old_path.name == "L6_observability":
            target = old_path.parent / "observability_from_L6"
            shutil.move(str(old_path), str(target))
            print(f"[✓] Renamed: L6_observability → observability_from_L6")
            folders_moved += 1
        else:
            # Create parent directory
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move entire folder
            shutil.move(str(old_path), str(new_path))
            folders_moved += 1
            print(f"[✓] Moved: {old_path.name}/ → {new_path.parent.name}/")
        
    except Exception as e:
        print(f"[!] Failed to move {old_path.name}: {e}")

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
print(f"Folders moved: {folders_moved}")
print("\nRe-run validation to verify:")
print("  python run_agentic_core_validation.py")
