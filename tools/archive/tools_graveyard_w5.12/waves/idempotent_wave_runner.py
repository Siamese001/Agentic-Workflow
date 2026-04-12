#!/usr/bin/env python3
"""
True Idempotent Wave Execution Framework.

This framework ensures waves are truly idempotent by combining
state management, pre-execution validation, and conditional execution.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add tools to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from idempotent_wave_template import IdempotentWave
from pre_execution_validator import PreExecutionValidator, validate_before_execution
from wave_state_manager import force_re_run_wave, get_state_manager


class IdempotentWaveRunner:
    """Manages execution of truly idempotent waves."""

    def __init__(self):
        self.state_manager = get_state_manager()
        self.validator = PreExecutionValidator()

    def run_wave(self, wave_name: str, force: bool = False, dry_run: bool = False) -> dict[str, Any]:
        """
        Run a single wave with full idempotency guarantees.

        Args:
            wave_name: Name of the wave to run
            force: Force execution regardless of conditions
            dry_run: Validate only, don't actually execute

        Returns:
            Execution result with full details
        """
        print(f"\n{'=' * 60}")
        print(f"Wave Execution: {wave_name}")
        print(f"{'=' * 60}")

        # Pre-execution validation
        if not validate_before_execution(wave_name, force):
            return {
                "wave_name": wave_name,
                "executed": False,
                "reason": "pre_execution_validation_failed",
                "timestamp": datetime.now().isoformat(),
            }

        if dry_run:
            return {
                "wave_name": wave_name,
                "executed": False,
                "reason": "dry_run_mode",
                "timestamp": datetime.now().isoformat(),
                "would_execute": True,
            }

        # Execute the wave
        try:
            wave_instance = self._create_wave_instance(wave_name)
            if wave_instance is None:
                return {
                    "wave_name": wave_name,
                    "executed": False,
                    "reason": "unknown_wave",
                    "timestamp": datetime.now().isoformat(),
                }

            result = wave_instance.execute()

            return {
                "wave_name": wave_name,
                "executed": True,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "wave_name": wave_name,
                "executed": False,
                "reason": "execution_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def run_wave_sequence(
        self, wave_names: list[str], force: bool = False, dry_run: bool = False
    ) -> dict[str, Any]:
        """
        Run a sequence of waves with dependency validation.

        Args:
            wave_names: List of wave names to run in order
            force: Force execution regardless of conditions
            dry_run: Validate only, don't actually execute

        Returns:
            Execution summary for all waves
        """
        print(f"\n{'=' * 80}")
        print("Wave Sequence Execution")
        print(f"{'=' * 80}")
        print(f"Waves: {', '.join(wave_names)}")
        print(f"Force: {force}")
        print(f"Dry Run: {dry_run}")

        # Generate execution plan
        plan = self.validator.generate_execution_plan(wave_names, force)

        print("\nExecution Plan:")
        print(f"  Waves to execute: {len(plan['execution_order'])}")
        print(f"  Waves to skip: {len(plan['skipped_waves'])}")

        results = {}

        # Execute waves in planned order
        for wave_name in plan["execution_order"]:
            result = self.run_wave(wave_name, force, dry_run)
            results[wave_name] = result

            # Stop on first failure unless forcing
            if not result["executed"] and not force:
                print(f"\n❌ Stopping execution due to failure in {wave_name}")
                break

        # Add skipped waves to results
        for skip in plan["skipped_waves"]:
            results[skip["wave"]] = {
                "wave_name": skip["wave"],
                "executed": False,
                "reason": skip["reason"],
                "details": skip["details"],
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "sequence": wave_names,
            "execution_plan": plan,
            "results": results,
            "summary": self._generate_execution_summary(results),
        }

    def _create_wave_instance(self, wave_name: str) -> IdempotentWave | None:
        """Create wave instance based on name."""
        # Import wave classes dynamically
        wave_classes = {
            "wave2a_first_party": "IdempotentWave2a",
            "wave5c_core_path_semantics": "IdempotentWave5c",
            # Add other wave classes as they're implemented
        }

        class_name = wave_classes.get(wave_name)
        if not class_name:
            print(f"❌ Unknown wave: {wave_name}")
            return None

        try:
            # Import and create instance
            if class_name == "IdempotentWave2a":
                from idempotent_wave_template import IdempotentWave2a

                return IdempotentWave2a()
            elif class_name == "IdempotentWave5c":
                from idempotent_wave_template import IdempotentWave5c

                return IdempotentWave5c()
            # Add other wave imports as needed

        except ImportError as e:
            print(f"❌ Could not import {class_name}: {e}")
            return None

        return None

    def _generate_execution_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate execution summary from results."""
        executed = len([r for r in results.values() if r["executed"]])
        skipped = len([r for r in results.values() if not r["executed"]])

        return {
            "total_waves": len(results),
            "executed": executed,
            "skipped": skipped,
            "success_rate": (executed / len(results)) * 100 if results else 0,
        }

    def reset_wave_state(self, wave_name: str):
        """Reset wave state for forced re-execution."""
        force_re_run_wave(wave_name)
        print(f"🔄 Wave {wave_name} state reset")

    def get_wave_status(self, wave_name: str) -> dict[str, Any]:
        """Get current status of a wave."""
        state = self.state_manager.get_wave_name(wave_name)

        if not state:
            return {
                "wave_name": wave_name,
                "status": "never_executed",
                "details": "No execution record found",
            }

        return {
            "wave_name": wave_name,
            "status": "completed" if state.is_complete else "incomplete",
            "execution_id": state.execution_id,
            "timestamp": state.timestamp,
            "files_modified": len(state.files_modified),
            "patterns_applied": sum(len(patterns) for patterns in state.patterns_applied.values()),
            "metrics": state.metrics,
        }

    def get_all_wave_status(self) -> dict[str, Any]:
        """Get status of all waves."""
        summary = self.state_manager.get_execution_summary()

        return {
            "timestamp": datetime.now().isoformat(),
            "total_waves": summary["total_waves"],
            "completed_waves": summary["completed_waves"],
            "waves": summary["waves"],
        }


def main():
    """Example usage of the idempotent wave runner."""
    runner = IdempotentWaveRunner()

    # Example 1: Run single wave
    print("Example 1: Single Wave Execution")
    result = runner.run_wave("wave5c_core_path_semantics", dry_run=True)
    print(f"Result: {result}")

    # Example 2: Run wave sequence
    print("\nExample 2: Wave Sequence Execution")
    waves = ["wave2a_first_party", "wave5c_core_path_semantics"]
    sequence_result = runner.run_wave_sequence(waves, dry_run=True)
    print(f"Sequence result: {sequence_result['summary']}")

    # Example 3: Get wave status
    print("\nExample 3: Wave Status")
    status = runner.get_wave_status("wave5c_core_path_semantics")
    print(f"Wave status: {status}")

    # Example 4: Get all wave status
    print("\nExample 4: All Wave Status")
    all_status = runner.get_all_wave_status()
    print(f"All waves: {all_status['total_waves']} completed, {all_status['completed_waves']}")


if __name__ == "__main__":
    main()
