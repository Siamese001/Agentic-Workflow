#!/usr/bin/env python3
"""
Find duplicate agents - same class name in multiple locations.

Identifies:
1. Exact duplicates (same class name in multiple files)
2. Similar names that might be duplicates
3. Backup/healing copies that should be cleaned up
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def extract_classes(file_path: Path) -> List[str]:
    """Extract all class names from a Python file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
    except Exception:
        return []


def find_duplicates():
    """Find duplicate agent classes across the codebase."""
    print("\n" + "="*80)
    print("DUPLICATE AGENT SCAN")
    print("="*80 + "\n")
    
    root_dir = Path("agentic_core")
    
    # Map: class_name -> list of file paths
    class_locations: Dict[str, List[Path]] = defaultdict(list)
    
    # Scan all Python files
    for file_path in root_dir.glob("**/*.py"):
        # Skip __pycache__ and test files
        if '__pycache__' in str(file_path) or 'test_' in file_path.name:
            continue
        
        classes = extract_classes(file_path)
        for class_name in classes:
            # Only track Agent classes
            if class_name.endswith('Agent'):
                class_locations[class_name].append(file_path)
    
    # Find duplicates
    duplicates = {name: paths for name, paths in class_locations.items() if len(paths) > 1}
    
    if not duplicates:
        print("✅ No duplicate agent classes found!\n")
        return
    
    # Categorize duplicates
    backup_duplicates = {}
    true_duplicates = {}
    
    for class_name, paths in duplicates.items():
        # Check if any path is in a backup directory
        has_backup = any('.sovereign_healing_backup' in str(p) or 
                        'hygiene_surgery' in str(p) or
                        '.backup' in str(p) for p in paths)
        
        if has_backup:
            backup_duplicates[class_name] = paths
        else:
            true_duplicates[class_name] = paths
    
    # Print backup duplicates
    if backup_duplicates:
        print("="*80)
        print(f"🗂️  BACKUP/HEALING DUPLICATES - {len(backup_duplicates)} classes")
        print("="*80 + "\n")
        print("These are likely backup copies from healing operations.\n")
        
        for class_name, paths in sorted(backup_duplicates.items()):
            print(f"📦 {class_name} ({len(paths)} copies)")
            for path in sorted(paths):
                is_backup = '.sovereign_healing_backup' in str(path) or 'hygiene_surgery' in str(path)
                marker = "🗄️  BACKUP" if is_backup else "✅ ACTIVE"
                print(f"   {marker}: {path}")
            print()
    
    # Print true duplicates
    if true_duplicates:
        print("="*80)
        print(f"⚠️  TRUE DUPLICATES - {len(true_duplicates)} classes")
        print("="*80 + "\n")
        print("These are duplicate implementations in active code.\n")
        
        for class_name, paths in sorted(true_duplicates.items()):
            print(f"🚨 {class_name} ({len(paths)} copies)")
            for path in sorted(paths):
                print(f"   📄 {path}")
            print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"  Total duplicate classes: {len(duplicates)}")
    print(f"  Backup duplicates: {len(backup_duplicates)}")
    print(f"  True duplicates: {len(true_duplicates)}")
    print("="*80 + "\n")
    
    # Recommendations
    if backup_duplicates:
        print("\n" + "="*80)
        print("RECOMMENDATIONS: Backup Duplicates")
        print("="*80 + "\n")
        print("Consider cleaning up backup directories:")
        print("  - .sovereign_healing_backup/")
        print("  - hygiene_surgery/")
        print("\nThese are likely safe to delete if healing is complete.\n")
    
    if true_duplicates:
        print("\n" + "="*80)
        print("RECOMMENDATIONS: True Duplicates")
        print("="*80 + "\n")
        print("Review each duplicate to determine:")
        print("  1. Which is the canonical version?")
        print("  2. Are they truly duplicates or different implementations?")
        print("  3. Can one be deleted or should they be consolidated?\n")
        
        # Generate suggested deletions for obvious cases
        print("Suggested actions for review:\n")
        for class_name, paths in sorted(true_duplicates.items()):
            # Check if one is in a more "canonical" location
            canonical_candidates = []
            for path in paths:
                # Prefer files in their proper layer directories
                if f'L2_execution' in str(path) and 'L2' in class_name:
                    canonical_candidates.append(path)
                elif f'L3_orchestration' in str(path) and 'L3' in class_name:
                    canonical_candidates.append(path)
                elif f'L4_state' in str(path) and 'L4' in class_name:
                    canonical_candidates.append(path)
                elif f'L5_safety' in str(path) and 'L5' in class_name:
                    canonical_candidates.append(path)
                elif f'L6_observability' in str(path) and 'L6' in class_name:
                    canonical_candidates.append(path)
            
            if len(canonical_candidates) == 1:
                canonical = canonical_candidates[0]
                others = [p for p in paths if p != canonical]
                print(f"  {class_name}:")
                print(f"    ✅ Keep: {canonical}")
                for other in others:
                    print(f"    ❌ Consider deleting: {other}")
                print()


if __name__ == "__main__":
    find_duplicates()
