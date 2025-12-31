#!/usr/bin/env python3
"""
Script to run FileCleanupAgent on the codebase.
Identifies and removes files with repeated strings in filenames.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.L5_safety.guardrails.FileCleanupAgent import FileCleanupAgent


class CleanupContext:
    """Context for file cleanup agent."""
    def __init__(self, scan_dirs):
        self.scan_directories = scan_dirs


def main():
    """Run file cleanup agent."""
    project_root = Path(__file__).parent
    
    # Directories to scan
    scan_dirs = [
        str(project_root / 'agentic_core'),
        str(project_root / 'data'),
    ]
    
    ctx = CleanupContext(scan_dirs)
    
    # First run in dry-run mode to see what would be removed
    print("=" * 80)
    print("PHASE 1: DRY RUN - Scanning for files with repeated strings")
    print("=" * 80)
    
    agent = FileCleanupAgent(project_root, ctx, dry_run=True)
    results = agent.scan_for_repeated_filenames(scan_dirs)
    
    print("\n" + "=" * 80)
    print("SCAN RESULTS")
    print("=" * 80)
    print(f"Total files scanned: {results['total_files_scanned']}")
    print(f"Canonical groups found: {results['canonical_groups']}")
    print(f"Files to remove: {results['files_to_remove']}")
    print(f"Files to keep: {results['files_to_keep']}")
    
    if agent.files_to_remove:
        print("\n" + "=" * 80)
        print("FILES THAT WOULD BE REMOVED (DRY RUN)")
        print("=" * 80)
        for i, file_path in enumerate(agent.files_to_remove[:20], 1):
            print(f"{i:3d}. {file_path.relative_to(project_root)}")
        
        if len(agent.files_to_remove) > 20:
            print(f"     ... and {len(agent.files_to_remove) - 20} more files")
        
        print("\n" + "=" * 80)
        print("FILES THAT WOULD BE KEPT")
        print("=" * 80)
        for canonical, file_path in list(agent.files_to_keep.items())[:20]:
            print(f"  {canonical:40s} -> {file_path.name}")
        
        # Ask for confirmation
        print("\n" + "=" * 80)
        print("CONFIRMATION REQUIRED")
        print("=" * 80)
        response = input(f"\nProceed with removing {len(agent.files_to_remove)} files? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            print("\n" + "=" * 80)
            print("PHASE 2: EXECUTING CLEANUP")
            print("=" * 80)
            
            # Create new agent with dry_run=False
            agent_live = FileCleanupAgent(project_root, ctx, dry_run=False)
            agent_live.files_to_remove = agent.files_to_remove
            agent_live.files_to_keep = agent.files_to_keep
            
            cleanup_results = agent_live.execute_cleanup()
            
            print("\n" + "=" * 80)
            print("CLEANUP COMPLETE")
            print("=" * 80)
            print(f"Files removed: {cleanup_results['removed']}")
            print(f"Failed removals: {cleanup_results['failed']}")
        else:
            print("\n[CANCELLED] No files were removed.")
    else:
        print("\n[OK] No files with repeated strings found.")


if __name__ == '__main__':
    main()
