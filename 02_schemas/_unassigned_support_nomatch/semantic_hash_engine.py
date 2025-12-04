#!/usr/bin/env python3
"""
Semantic Hash Engine for Agentic-Workflow

Implements Phase 0.5 semantic hashing capabilities for K7-K10 validation

Provides semantic hash generation, integrity records, and validation
for the SSoT structure and metadata.
"""

import hashlib
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SemanticHash:
    path: str
    content_hash: str
    semantic_hash: str
    timestamp: str
    integrity_level: str


class SemanticHashEngine:
    """
    Semantic hash generation and validation engine
    
    Generates content hashes, semantic hashes, and maintains
    integrity records for SSoT validation.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.main_yaml_path = self.workspace_root / "unified_structure_subatomic.yaml"
        self.meta_yaml_path = self.workspace_root / "unified_structure_subatomic_meta.yaml"
        
        # Add path for imports
        sys.path.insert(0, str(self.workspace_root / "02_schemas"))
        
        # Load SSoT merger for canonical structure
        from ssot_merger import SSoTMerger
        self.ssot_merger = SSoTMerger(workspace_root)
        
        self.semantic_hashes: List[SemanticHash] = []
        self.integrity_records: Dict[str, Any] = {}
    
    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 content hash"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def generate_semantic_hash(self, structure: Dict[str, Any]) -> str:
        """Generate semantic hash based on structure keys and organization"""
        # Extract semantic structure (keys only, ignoring values)
        semantic_structure = self._extract_semantic_structure(structure)
        
        # Convert to deterministic JSON string
        semantic_json = json.dumps(semantic_structure, sort_keys=True, separators=(',', ':'))
        
        return hashlib.sha256(semantic_json.encode('utf-8')).hexdigest()
    
    def _extract_semantic_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Extract semantic structure (keys and types) from YAML structure"""
        if not isinstance(structure, dict):
            return {}
        
        semantic = {}
        
        for key, value in structure.items():
            if isinstance(value, dict):
                semantic[key] = self._extract_semantic_structure(value)
            elif value is None:
                semantic[key] = "file"
            elif isinstance(value, str):
                semantic[key] = "string_content"
            elif isinstance(value, list):
                semantic[key] = "list"
            else:
                semantic[key] = type(value).__name__
        
        return semantic
    
    def generate_main_yaml_hashes(self) -> SemanticHash:
        """Generate hashes for main YAML file"""
        try:
            with open(self.main_yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            structure = yaml.safe_load(content)
            
            content_hash = self.generate_content_hash(content)
            semantic_hash = self.generate_semantic_hash(structure)
            
            hash_record = SemanticHash(
                path=str(self.main_yaml_path.relative_to(self.workspace_root)),
                content_hash=content_hash,
                semantic_hash=semantic_hash,
                timestamp=datetime.now().isoformat(),
                integrity_level="canonical_ssot"
            )
            
            return hash_record
            
        except Exception as e:
            raise ValueError(f"Failed to generate main YAML hashes: {e}")
    
    def generate_meta_yaml_hashes(self) -> SemanticHash:
        """Generate hashes for META YAML file"""
        try:
            with open(self.meta_yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            structure = yaml.safe_load(content)
            
            content_hash = self.generate_content_hash(content)
            semantic_hash = self.generate_semantic_hash(structure)
            
            hash_record = SemanticHash(
                path=str(self.meta_yaml_path.relative_to(self.workspace_root)),
                content_hash=content_hash,
                semantic_hash=semantic_hash,
                timestamp=datetime.now().isoformat(),
                integrity_level="vocab_constraints"
            )
            
            return hash_record
            
        except Exception as e:
            raise ValueError(f"Failed to generate META YAML hashes: {e}")
    
    def generate_canonical_ssot_hashes(self) -> SemanticHash:
        """Generate hashes for canonical SSoT (merged structure)"""
        try:
            canonical_ssot = self.ssot_merger.merge()
            
            # Convert to JSON for content hashing
            canonical_json = json.dumps(canonical_ssot, sort_keys=True, separators=(',', ':'))
            content_hash = self.generate_content_hash(canonical_json)
            semantic_hash = self.generate_semantic_hash(canonical_ssot)
            
            hash_record = SemanticHash(
                path="canonical_ssot.json",
                content_hash=content_hash,
                semantic_hash=semantic_hash,
                timestamp=datetime.now().isoformat(),
                integrity_level="merged_canonical"
            )
            
            return hash_record
            
        except Exception as e:
            raise ValueError(f"Failed to generate canonical SSoT hashes: {e}")
    
    def validate_integrity(self, expected_hashes: Dict[str, str]) -> bool:
        """Validate current structure against expected hashes"""
        try:
            current_hashes = {}
            
            # Generate current hashes
            main_hash = self.generate_main_yaml_hashes()
            meta_hash = self.generate_meta_yaml_hashes()
            canonical_hash = self.generate_canonical_ssot_hashes()
            
            current_hashes[main_hash.path] = main_hash.content_hash
            current_hashes[meta_hash.path] = meta_hash.content_hash
            current_hashes[canonical_hash.path] = canonical_hash.content_hash
            
            # Validate against expected
            for path, expected_hash in expected_hashes.items():
                if path not in current_hashes:
                    return False
                if current_hashes[path] != expected_hash:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def create_integrity_records(self) -> Dict[str, Any]:
        """Create comprehensive integrity records"""
        try:
            # Generate all hashes
            main_hash = self.generate_main_yaml_hashes()
            meta_hash = self.generate_meta_yaml_hashes()
            canonical_hash = self.generate_canonical_ssot_hashes()
            
            self.semantic_hashes = [main_hash, meta_hash, canonical_hash]
            
            # Create integrity record
            integrity_record = {
                "creation_timestamp": datetime.now().isoformat(),
                "workspace_root": str(self.workspace_root),
                "semantic_hashes": [
                    {
                        "path": h.path,
                        "content_hash": h.content_hash,
                        "semantic_hash": h.semantic_hash,
                        "timestamp": h.timestamp,
                        "integrity_level": h.integrity_level
                    }
                    for h in self.semantic_hashes
                ],
                "validation_status": "created",
                "total_hashes": len(self.semantic_hashes)
            }
            
            self.integrity_records = integrity_record
            return integrity_record
            
        except Exception as e:
            raise ValueError(f"Failed to create integrity records: {e}")
    
    def load_integrity_records(self, record_path: Path) -> Dict[str, Any]:
        """Load existing integrity records"""
        try:
            with open(record_path, 'r', encoding='utf-8') as f:
                self.integrity_records = json.load(f)
            return self.integrity_records
        except Exception as e:
            raise ValueError(f"Failed to load integrity records: {e}")
    
    def save_integrity_records(self, output_path: Optional[Path] = None) -> Path:
        """Save integrity records to file"""
        if output_path is None:
            output_path = self.workspace_root / "02_schemas" / "semantic_integrity_records.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.integrity_records:
            self.create_integrity_records()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.integrity_records, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def validate_semantic_consistency(self) -> bool:
        """Validate semantic consistency across all components"""
        try:
            # Check if main and META are semantically aligned
            main_hash = self.generate_main_yaml_hashes()
            meta_hash = self.generate_meta_yaml_hashes()
            
            # Basic semantic consistency check
            main_structure = yaml.safe_load(open(self.main_yaml_path, 'r', encoding='utf-8'))
            meta_structure = yaml.safe_load(open(self.meta_yaml_path, 'r', encoding='utf-8'))
            
            # Check if domains in main match META domains
            main_domains = set(main_structure.keys()) - {'meta_sidecar', 'canonical_definition'}
            meta_domains = set(meta_structure.get('domains', {}).keys())
            
            return main_domains == meta_domains
            
        except Exception:
            return False


def main():
    """CLI entry point for semantic hash engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Semantic hash engine for SSoT validation")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Path to Agentic-Workflow workspace")
    parser.add_argument("--action", type=str, default="generate",
                       choices=["generate", "validate", "check-consistency"],
                       help="Action to perform")
    parser.add_argument("--records", type=Path,
                       help="Path to integrity records file")
    
    args = parser.parse_args()
    
    engine = SemanticHashEngine(args.workspace)
    
    try:
        if args.action == "generate":
            records = engine.create_integrity_records()
            output_path = engine.save_integrity_records(args.records)
            print(f"Generated semantic hashes for {records['total_hashes']} components")
            print(f"Integrity records saved: {output_path}")
            
        elif args.action == "validate":
            if not args.records:
                print("Error: --records path required for validation")
                return 1
            
            expected_records = engine.load_integrity_records(args.records)
            expected_hashes = {
                h["path"]: h["content_hash"] 
                for h in expected_records["semantic_hashes"]
            }
            
            is_valid = engine.validate_integrity(expected_hashes)
            print(f"Integrity validation: {'PASS' if is_valid else 'FAIL'}")
            return 0 if is_valid else 1
            
        elif args.action == "check-consistency":
            is_consistent = engine.validate_semantic_consistency()
            print(f"Semantic consistency: {'PASS' if is_consistent else 'FAIL'}")
            return 0 if is_consistent else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
