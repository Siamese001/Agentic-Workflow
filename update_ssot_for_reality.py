#!/usr/bin/env python3
"""
Update SSOT (structure_blueprint.py) to match actual folder structure
This legitimizes existing folders rather than trying to move everything
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP

project_root = Path(__file__).parent
agentic_core = project_root / "agentic_core"

# Scan actual L2 subfolders for each L1 layer
actual_structure = {}
for l1_folder in agentic_core.iterdir():
    if not l1_folder.is_dir() or l1_folder.name.startswith('.') or l1_folder.name == '__pycache__':
        continue
    
    if l1_folder.name in CORE_SUBFOLDER_MAP:
        # Get actual L2 subfolders
        actual_l2 = set()
        for item in l1_folder.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                actual_l2.add(item.name)
        
        if actual_l2:
            actual_structure[l1_folder.name] = sorted(actual_l2)

# Compare with SSOT
print("="*70)
print("SSOT vs REALITY COMPARISON")
print("="*70)

updates_needed = {}
for l1_name, actual_l2 in actual_structure.items():
    expected_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
    actual_l2_set = set(actual_l2)
    
    missing_from_ssot = actual_l2_set - expected_l2
    
    if missing_from_ssot:
        updates_needed[l1_name] = {
            'current': list(expected_l2),
            'actual': actual_l2,
            'missing': sorted(missing_from_ssot)
        }
        
        print(f"\n{l1_name}:")
        print(f"  SSOT: {sorted(expected_l2)}")
        print(f"  Actual: {actual_l2}")
        print(f"  Missing from SSOT: {sorted(missing_from_ssot)}")

# Generate updated CORE_SUBFOLDER_MAP
if updates_needed:
    print("\n" + "="*70)
    print("PROPOSED SSOT UPDATE")
    print("="*70)
    print("\nCORE_SUBFOLDER_MAP = {")
    
    for l1_name in sorted(CORE_SUBFOLDER_MAP.keys()):
        if l1_name in updates_needed:
            # Use actual structure
            folders = updates_needed[l1_name]['actual']
        else:
            # Keep existing
            folders = CORE_SUBFOLDER_MAP[l1_name]
        
        folders_str = ', '.join(f'"{f}"' for f in sorted(folders))
        print(f'    "{l1_name}": [{folders_str}],')
    
    print("}")
    
    print("\n" + "="*70)
    print(f"SUMMARY: {len(updates_needed)} L1 layers need SSOT updates")
    print("="*70)
else:
    print("\n✅ SSOT matches reality - no updates needed")
