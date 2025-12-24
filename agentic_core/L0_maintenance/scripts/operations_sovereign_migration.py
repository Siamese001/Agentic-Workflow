#!/usr/bin/env python3
"""
Sovereign Migration Script - Physical Path Remediation
Responsible for:
- Moving files from Depth 1 (agentic_core root) to Depth 3 (L-layers).
- Initializing missing __init__.py markers.
- Recording moves in the Mission Audit Log.
- Dry-run mode for safety validation.
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict
from typing import Any, Optional, Protocol, Dict, List

# Import SSOT heuristics from void_compliance
try:
    from agentic_core.runtime.shared.void_compliance import (
        get_placement_guidance,
        validate_file_location,
        validate_file_naming
    )
    from agentic_core.config.P1_core.structure_blueprint import SOVEREIGN_REGISTRY
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from agentic_core.runtime.shared.void_compliance import (
        get_placement_guidance,
        validate_file_location,
        validate_file_naming
    )
    from agentic_core.config.P1_core.structure_blueprint import SOVEREIGN_REGISTRY


class MigrationAuditLog:
    """Records all migration operations for rollback and compliance tracking."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.entries: List[Dict] = []
        self.timestamp = datetime.now().isoformat()
    
    def record_move(self, source: Path, destination: Path, success: bool, reason: str = ""):
        """Record a file move operation."""
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "move",
            "source": str(source),
            "destination": str(destination),
            "success": success,
            "reason": reason
        })
    
    def record_init_creation(self, init_path: Path, success: bool):
        """Record __init__.py creation."""
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "operation": "create_init",
            "path": str(init_path),
            "success": success
        })
    
    def save(self):
        """Persist audit log to disk."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump({
                "migration_timestamp": self.timestamp,
                "total_operations": len(self.entries),
                "operations": self.entries
            }, f, indent=2)
        print(f"\n[✓] Audit log saved: {self.log_path}")


def analyze_file_content(file_path: Path) -> Tuple[str, str]:
    """
    Analyze file content to determine best L-layer placement.
    Returns: (target_subpath, reasoning)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(3000)  # Read first 3000 chars for analysis
        
        # Use SSOT heuristics
        target_subpath = get_placement_guidance(content)
        
        # Enhanced reasoning based on content patterns
        reasoning_map = {
            "L1_cognition": "Strategic planning, reasoning, mission logic, or thought processing detected",
            "L3_orchestration": "Orchestration, routing, or hop management detected",
            "L4_state": "State management, memory, or persistence detected",
            "L5_safety": "Safety, guardrails, or security logic detected"
        }
        
        layer = target_subpath.split('/')[-1] if '/' in target_subpath else target_subpath
        reasoning = reasoning_map.get(layer, "Default cognition layer")
        
        return target_subpath, reasoning
        
    except Exception as e:
        return "agentic_core/L1_cognition", f"Error analyzing file: {e}"


def ensure_package_markers(target_path: Path, project_root: Path, audit_log: MigrationAuditLog):
    """
    Ensure all parent directories have __init__.py markers.
    Creates them if missing to maintain package integrity.
    """
    for parent in target_path.parents:
        if parent == project_root:
            break
        
        init_file = parent / "__init__.py"
        if not init_file.exists():
            try:
                init_file.write_text(
                    f'"""\n{parent.name} package initialization.\n"""\n',
                    encoding='utf-8'
                )
                audit_log.record_init_creation(init_file, success=True)
                print(f"   [+] Created: {init_file.relative_to(project_root)}")
            except Exception as e:
                audit_log.record_init_creation(init_file, success=False)
                print(f"   [!] Failed to create {init_file.name}: {e}")


def migrate_shallow_files(
    project_root: str,
    dry_run: bool = True,
    specific_files: List[str] = None
) -> Tuple[int, int, int]:
    """
    Main migration function.
    
    Args:
        project_root: Path to project root
        dry_run: If True, only simulate moves without executing
        specific_files: Optional list of specific filenames to migrate
    
    Returns:
        Tuple of (total_files, successful_moves, failed_moves)
    """
    root_path = Path(project_root).resolve()
    agentic_core = root_path / "agentic_core"
    
    if not agentic_core.exists():
        print(f"[X] Could not find agentic_core at {agentic_core}")
        return 0, 0, 0
    
    # Initialize audit log
    log_dir = root_path / "observability" / "logs" / "migrations"
    log_file = log_dir / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    audit_log = MigrationAuditLog(log_file)
    
    # Find all Python files directly in agentic_core root (Depth 1)
    shallow_files = [
        f for f in agentic_core.iterdir()
        if f.is_file() and f.suffix == ".py"
    ]
    
    # Filter to specific files if requested
    if specific_files:
        shallow_files = [f for f in shallow_files if f.name in specific_files]
    
    print(f"\n{'='*70}")
    print(f"SOVEREIGN MIGRATION - {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"{'='*70}")
    print(f"[*] Found {len(shallow_files)} shallow files requiring migration.\n")
    
    if not shallow_files:
        print("[✓] No shallow files found. Migration complete!")
        return 0, 0, 0
    
    successful_moves = 0
    failed_moves = 0
    
    for file_path in shallow_files:
        print(f"\n[→] Processing: {file_path.name}")
        
        try:
            # Analyze content to determine target location
            target_subpath, reasoning = analyze_file_content(file_path)
            target_dir = root_path / target_subpath
            destination = target_dir / file_path.name
            
            print(f"   Target: {target_subpath}")
            print(f"   Reason: {reasoning}")
            
            # Validate naming conventions before move
            is_name_valid, name_reason = validate_file_naming(destination, root_path)
            if not is_name_valid:
                print(f"   [!] NAMING VIOLATION: {name_reason}")
                audit_log.record_move(file_path, destination, success=False, reason=name_reason)
                failed_moves += 1
                continue
            
            # Check if destination already exists
            if destination.exists():
                print(f"   [!] CONFLICT: File already exists at destination")
                audit_log.record_move(
                    file_path, destination,
                    success=False,
                    reason="Destination file already exists"
                )
                failed_moves += 1
                continue
            
            if dry_run:
                print(f"   [DRY RUN] Would move to: {destination.relative_to(root_path)}")
                audit_log.record_move(file_path, destination, success=True, reason="Dry run")
                successful_moves += 1
            else:
                # Execute physical move
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(destination))
                
                # Ensure package markers exist
                ensure_package_markers(destination, root_path, audit_log)
                
                print(f"   [✓] Moved to: {destination.relative_to(root_path)}")
                audit_log.record_move(file_path, destination, success=True, reason=reasoning)
                successful_moves += 1
            
        except Exception as e:
            print(f"   [!] Failed: {e}")
            audit_log.record_move(
                file_path,
                Path("unknown"),
                success=False,
                reason=str(e)
            )
            failed_moves += 1
    
    # Save audit log
    audit_log.save()
    
    # Summary
    print(f"\n{'='*70}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total files processed: {len(shallow_files)}")
    print(f"Successful moves: {successful_moves}")
    print(f"Failed moves: {failed_moves}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print(f"{'='*70}\n")
    
    return len(shallow_files), successful_moves, failed_moves


def main():
    """CLI entry point with argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrate shallow files from agentic_core root to L-layers"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute live migration (default is dry-run)"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific files to migrate (optional)"
    )
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    migrate_shallow_files(
        project_root=args.project_root,
        dry_run=not args.live,
        specific_files=args.files
    )


if __name__ == "__main__":
    main()