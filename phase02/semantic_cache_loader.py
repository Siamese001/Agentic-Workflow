#!/usr/bin/env python3
"""
Phase 2 Semantic Structural & Code Diff Planning - Semantic Cache Loader

Implements loading and normalization of semantic cache data for Phase 2.
Handles path mapping between archive-relative cache paths and current filesystem
paths, loads all semantic artifacts, and validates cache health.

ZERO-LOSS CONSTRAINTS:
- Read-only operations for semantic cache
- Validates all semantic cache loading K-keys (K11-K16)
- Path normalization between cache and FS
- Docker-safe paths only
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml

from .common import (
    PROJECT_ROOT, SEMANTIC_CACHE_ROOT, TARGET_ROOT, ValidationResult, 
    SemanticCacheState, SEMANTIC_CACHE_LOADING_KEYS, SEMANTIC_ARTIFACT_TYPES,
    create_validation_result, print_validation_status, normalize_path
)

class SemanticCacheLoader:
    """
    Loads and normalizes semantic cache data for Phase 2.
    
    This class handles:
    - Loading semantic cache for target root (agentic_core)
    - Loading global semantic objects
    - Path normalization between cache and filesystem
    - Validating semantic cache health and completeness
    """
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = PROJECT_ROOT
        self.semantic_cache_root = SEMANTIC_CACHE_ROOT
        self.target_root = TARGET_ROOT.rstrip('/')
        self.bucket_path = SEMANTIC_CACHE_ROOT / "agentic_core"
        
        # Validation results
        self.validation_results: List[ValidationResult] = []
        
        # Loaded state
        self.cache_state: Optional[SemanticCacheState] = None
        
        if self.verbose:
            print(f"Phase 2 Semantic Cache Loader initialized:")
            print(f"  Cache Root: {self.semantic_cache_root}")
            print(f"  Target Bucket: {self.bucket_path}")
            print(f"  Dry Run: {self.dry_run}")
    
    def _add_validation_result(self, key: str, status: str, message: str, details: Optional[Dict] = None):
        """Add a validation result and print status"""
        result = create_validation_result(key, status, message, details)
        self.validation_results.append(result)
        print_validation_status(result)
    
    def load_semantic_cache(self) -> bool:
        """
        Load semantic cache data (K11-K16).
        
        Returns:
            bool: True if loading successful
        """
        if self.verbose:
            print("=== Loading Semantic Cache (K11-K16) ===")
        
        try:
            # K11: SEMANTIC_CACHE_LOADED_READONLY == true
            if not self.semantic_cache_root.exists():
                self._add_validation_result("K11", "FAIL", "Semantic cache root does not exist")
                return False
            
            self._add_validation_result("K11", "PASS", "Semantic cache loaded read-only")
            
            # K12: SEMANTIC_CACHE_FOR_TARGET_ROOT_LOADED(agentic_core) == true
            if not self.bucket_path.exists():
                self._add_validation_result("K12", "FAIL", "Semantic cache bucket for agentic_core does not exist")
                return False
            
            # Load target root specific objects
            target_root_objects = self._load_target_root_objects()
            if not target_root_objects:
                self._add_validation_result("K12", "FAIL", "Failed to load target root objects")
                return False
            
            self._add_validation_result("K12", "PASS", "Semantic cache for target root loaded")
            
            # K13: GLOBAL_SEMANTIC_OBJECTS_LOADED == true
            global_objects = self._load_global_objects()
            if not global_objects:
                self._add_validation_result("K13", "FAIL", "Failed to load global semantic objects")
                return False
            
            self._add_validation_result("K13", "PASS", "Global semantic objects loaded")
            
            # Load specific semantic artifacts
            ast_data = self._load_semantic_artifacts("ast")
            embedding_data = self._load_semantic_artifacts("embeddings")
            diff_data = self._load_semantic_artifacts("diffs")
            golden_data = self._load_semantic_artifacts("golden")
            integrity_data = self._load_semantic_artifacts("integrity")
            
            # K14: SEMANTIC_CACHE_PATHS_NORMALIZED == true
            path_mappings = self._create_path_mappings(ast_data, embedding_data, diff_data, golden_data, integrity_data)
            if not path_mappings:
                self._add_validation_result("K14", "FAIL", "Failed to normalize semantic cache paths")
                return False
            
            self._add_validation_result("K14", "PASS", "Semantic cache paths normalized")
            
            # K15: FS_AND_CACHE_PATHS_SHARE_CANONICAL_RELATIVE_PREFIX == true
            if not self._validate_path_prefix_consistency(path_mappings):
                self._add_validation_result("K15", "FAIL", "FS and cache paths do not share canonical prefix")
                return False
            
            self._add_validation_result("K15", "PASS", "FS and cache paths share canonical relative prefix")
            
            # K16: NO_SYSTEM_DIRS_INCLUDED == true
            if not self._validate_no_system_dirs(path_mappings):
                self._add_validation_result("K16", "FAIL", "System directories found in semantic cache")
                return False
            
            self._add_validation_result("K16", "PASS", "No system directories included")
            
            # Create cache state
            self.cache_state = SemanticCacheState(
                bucket_path=self.bucket_path,
                global_objects=global_objects,
                target_root_objects=target_root_objects,
                ast_data=ast_data,
                embedding_data=embedding_data,
                diff_data=diff_data,
                golden_data=golden_data,
                integrity_data=integrity_data,
                path_mappings=path_mappings
            )
            
            return True
            
        except Exception as e:
            self._add_validation_result("CACHE_LOAD_ERROR", "FAIL", f"Failed to load semantic cache: {str(e)}")
            return False
    
    def _load_target_root_objects(self) -> Dict:
        """Load target root specific semantic objects"""
        try:
            objects = {}
            
            # Load canonical pointers for agentic_core
            canonical_pointers_file = self.bucket_path / "canonical_pointers.json"
            if canonical_pointers_file.exists():
                with open(canonical_pointers_file, 'r', encoding='utf-8') as f:
                    objects["canonical_pointers"] = json.load(f)
            
            # Load unmapped files (if any)
            unmapped_files_file = self.bucket_path / "unmapped_files.json"
            if unmapped_files_file.exists():
                with open(unmapped_files_file, 'r', encoding='utf-8') as f:
                    objects["unmapped_files"] = json.load(f)
            
            return objects
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to load target root objects: {str(e)}")
            return {}
    
    def _load_global_objects(self) -> Dict:
        """Load global semantic objects"""
        try:
            objects = {}
            
            # Load global artifact records
            global_artifacts_file = self.semantic_cache_root / "global_artifacts.json"
            if global_artifacts_file.exists():
                with open(global_artifacts_file, 'r', encoding='utf-8') as f:
                    objects["global_artifacts"] = json.load(f)
            
            # Load global hash index
            hash_index_file = self.semantic_cache_root / "hash_index.json"
            if hash_index_file.exists():
                with open(hash_index_file, 'r', encoding='utf-8') as f:
                    objects["hash_index"] = json.load(f)
            
            return objects
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to load global objects: {str(e)}")
            return {}
    
    def _load_semantic_artifacts(self, artifact_type: str) -> Dict:
        """Load specific semantic artifacts from bucket"""
        try:
            artifacts = {}
            artifact_dir = self.bucket_path / artifact_type
            
            if not artifact_dir.exists():
                if self.verbose:
                    print(f"Artifact directory not found: {artifact_dir}")
                return artifacts
            
            # Load all JSON files in the artifact directory
            for file_path in artifact_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        artifact_data = json.load(f)
                    
                    # Use filename as key (without extension)
                    key = file_path.stem
                    artifacts[key] = artifact_data
                    
                except Exception as e:
                    if self.verbose:
                        print(f"Failed to load artifact {file_path}: {str(e)}")
                    continue
            
            if self.verbose:
                print(f"Loaded {len(artifacts)} {artifact_type} artifacts")
            
            return artifacts
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to load {artifact_type} artifacts: {str(e)}")
            return {}
    
    def _create_path_mappings(self, *artifact_data_sets) -> Dict[str, str]:
        """Create path mappings between cache and filesystem"""
        try:
            path_mappings = {}
            
            # Collect all unique paths from artifacts
            all_cache_paths = set()
            for artifacts in artifact_data_sets:
                for artifact_key, artifact_data in artifacts.items():
                    if isinstance(artifact_data, dict) and "file_info" in artifact_data:
                        file_info = artifact_data["file_info"]
                        if "relative_path" in file_info:
                            cache_path = file_info["relative_path"]
                            all_cache_paths.add(cache_path)
            
            # Create mappings from cache paths to filesystem paths
            target_root_path = self.project_root / self.target_root
            
            for cache_path in all_cache_paths:
                # Normalize cache path
                normalized_cache = normalize_path(cache_path)
                
                # Try to map to filesystem path
                # This is a simplified mapping - in practice would use more sophisticated logic
                fs_path = self._map_cache_to_fs_path(normalized_cache, target_root_path)
                
                if fs_path:
                    path_mappings[normalized_cache] = fs_path
            
            if self.verbose:
                print(f"Created {len(path_mappings)} path mappings")
            
            return path_mappings
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to create path mappings: {str(e)}")
            return {}
    
    def _map_cache_to_fs_path(self, cache_path: str, target_root_path: Path) -> Optional[str]:
        """Map a cache-relative path to filesystem path"""
        try:
            # Remove common archive prefixes that might be in cache paths
            prefixes_to_remove = [
                "plan-layer/", "exec-layer/", "safe-layer/", "mem-layer/",
                "orc-layer/", "observer-microagent-layer/", "executor-microagent-layer/",
                "planner-microagent-layer/", "retriever-microagent-layer/", 
                "router-microagent-layer/", "budget-manager-layer/"
            ]
            
            normalized_path = cache_path
            for prefix in prefixes_to_remove:
                if normalized_path.startswith(prefix):
                    normalized_path = normalized_path[len(prefix):]
                    break
            
            # Convert to filesystem path under target root
            fs_relative_path = f"{self.target_root}/{normalized_path}"
            fs_absolute_path = self.project_root / fs_relative_path
            
            # Check if file exists
            if fs_absolute_path.exists():
                return normalize_path(fs_relative_path)
            
            # Try some common transformations
            # Add .py extension if missing
            if not normalized_path.endswith('.py'):
                test_path = f"{self.target_root}/{normalized_path}.py"
                if (self.project_root / test_path).exists():
                    return normalize_path(test_path)
            
            # Try converting underscores to hyphens
            if '_' in normalized_path:
                test_path = normalized_path.replace('_', '-')
                test_full = f"{self.target_root}/{test_path}"
                if (self.project_root / test_full).exists():
                    return normalize_path(test_full)
            
            return None
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to map cache path {cache_path}: {str(e)}")
            return None
    
    def _validate_path_prefix_consistency(self, path_mappings: Dict[str, str]) -> bool:
        """Validate that FS and cache paths share canonical relative prefix"""
        try:
            for cache_path, fs_path in path_mappings.items():
                # Both should be relative to project root
                if not (cache_path.startswith("agentic_core/") or cache_path == "agentic_core"):
                    if self.verbose:
                        print(f"Cache path doesn't start with agentic_core/: {cache_path}")
                    return False
                
                if not fs_path.startswith("01_agentic_core/"):
                    if self.verbose:
                        print(f"FS path doesn't start with 01_agentic_core/: {fs_path}")
                    return False
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to validate path prefix consistency: {str(e)}")
            return False
    
    def _validate_no_system_dirs(self, path_mappings: Dict[str, str]) -> bool:
        """Validate that no system directories are included"""
        try:
            system_dirs = {
                "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                ".git", ".venv", ".idea", ".vscode", "node_modules", ".DS_Store"
            }
            
            for cache_path, fs_path in path_mappings.items():
                for system_dir in system_dirs:
                    if f"/{system_dir}/" in cache_path or cache_path.endswith(f"/{system_dir}"):
                        if self.verbose:
                            print(f"System directory found in cache path: {cache_path}")
                        return False
                    
                    if f"/{system_dir}/" in fs_path or fs_path.endswith(f"/{system_dir}"):
                        if self.verbose:
                            print(f"System directory found in FS path: {fs_path}")
                        return False
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Failed to validate no system dirs: {str(e)}")
            return False
    
    def get_loaded_state(self) -> Optional[SemanticCacheState]:
        """Get the loaded semantic cache state"""
        return self.cache_state
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary with all K-keys"""
        passed = sum(1 for r in self.validation_results if r.status == "PASS")
        failed = sum(1 for r in self.validation_results if r.status == "FAIL")
        
        summary = {
            "total_keys": len(self.validation_results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(self.validation_results) if self.validation_results else 0,
            "results": [asdict(r) for r in self.validation_results],
            "cache_state_loaded": self.cache_state is not None
        }
        
        if self.cache_state:
            summary["artifacts_loaded"] = {
                "ast": len(self.cache_state.ast_data),
                "embeddings": len(self.cache_state.embedding_data),
                "diffs": len(self.cache_state.diff_data),
                "golden": len(self.cache_state.golden_data),
                "integrity": len(self.cache_state.integrity_data),
                "path_mappings": len(self.cache_state.path_mappings)
            }
        
        return summary
    
    def save_loading_report(self) -> bool:
        """Save loading report to schemas directory"""
        try:
            schemas_dir = PROJECT_ROOT / "02_schemas"
            report_path = schemas_dir / "phase02_semantic_cache_loading_report.json"
            
            if not self.dry_run:
                schemas_dir.mkdir(parents=True, exist_ok=True)
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(self.get_validation_summary(), f, indent=2)
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Failed to save semantic cache loading report: {str(e)}")
            return False

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2 Semantic Cache Loader")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    loader = SemanticCacheLoader(dry_run=args.dry_run, verbose=args.verbose)
    
    print("=== Phase 2 Semantic Cache Loader ===")
    
    success = loader.load_semantic_cache()
    
    if success:
        loader.save_loading_report()
        print()
        summary = loader.get_validation_summary()
        print(f"Semantic Cache Loading Complete: {summary['passed']}/{summary['total_keys']} keys passed")
        
        if summary['failed'] == 0:
            print("PHASE VALIDATION COMPLETE — ALL KEYS PASS")
        else:
            print("VALIDATION FAILED — Some keys did not pass")
            return 1
    else:
        print("CRITICAL FAILURE — Semantic cache loading failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
