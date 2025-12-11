#!/usr/bin/env python3
"""
Automated filename fixer for Key 49 violations.

Loads key49.json and renames files by taking only the last 3 words
of the stem (separated by underscores) + .py extension.
Handles duplicates by appending _2, _3, etc.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path.cwd()


def load_violations() -> List[str]:
    """Load Key 49 violations from key49.json."""
    json_path = ROOT / "key49.json"
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        sys.exit(1)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if there are any failures for key 49
    failures = data.get("failures", {})
    if "49" not in failures:
        print("No Key 49 violations found. All filenames are compliant!")
        return []
    
    files = failures["49"].get("files", [])
    print(f"Found {len(files)} files with Key 49 violations")
    return files


def calculate_new_name(file_path: str) -> str:
    """
    Calculate new filename by taking last 3 words of stem.
    
    Args:
        file_path: Original file path (relative or absolute)
        
    Returns:
        New filename (just the name, not full path)
    """
    path = Path(file_path)
    stem = path.stem
    
    # Split by underscores
    words = stem.split('_')
    
    # Take last 3 words
    if len(words) <= 3:
        new_stem = stem  # Already short enough
    else:
        new_stem = '_'.join(words[-3:])
    
    return f"{new_stem}.py"


def rename_files(violations: List[str]) -> None:
    """
    Rename all violating files.
    
    Args:
        violations: List of file paths with Key 49 violations
    """
    if not violations:
        return
    
    renamed_count = 0
    skipped_count = 0
    seen_names: Dict[str, int] = {}  # Track duplicates
    
    for file_rel_path in violations:
        # Convert to absolute path
        old_path = ROOT / file_rel_path
        
        if not old_path.exists():
            print(f"⚠️  Skipped (not found): {file_rel_path}")
            skipped_count += 1
            continue
        
        # Calculate new name
        new_name = calculate_new_name(file_rel_path)
        
        # Handle duplicates
        if new_name in seen_names:
            seen_names[new_name] += 1
            stem = new_name.replace('.py', '')
            new_name = f"{stem}_{seen_names[new_name]}.py"
        else:
            seen_names[new_name] = 1
        
        new_path = old_path.parent / new_name
        
        # Check if target already exists
        if new_path.exists() and new_path != old_path:
            # Try adding suffix
            counter = 2
            while new_path.exists():
                stem = new_name.replace('.py', '')
                new_name = f"{stem}_{counter}.py"
                new_path = old_path.parent / new_name
                counter += 1
        
        # Perform rename
        if new_path != old_path:
            try:
                old_path.rename(new_path)
                print(f"✅ Renamed: {old_path.name} → {new_name}")
                renamed_count += 1
            except OSError as e:
                print(f"❌ Failed to rename {old_path.name}: {e}")
                skipped_count += 1
        else:
            print(f"⏭️  Skipped (already correct): {old_path.name}")
            skipped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Renamed: {renamed_count} files")
    print(f"  Skipped: {skipped_count} files")
    print(f"{'='*60}")


def main():
    """Main execution."""
    print("=" * 60)
    print("AUTOMATED FILENAME FIXER FOR KEY 49")
    print("=" * 60)
    print()
    
    # Load violations
    violations = load_violations()
    
    if not violations:
        print("\n✨ No fixes needed - all filenames are compliant!")
        return
    
    # Rename files
    print(f"\nProcessing {len(violations)} files...\n")
    rename_files(violations)
    
    print("\n✨ Done! Run 'python canon_validator.py --only 49' to verify.")


if __name__ == "__main__":
    main()
