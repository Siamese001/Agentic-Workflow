"""
SURGICAL DEDUPLICATION: Baseline Stabilizer
Target: 294 -> 287 agents by removing 7 duplicate files.

Removes:
- 4 legacy duplicates (outdated implementations)
- 3 true duplicates (identical code in multiple locations)
"""
import json
from pathlib import Path

def surgical_deduplication():
    """Remove the 7 identified duplicate files."""
    
    # Load the list of files to remove
    duplicates_file = Path('duplicates_to_remove.json')
    
    if not duplicates_file.exists():
        print("❌ duplicates_to_remove.json not found")
        print("   Run: python scripts/refactor/identify_duplicates.py")
        return
    
    with open(duplicates_file) as f:
        data = json.load(f)
    
    files_to_remove = data['files_to_remove']
    expected_count = data['expected_result']
    
    print("="*80)
    print("SURGICAL DEDUPLICATION: Baseline Stabilizer")
    print("="*80)
    print(f"Target: Remove {len(files_to_remove)} duplicate files")
    print(f"Expected result: {expected_count} agents")
    print()
    
    removed_count = 0
    not_found_count = 0
    
    for file_path in files_to_remove:
        path = Path(file_path)
        
        if path.exists():
            # Create backup before deletion
            backup_path = Path('.refactor_backups') / f"{path.name}.dedup_backup"
            backup_path.parent.mkdir(exist_ok=True)
            
            # Copy to backup
            import shutil
            shutil.copy2(path, backup_path)
            
            # Remove the file
            path.unlink()
            print(f"✓ REMOVED: {file_path}")
            removed_count += 1
        else:
            print(f"⚠ NOT FOUND: {file_path}")
            not_found_count += 1
    
    print()
    print("="*80)
    print("DEDUPLICATION COMPLETE")
    print("="*80)
    print(f"Files removed: {removed_count}/{len(files_to_remove)}")
    print(f"Files not found: {not_found_count}")
    print(f"Backups saved to: .refactor_backups/")
    print()
    
    if removed_count > 0:
        print("✅ Next steps:")
        print("   1. Run: python scripts/full_agent_discovery.py")
        print(f"   2. Verify agent count is exactly {expected_count}")
        print("   3. Run pilot extraction with --live flag")
    else:
        print("❌ No files were removed. Check file paths.")


if __name__ == "__main__":
    surgical_deduplication()
