#!/usr/bin/env python3
"""
Integrity Records Engine for Agentic-Workflow

Implements Phase 0.5 integrity records management for K8-K10 validation

Provides integrity record creation, validation, and management
for maintaining SSoT integrity across operations.
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IntegrityRecord:
    component: str
    operation: str
    timestamp: str
    hash_before: str
    hash_after: str
    status: str
    validated_by: str


class IntegrityRecordsEngine:
    """
    Integrity records management engine
    
    Creates, maintains, and validates integrity records
    for all SSoT operations and components.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.records_file = self.workspace_root / "02_schemas" / "integrity_records.json"
        
        # Add path for imports
        sys.path.insert(0, str(self.workspace_root / "02_schemas"))
        
        # Load semantic hash engine
        from semantic_hash_engine import SemanticHashEngine
        self.hash_engine = SemanticHashEngine(workspace_root)
        
        self.integrity_records: List[IntegrityRecord] = []
        self.current_state: Dict[str, str] = {}
    
    def initialize_integrity_records(self) -> bool:
        """Initialize integrity records for current SSoT state"""
        try:
            # Generate current hashes
            main_hash = self.hash_engine.generate_main_yaml_hashes()
            meta_hash = self.hash_engine.generate_meta_yaml_hashes()
            canonical_hash = self.hash_engine.generate_canonical_ssot_hashes()
            
            # Create initial state record
            initial_record = IntegrityRecord(
                component="initialization",
                operation="baseline_creation",
                timestamp=datetime.now().isoformat(),
                hash_before="",
                hash_after=f"{main_hash.content_hash}:{meta_hash.content_hash}:{canonical_hash.content_hash}",
                status="initialized",
                validated_by="integrity_records_engine"
            )
            
            self.integrity_records = [initial_record]
            self.current_state = {
                "main_yaml": main_hash.content_hash,
                "meta_yaml": meta_hash.content_hash,
                "canonical_ssot": canonical_hash.content_hash
            }
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize integrity records: {e}")
            return False
    
    def record_operation(self, component: str, operation: str, 
                        hash_before: str, hash_after: str) -> bool:
        """Record an operation with integrity tracking"""
        try:
            record = IntegrityRecord(
                component=component,
                operation=operation,
                timestamp=datetime.now().isoformat(),
                hash_before=hash_before,
                hash_after=hash_after,
                status="recorded",
                validated_by="integrity_records_engine"
            )
            
            self.integrity_records.append(record)
            return True
            
        except Exception as e:
            print(f"Failed to record operation: {e}")
            return False
    
    def validate_current_integrity(self) -> bool:
        """Validate current state against last recorded integrity"""
        try:
            if not self.integrity_records:
                return self.initialize_integrity_records()
            
            # Get current hashes
            main_hash = self.hash_engine.generate_main_yaml_hashes()
            meta_hash = self.hash_engine.generate_meta_yaml_hashes()
            canonical_hash = self.hash_engine.generate_canonical_ssot_hashes()
            
            current_hashes = {
                "main_yaml": main_hash.content_hash,
                "meta_yaml": meta_hash.content_hash,
                "canonical_ssot": canonical_hash.content_hash
            }
            
            # Compare with last record
            last_record = self.integrity_records[-1]
            expected_hashes = last_record.hash_after.split(":")
            
            if len(expected_hashes) >= 3:
                expected_main, expected_meta, expected_canonical = expected_hashes[:3]
                
                return (current_hashes["main_yaml"] == expected_main and
                       current_hashes["meta_yaml"] == expected_meta and
                       current_hashes["canonical_ssot"] == expected_canonical)
            
            return False
            
        except Exception as e:
            print(f"Failed to validate integrity: {e}")
            return False
    
    def create_integrity_snapshot(self, description: str = "") -> Dict[str, Any]:
        """Create integrity snapshot with current state"""
        try:
            # Generate current hashes
            main_hash = self.hash_engine.generate_main_yaml_hashes()
            meta_hash = self.hash_engine.generate_meta_yaml_hashes()
            canonical_hash = self.hash_engine.generate_canonical_ssot_hashes()
            
            snapshot = {
                "snapshot_timestamp": datetime.now().isoformat(),
                "description": description,
                "workspace_root": str(self.workspace_root),
                "component_hashes": {
                    "main_yaml": {
                        "path": main_hash.path,
                        "content_hash": main_hash.content_hash,
                        "semantic_hash": main_hash.semantic_hash
                    },
                    "meta_yaml": {
                        "path": meta_hash.path,
                        "content_hash": meta_hash.content_hash,
                        "semantic_hash": meta_hash.semantic_hash
                    },
                    "canonical_ssot": {
                        "path": canonical_hash.path,
                        "content_hash": canonical_hash.content_hash,
                        "semantic_hash": canonical_hash.semantic_hash
                    }
                },
                "integrity_status": "snapshot_created",
                "total_records": len(self.integrity_records)
            }
            
            return snapshot
            
        except Exception as e:
            raise ValueError(f"Failed to create integrity snapshot: {e}")
    
    def load_integrity_records(self) -> bool:
        """Load existing integrity records from file"""
        try:
            if self.records_file.exists():
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert records back to IntegrityRecord objects
                self.integrity_records = [
                    IntegrityRecord(**record) for record in data.get("records", [])
                ]
                
                self.current_state = data.get("current_state", {})
                return True
            else:
                return self.initialize_integrity_records()
                
        except Exception as e:
            print(f"Failed to load integrity records: {e}")
            return False
    
    def save_integrity_records(self) -> bool:
        """Save integrity records to file"""
        try:
            self.records_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "last_updated": datetime.now().isoformat(),
                "workspace_root": str(self.workspace_root),
                "current_state": self.current_state,
                "records": [
                    {
                        "component": r.component,
                        "operation": r.operation,
                        "timestamp": r.timestamp,
                        "hash_before": r.hash_before,
                        "hash_after": r.hash_after,
                        "status": r.status,
                        "validated_by": r.validated_by
                    }
                    for r in self.integrity_records
                ],
                "total_records": len(self.integrity_records)
            }
            
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Failed to save integrity records: {e}")
            return False
    
    def get_integrity_summary(self) -> Dict[str, Any]:
        """Get summary of integrity records"""
        if not self.integrity_records:
            self.load_integrity_records()
        
        operations_by_component = {}
        for record in self.integrity_records:
            component = record.component
            if component not in operations_by_component:
                operations_by_component[component] = []
            operations_by_component[component].append(record.operation)
        
        return {
            "total_records": len(self.integrity_records),
            "components_tracked": list(operations_by_component.keys()),
            "operations_by_component": operations_by_component,
            "last_operation": self.integrity_records[-1].timestamp if self.integrity_records else None,
            "integrity_valid": self.validate_current_integrity()
        }


