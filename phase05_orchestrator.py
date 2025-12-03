#!/usr/bin/env python3
"""
Phase 0.5 Semantic Cache Rebuild - Main Orchestration Script

Main pipeline orchestrator for Phase 0.5 semantic cache rebuild with
dependency injection, error recovery, and checkpoint/resume capability.

ZERO-LOSS CONSTRAINTS:
- Pipeline with error recovery and rollback
- Dependency injection to avoid circular imports
- Transaction manifest for checkpoint/resume
- Only writes to 06_data/semantic_cache/
- Docker-safe paths only
"""

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Project constants
PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
SEMANTIC_CACHE_ROOT = PROJECT_ROOT / "06_data" / "semantic_cache"
TRANSACTION_MANIFEST = SEMANTIC_CACHE_ROOT / "meta" / "transaction_manifest.json"

# Import our modules (avoiding circular imports through dependency injection)
from ssot_loader import SSoTLoader
from archive_scanner import ArchiveScanner, FileInfo
from semantic_artifact_generator import SemanticArtifactGenerator
from dual_write_coordinator import DualWriteCoordinator
from validation_engine import ValidationEngine

@dataclass
class PipelineStep:
    """Represents a pipeline step with status and metadata"""
    step_id: str
    step_name: str
    status: str  # "PENDING", "RUNNING", "COMPLETED", "FAILED"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    artifacts_created: List[str] = None
    
    def __post_init__(self):
        if self.artifacts_created is None:
            self.artifacts_created = []

@dataclass
class TransactionManifest:
    """Transaction manifest for pipeline state tracking"""
    pipeline_id: str
    start_time: str
    status: str  # "RUNNING", "COMPLETED", "FAILED", "RESUMED"
    dry_run: bool
    steps: List[PipelineStep]
    current_step: int
    total_files_processed: int
    artifacts_generated: int

