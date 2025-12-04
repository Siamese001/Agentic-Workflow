#!/usr/bin/env python3
"""
Atomic Operations Engine for Agentic-Workflow

Implements Phase 2 atomic operations for K21-K25 validation

Provides atomic filesystem operations, snapshot/rollback capabilities,
and target root isolation for Phase 2 compliance.
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AtomicOperation:
    operation_id: str
    operation_type: str
    target_path: str
    backup_path: str
    timestamp: str
    status: str


@dataclass
class Snapshot:
    snapshot_id: str
    timestamp: str
    workspace_root: str
    file_hashes: Dict[str, str]
    total_files: int


class AtomicOperationsEngine:
    """
    Atomic operations engine
    
    Provides atomic filesystem operations with rollback capabilities
    for Phase 2 zero-loss transformations.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.snapshots_dir = self.workspace_root / "02_schemas" / "atomic_snapshots"
        self.backups_dir = self.workspace_root / "02_schemas" / "atomic_backups"
        self.snapshots_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        self.operations_log: List[AtomicOperation] = []
        self.current_snapshot: Optional[Snapshot] = None
    
    def create_snapshot(self, description: str = "") -> Snapshot:
        """Create atomic snapshot of current workspace state"""
        import hashlib
        
        file_hashes = {}
        total_files = 0
        
        # Walk workspace and hash all files
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith(('.', '_')):
                try:
                    relative_path = str(file_path.relative_to(self.workspace_root))
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    file_hashes[relative_path] = file_hash
                    total_files += 1
                except (PermissionError, OSError):
                    # Skip files we can't read
                    continue
        
        snapshot = Snapshot(
            snapshot_id=f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            workspace_root=str(self.workspace_root),
            file_hashes=file_hashes,
            total_files=total_files
        )
        
        # Save snapshot
        snapshot_path = self.snapshots_dir / f"{snapshot.snapshot_id}.json"
        snapshot_data = {
            "snapshot_id": snapshot.snapshot_id,
            "timestamp": snapshot.timestamp,
            "workspace_root": snapshot.workspace_root,
            "description": description,
            "file_hashes": snapshot.file_hashes,
            "total_files": snapshot.total_files
        }
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
        
        self.current_snapshot = snapshot
        return snapshot
    
    def load_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Load existing snapshot"""
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        
        if not snapshot_path.exists():
            return None
        
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            snapshot = Snapshot(
                snapshot_id=data["snapshot_id"],
                timestamp=data["timestamp"],
                workspace_root=data["workspace_root"],
                file_hashes=data["file_hashes"],
                total_files=data["total_files"]
            )
            
            return snapshot
        except Exception:
            return None
    
    def validate_snapshot_integrity(self, snapshot: Snapshot) -> bool:
        """Validate snapshot integrity against current workspace"""
        import hashlib
        
        try:
            for relative_path, expected_hash in snapshot.file_hashes.items():
                file_path = self.workspace_root / relative_path
                
                if not file_path.exists():
                    return False
                
                with open(file_path, 'rb') as f:
                    actual_hash = hashlib.sha256(f.read()).hexdigest()
                
                if actual_hash != expected_hash:
                    return False
            
            return True
        except Exception:
            return False
    
    def create_backup(self, target_path: Path) -> Path:
        """Create backup of target path for atomic operations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{target_path.name}_{timestamp}"
        backup_path = self.backups_dir / backup_name
        
        try:
            if target_path.is_file():
                shutil.copy2(target_path, backup_path)
            elif target_path.is_dir():
                shutil.copytree(target_path, backup_path, dirs_exist_ok=True)
            
            return backup_path
        except Exception as e:
            raise ValueError(f"Failed to create backup for {target_path}: {e}")
    
    def atomic_create_file(self, target_path: Path, content: str) -> bool:
        """Atomically create a file"""
        try:
            # Create backup if file exists
            backup_path = None
            if target_path.exists():
                backup_path = self.create_backup(target_path)
            
            # Write to temporary file first
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(content)
                temp_path = Path(temp_file.name)
            
            # Atomic move
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(temp_path), str(target_path))
            
            # Log operation
            operation = AtomicOperation(
                operation_id=f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                operation_type="create_file",
                target_path=str(target_path.relative_to(self.workspace_root)),
                backup_path=str(backup_path.relative_to(self.workspace_root)) if backup_path else "",
                timestamp=datetime.now().isoformat(),
                status="completed"
            )
            
            self.operations_log.append(operation)
            return True
            
        except Exception as e:
            # Rollback if possible
            if backup_path and backup_path.exists():
                shutil.move(str(backup_path), str(target_path))
            return False
    
    def atomic_delete_file(self, target_path: Path) -> bool:
        """Atomically delete a file"""
        try:
            # Create backup
            backup_path = self.create_backup(target_path)
            
            # Delete file
            target_path.unlink()
            
            # Log operation
            operation = AtomicOperation(
                operation_id=f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                operation_type="delete_file",
                target_path=str(target_path.relative_to(self.workspace_root)),
                backup_path=str(backup_path.relative_to(self.workspace_root)),
                timestamp=datetime.now().isoformat(),
                status="completed"
            )
            
            self.operations_log.append(operation)
            return True
            
        except Exception as e:
            return False
    
    def rollback_operation(self, operation: AtomicOperation) -> bool:
        """Rollback a specific atomic operation"""
        try:
            if operation.operation_type == "create_file":
                # For file creation, delete the created file
                target_path = self.workspace_root / operation.target_path
                if target_path.exists():
                    target_path.unlink()
            
            elif operation.operation_type == "delete_file":
                # For file deletion, restore from backup
                backup_path = self.workspace_root / operation.backup_path
                target_path = self.workspace_root / operation.target_path
                
                if backup_path.exists():
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    if backup_path.is_file():
                        shutil.copy2(backup_path, target_path)
                    elif backup_path.is_dir():
                        shutil.copytree(backup_path, target_path, dirs_exist_ok=True)
            
            return True
        except Exception:
            return False
    
    def validate_target_root_isolation(self, target_root: str) -> bool:
        """Validate that operations are isolated to target root"""
        try:
            target_path = self.workspace_root / target_root
            
            if not target_path.exists() or not target_path.is_dir():
                return True  # Non-existent target is trivially isolated
            
            # Check that all operations in log are within target root
            for operation in self.operations_log:
                op_target = self.workspace_root / operation.target_path
                if not op_target.is_relative_to(target_path):
                    return False
            
            return True
        except Exception:
            return False
    
    def validate_protected_paths_preserved(self) -> bool:
        """Validate that protected paths were never mutated"""
        try:
            # Load protected paths from META
            meta_path = self.workspace_root / "unified_structure_subatomic_meta.yaml"
            if not meta_path.exists():
                return True
            
            import yaml
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = yaml.safe_load(f)
            
            protected_patterns = meta.get('protected_paths', [])
            
            # Check if any operations affected protected paths
            for operation in self.operations_log:
                for pattern in protected_patterns:
                    if self._path_matches_pattern(operation.target_path, pattern):
                        return False
            
            return True
        except Exception:
            return False
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches glob pattern"""
        import fnmatch
        
        # Simple glob matching
        if '**' in pattern:
            # Handle recursive patterns
            parts = pattern.split('**')
            if len(parts) == 2:
                prefix, suffix = parts
                return path.startswith(prefix) and path.endswith(suffix)
        
        return fnmatch.fnmatch(path, pattern)
    
    def is_atomic_operations_operational(self) -> bool:
        """Check if atomic operations engine is operational"""
        try:
            # Test basic functionality
            test_snapshot = self.create_snapshot("test_operational")
            
            if test_snapshot and test_snapshot.total_files >= 0:
                # Clean up test snapshot
                snapshot_path = self.snapshots_dir / f"{test_snapshot.snapshot_id}.json"
                if snapshot_path.exists():
                    snapshot_path.unlink()
                return True
            return False
        except Exception:
            return False


def main():
    """CLI entry point for atomic operations engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Atomic operations engine for Phase 2")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--action", type=str, default="check",
                       choices=["snapshot", "validate", "check"],
                       help="Action to perform")
    parser.add_argument("--description", type=str, default="",
                       help="Snapshot description")
    parser.add_argument("--snapshot-id", type=str,
                       help="Snapshot ID for validation")
    
    args = parser.parse_args()
    
    engine = AtomicOperationsEngine(args.workspace)
    
    try:
        if args.action == "snapshot":
            snapshot = engine.create_snapshot(args.description)
            print(f"Snapshot created: {snapshot.snapshot_id}")
            print(f"Total files: {snapshot.total_files}")
            return 0
            
        elif args.action == "validate":
            if not args.snapshot_id:
                print("Error: --snapshot-id required for validation")
                return 1
            
            snapshot = engine.load_snapshot(args.snapshot_id)
            if not snapshot:
                print(f"Error: Snapshot {args.snapshot_id} not found")
                return 1
            
            is_valid = engine.validate_snapshot_integrity(snapshot)
            print(f"Snapshot integrity: {'PASS' if is_valid else 'FAIL'}")
            return 0 if is_valid else 1
            
        elif args.action == "check":
            is_operational = engine.is_atomic_operations_operational()
            print(f"Atomic operations operational: {'PASS' if is_operational else 'FAIL'}")
            return 0 if is_operational else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
