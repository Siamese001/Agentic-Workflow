#!/usr/bin/env python3
"""
Batch Gravity Healing Orchestrator
Processes violations in controlled batches for system stability

SAFETY FEATURES:
- Processes violations in batches of 5 (configurable)
- Creates checkpoints before each batch
- Skips already-healed imports via GravityStateAgent
- Provides detailed progress reporting
- Supports pause/resume via state tracking
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.GravityValidatorAgent import (
    GravityValidatorAgent,
    GravityViolation,
)
from agentic_core.L2_execution.ToolRegistry.GravityHealerAgent import GravityHealerAgent
from agentic_core.L4_state.GravityStateAgent import GravityStateAgent, HealingRecord
from datetime import datetime


class BatchGravityOrchestrator:
    """
    Orchestrates batch healing of gravity violations.
    
    Features:
    - Batch processing (default: 5 violations per batch)
    - State tracking to prevent re-healing
    - Checkpoint creation before each batch
    - Progress reporting and statistics
    """
    
    def __init__(
        self,
        project_root: Path,
        batch_size: int = 5,
        target_directory: str = "agentic_core/L1_cognition"
    ):
        self.root = project_root
        self.batch_size = batch_size
        self.target_dir = project_root / target_directory
        
        # Initialize agents
        self.validator = GravityValidatorAgent(project_root)
        self.healer = GravityHealerAgent(project_root)
        self.state_tracker = GravityStateAgent(project_root)
    
    async def scan_violations(self) -> List[GravityViolation]:
        """
        Scan target directory for violations, excluding already-healed imports.
        
        Returns:
            List of unhealed GravityViolation objects
        """
        print(f"\n📂 Scanning: {self.target_dir.relative_to(self.root)}")
        
        all_violations = []
        files_scanned = 0
        
        for py_file in self.target_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            
            files_scanned += 1
            violations = await self.validator.detect_violations(py_file)
            
            # Filter out already-healed violations AND architectural violations requiring manual intervention
            unhealed = [
                v for v in violations
                if not self.state_tracker.is_healed(v.file_path, v.import_line)
                and v.suggested_action != "RELOCATE_FILE"
            ]
            
            all_violations.extend(unhealed)
        
        print(f"   Files scanned: {files_scanned}")
        print(f"   Total violations: {len(all_violations)}")
        
        return all_violations
    
    def group_violations_by_file(
        self, violations: List[GravityViolation]
    ) -> Dict[Path, List[GravityViolation]]:
        """Group violations by file for efficient batch processing."""
        by_file = {}
        for v in violations:
            if v.file_path not in by_file:
                by_file[v.file_path] = []
            by_file[v.file_path].append(v)
        return by_file
    
    async def heal_batch(
        self, batch: List[GravityViolation], batch_num: int
    ) -> Dict[str, Any]:
        """
        Heal a single batch of violations.
        
        Args:
            batch: List of violations to heal
            batch_num: Batch number for logging
            
        Returns:
            Dict with healing results
        """
        print(f"\n🔧 BATCH {batch_num}: Healing {len(batch)} violation(s)...")
        
        # Create checkpoint before healing
        checkpoint = self.state_tracker.create_checkpoint(f"batch_{batch_num}")
        print(f"   💾 Checkpoint: {Path(checkpoint).name}")
        
        # Heal violations
        results = await self.healer.heal(batch)
        
        # Record successful healings in state tracker
        for result in results['results']:
            if result['result']['success']:
                # Find the original violation
                violation = next(
                    (v for v in batch if str(v.file_path) == result['file']),
                    None
                )
                
                if violation:
                    record = HealingRecord(
                        file_path=str(violation.file_path),
                        original_import=violation.import_line,
                        healed_import="dynamic_import",
                        violation_type=violation.violation_type,
                        healing_strategy=result['result']['strategy'],
                        timestamp=datetime.now().isoformat(),
                        line_number=violation.line_number,
                    )
                    self.state_tracker.record_healing(record)
        
        # Display results
        stats = results['statistics']
        print(f"   ✅ Healed: {stats['healed']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print(f"   ⏭️  Skipped: {stats['skipped']}")
        
        return results
    
    async def verify_batch_integrity(self, batch: List[GravityViolation]) -> bool:
        """
        Post-healing verification: Scans modified files to ensure 
        the specific violations are no longer detected.
        """
        files_to_check = {v.file_path for v in batch}
        all_clear = True
        
        for file_path in files_to_check:
            remaining_violations = await self.validator.detect_violations(file_path)
            # ARCHITECTURAL HARDENING: Skip verification for RELOCATE_FILE actions 
            # since those require manual architectural intervention.
            healed_lines = {
                v.line_number for v in batch 
                if v.file_path == file_path 
                and v.suggested_action != "RELOCATE_FILE"
            }
            lingering = [v for v in remaining_violations if v.line_number in healed_lines]
            
            if lingering:
                print(f"   ⚠️  Verification Failed for {file_path.name}: {len(lingering)} violations persist.")
                all_clear = False
        
        return all_clear
    
    async def run(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Run batch healing orchestration.
        
        Args:
            dry_run: If True, only scan and report (no healing)
            
        Returns:
            Dict with comprehensive results
        """
        print("=" * 80)
        print("BATCH GRAVITY HEALING ORCHESTRATOR")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE HEALING'}")
        print(f"Batch size: {self.batch_size}")
        print(f"Target: {self.target_dir.relative_to(self.root)}")
        
        # Scan for violations
        violations = await self.scan_violations()
        
        if not violations:
            print("\n✅ No violations found!")
            return {"total_violations": 0, "batches_processed": 0}
        
        # Group by file
        by_file = self.group_violations_by_file(violations)
        print(f"\n📊 Violations by file:")
        for file_path, file_violations in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"   {file_path.relative_to(self.root)}: {len(file_violations)} violation(s)")
        
        if dry_run:
            print("\n" + "=" * 80)
            print("DRY RUN COMPLETE - No files modified")
            print("=" * 80)
            print(f"\nTo run actual healing:")
            print(f"  python batch_gravity_heal.py --live")
            return {
                "total_violations": len(violations),
                "batches_needed": (len(violations) + self.batch_size - 1) // self.batch_size,
                "files_affected": len(by_file),
            }
        
        # Batch processing
        print("\n" + "=" * 80)
        print("STARTING BATCH HEALING")
        print("=" * 80)
        
        batches = [
            violations[i:i + self.batch_size]
            for i in range(0, len(violations), self.batch_size)
        ]
        
        all_results = []
        total_healed = 0
        total_failed = 0
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n{'=' * 80}")
            print(f"BATCH {batch_num}/{len(batches)}")
            print(f"{'=' * 80}")
            
            result = await self.heal_batch(batch, batch_num)
            all_results.append(result)
            
            total_healed += result['statistics']['healed']
            total_failed += result['statistics']['failed']
            
            # Active verification instead of blind sleep
            if batch_num < len(batches):
                verified = await self.verify_batch_integrity(batch)
                if not verified:
                    print("   🛑 Batch verification failed. Stopping pipeline for investigation.")
                    break
                print(f"   ✅ Batch {batch_num} verified. Proceeding...")
                await asyncio.sleep(0.5)  # Minimal breather
        
        # Final summary
        print("\n" + "=" * 80)
        print("BATCH HEALING COMPLETE")
        print("=" * 80)
        
        summary = self.state_tracker.get_healing_summary()
        
        print(f"\n📊 Final Statistics:")
        print(f"   Total violations processed: {len(violations)}")
        print(f"   Batches processed: {len(batches)}")
        print(f"   Successfully healed: {total_healed}")
        print(f"   Failed: {total_failed}")
        print(f"   Files modified: {summary['total_files_healed']}")
        
        print(f"\n📈 By violation type:")
        for vtype, count in summary['by_violation_type'].items():
            print(f"   {vtype}: {count}")
        
        print(f"\n🔧 By healing strategy:")
        for strategy, count in summary['by_strategy'].items():
            print(f"   {strategy}: {count}")
        
        print("\n" + "=" * 80)
        
        return {
            "total_violations": len(violations),
            "batches_processed": len(batches),
            "total_healed": total_healed,
            "total_failed": total_failed,
            "summary": summary,
        }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch Gravity Healing Orchestrator")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run actual healing (default is dry run)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of violations per batch (default: 5)"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="agentic_core/L1_cognition",
        help="Target directory to heal (default: agentic_core/L1_cognition)"
    )
    
    args = parser.parse_args()
    
    orchestrator = BatchGravityOrchestrator(
        project_root=project_root,
        batch_size=args.batch_size,
        target_directory=args.target,
    )
    
    await orchestrator.run(dry_run=not args.live)


if __name__ == "__main__":
    asyncio.run(main())
