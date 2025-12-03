#!/usr/bin/env python3
"""
Rollback Engine for Agentic-Workflow

Implements Phase 2 rollback capabilities for K26-K30 validation

Provides rollback functionality, state restoration, and
operation reversal for Phase 2 atomic operations.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RollbackPoint:
    rollback_id: str
    timestamp: str
    description: str
    operations_count: int
    backup_location: str
    can_rollback: bool


class RollbackEngine:
    """
    Rollback engine for atomic operations
    
    Provides comprehensive rollback capabilities for Phase 2
    atomic operations with full state restoration.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.rollback_points_dir = self.workspace_root / "02_schemas" / "rollback_points"
        self.rollback_points_dir.mkdir(exist_ok=True)
        
        self.rollback_points: List[RollbackPoint] = []
        self.current_rollback_point: Optional[RollbackPoint] = None
    
    def create_rollback_point(self, description: str = "") -> RollbackPoint:
        """Create a rollback point with current workspace state"""
        rollback_id = f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        backup_location = self.rollback_points_dir / rollback_id
        backup_location.mkdir(exist_ok=True)
        
        # Copy entire workspace to backup location (excluding system files)
        copied_files = 0
        for item in self.workspace_root.rglob("*"):
            if item.is_file() and not any(part.startswith(('.', '_')) for part in item.parts):
                try:
                    relative_path = item.relative_to(self.workspace_root)
                    backup_path = backup_location / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, backup_path)
                    copied_files += 1
                except (PermissionError, OSError):
                    continue
        
        rollback_point = RollbackPoint(
            rollback_id=rollback_id,
            timestamp=datetime.now().isoformat(),
            description=description,
            operations_count=copied_files,
            backup_location=str(backup_location),
            can_rollback=True
        )
        
        # Save rollback point metadata
        metadata = {
            "rollback_id": rollback_point.rollback_id,
            "timestamp": rollback_point.timestamp,
            "description": rollback_point.description,
            "operations_count": rollback_point.operations_count,
            "backup_location": rollback_point.backup_location,
            "can_rollback": rollback_point.can_rollback
        }
        
        metadata_path = backup_location / "rollback_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        self.rollback_points.append(rollback_point)
        self.current_rollback_point = rollback_point
        
        return rollback_point
    
    def load_rollback_point(self, rollback_id: str) -> Optional[RollbackPoint]:
        """Load existing rollback point"""
        backup_location = self.rollback_points_dir / rollback_id
        metadata_path = backup_location / "rollback_metadata.json"
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            rollback_point = RollbackPoint(
                rollback_id=metadata["rollback_id"],
                timestamp=metadata["timestamp"],
                description=metadata["description"],
                operations_count=metadata["operations_count"],
                backup_location=metadata["backup_location"],
                can_rollback=metadata["can_rollback"]
            )
            
            return rollback_point
        except Exception:
            return None
    
    def execute_rollback(self, rollback_id: str) -> bool:
        """Execute rollback to specified rollback point"""
        try:
            rollback_point = self.load_rollback_point(rollback_id)
            if not rollback_point:
                return False
            
            backup_location = Path(rollback_point.backup_location)
            if not backup_location.exists():
                return False
            
            # Restore files from backup
            restored_files = 0
            for backup_file in backup_location.rglob("*"):
                if backup_file.is_file() and backup_file.name != "rollback_metadata.json":
                    try:
                        relative_path = backup_file.relative_to(backup_location)
                        target_path = self.workspace_root / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(backup_file, target_path)
                        restored_files += 1
                    except (PermissionError, OSError):
                        continue
            
            return restored_files > 0
            
        except Exception:
            return False
    
    def validate_rollback_integrity(self, rollback_id: str) -> bool:
        """Validate that rollback point is intact and usable"""
        try:
            rollback_point = self.load_rollback_point(rollback_id)
            if not rollback_point:
                return False
            
            backup_location = Path(rollback_point.backup_location)
            if not backup_location.exists():
                return False
            
            # Check metadata exists
            metadata_path = backup_location / "rollback_metadata.json"
            if not metadata_path.exists():
                return False
            
            # Count backup files
            backup_files = sum(1 for f in backup_location.rglob("*") 
                             if f.is_file() and f.name != "rollback_metadata.json")
            
            return backup_files > 0
            
        except Exception:
            return False
    
    def list_rollback_points(self) -> List[RollbackPoint]:
        """List all available rollback points"""
        rollback_points = []
        
        for backup_dir in self.rollback_points_dir.iterdir():
            if backup_dir.is_dir():
                rollback_point = self.load_rollback_point(backup_dir.name)
                if rollback_point:
                    rollback_points.append(rollback_point)
        
        return sorted(rollback_points, key=lambda x: x.timestamp, reverse=True)
    
    def cleanup_rollback_point(self, rollback_id: str) -> bool:
        """Clean up specified rollback point"""
        try:
            rollback_point = self.load_rollback_point(rollback_id)
            if not rollback_point:
                return False
            
            backup_location = Path(rollback_point.backup_location)
            if backup_location.exists():
                shutil.rmtree(backup_location)
            
            # Remove from internal list
            self.rollback_points = [rp for rp in self.rollback_points 
                                   if rp.rollback_id != rollback_id]
            
            return True
        except Exception:
            return False
    
    def validate_rollback_functionality(self) -> bool:
        """Validate rollback functionality with test operation"""
        try:
            # Create test rollback point
            test_rollback = self.create_rollback_point("test_rollback_functionality")
            
            # Validate rollback point
            is_valid = self.validate_rollback_integrity(test_rollback.rollback_id)
            
            # Clean up test rollback point
            self.cleanup_rollback_point(test_rollback.rollback_id)
            
            return is_valid
        except Exception:
            return False
    
    def is_rollback_engine_operational(self) -> bool:
        """Check if rollback engine is operational"""
        try:
            # Test basic functionality
            return self.validate_rollback_functionality()
        except Exception:
            return False


