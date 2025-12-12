#!/usr/bin/env python3
"""
Phase 2 Semantic Structural & Code Diff Planning - Orchestrator

Orchestrates the complete Phase 2 pipeline with dependency injection,
checkpoint/resume capability, and comprehensive 88 K-key validation.
Integrates all Phase 2 components for deterministic migration plan generation.

ZERO-LOSS CONSTRAINTS:
- Read-only orchestration with transaction manifest
- Checkpoint/resume capability for reliability
- Comprehensive 88 K-key validation
- Docker-safe paths only
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, object
from dataclasses import dataclass, asdict
from datetime import datetime

from .common import (
    PROJECT_ROOT, TARGET_ROOT, SCHEMAS_ROOT, ValidationResult, Phase2Step,
    Phase2TransactionManifest, Phase2Config, ALL_PHASE2_VALIDATION_KEYS,
    create_validation_result, print_validation_status
)
from .ssot_filesystem_loader import SSoTFilesystemLoader, SSoTState, FilesystemState
from .semantic_cache_loader import SemanticCacheLoader, SemanticCacheState
from .structural_diff_engine import StructuralDiffEngine, StructuralDiff
from .semantic_diff_engine import SemanticDiffEngine, SemanticDiff
from .composite_intent_generator import CompositeIntentGenerator, CompositeIntent
from .unified_plan_generator import UnifiedPlanGenerator, MigrationPlan

class Phase02Orchestrator:
    """
    Orchestrates the complete Phase 2 pipeline with checkpoint/resume capability.
    
    This class handles:
    - Dependency injection for all Phase 2 components
    - Transaction manifest for checkpoint/resume
    - Comprehensive validation across all 88 K-keys
    - Error recovery and reporting
    """
    
    # Pipeline step definitions
    STEP_SSOT_LOAD = "SSOT_LOAD"
    STEP_CACHE_LOAD = "CACHE_LOAD"
    STEP_STRUCTURAL_DIFF = "STRUCTURAL_DIFF"
    STEP_SEMANTIC_DIFF = "SEMANTIC_DIFF"
    STEP_INTENT_GENERATION = "INTENT_GENERATION"
    STEP_PLAN_GENERATION = "PLAN_GENERATION"
    STEP_FINAL_VALIDATION = "FINAL_VALIDATION"
    
    ALL_STEPS = [
        STEP_SSOT_LOAD,
        STEP_CACHE_LOAD,
        STEP_STRUCTURAL_DIFF,
        STEP_SEMANTIC_DIFF,
        STEP_INTENT_GENERATION,
        STEP_PLAN_GENERATION,
        STEP_FINAL_VALIDATION
    ]
    
    def __init__(self, config: Phase2Config):
        self.config = config
        self.project_root = PROJECT_ROOT
        self.schemas_root = SCHEMAS_ROOT
        
        # Transaction manifest
        self.transaction_manifest: Optional[Phase2TransactionManifest] = None
        
        # Component instances
        self.fs_loader: Optional[SSoTFilesystemLoader] = None
        self.cache_loader: Optional[SemanticCacheLoader] = None
        self.structural_engine: Optional[StructuralDiffEngine] = None
        self.semantic_engine: Optional[SemanticDiffEngine] = None
        self.intent_generator: Optional[CompositeIntentGenerator] = None
        self.plan_generator: Optional[UnifiedPlanGenerator] = None
        
        # Pipeline state
        self.ssot_state: Optional[SSoTState] = None
        self.filesystem_state: Optional[FilesystemState] = None
        self.cache_state: Optional[SemanticCacheState] = None
        self.structural_diff: Optional[StructuralDiff] = None
        self.semantic_diffs: List[SemanticDiff] = []
        self.composite_intent: Optional[CompositeIntent] = None
        self.migration_plan: Optional[MigrationPlan] = None
        
        # Validation results from all components
        self.all_validation_results: List[ValidationResult] = []
        
        if self.config.verbose:
            print(f"Phase 2 Orchestrator initialized:")
            print(f"  Target Root: {self.config.target_root}")
            print(f"  Dry Run: {self.config.dry_run}")
            print(f"  Resume From: {self.config.resume_from}")
    
    def run_pipeline(self) -> bool:
        """
        Run the complete Phase 2 pipeline.
        
        Returns:
            bool: True if pipeline completed successfully
        """
        try:
            # Initialize transaction manifest
            self._initialize_transaction_manifest()
            
            # Run pipeline steps
            for step in self.ALL_STEPS:
                if self.config.resume_from and step != self.config.resume_from:
                    if self.config.verbose:
                        print(f"Skipping step {step} (resuming from {self.config.resume_from})")
                    continue
                
                if not self._run_pipeline_step(step):
                    return False
            
            # Final success
            self._finalize_transaction_manifest(True)
            self._print_final_summary()
            return True
            
        except Exception as e:
            if self.config.verbose:
                print(f"Pipeline failed with exception: {str(e)}")
            self._finalize_transaction_manifest(False)
            return False
    
    def _initialize_transaction_manifest(self):
        """Initialize the transaction manifest"""
        self.transaction_manifest = Phase2TransactionManifest(
            pipeline_id=f"phase02_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}",
            start_time=datetime.now().isoformat(),
            status="RUNNING",
            dry_run=self.config.dry_run,
            target_root=self.config.target_root,
            steps=[],
            current_step=0,
            total_files_processed=0,
            semantic_artifacts_loaded=0,
            operations_generated=0
        )
        
        if self.config.verbose:
            print(f"Transaction manifest initialized: {self.transaction_manifest.pipeline_id}")
    
    def _run_pipeline_step(self, step: str) -> bool:
        """Run a single pipeline step"""
        if self.config.verbose:
            print(f"\n=== Running Step: {step} ===")
        
        # Create step record
        step_record = Phase2Step(
            step_id=step,
            step_name=step,
            status="RUNNING",
            start_time=datetime.now().isoformat()
        )
        
        self.transaction_manifest.steps.append(step_record)
        self.transaction_manifest.current_step = len(self.transaction_manifest.steps)
        
        try:
            success = False
            
            if step == self.STEP_SSOT_LOAD:
                success = self._step_ssot_load()
            elif step == self.STEP_CACHE_LOAD:
                success = self._step_cache_load()
            elif step == self.STEP_STRUCTURAL_DIFF:
                success = self._step_structural_diff()
            elif step == self.STEP_SEMANTIC_DIFF:
                success = self._step_semantic_diff()
            elif step == self.STEP_INTENT_GENERATION:
                success = self._step_intent_generation()
            elif step == self.STEP_PLAN_GENERATION:
                success = self._step_plan_generation()
            elif step == self.STEP_FINAL_VALIDATION:
                success = self._step_final_validation()
            
            # Update step record
            step_record.status = "COMPLETED" if success else "FAILED"
            step_record.end_time = datetime.now().isoformat()
            
            # Save checkpoint
            self._save_checkpoint()
            
            return success
            
        except Exception as e:
            step_record.status = "FAILED"
            step_record.end_time = datetime.now().isoformat()
            step_record.error_message = str(e)
            
            if self.config.verbose:
                print(f"Step {step} failed: {str(e)}")
            
            self._save_checkpoint()
            return False
    
    def _step_ssot_load(self) -> bool:
        """Step: Load SSoT and filesystem state"""
        self.fs_loader = SSoTFilesystemLoader(
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )
        
        success = self.fs_loader.load_all_states()
        
        if success:
            self.ssot_state = self.fs_loader.ssot_state
            self.filesystem_state = self.fs_loader.filesystem_state
            self.transaction_manifest.total_files_processed = len(self.filesystem_state.file_list)
            
            # Collect validation results
            self.all_validation_results.extend(self.fs_loader.validation_results)
            
            # Save loading report
            self.fs_loader.save_loading_report()
        
        return success
    
    def _step_cache_load(self) -> bool:
        """Step: Load semantic cache state"""
        self.cache_loader = SemanticCacheLoader(
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )
        
        success = self.cache_loader.load_semantic_cache()
        
        if success:
            self.cache_state = self.cache_loader.get_loaded_state()
            if self.cache_state:
                self.transaction_manifest.semantic_artifacts_loaded = (
                    len(self.cache_state.ast_data) +
                    len(self.cache_state.embedding_data) +
                    len(self.cache_state.diff_data) +
                    len(self.cache_state.golden_data) +
                    len(self.cache_state.integrity_data)
                )
            
            # Collect validation results
            self.all_validation_results.extend(self.cache_loader.validation_results)
            
            # Save loading report
            self.cache_loader.save_loading_report()
        
        return success
    
    def _step_structural_diff(self) -> bool:
        """Step: Compute structural differences"""
        self.structural_engine = StructuralDiffEngine(
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )
        
        success = self.structural_engine.compute_structural_diff(
            self.ssot_state,
            self.filesystem_state
        )
        
        if success:
            self.structural_diff = self.structural_engine.get_structural_diff()
            
            # Collect validation results
            self.all_validation_results.extend(self.structural_engine.validation_results)
            
            # Save diff report
            self.structural_engine.save_diff_report()
        
        return success
    
    def _step_semantic_diff(self) -> bool:
        """Step: Compute semantic differences"""
        self.semantic_engine = SemanticDiffEngine(
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )
        
        success = self.semantic_engine.compute_semantic_diffs(
            self.cache_state,
            self.filesystem_state
        )
        
        if success:
            self.semantic_diffs = self.semantic_engine.get_semantic_diffs()
            
            # Collect validation results
            self.all_validation_results.extend(self.semantic_engine.validation_results)
            
            # Save diff report
            self.semantic_engine.save_diff_report()
        
        return success
    
    def _step_intent_generation(self) -> bool:
        """Step: Generate composite intent"""
        self.intent_generator = CompositeIntentGenerator(
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )
        
        success = self.intent_generator.compute_composite_intent(
            self.structural_diff,
            self.semantic_diffs
        )
        
        if success:
            self.composite_intent = self.intent_generator.get_composite_intent()
            
            # Collect validation results
            self.all_validation_results.extend(self.intent_generator.validation_results)
            
            # Save intent report
            self.intent_generator.save_intent_report()
        
        return success
    
    def _step_plan_generation(self) -> bool:
        """Step: Generate unified migration plan"""
        self.plan_generator = UnifiedPlanGenerator(
            dry_run=self.config.dry_run,
            verbose=self.config.verbose
        )
        
        success = self.plan_generator.generate_unified_plan(self.composite_intent)
        
        if success:
            self.migration_plan = self.plan_generator.get_migration_plan()
            if self.migration_plan:
                self.transaction_manifest.operations_generated = len(self.migration_plan.operations)
            
            # Collect validation results
            self.all_validation_results.extend(self.plan_generator.validation_results)
            
            # Save migration plan
            self.plan_generator.save_migration_plan()
        
        return success
    
    def _step_final_validation(self) -> bool:
        """Step: Final validation of all 88 K-keys"""
        if self.config.verbose:
            print("=== Final Validation of All 88 K-Keys ===")
        
        # Check that all expected keys are present
        all_keys_found = {r.key for r in self.all_validation_results}
        missing_keys = set(ALL_PHASE2_VALIDATION_KEYS) - all_keys_found
        
        if missing_keys:
            print(f"ERROR: Missing validation keys: {sorted(missing_keys)}")
            return False
        
        # Check that all keys passed
        failed_keys = [r.key for r in self.all_validation_results if r.status == "FAIL"]
        
        if failed_keys:
            print(f"ERROR: Failed validation keys: {sorted(failed_keys)}")
            return False
        
        # Validate final plan integrity
        if not self.migration_plan:
            print("ERROR: No migration plan generated")
            return False
        
        if self.config.verbose:
            print(f"SUCCESS: All {len(self.all_validation_results)} K-keys validated")
            print(f"Migration plan: {len(self.migration_plan.operations)} operations")
        
        return True
    
    def _save_checkpoint(self):
        """Save transaction manifest checkpoint"""
        try:
            checkpoint_path = self.schemas_root / "phase02_transaction_manifest.json"
            
            if not self.config.dry_run:
                self.schemas_root.mkdir(parents=True, exist_ok=True)
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.transaction_manifest), f, indent=2)
            
            if self.config.verbose:
                print(f"Checkpoint saved: {checkpoint_path}")
                
        except Exception as e:
            if self.config.verbose:
                print(f"Failed to save checkpoint: {str(e)}")
    
    def _finalize_transaction_manifest(self, success: bool):
        """Finalize the transaction manifest"""
        if self.transaction_manifest:
            self.transaction_manifest.status = "COMPLETED" if success else "FAILED"
            self.transaction_manifest.end_time = datetime.now().isoformat()
            
            # Save final manifest
            self._save_checkpoint()
    
    def _print_final_summary(self):
        """Print final pipeline summary"""
        if not self.config.verbose:
            return
        
        print("\n" + "="*80)
        print("PHASE 2 PIPELINE SUMMARY")
        print("="*80)
        
        print(f"Pipeline ID: {self.transaction_manifest.pipeline_id}")
        print(f"Status: {self.transaction_manifest.status}")
        print(f"Target Root: {self.config.target_root}")
        print(f"Total Files Processed: {self.transaction_manifest.total_files_processed}")
        print(f"Semantic Artifacts Loaded: {self.transaction_manifest.semantic_artifacts_loaded}")
        print(f"Operations Generated: {self.transaction_manifest.operations_generated}")
        
        print("\nValidation Summary:")
        passed = sum(1 for r in self.all_validation_results if r.status == "PASS")
        failed = sum(1 for r in self.all_validation_results if r.status == "FAIL")
        print(f"  Total Keys: {len(self.all_validation_results)}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        
        if self.migration_plan:
            print(f"\nMigration Plan:")
            print(f"  Schema Version: {self.migration_plan.schema_version}")
            print(f"  Mode: {self.migration_plan.mode}")
            print(f"  Operations: {len(self.migration_plan.operations)}")
            print(f"  Output: {SCHEMAS_ROOT / '01_agentic_core_migration_and_rewrite_plan.json'}")
        
        print("\n" + "="*80)
        
        if failed == 0:
            print("🎉 PHASE VALIDATION COMPLETE — ALL 88 KEYS PASS")
        else:
            print("❌ VALIDATION FAILED — Some keys did not pass")
        
        print("="*80)

def create_config_from_args(args) -> Phase2Config:
    """Create configuration from command line arguments"""
    return Phase2Config(
        target_root=args.target_root,
        semantic_cache_bucket=args.semantic_cache_bucket,
        write_target=args.write_target,
        dry_run=args.dry_run,
        resume_from=args.resume_from,
        validate_only=args.validate_only,
        verbose=args.verbose
    )

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Phase 2 Semantic Structural & Code Diff Planning Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python phase02_orchestrator.py                    # Full pipeline
  python phase02_orchestrator.py --dry-run          # Dry run mode
  python phase02_orchestrator.py --resume-from SEMANTIC_DIFF  # Resume from step
  python phase02_orchestrator.py --validate-only    # Validate only
  python phase02_orchestrator.py --verbose          # Verbose output
        """
    )
    
    parser.add_argument("--target-root", default="01_agentic_core/",
                       help="Target root directory (default: 01_agentic_core/)")
    parser.add_argument("--semantic-cache-bucket", default="06_data/semantic_cache/agentic_core/",
                       help="Semantic cache bucket path")
    parser.add_argument("--write-target", default="02_schemas/01_agentic_core_migration_and_rewrite_plan.json",
                       help="Output plan file path")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run in dry-run mode (no file writes)")
    parser.add_argument("--resume-from", choices=Phase02Orchestrator.ALL_STEPS,
                       help="Resume from specific step")
    parser.add_argument("--validate-only", action="store_true",
                       help="Run validation only (no plan generation)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Create configuration
    config = create_config_from_args(args)
    
    if args.verbose:
        print("Phase 2 Semantic Structural & Code Diff Planning Orchestrator")
        print("=" * 70)
        print(f"Configuration:")
        print(f"  Target Root: {config.target_root}")
        print(f"  Semantic Cache Bucket: {config.semantic_cache_bucket}")
        print(f"  Write Target: {config.write_target}")
        print(f"  Dry Run: {config.dry_run}")
        print(f"  Resume From: {config.resume_from}")
        print(f"  Validate Only: {config.validate_only}")
        print(f"  Verbose: {config.verbose}")
        print("=" * 70)
    
    # Create and run orchestrator
    orchestrator = Phase02Orchestrator(config)
    
    start_time = time.time()
    success = orchestrator.run_pipeline()
    end_time = time.time()
    
    if args.verbose:
        print(f"\nPipeline completed in {end_time - start_time:.2f} seconds")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
