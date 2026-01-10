#!/usr/bin/env python3
"""
Archive Duplicate Test Files

Identifies test files with the same name in different directories
and archives the duplicates to preserve SSOT.
"""
from pathlib import Path
from datetime import datetime
import shutil

def main():
    test_dir = Path(__file__).parent.parent / "tests"
    
    # Find all test files and group by name
    seen = {}
    for test_file in test_dir.rglob("test_*.py"):
        seen.setdefault(test_file.name, []).append(test_file)
    
    # Identify duplicates (files with same name in different locations)
    duplicates = [files[1:] for files in seen.values() if len(files) > 1]
    duplicate_count = sum(len(d) for d in duplicates)
    
    print(f"\n{'='*80}")
    print(f"DUPLICATE TEST FILE ARCHIVAL")
    print(f"{'='*80}")
    print(f"Found {duplicate_count} duplicate test files")
    
    if duplicate_count == 0:
        print("No duplicates to archive.")
        return 0
    
    # Create archive directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = Path(__file__).parent.parent / "archives" / f"duplicate_tests_{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Archive duplicates (keep first occurrence, archive rest)
    archived = 0
    for dup_list in duplicates:
        for dup in dup_list:
            try:
                # Create subdirectory structure in archive
                relative_path = dup.relative_to(test_dir)
                archive_target = archive_dir / relative_path
                archive_target.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(dup), str(archive_target))
                print(f"✅ Archived: {relative_path}")
                archived += 1
            except Exception as e:
                print(f"❌ Failed to archive {dup}: {e}")
    
    print(f"\n{'='*80}")
    print(f"ARCHIVAL COMPLETE")
    print(f"{'='*80}")
    print(f"Archived: {archived} files")
    print(f"Location: {archive_dir}")
    print(f"{'='*80}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
