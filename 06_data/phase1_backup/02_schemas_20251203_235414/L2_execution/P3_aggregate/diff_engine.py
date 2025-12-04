#!/usr/bin/env python3
"""
Diff Engine for Agentic-Workflow

Implements Phase 1 filesystem diff capabilities for K18-K20 validation

Provides filesystem structure comparison, change detection,
and diff generation for Phase 1 operations.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiffResult:
    added_paths: List[str]
    removed_paths: List[str]
    modified_paths: List[str]
    unchanged_paths: List[str]
    total_changes: int
    timestamp: str


class DiffEngine:
    """
    Filesystem diff engine
    
    Compares filesystem structures and generates detailed diffs
    for Phase 1 change tracking and validation.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.snapshot_dir = self.workspace_root / "02_schemas" / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)
        
        # Add path for imports
        sys.path.insert(0, str(self.workspace_root / "02_schemas"))
    
    def extract_structure_snapshot(self, structure: Dict[str, Any], prefix: str = "") -> Set[str]:
        """Extract all paths from structure as a set"""
        paths = set()
        
        for key, value in structure.items():
            current_path = f"{prefix}/{key}" if prefix else key
            
            if isinstance(value, dict) and value:
                # Non-empty directory - recurse
                paths.add(current_path + "/")
                paths.update(self.extract_structure_snapshot(value, current_path))
            elif value is None or (isinstance(value, dict) and not value):
                # File or empty directory
                paths.add(current_path)
        
        return paths
    
    def capture_workspace_snapshot(self, name: str) -> Dict[str, Any]:
        """Capture current workspace structure snapshot"""
        def build_structure(path: Path, prefix: str = "") -> Dict[str, Any]:
            structure = {}
            
            try:
                for item in sorted(path.iterdir()):
                    # Skip system files and directories
                    if item.name.startswith(('.', '_')):
                        continue
                    
                    if item.is_dir():
                        # Directory - recurse
                        structure[item.name] = build_structure(item, f"{prefix}/{item.name}" if prefix else item.name)
                    elif item.is_file():
                        # File - represent as null
                        structure[item.name] = None
            except PermissionError:
                # Skip directories we can't access
                pass
            
            return structure
        
        workspace_structure = build_structure(self.workspace_root)
        
        snapshot = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "structure": workspace_structure,
            "total_paths": len(self.extract_structure_snapshot(workspace_structure))
        }
        
        # Save snapshot
        snapshot_path = self.snapshot_dir / f"{name}.json"
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        return snapshot
    
    def load_snapshot(self, name: str) -> Dict[str, Any]:
        """Load a previously saved snapshot"""
        snapshot_path = self.snapshot_dir / f"{name}.json"
        
        if not snapshot_path.exists():
            raise ValueError(f"Snapshot {name} not found")
        
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def compare_structures(self, structure1: Dict[str, Any], structure2: Dict[str, Any]) -> DiffResult:
        """Compare two structures and generate diff"""
        paths1 = self.extract_structure_snapshot(structure1)
        paths2 = self.extract_structure_snapshot(structure2)
        
        added = sorted(list(paths2 - paths1))
        removed = sorted(list(paths1 - paths2))
        unchanged = sorted(list(paths1 & paths2))
        
        # For modified paths, we'd need content comparison - for now, assume no modifications
        # since we're only tracking structure
        modified = []
        
        return DiffResult(
            added_paths=added,
            removed_paths=removed,
            modified_paths=modified,
            unchanged_paths=unchanged,
            total_changes=len(added) + len(removed) + len(modified),
            timestamp=datetime.now().isoformat()
        )
    
    def generate_diff_report(self, snapshot1_name: str, snapshot2_name: str) -> Dict[str, Any]:
        """Generate comprehensive diff report between two snapshots"""
        try:
            snapshot1 = self.load_snapshot(snapshot1_name)
            snapshot2 = self.load_snapshot(snapshot2_name)
            
            diff_result = self.compare_structures(snapshot1["structure"], snapshot2["structure"])
            
            report = {
                "comparison": {
                    "snapshot1": {
                        "name": snapshot1["name"],
                        "timestamp": snapshot1["timestamp"]
                    },
                    "snapshot2": {
                        "name": snapshot2["name"],
                        "timestamp": snapshot2["timestamp"]
                    }
                },
                "diff_results": {
                    "added_paths": diff_result.added_paths,
                    "removed_paths": diff_result.removed_paths,
                    "modified_paths": diff_result.modified_paths,
                    "unchanged_paths": diff_result.unchanged_paths,
                    "total_changes": diff_result.total_changes
                },
                "summary": {
                    "paths_added": len(diff_result.added_paths),
                    "paths_removed": len(diff_result.removed_paths),
                    "paths_modified": len(diff_result.modified_paths),
                    "paths_unchanged": len(diff_result.unchanged_paths),
                    "net_change": len(diff_result.added_paths) - len(diff_result.removed_paths)
                },
                "generated_at": diff_result.timestamp
            }
            
            return report
            
        except Exception as e:
            raise ValueError(f"Failed to generate diff report: {e}")
    
    def save_diff_report(self, snapshot1_name: str, snapshot2_name: str, 
                        output_path: Optional[Path] = None) -> Path:
        """Save diff report to file"""
        if output_path is None:
            output_path = self.snapshot_dir / f"diff_{snapshot1_name}_vs_{snapshot2_name}.json"
        
        report = self.generate_diff_report(snapshot1_name, snapshot2_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def validate_no_structural_changes(self, baseline_snapshot: str) -> bool:
        """Validate that no structural changes have occurred since baseline"""
        try:
            baseline = self.load_snapshot(baseline_snapshot)
            current = self.capture_workspace_snapshot("current_validation")
            
            diff = self.compare_structures(baseline["structure"], current["structure"])
            
            # Clean up current validation snapshot
            current_snapshot_path = self.snapshot_dir / "current_validation.json"
            if current_snapshot_path.exists():
                current_snapshot_path.unlink()
            
            return diff.total_changes == 0
            
        except Exception:
            return False
    
    def is_diff_engine_operational(self) -> bool:
        """Check if diff engine is operational"""
        try:
            # Test basic functionality
            test_snapshot = self.capture_workspace_snapshot("test_operational")
            
            # Clean up test snapshot
            test_snapshot_path = self.snapshot_dir / "test_operational.json"
            if test_snapshot_path.exists():
                test_snapshot_path.unlink()
            
            return True
        except Exception:
            return False


def main():
    """CLI entry point for diff engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Diff engine for Phase 1 operations")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--action", type=str, default="check",
                       choices=["snapshot", "diff", "validate", "check"],
                       help="Action to perform")
    parser.add_argument("--name", type=str,
                       help="Snapshot name")
    parser.add_argument("--snapshot1", type=str,
                       help="First snapshot name")
    parser.add_argument("--snapshot2", type=str,
                       help="Second snapshot name")
    parser.add_argument("--baseline", type=str,
                       help="Baseline snapshot for validation")
    
    args = parser.parse_args()
    
    engine = DiffEngine(args.workspace)
    
    try:
        if args.action == "snapshot":
            if not args.name:
                print("Error: --name required for snapshot action")
                return 1
            
            snapshot = engine.capture_workspace_snapshot(args.name)
            print(f"Snapshot '{args.name}' created with {snapshot['total_paths']} paths")
            return 0
            
        elif args.action == "diff":
            if not args.snapshot1 or not args.snapshot2:
                print("Error: --snapshot1 and --snapshot2 required for diff action")
                return 1
            
            output_path = engine.save_diff_report(args.snapshot1, args.snapshot2)
            print(f"Diff report generated: {output_path}")
            return 0
            
        elif args.action == "validate":
            if not args.baseline:
                print("Error: --baseline required for validate action")
                return 1
            
            is_valid = engine.validate_no_structural_changes(args.baseline)
            print(f"No structural changes: {'PASS' if is_valid else 'FAIL'}")
            return 0 if is_valid else 1
            
        elif args.action == "check":
            is_operational = engine.is_diff_engine_operational()
            print(f"Diff engine operational: {'PASS' if is_operational else 'FAIL'}")
            return 0 if is_operational else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
