#!/usr/bin/env python3
"""
Simplified Canon Validator for agentic_core folder only
Focuses on core validation without optional agent imports
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.runtime.shared_runtime.void_compliance import (
    validate_canonical_hierarchy,
    validate_file_location,
    check_span_of_two_violations,
    check_import_waterfall_violations,
)
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

print("="*70)
print("AGENTIC_CORE VALIDATION - SIMPLIFIED")
print("="*70)

# Check 1: Hierarchy violations (unapproved folders)
print("\n[1] Checking hierarchy alignment (SSOT compliance)...")
hierarchy_violations = validate_canonical_hierarchy(project_root)
hierarchy_violations = [
    v for v in hierarchy_violations 
    if 'agentic_core' in str(v[0])
    and '.git' not in str(v[0])
    and '__pycache__' not in str(v[0])
    and 'archives' not in str(v[0])
]

print(f"   Found {len(hierarchy_violations)} hierarchy violations")
if hierarchy_violations:
    for folder_path, reason in hierarchy_violations[:10]:
        rel_path = folder_path.relative_to(project_root)
        print(f"   [X] {rel_path}: {reason[:80]}")
    if len(hierarchy_violations) > 10:
        print(f"   ... and {len(hierarchy_violations) - 10} more")

# Check 2: Span of two violations
print("\n[2] Checking span of two violations...")
span_violations = check_span_of_two_violations(project_root)
span_violations = [v for v in span_violations if 'agentic_core' in str(v[0])]
print(f"   Found {len(span_violations)} span violations")
if span_violations:
    for folder_path, reason in span_violations[:5]:
        rel_path = folder_path.relative_to(project_root)
        print(f"   [X] {rel_path}: {reason[:80]}")

# Check 3: File location violations (depth enforcement)
print("\n[3] Checking file locations (depth enforcement)...")
location_violations = []
for py_file in (project_root / 'agentic_core').rglob("*.py"):
    if '__pycache__' in str(py_file) or 'archives' in str(py_file):
        continue
    try:
        is_valid, reason = validate_file_location(py_file, project_root)
        if not is_valid:
            location_violations.append((py_file, reason))
    except Exception:
        continue

print(f"   Found {len(location_violations)} location violations")
if location_violations:
    for file_path, reason in location_violations[:10]:
        rel_path = file_path.relative_to(project_root)
        print(f"   [X] {rel_path.name}: {reason[:80]}")
    if len(location_violations) > 10:
        print(f"   ... and {len(location_violations) - 10} more")

# Check 4: Import waterfall violations
print("\n[4] Checking import waterfall violations...")
waterfall_violations = []
for py_file in (project_root / 'agentic_core').rglob("*.py"):
    if '__pycache__' in str(py_file) or 'archives' in str(py_file):
        continue
    try:
        violations = check_import_waterfall_violations(py_file, project_root)
        if violations:
            waterfall_violations.extend([(py_file, v) for v in violations])
    except Exception:
        continue

print(f"   Found {len(waterfall_violations)} waterfall violations")
if waterfall_violations:
    for file_path, reason in waterfall_violations[:10]:
        print(f"   [X] {file_path.name}: {reason[:80]}")
    if len(waterfall_violations) > 10:
        print(f"   ... and {len(waterfall_violations) - 10} more")

# Summary
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)
total_violations = (
    len(hierarchy_violations) + 
    len(span_violations) + 
    len(location_violations) + 
    len(waterfall_violations)
)

print(f"Hierarchy violations: {len(hierarchy_violations)}")
print(f"Span violations: {len(span_violations)}")
print(f"Location violations: {len(location_violations)}")
print(f"Waterfall violations: {len(waterfall_violations)}")
print(f"\nTotal violations: {total_violations}")

if total_violations == 0:
    print("\n[OK] ALL CHECKS PASSED - 100% COMPLIANCE")
else:
    print(f"\n[X] {total_violations} VIOLATIONS FOUND")
    
    # Offer auto-healing
    print("\n" + "="*70)
    print("AUTO-HEALING AVAILABLE")
    print("="*70)
    print("Run with --heal flag to automatically fix violations:")
    print("  python run_agentic_core_validation.py --heal")

# Auto-healing mode
if "--heal" in sys.argv and hierarchy_violations:
    print("\n" + "="*70)
    print("AUTO-HEALING MODE")
    print("="*70)
    
    from agentic_core.runtime.shared_runtime.import_healer import ImportHealer
    import shutil
    
    healer = ImportHealer(project_root)
    relocated_count = 0
    folders_removed = []
    
    # Group violations by unapproved folder
    unapproved_folders = {}
    for folder_path, reason in hierarchy_violations:
        if 'Unapproved' in reason:
            parent = folder_path.parent
            if parent not in unapproved_folders:
                unapproved_folders[parent] = []
            unapproved_folders[parent].append((folder_path, reason))
    
    for parent_path, violations in unapproved_folders.items():
        for folder_path, reason in violations:
            if not folder_path.exists() or not folder_path.is_dir():
                continue
            
            # Get all Python files
            py_files = list(folder_path.rglob("*.py"))
            if not py_files:
                # Empty folder, remove it
                try:
                    shutil.rmtree(folder_path)
                    folders_removed.append(str(folder_path.relative_to(project_root)))
                    print(f"[✓] Removed empty folder: {folder_path.relative_to(project_root)}")
                except Exception as e:
                    print(f"[!] Failed to remove {folder_path.name}: {e}")
                continue
            
            # Determine target location
            try:
                rel_parent = parent_path.relative_to(project_root)
                parts = rel_parent.parts
                
                if len(parts) >= 2 and parts[0] == 'agentic_core':
                    l1_layer = parts[1]
                    approved_l2 = CORE_SUBFOLDER_MAP.get(l1_layer, [])
                    if approved_l2:
                        target_folder = parent_path / approved_l2[0]
                        target_folder.mkdir(parents=True, exist_ok=True)
                        
                        # Move files
                        for py_file in py_files:
                            try:
                                target_file = target_folder / py_file.name
                                if target_file.exists():
                                    print(f"[!] Skipping {py_file.name}: already exists")
                                    continue
                                
                                # Register for import healing
                                old_path = str(py_file.relative_to(project_root)).replace('\\', '/')
                                new_path = str(target_file.relative_to(project_root)).replace('\\', '/')
                                healer.register_relocation(old_path, new_path)
                                
                                shutil.move(str(py_file), str(target_file))
                                relocated_count += 1
                                print(f"[✓] Moved: {py_file.name} → {approved_l2[0]}/")
                            except Exception as e:
                                print(f"[!] Failed to move {py_file.name}: {e}")
                        
                        # Remove empty folder
                        try:
                            if folder_path.exists() and not any(folder_path.iterdir()):
                                shutil.rmtree(folder_path)
                                folders_removed.append(str(folder_path.relative_to(project_root)))
                        except Exception as e:
                            print(f"[!] Failed to remove {folder_path.name}: {e}")
            
            except Exception as e:
                print(f"[!] Error processing {folder_path.name}: {e}")
    
    # Fix imports
    if relocated_count > 0:
        print(f"\n[IMPORT-HEAL] Fixing imports after {relocated_count} relocations...")
        results = healer.heal_all_imports_in_directory(project_root / 'agentic_core')
        if results:
            print(f"[✓] Fixed imports in {len(results)} files")
    
    print(f"\n[SUMMARY] Files relocated: {relocated_count}, Folders removed: {len(folders_removed)}")