def main():
    """CLI entry point for integrity records engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrity records engine for SSoT management")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--action", type=str, default="validate",
                       choices=["initialize", "validate", "snapshot", "summary"],
                       help="Action to perform")
    parser.add_argument("--description", type=str, default="",
                       help="Description for snapshot")
    
    args = parser.parse_args()
    
    engine = IntegrityRecordsEngine(args.workspace)
    
    try:
        if args.action == "initialize":
            success = engine.initialize_integrity_records()
            if success:
                engine.save_integrity_records()
                print("Integrity records initialized successfully")
            return 0 if success else 1
            
        elif args.action == "validate":
            engine.load_integrity_records()
            is_valid = engine.validate_current_integrity()
            print(f"Integrity validation: {'PASS' if is_valid else 'FAIL'}")
            return 0 if is_valid else 1
            
        elif args.action == "snapshot":
            engine.load_integrity_records()
            snapshot = engine.create_integrity_snapshot(args.description)
            
            snapshot_path = engine.workspace_root / "02_schemas" / "integrity_snapshot.json"
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
            print(f"Integrity snapshot created: {snapshot_path}")
            return 0
            
        elif args.action == "summary":
            engine.load_integrity_records()
            summary = engine.get_integrity_summary()
            print(f"Total records: {summary['total_records']}")
            print(f"Components tracked: {summary['components_tracked']}")
            print(f"Integrity valid: {summary['integrity_valid']}")
            return 0
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