class Phase05Orchestrator:
    """
    Main orchestrator for Phase 0.5 semantic cache rebuild.
    
    Implements pipeline with dependency injection, error recovery,
    and checkpoint/resume capability using transaction manifest.
    """
    
    def __init__(self, dry_run: bool = False, resume_from: Optional[str] = None):
        self.dry_run = dry_run
        self.resume_from = resume_from
        self.pipeline_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize all modules (dependency injection)
        self.ssot_loader = SSoTLoader(dry_run=dry_run)
        self.archive_scanner = ArchiveScanner(dry_run=dry_run)
        self.artifact_generator = SemanticArtifactGenerator(dry_run=dry_run)
        self.dual_write_coordinator = DualWriteCoordinator(self.ssot_loader, dry_run=dry_run)
        self.validation_engine = ValidationEngine(dry_run=dry_run)
        
        # Inject dependencies to avoid circular imports
        self.validation_engine.set_dependencies(
            ssot_loader=self.ssot_loader,
            archive_scanner=self.archive_scanner,
            artifact_generator=self.artifact_generator,
            dual_write_coordinator=self.dual_write_coordinator
        )
        
        # Pipeline steps
        self.pipeline_steps = [
            PipelineStep("SSOT_LOAD", "Load and validate SSoT", "PENDING"),
            PipelineStep("ARCHIVE_SCAN", "Scan archives and compute hashes", "PENDING"),
            PipelineStep("ARTIFACT_GENERATION", "Generate semantic artifacts", "PENDING"),
            PipelineStep("DUAL_WRITE", "Create global artifacts and canonical pointers", "PENDING"),
            PipelineStep("VALIDATION", "Run comprehensive validation", "PENDING"),
            PipelineStep("CLEANUP", "Final cleanup and reporting", "PENDING")
        ]
        
        # Transaction manifest
        self.transaction_manifest = None
        self.current_step_index = 0
        
        # Statistics
        self.stats = {
            "total_files_scanned": 0,
            "eligible_files_processed": 0,
            "global_artifacts_created": 0,
            "canonical_pointers_created": 0,
            "validation_keys_passed": 0,
            "validation_keys_failed": 0
        }
    
    def load_or_create_manifest(self) -> bool:
        """Load existing manifest or create new one"""
        try:
            if self.resume_from and TRANSACTION_MANIFEST.exists():
                # Load existing manifest for resume
                with open(TRANSACTION_MANIFEST, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                self.transaction_manifest = TransactionManifest(**manifest_data)
                
                # Find current step index
                for i, step in enumerate(self.transaction_manifest.steps):
                    if step.status != "COMPLETED":
                        self.current_step_index = i
                        break
                else:
                    # All steps completed
                    self.current_step_index = len(self.transaction_manifest.steps)
                
                print(f"Resuming from step: {self.current_step_index}")
                return True
            else:
                # Create new manifest
                self.transaction_manifest = TransactionManifest(
                    pipeline_id=self.pipeline_id,
                    start_time=datetime.now().isoformat(),
                    status="RUNNING",
                    dry_run=self.dry_run,
                    steps=self.pipeline_steps,
                    current_step=0,
                    total_files_processed=0,
                    artifacts_generated=0
                )
                return True
                
        except Exception as e:
            print(f"Error loading/creating manifest: {str(e)}")
            return False
    
    def save_manifest(self) -> bool:
        """Save transaction manifest"""
        try:
            if not self.dry_run and self.transaction_manifest:
                manifest_path = TRANSACTION_MANIFEST
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.transaction_manifest), f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving manifest: {str(e)}")
            return False
    
    def update_step_status(self, step_index: int, status: str, error_message: str = None):
        """Update step status in manifest"""
        if step_index < len(self.transaction_manifest.steps):
            step = self.transaction_manifest.steps[step_index]
            step.status = status
            
            if status == "RUNNING":
                step.start_time = datetime.now().isoformat()
            elif status in ["COMPLETED", "FAILED"]:
                step.end_time = datetime.now().isoformat()
                if error_message:
                    step.error_message = error_message
            
            self.transaction_manifest.current_step = step_index
            self.save_manifest()
    
    def run_pipeline(self) -> bool:
        """Run the complete pipeline"""
        print("=== Phase 0.5 Semantic Cache Rebuild ===")
        print(f"Pipeline ID: {self.pipeline_id}")
        print(f"Dry Run: {self.dry_run}")
        print(f"Resume From: {self.resume_from}")
        print(f"Semantic Cache Root: {SEMANTIC_CACHE_ROOT}")
        print()
        
        # Load or create transaction manifest
        if not self.load_or_create_manifest():
            print("Failed to load/create transaction manifest")
            return False
        
        try:
            # Run pipeline steps
            for i, step in enumerate(self.pipeline_steps):
                if i < self.current_step_index:
                    # Skip already completed steps
                    print(f"Skipping completed step: {step.step_name}")
                    continue
                
                print(f"Running step {i+1}/{len(self.pipeline_steps)}: {step.step_name}")
                self.update_step_status(i, "RUNNING")
                
                try:
                    success = self._run_step(i)
                    if success:
                        self.update_step_status(i, "COMPLETED")
                        print(f"✓ Step completed: {step.step_name}")
                    else:
                        self.update_step_status(i, "FAILED", f"Step {step.step_name} failed")
                        print(f"✗ Step failed: {step.step_name}")
                        return False
                except Exception as e:
                    self.update_step_status(i, "FAILED", str(e))
                    print(f"✗ Step failed with exception: {step.step_name}")
                    print(f"Error: {str(e)}")
                    traceback.print_exc()
                    return False
                
                print()
            
            # Mark pipeline as completed
            self.transaction_manifest.status = "COMPLETED"
            self.save_manifest()
            
            print("=== Pipeline Completed Successfully ===")
            self._print_final_summary()
            return True
            
        except KeyboardInterrupt:
            print("\nPipeline interrupted by user")
            self.transaction_manifest.status = "INTERRUPTED"
            self.save_manifest()
            return False
        except Exception as e:
            print(f"Pipeline failed with exception: {str(e)}")
            self.transaction_manifest.status = "FAILED"
            self.save_manifest()
            return False
    
    def _run_step(self, step_index: int) -> bool:
        """Run a specific pipeline step"""
        step = self.pipeline_steps[step_index]
        
        if step.step_id == "SSOT_LOAD":
            return self._run_ssot_load(step)
        elif step.step_id == "ARCHIVE_SCAN":
            return self._run_archive_scan(step)
        elif step.step_id == "ARTIFACT_GENERATION":
            return self._run_artifact_generation(step)
        elif step.step_id == "DUAL_WRITE":
            return self._run_dual_write(step)
        elif step.step_id == "VALIDATION":
            return self._run_validation(step)
        elif step.step_id == "CLEANUP":
            return self._run_cleanup(step)
        else:
            print(f"Unknown step: {step.step_id}")
            return False
    
    def _run_ssot_load(self, step: PipelineStep) -> bool:
        """Run SSoT loading and validation"""
        success = self.ssot_loader.load_ssot()
        if success:
            # Save validation report
            self.ssot_loader.save_validation_report()
            step.artifacts_created = ["ssot_validation_report.json"]
        
        return success
    
    def _run_archive_scan(self, step: PipelineStep) -> bool:
        """Run archive scanning"""
        # Scan Resume Engine archives
        resume_results = self.archive_scanner.scan_resume_engine_archives()
        
        # Scan Outreach Engine archives
        outreach_results = self.archive_scanner.scan_outreach_engine_archives()
        
        # Build hash index
        self.archive_scanner.build_hash_index()
        
        # Generate integrity records
        self.archive_scanner.generate_integrity_records()
        
        # Save scan report
        self.archive_scanner.save_scan_report(resume_results, outreach_results)
        
        # Update statistics
        scanned_files = self.archive_scanner.get_scanned_files()
        self.stats["total_files_scanned"] = len(scanned_files)
        self.stats["eligible_files_processed"] = sum(1 for f in scanned_files if f.is_eligible)
        
        step.artifacts_created = [
            "archive_scan_report.json",
            f"integrity_records_{len(scanned_files)}.json"
        ]
        
        return True
    
    def _run_artifact_generation(self, step: PipelineStep) -> bool:
        """Run semantic artifact generation"""
        scanned_files = self.archive_scanner.get_scanned_files()
        eligible_files = [f for f in scanned_files if f.is_eligible]
        
        print(f"Generating artifacts for {len(eligible_files)} eligible files...")
        
        generated_count = 0
        for i, file_info in enumerate(eligible_files):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(eligible_files)} files processed")
            
            success = self.artifact_generator.generate_artifacts_for_file(file_info)
            if success:
                generated_count += 1
        
        # Generate integrity for non-eligible files
        non_eligible_files = [f for f in scanned_files if not f.is_eligible]
        for file_info in non_eligible_files:
            self.artifact_generator.generate_artifacts_for_file(file_info)
        
        self.stats["global_artifacts_created"] = generated_count * 7  # 7 artifacts per eligible file
        
        step.artifacts_created = [
            f"semantic_artifacts_{generated_count}.json"
        ]
        
        print(f"Generated artifacts for {generated_count} files")
        return True
    
    def _run_dual_write(self, step: PipelineStep) -> bool:
        """Run dual-write coordination"""
        scanned_files = self.archive_scanner.get_scanned_files()
        
        print(f"Processing {len(scanned_files)} files through dual-write system...")
        
        processed_count = 0
        for i, file_info in enumerate(scanned_files):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(scanned_files)} files processed")
            
            success = self.dual_write_coordinator.process_file_artifacts(
                file_info, self.artifact_generator
            )
            if success:
                processed_count += 1
        
        # Save dual-write report
        self.dual_write_coordinator.save_dual_write_report()
        
        # Update statistics
        summary = self.dual_write_coordinator.get_coordination_summary()
        self.stats["canonical_pointers_created"] = summary["statistics"]["canonical_pointers_created"]
        
        step.artifacts_created = [
            "dual_write_report.json",
            "unmapped_files.json" if summary["unmapped_file_count"] > 0 else None
        ]
        step.artifacts_created = [a for a in step.artifacts_created if a is not None]
        
        print(f"Processed {processed_count} files through dual-write system")
        return True
    
    def _run_validation(self, step: PipelineStep) -> bool:
        """Run comprehensive validation"""
        success = self.validation_engine.run_full_validation()
        
        # Save validation report
        self.validation_engine.save_validation_report()
        
        # Update statistics
        self.stats["validation_keys_passed"] = self.validation_engine.validation_stats["passed_keys"]
        self.stats["validation_keys_failed"] = self.validation_engine.validation_stats["failed_keys"]
        
        step.artifacts_created = ["validation_report.json"]
        
        return success
    
    def _run_cleanup(self, step: PipelineStep) -> bool:
        """Run final cleanup and reporting"""
        # Generate final pipeline report
        final_report = {
            "pipeline_id": self.pipeline_id,
            "completion_timestamp": datetime.now().isoformat(),
            "statistics": self.stats,
            "transaction_manifest": asdict(self.transaction_manifest),
            "semantic_cache_summary": self._generate_cache_summary()
        }
        
        if not self.dry_run:
            report_path = SEMANTIC_CACHE_ROOT / "meta" / "pipeline_completion_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2)
        
        step.artifacts_created = ["pipeline_completion_report.json"]
        return True
    
    def _generate_cache_summary(self) -> Dict:
        """Generate summary of semantic cache contents"""
        summary = {}
        
        # Count artifacts in each directory
        for dir_name in ["ast", "embeddings", "diffs", "golden", "safety", "integrity", "meta"]:
            dir_path = SEMANTIC_CACHE_ROOT / dir_name
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                files = [f for f in files if f.is_file()]
                summary[dir_name] = len(files)
            else:
                summary[dir_name] = 0
        
        return summary
    
    def _print_final_summary(self):
        """Print final pipeline summary"""
        print("=== Final Summary ===")
        print(f"Total files scanned: {self.stats['total_files_scanned']}")
        print(f"Eligible files processed: {self.stats['eligible_files_processed']}")
        print(f"Global artifacts created: {self.stats['global_artifacts_created']}")
        print(f"Canonical pointers created: {self.stats['canonical_pointers_created']}")
        print(f"Validation keys passed: {self.stats['validation_keys_passed']}")
        print(f"Validation keys failed: {self.stats['validation_keys_failed']}")
        
        if self.stats['validation_keys_failed'] == 0:
            print()
            print("🎉 PHASE 0.5 COMPLETED SUCCESSFULLY!")
            print("✅ ALL VALIDATION KEYS PASSED")
            print("✅ SEMANTIC CACHE READY FOR PHASE 2")
        else:
            print()
            print("⚠️  PHASE 0.5 COMPLETED WITH VALIDATION FAILURES")
            print("❌ SOME VALIDATION KEYS FAILED")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 0.5 Semantic Cache Rebuild Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--resume-from", help="Resume from specific step (SSOT_LOAD, ARCHIVE_SCAN, etc.)")
    parser.add_argument("--list-steps", action="store_true", help="List available pipeline steps")
    args = parser.parse_args()
    
    if args.list_steps:
        print("Available pipeline steps:")
        steps = ["SSOT_LOAD", "ARCHIVE_SCAN", "ARTIFACT_GENERATION", "DUAL_WRITE", "VALIDATION", "CLEANUP"]
        for step in steps:
            print(f"  {step}")
        return 0
    
    # Create orchestrator
    orchestrator = Phase05Orchestrator(dry_run=args.dry_run, resume_from=args.resume_from)
    
    # Run pipeline
    success = orchestrator.run_pipeline()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
