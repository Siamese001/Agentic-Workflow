#!/usr/bin/env python3
"""
Sovereign Migration Script - L2_execution Alignment
Moves Depth 2 'module' folders into Depth 3 L-layers to comply with Key 41.
Resolves shallow violations for action_node_modules and action_registry_modules.
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


def migrate_to_l2_execution(project_root: str, dry_run: bool = True) -> Tuple[int, int]:
    """
    Migrate depth 2 module folders to L2_execution/tools.
    
    Args:
        project_root: Path to project root
        dry_run: If True, only simulate moves
    
    Returns:
        Tuple of (successful_moves, failed_moves)
    """
    root = Path(project_root).resolve()
    agentic_core = root / "agentic_core"
    
    if not agentic_core.exists():
        print(f"[X] Could not find agentic_core at {agentic_core}")
        return 0, 0
    
    # Target for all action/registry logic
    target_base = agentic_core / "L2_execution" / "tools"
    
    # Folders identified as "Shallow Violations" (Depth 2)
    problem_folders = ["action_node_modules", "action_registry_modules"]
    
    print(f"\n{'='*70}")
    print(f"L2_EXECUTION MIGRATION - {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"{'='*70}")
    print(f"[*] Migrating depth 2 module folders to L2_execution/tools\n")
    
    successful_moves = 0
    failed_moves = 0
    total_files = 0
    
    # Create audit log
    log_dir = root / "observability" / "logs" / "migrations"
    log_file = log_dir / f"l2_execution_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    audit_entries = []
    
    for folder_name in problem_folders:
        source_dir = agentic_core / folder_name
        
        if not source_dir.exists():
            print(f"[!] Folder {folder_name} not found, skipping")
            continue
        
        print(f"\n[→] Processing: {folder_name}")
        
        # Find all Python files in the source directory
        py_files = list(source_dir.glob("*.py"))
        
        if not py_files:
            print(f"   [!] No Python files found in {folder_name}")
            continue
        
        print(f"   Found {len(py_files)} Python files")
        total_files += len(py_files)
        
        for file_path in py_files:
            dest = target_base / file_path.name
            
            print(f"   [→] {file_path.name}")
            
            # Check if destination already exists
            if dest.exists():
                print(f"      [!] CONFLICT: File already exists at destination")
                audit_entries.append({
                    "timestamp": datetime.now().isoformat(),
                    "operation": "move",
                    "source": str(file_path),
                    "destination": str(dest),
                    "success": False,
                    "reason": "Destination file already exists"
                })
                failed_moves += 1
                continue
            
            if dry_run:
                print(f"      [DRY RUN] Would move to: {dest.relative_to(root)}")
                audit_entries.append({
                    "timestamp": datetime.now().isoformat(),
                    "operation": "move",
                    "source": str(file_path),
                    "destination": str(dest),
                    "success": True,
                    "reason": "Dry run"
                })
                successful_moves += 1
            else:
                try:
                    # Create target directory if needed
                    target_base.mkdir(parents=True, exist_ok=True)
                    
                    # Ensure __init__.py exists in all parent directories
                    for parent in dest.parents:
                        if parent == root:
                            break
                        init_file = parent / "__init__.py"
                        if not init_file.exists():
                            init_file.write_text(
                                f'"""\n{parent.name} package initialization.\n"""\n',
                                encoding='utf-8'
                            )
                    
                    # Execute move
                    shutil.move(str(file_path), str(dest))
                    print(f"      [✓] Moved to: {dest.relative_to(root)}")
                    
                    audit_entries.append({
                        "timestamp": datetime.now().isoformat(),
                        "operation": "move",
                        "source": str(file_path),
                        "destination": str(dest),
                        "success": True,
                        "reason": "Depth 2 → Depth 3 migration"
                    })
                    successful_moves += 1
                    
                except Exception as e:
                    print(f"      [!] Failed: {e}")
                    audit_entries.append({
                        "timestamp": datetime.now().isoformat(),
                        "operation": "move",
                        "source": str(file_path),
                        "destination": str(dest),
                        "success": False,
                        "reason": str(e)
                    })
                    failed_moves += 1
        
        # Cleanup empty shallow folder (only in live mode)
        if not dry_run and source_dir.exists():
            try:
                remaining_files = list(source_dir.glob("*"))
                if not remaining_files:
                    source_dir.rmdir()
                    print(f"   [✓] Removed empty folder: {folder_name}")
                    audit_entries.append({
                        "timestamp": datetime.now().isoformat(),
                        "operation": "cleanup",
                        "path": str(source_dir),
                        "success": True,
                        "reason": "Empty folder removed"
                    })
                else:
                    print(f"   [!] Folder {folder_name} not empty ({len(remaining_files)} items), skipping delete")
            except OSError as e:
                print(f"   [!] Could not remove {folder_name}: {e}")
    
    # Save audit log
    if audit_entries:
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                "migration_timestamp": datetime.now().isoformat(),
                "total_files": total_files,
                "successful_moves": successful_moves,
                "failed_moves": failed_moves,
                "operations": audit_entries
            }, f, indent=2)
        print(f"\n[✓] Audit log saved: {log_file}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total files processed: {total_files}")
    print(f"Successful moves: {successful_moves}")
    print(f"Failed moves: {failed_moves}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"{'='*70}\n")
    
    return successful_moves, failed_moves


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate depth 2 module folders to L2_execution/tools"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute live migration (default is dry-run)"
    )
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    migrate_to_l2_execution(
        project_root=args.project_root,
        dry_run=not args.live
    )


if __name__ == "__main__":
    main()
