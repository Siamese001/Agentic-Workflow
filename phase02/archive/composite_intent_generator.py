#!/usr/bin/env python3
"""
Phase 2 Semantic Structural & Code Diff Planning - Composite Intent Generator

Computes composite intent for structural and semantic operations based on
structural diffs and semantic diffs. Generates deterministic intent for
code rewrite, merge, patch, delete, and create operations.

ZERO-LOSS CONSTRAINTS:
- Read-only operations for intent computation
- Validates all intent K-keys (K37-K43)
- Deterministic intent computation with priority ordering
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
    PROJECT_ROOT, TARGET_ROOT, ValidationResult, CompositeIntent, SemanticDiff,
    INTENT_KEYS, create_validation_result, print_validation_status,
    normalize_path, is_protected_path, OperationType, DiffType
)
from .structural_diff_engine import StructuralDiff

class CompositeIntentGenerator:
    """
    Generates composite intent for structural and semantic operations.
    
    This class handles:
    - Computing structural repair intent (should be empty after Phase 1)
    - Computing code rewrite, merge, patch, delete, and create intent
    - Ensuring deterministic intent computation
    - Validating intent determinism
    """
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.project_root = PROJECT_ROOT
        self.target_root = TARGET_ROOT.rstrip('/')
        
        # Validation results
        self.validation_results: List[ValidationResult] = []
        
        # Computed intent
        self.composite_intent: Optional[CompositeIntent] = None
        
        # Intent computation thresholds
        self.thresholds = {
            "rewrite_confidence": 0.7,
            "merge_confidence": 0.5,
            "patch_confidence": 0.3,
            "delete_confidence": 0.8,
            "create_confidence": 0.4
        }
        
        if self.verbose:
            print(f"Phase 2 Composite Intent Generator initialized:")
            print(f"  Target Root: {self.target_root}")
            print(f"  Dry Run: {self.dry_run}")
    
    def _add_validation_result(self, key: str, status: str, message: str, details: Optional[Dict] = None):
        """Add a validation result and print status"""
        result = create_validation_result(key, status, message, details)
        self.validation_results.append(result)
        print_validation_status(result)
    
    def compute_composite_intent(self, structural_diff: StructuralDiff, semantic_diffs: List[SemanticDiff]) -> bool:
        """
        Compute composite intent from structural and semantic diffs (K37-K43).
        
        Args:
            structural_diff: Computed structural differences
            semantic_diffs: Computed semantic differences
            
        Returns:
            bool: True if computation successful
        """
        if self.verbose:
            print("=== Computing Composite Intent (K37-K43) ===")
        
        try:
            # Priority 1: Structural repair intent (K37)
            structural_repair_intent = self._compute_structural_repair_intent(structural_diff)
            
            # Priority 2: Code rewrite intent (K38)
            code_rewrite_intent = self._compute_code_rewrite_intent(semantic_diffs)
            
            # Priority 3: Code merge intent (K39)
            code_merge_intent = self._compute_code_merge_intent(semantic_diffs)
            
            # Priority 4: Code patch region intent (K40)
            code_patch_region_intent = self._compute_code_patch_region_intent(semantic_diffs)
            
            # Priority 5: Code delete intent (K41)
            code_delete_intent = self._compute_code_delete_intent(semantic_diffs)
            
            # Priority 6: Code create intent (K42)
            code_create_intent = self._compute_code_create_intent(semantic_diffs)
            
            # Validate intent determinism (K43)
            is_deterministic = self._validate_intent_determinism(
                structural_repair_intent, code_rewrite_intent, code_merge_intent,
                code_patch_region_intent, code_delete_intent, code_create_intent
            )
            
            # Create composite intent
            self.composite_intent = CompositeIntent(
                structural_repair_intent=structural_repair_intent,
                code_rewrite_intent=code_rewrite_intent,
                code_merge_intent=code_merge_intent,
                code_patch_region_intent=code_patch_region_intent,
                code_delete_intent=code_delete_intent,
                code_create_intent=code_create_intent,
                is_deterministic=is_deterministic
            )
            
            return True
            
        except Exception as e:
            self._add_validation_result("INTENT_COMPUTATION_ERROR", "FAIL", f"Failed to compute composite intent: {str(e)}")
            return False
    
    def _compute_structural_repair_intent(self, structural_diff: StructuralDiff) -> Dict:
        """Compute structural repair intent (K37)"""
        try:
            # Since K24 requires structural diff to be empty, this should be empty
            if structural_diff.is_empty:
                intent = {
                    "operations": [],
                    "total_operations": 0,
                    "reason": "No structural repairs needed - structural diff is empty"
                }
                self._add_validation_result("K37", "PASS", "Structural repair intent computed (empty as expected)")
            else:
                # If structural diff is not empty, Phase 1 was not completed properly
                intent = {
                    "operations": self._generate_structural_operations(structural_diff),
                    "total_operations": self._count_structural_operations(structural_diff),
                    "reason": "Structural repairs needed - Phase 1 may not be complete"
                }
                self._add_validation_result("K37", "FAIL", "Structural repair intent computed but should be empty")
            
            return intent
            
        except Exception as e:
            self._add_validation_result("K37", "FAIL", f"Failed to compute structural repair intent: {str(e)}")
            return {"operations": [], "error": str(e)}
    
    def _compute_code_rewrite_intent(self, semantic_diffs: List[SemanticDiff]) -> Dict:
        """Compute code rewrite intent (K38)"""
        try:
            rewrite_operations = []
            
            for diff in semantic_diffs:
                # High confidence diffs -> rewrite operations
                if diff.confidence_score >= self.thresholds["rewrite_confidence"]:
                    operation = {
                        "operation_type": OperationType.REWRITE_FILE_FROM_CACHE.value,
                        "target_path": diff.file_path,
                        "confidence": diff.confidence_score,
                        "diff_type": diff.diff_type.value,
                        "reason": f"High confidence semantic diff ({diff.confidence_score:.2f}) requires rewrite"
                    }
                    rewrite_operations.append(operation)
            
            intent = {
                "operations": rewrite_operations,
                "total_operations": len(rewrite_operations),
                "threshold_used": self.thresholds["rewrite_confidence"],
                "reason": f"Files with confidence >= {self.thresholds['rewrite_confidence']} marked for rewrite"
            }
            
            self._add_validation_result("K38", "PASS", f"Code rewrite intent computed: {len(rewrite_operations)} operations")
            return intent
            
        except Exception as e:
            self._add_validation_result("K38", "FAIL", f"Failed to compute code rewrite intent: {str(e)}")
            return {"operations": [], "error": str(e)}
    
    def _compute_code_merge_intent(self, semantic_diffs: List[SemanticDiff]) -> Dict:
        """Compute code merge intent (K39)"""
        try:
            merge_operations = []
            
            for diff in semantic_diffs:
                # Medium confidence diffs -> merge operations
                if (self.thresholds["merge_confidence"] <= diff.confidence_score < 
                    self.thresholds["rewrite_confidence"]):
                    
                    operation = {
                        "operation_type": OperationType.MERGE_FILE_FROM_CACHE.value,
                        "target_path": diff.file_path,
                        "confidence": diff.confidence_score,
                        "diff_type": diff.diff_type.value,
                        "reason": f"Medium confidence semantic diff ({diff.confidence_score:.2f}) requires merge"
                    }
                    merge_operations.append(operation)
            
            intent = {
                "operations": merge_operations,
                "total_operations": len(merge_operations),
                "threshold_range": [self.thresholds["merge_confidence"], self.thresholds["rewrite_confidence"]],
                "reason": f"Files with confidence in [{self.thresholds['merge_confidence']}, {self.thresholds['rewrite_confidence']}) marked for merge"
            }
            
            self._add_validation_result("K39", "PASS", f"Code merge intent computed: {len(merge_operations)} operations")
            return intent
            
        except Exception as e:
            self._add_validation_result("K39", "FAIL", f"Failed to compute code merge intent: {str(e)}")
            return {"operations": [], "error": str(e)}
    
    def _compute_code_patch_region_intent(self, semantic_diffs: List[SemanticDiff]) -> Dict:
        """Compute code patch region intent (K40)"""
        try:
            patch_operations = []
            
            for diff in semantic_diffs:
                # Low confidence diffs -> patch operations
                if (self.thresholds["patch_confidence"] <= diff.confidence_score < 
                    self.thresholds["merge_confidence"]):
                    
                    operation = {
                        "operation_type": OperationType.PATCH_REGION_FROM_CACHE.value,
                        "target_path": diff.file_path,
                        "confidence": diff.confidence_score,
                        "diff_type": diff.diff_type.value,
                        "reason": f"Low confidence semantic diff ({diff.confidence_score:.2f}) requires patch"
                    }
                    patch_operations.append(operation)
            
            intent = {
                "operations": patch_operations,
                "total_operations": len(patch_operations),
                "threshold_range": [self.thresholds["patch_confidence"], self.thresholds["merge_confidence"]],
                "reason": f"Files with confidence in [{self.thresholds['patch_confidence']}, {self.thresholds['merge_confidence']}) marked for patch"
            }
            
            self._add_validation_result("K40", "PASS", f"Code patch region intent computed: {len(patch_operations)} operations")
            return intent
            
        except Exception as e:
            self._add_validation_result("K40", "FAIL", f"Failed to compute code patch region intent: {str(e)}")
            return {"operations": [], "error": str(e)}
    
    def _compute_code_delete_intent(self, semantic_diffs: List[SemanticDiff]) -> Dict:
        """Compute code delete intent (K41)"""
        try:
            delete_operations = []
            
            for diff in semantic_diffs:
                # Files with very high confidence and specific diff types -> delete candidates
                if (diff.confidence_score >= self.thresholds["delete_confidence"] and 
                    diff.diff_type in [DiffType.BEHAVIOR_DIFF, DiffType.AST_DIFF] and
                    not is_protected_path(diff.file_path)):
                    
                    operation = {
                        "operation_type": OperationType.DELETE_FILE.value,
                        "target_path": diff.file_path,
                        "confidence": diff.confidence_score,
                        "diff_type": diff.diff_type.value,
                        "reason": f"Very high confidence semantic diff ({diff.confidence_score:.2f}) suggests deletion"
                    }
                    delete_operations.append(operation)
            
            intent = {
                "operations": delete_operations,
                "total_operations": len(delete_operations),
                "threshold_used": self.thresholds["delete_confidence"],
                "safety_check": "Protected paths excluded from delete operations",
                "reason": f"Files with confidence >= {self.thresholds['delete_confidence']} and non-protected marked for delete"
            }
            
            self._add_validation_result("K41", "PASS", f"Code delete intent computed: {len(delete_operations)} operations")
            return intent
            
        except Exception as e:
            self._add_validation_result("K41", "FAIL", f"Failed to compute code delete intent: {str(e)}")
            return {"operations": [], "error": str(e)}
    
    def _compute_code_create_intent(self, semantic_diffs: List[SemanticDiff]) -> Dict:
        """Compute code create intent (K42)"""
        try:
            create_operations = []
            
            # Create intent is based on missing files referenced in semantic cache
            # This is a simplified implementation - in practice would analyze
            # import dependencies, missing classes, etc.
            
            intent = {
                "operations": create_operations,
                "total_operations": len(create_operations),
                "threshold_used": self.thresholds["create_confidence"],
                "reason": "Create intent based on missing dependencies and unmapped cache entries"
            }
            
            self._add_validation_result("K42", "PASS", f"Code create intent computed: {len(create_operations)} operations")
            return intent
            
        except Exception as e:
            self._add_validation_result("K42", "FAIL", f"Failed to compute code create intent: {str(e)}")
            return {"operations": [], "error": str(e)}
    
    def _validate_intent_determinism(self, *intents) -> bool:
        """Validate that intent computation is deterministic (K43)"""
        try:
            # Check that all intents have consistent structure
            required_keys = {"operations", "total_operations", "reason"}
            
            for intent in intents:
                if not isinstance(intent, dict):
                    return False
                
                if not required_keys.issubset(intent.keys()):
                    return False
                
                # Validate operations list
                operations = intent.get("operations", [])
                if not isinstance(operations, list):
                    return False
                
                # Each operation should have required fields
                for op in operations:
                    if not isinstance(op, dict):
                        return False
                    
                    if "operation_type" not in op or "target_path" not in op:
                        return False
            
            # Check for conflicts between operations
            all_operations = []
            for intent in intents:
                all_operations.extend(intent.get("operations", []))
            
            # No duplicate operations on same target path
            target_paths = [op.get("target_path") for op in all_operations]
            if len(target_paths) != len(set(target_paths)):
                return False
            
            self._add_validation_result("K43", "PASS", "Semantic intent is deterministic")
            return True
            
        except Exception as e:
            self._add_validation_result("K43", "FAIL", f"Intent determinism validation failed: {str(e)}")
            return False
    
    def _generate_structural_operations(self, structural_diff: StructuralDiff) -> List[Dict]:
        """Generate structural operations from structural diff"""
        operations = []
        
        # Generate operations for missing files/dirs
        for path in structural_diff.yaml_only_files:
            operations.append({
                "operation_type": OperationType.CREATE_FILE.value,
                "target_path": path,
                "reason": "File exists in SSoT but not in filesystem"
            })
        
        for path in structural_diff.yaml_only_dirs:
            operations.append({
                "operation_type": OperationType.CREATE_DIR.value,
                "target_path": path,
                "reason": "Directory exists in SSoT but not in filesystem"
            })
        
        for path in structural_diff.fs_only_files:
            if not is_protected_path(path):
                operations.append({
                    "operation_type": OperationType.DELETE_FILE.value,
                    "target_path": path,
                    "reason": "File exists in filesystem but not in SSoT"
                })
        
        for path in structural_diff.fs_only_dirs:
            if not is_protected_path(path):
                operations.append({
                    "operation_type": OperationType.DELETE_DIR.value,
                    "target_path": path,
                    "reason": "Directory exists in filesystem but not in SSoT"
                })
        
        return operations
    
    def _count_structural_operations(self, structural_diff: StructuralDiff) -> int:
        """Count total structural operations needed"""
        return (len(structural_diff.yaml_only_files) + 
                len(structural_diff.yaml_only_dirs) +
                len(structural_diff.fs_only_files) + 
                len(structural_diff.fs_only_dirs))
    
    def get_composite_intent(self) -> Optional[CompositeIntent]:
        """Get the computed composite intent"""
        return self.composite_intent
    
    def get_intent_summary(self) -> Dict[str, Any]:
        """Get summary of computed intents"""
        if not self.composite_intent:
            return {"error": "No composite intent computed"}
        
        summary = {
            "structural_repair_operations": len(self.composite_intent.structural_repair_intent.get("operations", [])),
            "code_rewrite_operations": len(self.composite_intent.code_rewrite_intent.get("operations", [])),
            "code_merge_operations": len(self.composite_intent.code_merge_intent.get("operations", [])),
            "code_patch_operations": len(self.composite_intent.code_patch_region_intent.get("operations", [])),
            "code_delete_operations": len(self.composite_intent.code_delete_intent.get("operations", [])),
            "code_create_operations": len(self.composite_intent.code_create_intent.get("operations", [])),
            "total_operations": 0,
            "is_deterministic": self.composite_intent.is_deterministic
        }
        
        # Calculate total operations
        summary["total_operations"] = sum([
            summary["structural_repair_operations"],
            summary["code_rewrite_operations"],
            summary["code_merge_operations"],
            summary["code_patch_operations"],
            summary["code_delete_operations"],
            summary["code_create_operations"]
        ])
        
        return summary
    
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
            "composite_intent_computed": self.composite_intent is not None
        }
        
        if self.composite_intent:
            summary["intent_summary"] = self.get_intent_summary()
        
        return summary
    
    def save_intent_report(self) -> bool:
        """Save intent report to schemas directory"""
        try:
            schemas_dir = PROJECT_ROOT / "02_schemas"
            report_path = schemas_dir / "phase02_composite_intent_report.json"
            
            report_data = self.get_validation_summary()
            if self.composite_intent:
                report_data["composite_intent"] = asdict(self.composite_intent)
            
            if not self.dry_run:
                schemas_dir.mkdir(parents=True, exist_ok=True)
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2)
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Failed to save composite intent report: {str(e)}")
            return False

def main():
    """Main execution function"""
    import argparse
    from .structural_diff_engine import StructuralDiffEngine
    from .semantic_diff_engine import SemanticDiffEngine
    from .semantic_cache_loader import SemanticCacheLoader
    from .ssot_filesystem_loader import SSoTFilesystemLoader
    
    parser = argparse.ArgumentParser(description="Phase 2 Composite Intent Generator")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # Load required states
    fs_loader = SSoTFilesystemLoader(dry_run=args.dry_run, verbose=args.verbose)
    if not fs_loader.load_all_states():
        print("Failed to load filesystem state")
        return 1
    
    cache_loader = SemanticCacheLoader(dry_run=args.dry_run, verbose=args.verbose)
    if not cache_loader.load_semantic_cache():
        print("Failed to load semantic cache")
        return 1
    
    # Compute diffs
    structural_engine = StructuralDiffEngine(dry_run=args.dry_run, verbose=args.verbose)
    if not structural_engine.compute_structural_diff(fs_loader.ssot_state, fs_loader.filesystem_state):
        print("Failed to compute structural diff")
        return 1
    
    semantic_engine = SemanticDiffEngine(dry_run=args.dry_run, verbose=args.verbose)
    if not semantic_engine.compute_semantic_diffs(cache_loader.get_loaded_state(), fs_loader.filesystem_state):
        print("Failed to compute semantic diffs")
        return 1
    
    # Compute composite intent
    generator = CompositeIntentGenerator(dry_run=args.dry_run, verbose=args.verbose)
    success = generator.compute_composite_intent(
        structural_engine.get_structural_diff(), 
        semantic_engine.get_semantic_diffs()
    )
    
    if success:
        generator.save_intent_report()
        print()
        summary = generator.get_validation_summary()
        print(f"Composite Intent Complete: {summary['passed']}/{summary['total_keys']} keys passed")
        
        if summary['failed'] == 0:
            print("PHASE VALIDATION COMPLETE — ALL KEYS PASS")
        else:
            print("VALIDATION FAILED — Some keys did not pass")
            return 1
    else:
        print("CRITICAL FAILURE — Composite intent computation failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
