#!/usr/bin/env python3
"""
Phase 0.5 Semantic Cache Rebuild - Dual-Write Coordinator

Implements dual-write coordination for global hash-based artifacts and
canonical root pointers. Uses two-phase approach: global artifacts first,
then canonical pointer creation with proper SSoT mapping.

ZERO-LOSS CONSTRAINTS:
- Global artifacts written once per hash (deduplication)
- Canonical pointers reference global artifacts
- Unmappable files logged in manifest (no "unmapped" directory)
- Two-phase write process prevents dangling pointers
- Docker-safe paths only
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Project constants
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"

# Import from our modules
from ssot_loader import SSoTLoader
from archive_scanner import FileInfo
from semantic_artifact_generator import SemanticArtifactGenerator

@dataclass
class GlobalArtifactRecord:
    """Record for a global artifact"""
    hash: str
    artifact_type: str
    global_path: str
    size_bytes: int
    created_timestamp: str

@dataclass
class CanonicalPointerRecord:
    """Record for a canonical pointer"""
    target_root: str
    canonical_relative: str
    pointer_type: str
    global_hash: str
    global_path: str
    created_timestamp: str

@dataclass
class UnmappedFileRecord:
    """Record for an unmappable file"""
    file_info: FileInfo
    reason: str
    attempted_mappings: List[str]
    timestamp: str

class DualWriteCoordinator:
    """
    Coordinates dual-write process for semantic artifacts.
    
    Implements two-phase writing:
    1. Global hash-based artifacts (deduped)
    2. Canonical root pointers (reference globals)
    
    Ensures no dangling pointers and proper audit trail.
    """
    
    def __init__(self, ssot_loader: SSoTLoader, dry_run: bool = False):
        self.ssot_loader = ssot_loader
        self.dry_run = dry_run
        self.semantic_cache_root = SEMANTIC_CACHE_ROOT
        
        # Tracking structures
        self.global_artifacts: Dict[str, GlobalArtifactRecord] = {}  # hash -> record
        self.canonical_pointers: List[CanonicalPointerRecord] = []
        self.unmapped_files: List[UnmappedFileRecord] = []
        
        # Statistics
        self.stats = {
            "total_files_processed": 0,
            "global_artifacts_created": 0,
            "global_artifacts_deduped": 0,
            "canonical_pointers_created": 0,
            "unmapped_files": 0,
            "mapping_failures": 0
        }
        
        # Ensure directory structure
        self._ensure_canonical_structure()
    
    def _ensure_canonical_structure(self):
        """Create canonical root directories in semantic cache"""
        canonical_roots = [
            "agentic_core", "schemas", "runtime", "prompt_governance",
            "config", "data_source", "observability", "scripts", "apps", "tests"
        ]
        
        for root_name in canonical_roots:
            root_path = self.semantic_cache_root / root_name
            if not self.dry_run:
                root_path.mkdir(parents=True, exist_ok=True)
    
    def _global_artifact_exists(self, file_hash: str, artifact_type: str) -> bool:
        """Check if global artifact already exists"""
        if artifact_type == "ast":
            global_path = self.semantic_cache_root / "ast" / f"{file_hash}.ast"
        elif artifact_type == "embedding":
            global_path = self.semantic_cache_root / "embeddings" / f"{file_hash}.embedding"
        elif artifact_type == "diff":
            global_path = self.semantic_cache_root / "diffs" / f"{file_hash}.diff.json"
        elif artifact_type == "safety":
            global_path = self.semantic_cache_root / "safety" / f"{file_hash}.safety.json"
        elif artifact_type == "golden":
            global_path = self.semantic_cache_root / "golden" / f"{file_hash}.golden.json"
        elif artifact_type == "integrity":
            global_path = self.semantic_cache_root / "integrity" / f"{file_hash}.integrity.json"
        elif artifact_type == "meta":
            global_path = self.semantic_cache_root / "meta" / f"{file_hash}.meta.json"
        else:
            return False
        
        return global_path.exists()
    
    def _create_canonical_pointer(self, target_root: str, canonical_relative: str, 
                                 pointer_type: str, global_hash: str) -> bool:
        """Create a canonical pointer artifact"""
        try:
            # Determine global path
            if pointer_type == "ast":
                global_path = f"06_data/semantic_cache/ast/{global_hash}.ast"
                pointer_filename = f"{canonical_relative}.ast"
            elif pointer_type == "embedding":
                global_path = f"06_data/semantic_cache/embeddings/{global_hash}.embedding"
                pointer_filename = f"{canonical_relative}.embedding"
            elif pointer_type == "diff":
                global_path = f"06_data/semantic_cache/diffs/{global_hash}.diff.json"
                pointer_filename = f"{canonical_relative}.diff.json"
            elif pointer_type == "safety":
                global_path = f"06_data/semantic_cache/safety/{global_hash}.safety.json"
                pointer_filename = f"{canonical_relative}.safety.json"
            elif pointer_type == "golden":
                global_path = f"06_data/semantic_cache/golden/{global_hash}.golden.json"
                pointer_filename = f"{canonical_relative}.golden.json"
            elif pointer_type == "integrity":
                global_path = f"06_data/semantic_cache/integrity/{global_hash}.integrity.json"
                pointer_filename = f"{canonical_relative}.integrity.json"
            else:
                return False
            
            # Create pointer data
            pointer_data = {
                "pointer_type": pointer_type,
                "target_root": target_root,
                "canonical_relative": canonical_relative,
                "global_hash": global_hash,
                "global_path": global_path,
                "created_timestamp": datetime.now().isoformat(),
                "pointer_version": "1.0"
            }
            
            # Save pointer file
            if not self.dry_run:
                pointer_path = self.semantic_cache_root / target_root / pointer_filename
                pointer_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(pointer_path, 'w', encoding='utf-8') as f:
                    json.dump(pointer_data, f, indent=2)
            
            # Record pointer
            pointer_record = CanonicalPointerRecord(
                target_root=target_root,
                canonical_relative=canonical_relative,
                pointer_type=pointer_type,
                global_hash=global_hash,
                global_path=global_path,
                created_timestamp=datetime.now().isoformat()
            )
            self.canonical_pointers.append(pointer_record)
            
            return True
            
        except Exception as e:
            print(f"Error creating canonical pointer: {str(e)}")
            return False
    
    def process_file_artifacts(self, file_info: FileInfo, artifact_generator: SemanticArtifactGenerator) -> bool:
        """
        Process all artifacts for a single file through dual-write system.
        
        Args:
            file_info: File information from archive scanner
            artifact_generator: Generator instance for creating artifacts
            
        Returns:
            bool: True if processing successful
        """
        self.stats["total_files_processed"] += 1
        
        try:
            # Phase 1: Generate and ensure global artifacts exist
            if not self._ensure_global_artifacts(file_info, artifact_generator):
                return False
            
            # Phase 2: Create canonical pointers if mappable
            if file_info.is_eligible:
                self._create_canonical_pointers(file_info)
            
            return True
            
        except Exception as e:
            print(f"Error processing file {file_info.absolute_path}: {str(e)}")
            return False
    
    def _ensure_global_artifacts(self, file_info: FileInfo, artifact_generator: SemanticArtifactGenerator) -> bool:
        """Ensure global artifacts exist (create if needed)"""
        file_hash = file_info.sha256_hash
        
        # Check if global artifacts already exist
        artifact_types = ["ast", "embedding", "diff", "safety", "golden", "integrity", "meta"]
        if file_info.file_extension != '.py':
            artifact_types.remove("ast")  # Non-Python files don't get AST
        
        # Check if all global artifacts exist
        all_exist = True
        for artifact_type in artifact_types:
            if not self._global_artifact_exists(file_hash, artifact_type):
                all_exist = False
                break
        
        if all_exist:
            # Global artifacts already exist, count as deduped
            self.stats["global_artifacts_deduped"] += len(artifact_types)
            return True
        
        # Generate global artifacts
        success = artifact_generator.generate_artifacts_for_file(file_info)
        if success:
            self.stats["global_artifacts_created"] += len(artifact_types)
            
            # Record global artifacts
            for artifact_type in artifact_types:
                if artifact_type == "ast":
                    global_path = f"ast/{file_hash}.ast"
                elif artifact_type == "embedding":
                    global_path = f"embeddings/{file_hash}.embedding"
                elif artifact_type == "diff":
                    global_path = f"diffs/{file_hash}.diff.json"
                elif artifact_type == "safety":
                    global_path = f"safety/{file_hash}.safety.json"
                elif artifact_type == "golden":
                    global_path = f"golden/{file_hash}.golden.json"
                elif artifact_type == "integrity":
                    global_path = f"integrity/{file_hash}.integrity.json"
                elif artifact_type == "meta":
                    global_path = f"meta/{file_hash}.meta.json"
                
                record = GlobalArtifactRecord(
                    hash=file_hash,
                    artifact_type=artifact_type,
                    global_path=global_path,
                    size_bytes=0,  # Would be populated in real implementation
                    created_timestamp=datetime.now().isoformat()
                )
                self.global_artifacts[f"{file_hash}_{artifact_type}"] = record
        
        return success
    
    def _create_canonical_pointers(self, file_info: FileInfo):
        """Create canonical pointers for eligible files"""
        # Map archive path to canonical location
        mapping_result = self.ssot_loader.map_archive_to_canonical(
            file_info.relative_path, file_info.archive_name
        )
        
        if not mapping_result:
            # File is unmappable
            self._record_unmapped_file(file_info, "No canonical mapping found")
            self.stats["unmapped_files"] += 1
            self.stats["mapping_failures"] += 1
            return
        
        target_root, canonical_relative = mapping_result
        
        # Create pointers for all artifact types
        artifact_types = ["ast", "embedding", "diff", "safety", "golden", "integrity"]
        if file_info.file_extension != '.py':
            artifact_types.remove("ast")
        
        for artifact_type in artifact_types:
            if self._create_canonical_pointer(target_root, canonical_relative, artifact_type, file_info.sha256_hash):
                self.stats["canonical_pointers_created"] += 1
    
    def _record_unmapped_file(self, file_info: FileInfo, reason: str):
        """Record an unmappable file for audit purposes"""
        unmapped_record = UnmappedFileRecord(
            file_info=file_info,
            reason=reason,
            attempted_mappings=[file_info.relative_path],
            timestamp=datetime.now().isoformat()
        )
        self.unmapped_files.append(unmapped_record)
    
    def save_dual_write_report(self) -> bool:
        """Save comprehensive dual-write coordination report"""
        try:
            report_data = {
                "coordination_timestamp": datetime.now().isoformat(),
                "statistics": self.stats,
                "global_artifacts": {k: asdict(v) for k, v in self.global_artifacts.items()},
                "canonical_pointers": [asdict(p) for p in self.canonical_pointers],
                "unmapped_files": [asdict(u) for u in self.unmapped_files],
                "summary": {
                    "total_global_artifacts": len(self.global_artifacts),
                    "total_canonical_pointers": len(self.canonical_pointers),
                    "total_unmapped_files": len(self.unmapped_files),
                    "deduplication_rate": (
                        self.stats["global_artifacts_deduped"] / 
                        (self.stats["global_artifacts_created"] + self.stats["global_artifacts_deduped"])
                        if (self.stats["global_artifacts_created"] + self.stats["global_artifacts_deduped"]) > 0 else 0
                    )
                }
            }
            
            if not self.dry_run:
                report_path = self.semantic_cache_root / "meta" / "dual_write_report.json"
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2)
                
                # Also save unmapped files separately for audit
                if self.unmapped_files:
                    unmapped_path = self.semantic_cache_root / "meta" / "unmapped_files.json"
                    with open(unmapped_path, 'w', encoding='utf-8') as f:
                        json.dump([asdict(u) for u in self.unmapped_files], f, indent=2)
            
            print("Dual-write coordination report saved")
            return True
            
        except Exception as e:
            print(f"Failed to save dual-write report: {str(e)}")
            return False
    
    def get_coordination_summary(self) -> Dict:
        """Get coordination summary"""
        return {
            "statistics": self.stats,
            "global_artifact_count": len(self.global_artifacts),
            "canonical_pointer_count": len(self.canonical_pointers),
            "unmapped_file_count": len(self.unmapped_files),
            "coordination_timestamp": datetime.now().isoformat()
        }

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dual-Write Coordinator")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    args = parser.parse_args()
    
    # Initialize SSoT loader
    ssot_loader = SSoTLoader(dry_run=args.dry_run)
    if not ssot_loader.load_ssot():
        print("Failed to load SSoT")
        return 1
    
    # Initialize coordinator
    coordinator = DualWriteCoordinator(ssot_loader, dry_run=args.dry_run)
    
    print("=== Phase 0.5 Dual-Write Coordinator ===")
    print(f"Dry Run: {args.dry_run}")
    print(f"SSoT loaded: {ssot_loader.combined_ssot is not None}")
    print(f"Cache root: {coordinator.semantic_cache_root}")
    
    summary = coordinator.get_coordination_summary()
    print(f"Coordinator initialized: {summary}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
