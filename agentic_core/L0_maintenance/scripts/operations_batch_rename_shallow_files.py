#!/usr/bin/env python3
"""
Batch Rename Script - Key 49 Naming Compliance
Renames shallow files to include high-signal keywords before migration.
"""
import os
import shutil
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List, Tuple

# Mapping of current names to compliant names with high-signal keywords
RENAME_MAP: Dict[str, str] = {
    "canon_orchestrator.py": "canon_orchestration_manager.py",
    "constants.py": "agentic_constants.py",
    "core_utils.py": "core_utilities_handler.py",
    "core_utils_wrapper.py": "core_utilities_wrapper_handler.py",
    "orchestrator.py": "orchestration_engine.py",
    "orchestrator_main.py": "orchestration_main_handler.py",
    "proactive_audit.py": "proactive_auditor.py",
    "test_orphan.py": "test_orphan_handler.py"
}


def batch_rename_files(project_root: str, dry_run: bool = True) -> Tuple[int, int]:
    """
    Rename files to comply with Key 49 high-signal naming requirements.
    
    Args:
        project_root: Path to project root
        dry_run: If True, only simulate renames
    
    Returns:
        Tuple of (successful_renames, failed_renames)
    """
    root_path = Path(project_root).resolve()
    agentic_core = root_path / "agentic_core"
    
    if not agentic_core.exists():
        print(f"[X] Could not find agentic_core at {agentic_core}")
        return 0, 0
    
    print(f"\n{'='*70}")
    print(f"BATCH RENAME - {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"{'='*70}")
    print(f"[*] Renaming {len(RENAME_MAP)} files for Key 49 compliance\n")
    
    successful = 0
    failed = 0
    
    for old_name, new_name in RENAME_MAP.items():
        old_path = agentic_core / old_name
        new_path = agentic_core / new_name
        
        print(f"[→] {old_name}")
        print(f"    → {new_name}")
        
        if not old_path.exists():
            print(f"    [!] Source file not found, skipping")
            failed += 1
            continue
        
        if new_path.exists():
            print(f"    [!] Destination already exists, skipping")
            failed += 1
            continue
        
        if dry_run:
            print(f"    [DRY RUN] Would rename")
            successful += 1
        else:
            try:
                shutil.move(str(old_path), str(new_path))
                print(f"    [✓] Renamed successfully")
                successful += 1
            except Exception as e:
                print(f"    [!] Failed: {e}")
                failed += 1
    
    print(f"\n{'='*70}")
    print(f"RENAME SUMMARY")
    print(f"{'='*70}")
    print(f"Successful renames: {successful}")
    print(f"Failed renames: {failed}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"{'='*70}\n")
    
    return successful, failed


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch rename shallow files for Key 49 compliance"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute live rename (default is dry-run)"
    )
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    batch_rename_files(
        project_root=args.project_root,
        dry_run=not args.live
    )


if __name__ == "__main__":
    main()