def main():
    """CLI entry point for rollback engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rollback engine for Phase 2 operations")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--action", type=str, default="check",
                       choices=["create", "rollback", "list", "validate", "check"],
                       help="Action to perform")
    parser.add_argument("--rollback-id", type=str,
                       help="Rollback point ID")
    parser.add_argument("--description", type=str, default="",
                       help="Description for rollback point")
    
    args = parser.parse_args()
    
    engine = RollbackEngine(args.workspace)
    
    try:
        if args.action == "create":
            rollback_point = engine.create_rollback_point(args.description)
            print(f"Rollback point created: {rollback_point.rollback_id}")
            print(f"Files backed up: {rollback_point.operations_count}")
            return 0
            
        elif args.action == "rollback":
            if not args.rollback_id:
                print("Error: --rollback-id required for rollback action")
                return 1
            
            success = engine.execute_rollback(args.rollback_id)
            print(f"Rollback execution: {'SUCCESS' if success else 'FAILED'}")
            return 0 if success else 1
            
        elif args.action == "list":
            rollback_points = engine.list_rollback_points()
            print(f"Available rollback points: {len(rollback_points)}")
            for rp in rollback_points:
                print(f"  {rp.rollback_id} - {rp.timestamp} - {rp.description}")
            return 0
            
        elif args.action == "validate":
            if not args.rollback_id:
                print("Error: --rollback-id required for validation")
                return 1
            
            is_valid = engine.validate_rollback_integrity(args.rollback_id)
            print(f"Rollback point integrity: {'PASS' if is_valid else 'FAIL'}")
            return 0 if is_valid else 1
            
        elif args.action == "check":
            is_operational = engine.is_rollback_engine_operational()
            print(f"Rollback engine operational: {'PASS' if is_operational else 'FAIL'}")
            return 0 if is_operational else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
