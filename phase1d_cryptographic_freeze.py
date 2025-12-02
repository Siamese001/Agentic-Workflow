#!/usr/bin/env python3
"""
Phase 1D Cryptographic Freeze Script
Computes deterministic cryptographic snapshot of schemas/ directory
Creates migration_report.json with SHA-256 hashes and metadata
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any

class Phase1DCryptographicFreeze:
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.migration_report_path = self.schemas_dir / "migration_report.json"
        
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file content"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def get_file_size_bytes(self, file_path: Path) -> int:
        """Get file size in bytes"""
        return file_path.stat().st_size
    
    def collect_all_schema_files(self) -> Dict[str, Dict[str, Any]]:
        """Collect all files under schemas/ except migration_report.json"""
        files_data = {}
        
        # Walk through all files in schemas directory
        for file_path in self.schemas_dir.rglob("*"):
            # Skip directories, __pycache__, and the migration report itself
            if (file_path.is_file() and 
                file_path.name != "migration_report.json" and
                file_path.suffix == ".py" and
                "__pycache__" not in file_path.parts):
                
                # Get relative path from schemas/ with forward slashes
                relative_path = file_path.relative_to(self.schemas_dir).as_posix()
                
                # Compute hash and size
                sha256_hash = self.compute_file_hash(file_path)
                size_bytes = self.get_file_size_bytes(file_path)
                
                files_data[relative_path] = {
                    "sha256": sha256_hash,
                    "size_bytes": size_bytes
                }
        
        return files_data
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate the migration report with deterministic structure"""
        files_data = self.collect_all_schema_files()
        
        # Sort file keys lexicographically for determinism
        sorted_files = dict(sorted(files_data.items()))
        
        migration_report = {
            "schema_version": "v1",
            "root": "schemas/",
            "files": sorted_files
        }
        
        return migration_report
    
    def write_migration_report(self, migration_report: Dict[str, Any]) -> None:
        """Write migration report to JSON file with deterministic formatting"""
        # Use ensure_ascii=False and separators for consistent formatting
        json_content = json.dumps(
            migration_report,
            indent=2,
            ensure_ascii=False,
            separators=(',', ': '),
            sort_keys=True
        )
        
        with open(self.migration_report_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
    
    def validate_migration_report(self) -> bool:
        """Validate the generated migration report meets all requirements"""
        try:
            # Check if file exists and is valid JSON
            if not self.migration_report_path.exists():
                return False
            
            with open(self.migration_report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            # Validate required fields
            required_fields = ["schema_version", "root", "files"]
            for field in required_fields:
                if field not in report:
                    return False
            
            # Validate schema version
            if report["schema_version"] != "v1":
                return False
            
            # Validate root path
            if report["root"] != "schemas/":
                return False
            
            # Validate files field is object
            if not isinstance(report["files"], dict):
                return False
            
            # Validate each file entry
            for file_path, file_data in report["files"].items():
                if not isinstance(file_data, dict):
                    return False
                
                if "sha256" not in file_data or "size_bytes" not in file_data:
                    return False
                
                # Validate SHA-256 format (64 hex characters)
                sha256 = file_data["sha256"]
                if not isinstance(sha256, str) or len(sha256) != 64 or not all(c in "0123456789abcdef" for c in sha256.lower()):
                    return False
                
                # Validate size_bytes is non-negative integer
                size_bytes = file_data["size_bytes"]
                if not isinstance(size_bytes, int) or size_bytes < 0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def execute_freeze(self) -> bool:
        """Execute the complete cryptographic freeze process"""
        print("Phase 1D Cryptographic Freeze")
        print("=" * 40)
        
        # Generate migration report
        print("Computing hashes and generating migration report...")
        migration_report = self.generate_migration_report()
        
        # Write migration report
        print(f"Writing migration report to {self.migration_report_path}...")
        self.write_migration_report(migration_report)
        
        # Validate the report
        print("Validating migration report...")
        if self.validate_migration_report():
            print("✅ Migration report validation passed")
            print(f"✅ Generated report with {len(migration_report['files'])} files")
            return True
        else:
            print("❌ Migration report validation failed")
            return False

def main():
    freezer = Phase1DCryptographicFreeze()
    success = freezer.execute_freeze()
    
    if success:
        print("\n🎉 PHASE 1D CRYPTOGRAPHIC FREEZE COMPLETED SUCCESSFULLY! 🎉")
        return 0
    else:
        print("\n❌ PHASE 1D CRYPTOGRAPHIC FREEZE FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
