#!/usr/bin/env python3
"""
Enforce SSOT structure by moving files from unapproved folders to approved folders
Handles collisions intelligently and fixes imports
"""
import sys
import shutil
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP
from agentic_core.runtime.shared_runtime.import_healer import ImportHealer

project_root = Path(__file__).parent
agentic_core = project_root / "agentic_core"

print("="*70)
print("ENFORCING SSOT STRUCTURE")
print("="*70)

# Scan for unapproved L2 subfolders
unapproved_folders = []
for l1_folder in agentic_core.iterdir():
    if not l1_folder.is_dir() or l1_folder.name.startswith('.') or l1_folder.name == '__pycache__':
        continue
    
    if l1_folder.name in CORE_SUBFOLDER_MAP:
        approved_l2 = set(CORE_SUBFOLDER_MAP[l1_folder.name])
        
        for l2_folder in l1_folder.iterdir():
            if not l2_folder.is_dir() or l2_folder.name.startswith('.') or l2_folder.name == '__pycache__':
                continue
            
            if l2_folder.name not in approved_l2:
                unapproved_folders.append((l1_folder, l2_folder))

print(f"\nFound {len(unapproved_folders)} unapproved L2 subfolders")

if not unapproved_folders:
    print("\n[OK] All folders comply with SSOT")
    sys.exit(0)

# Group by L1 layer
by_l1 = defaultdict(list)
for l1, l2 in unapproved_folders:
    by_l1[l1.name].append(l2)

for l1_name, l2_folders in by_l1.items():
    print(f"\n{l1_name}:")
    for l2 in l2_folders:
        file_count = len(list(l2.rglob("*.py")))
        print(f"  • {l2.name} ({file_count} Python files)")

# Ask for confirmation
print("\n" + "="*70)
print("PROPOSED ACTION")
print("="*70)
print("Move all Python files from unapproved folders to first approved folder")
print("Files with name collisions will be renamed with folder prefix")
print("\nApproved target folders:")
for l1_name in sorted(by_l1.keys()):
    approved = CORE_SUBFOLDER_MAP.get(l1_name, [])
    if approved:
        print(f"  {l1_name} → {approved[0]}/")

response = input("\nProceed with file relocation? (yes/no): ")
if response.lower() != 'yes':
    print("Aborted by user")
    sys.exit(0)

# Execute relocation
healer = ImportHealer(project_root)
relocated_count = 0
folders_removed = []
rename_count = 0

for l1_folder, l2_folder in unapproved_folders:
    l1_name = l1_folder.name
    approved_l2 = CORE_SUBFOLDER_MAP.get(l1_name, [])
    
    if not approved_l2:
        print(f"\n[!] No approved folders for {l1_name}, skipping {l2_folder.name}")
        continue
    
    target_folder = l1_folder / approved_l2[0]
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Get all Python files
    py_files = list(l2_folder.rglob("*.py"))
    
    if not py_files:
        # Empty folder, just remove it
        try:
            shutil.rmtree(l2_folder)
            folders_removed.append(str(l2_folder.relative_to(project_root)))
            print(f"\n[✓] Removed empty folder: {l2_folder.relative_to(project_root)}")
        except Exception as e:
            print(f"\n[!] Failed to remove {l2_folder.name}: {e}")
        continue
    
    print(f"\n[*] Processing {l2_folder.name} → {approved_l2[0]}/")
    
    for py_file in py_files:
        try:
            # Calculate target path
            rel_path = py_file.relative_to(l2_folder)
            target_file = target_folder / rel_path
            
            # Handle collisions
            if target_file.exists():
                # Rename with folder prefix
                new_name = f"{l2_folder.name}_{py_file.name}"
                target_file = target_folder / new_name
                rename_count += 1
                print(f"  [~] Renamed: {py_file.name} → {new_name}")
            
            # Create parent directories if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Register for import healing
            old_path = str(py_file.relative_to(project_root)).replace('\\', '/')
            new_path = str(target_file.relative_to(project_root)).replace('\\', '/')
            healer.register_relocation(old_path, new_path)
            
            # Move file
            shutil.move(str(py_file), str(target_file))
            relocated_count += 1
            print(f"  [✓] Moved: {py_file.name}")
            
        except Exception as e:
            print(f"  [!] Failed to move {py_file.name}: {e}")
    
    # Remove empty source folder
    try:
        if l2_folder.exists():
            # Check if truly empty (no files left)
            remaining = list(l2_folder.rglob("*"))
            remaining = [f for f in remaining if f.is_file() and not f.name.startswith('.')]
            
            if not remaining:
                shutil.rmtree(l2_folder)
                folders_removed.append(str(l2_folder.relative_to(project_root)))
                print(f"  [✓] Removed: {l2_folder.name}/")
            else:
                print(f"  [!] Folder not empty, keeping: {l2_folder.name}/ ({len(remaining)} files remain)")
    except Exception as e:
        print(f"  [!] Failed to remove {l2_folder.name}: {e}")

# Fix imports
if relocated_count > 0:
    print(f"\n{'='*70}")
    print("FIXING IMPORTS")
    print(f"{'='*70}")
    print(f"Healing imports after {relocated_count} file relocations...")
    
    results = healer.heal_all_imports_in_directory(agentic_core)
    if results:
        print(f"[✓] Fixed imports in {len(results)} files")
        for file_path, message in list(results.items())[:10]:
            print(f"  • {Path(file_path).name}: {message}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more files")
    else:
        print("[!] No imports needed fixing")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Files relocated: {relocated_count}")
print(f"Files renamed (collisions): {rename_count}")
print(f"Folders removed: {len(folders_removed)}")

if folders_removed:
    print(f"\nRemoved folders:")
    for folder in folders_removed[:10]:
        print(f"  • {folder}")
    if len(folders_removed) > 10:
        print(f"  ... and {len(folders_removed) - 10} more")

print(f"\n{'='*70}")
print("Re-run validation to verify compliance:")
print("  python run_agentic_core_validation.py")
print(f"{'='*70}")
