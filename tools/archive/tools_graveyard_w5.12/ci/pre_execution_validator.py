#!/usr/bin/env python3
"""
Pre-Execution Validation - Validates conditions before wave execution.

This module provides validation functions to ensure waves only
execute when necessary conditions are met.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from wave_state_manager import get_state_manager


class PreExecutionValidator:
    """Validates pre-conditions for wave execution."""

    def __init__(self):
        self.state_manager = get_state_manager()

    def should_execute_wave(self, wave_name: str, force: bool = False) -> dict[str, Any]:
        """
        Determine if a wave should execute based on various conditions.

        Args:
            wave_name: Name of the wave to validate
            force: Force execution regardless of conditions

        Returns:
            Validation result with reasoning
        """
        if force:
            return {
                "should_execute": True,
                "reason": "forced_execution",
                "details": "Execution forced by user request",
            }

        # Check if wave was already completed
        if self.state_manager.is_wave_complete(wave_name):
            return {
                "should_execute": False,
                "reason": "already_completed",
                "details": f"Wave {wave_name} was already completed",
            }

        # Check wave dependencies
        dependency_result = self._check_dependencies(wave_name)
        if not dependency_result["satisfied"]:
            return {
                "should_execute": False,
                "reason": "dependencies_not_met",
                "details": dependency_result["missing_dependencies"],
            }

        # Check if target files have changed
        files_changed_result = self._check_target_files_changed(wave_name)
        if not files_changed_result["changed"]:
            return {
                "should_execute": False,
                "reason": "no_changes_detected",
                "details": "No target files have changed since last execution",
            }

        # Check if enough time has passed (for periodic waves)
        time_result = self._check_execution_frequency(wave_name)
        if not time_result["should_execute"]:
            return {
                "should_execute": False,
                "reason": "too_soon",
                "details": time_result["details"],
            }

        return {
            "should_execute": True,
            "reason": "conditions_met",
            "details": "All execution conditions satisfied",
        }

    def _check_dependencies(self, wave_name: str) -> dict[str, Any]:
        """Check if wave dependencies are satisfied."""
        # Define wave dependencies
        dependencies = {
            "wave2a_first_party": ["wave1d_categorization"],
            "wave2b_fixture_masking": ["wave1d_categorization"],
            "wave2c_hidden_failures": ["wave1d_categorization"],
            "wave3a_hollowed_import": ["wave2c_hidden_failures"],
            "wave3b_runtime_assertions": ["wave3a_hollowed_import"],
            "wave3c_contract_assertions": ["wave3b_runtime_assertions"],
            "wave4a_contract_skips": ["wave3c_contract_assertions"],
            "wave4b_fake_mock_skips": ["wave3c_contract_assertions"],
            "wave5a_pytest_config": ["wave4b_fake_mock_skips"],
            "wave5b_marker_hardening": ["wave5a_pytest_config"],
            "wave5c_core_path_semantics": ["wave5b_marker_hardening"],
            "wave6a_validation_enforcement": ["wave5c_core_path_semantics"],
            "wave6b_validation_testing": ["wave6a_validation_enforcement"],
            "wave7a_github_actions": ["wave6b_validation_testing"],
            "wave7b_multi_environment": ["wave7a_github_actions"],
        }

        wave_deps = dependencies.get(wave_name, [])
        missing_deps = []

        for dep in wave_deps:
            if not self.state_manager.is_wave_complete(dep):
                missing_deps.append(dep)

        return {
            "satisfied": len(missing_deps) == 0,
            "dependencies": wave_deps,
            "missing_dependencies": missing_deps,
        }

    def _check_target_files_changed(self, wave_name: str) -> dict[str, Any]:
        """Check if target files for a wave have changed."""
        # Define target file patterns for each wave
        target_patterns = {
            "wave2a_first_party": ["tests/**/*.py"],
            "wave2b_fixture_masking": ["tests/**/*.py"],
            "wave2c_hidden_failures": ["tests/**/*.py"],
            "wave3a_hollowed_import": ["tests/**/*.py"],
            "wave3b_runtime_assertions": ["tests/**/*.py"],
            "wave3c_contract_assertions": ["tests/**/*.py"],
            "wave4a_contract_skips": ["tests/**/*.py"],
            "wave4b_fake_mock_skips": ["tests/**/*.py"],
            "wave5a_pytest_config": ["pytest.ini", "pyproject.toml", "setup.cfg"],
            "wave5b_marker_hardening": ["tests/**/*.py"],
            "wave5c_core_path_semantics": ["**/conftest.py"],
            "wave6a_validation_enforcement": ["tools/**/*.py"],
            "wave6b_validation_testing": ["tools/**/*.py"],
            "wave7a_github_actions": [".github/workflows/*.yml"],
            "wave7b_multi_environment": [".github/workflows/*.yml"],
        }

        patterns = target_patterns.get(wave_name, [])

        if not patterns:
            return {"changed": True, "details": "No target patterns defined"}

        # Get previous execution state
        state = self.state_manager.get_wave_name(wave_name)
        if not state:
            return {"changed": True, "details": "No previous execution found"}

        # Check if any target files have changed
        changed_files = []
        for pattern in patterns:
            for file_path in Path(".").glob(pattern):
                if self.state_manager.has_file_changed_since_wave(wave_name, file_path):
                    changed_files.append(str(file_path))

        return {
            "changed": len(changed_files) > 0,
            "changed_files": changed_files,
            "details": f"{len(changed_files)} files changed since last execution",
        }

    def _check_execution_frequency(self, wave_name: str, min_hours: int = 1) -> dict[str, Any]:
        """Check if enough time has passed since last execution."""
        state = self.state_manager.get_wave_name(wave_name)

        if not state:
            return {"should_execute": True, "details": "No previous execution"}

        try:
            last_execution = datetime.fromisoformat(state.timestamp)
            time_since = datetime.now() - last_execution

            if time_since < timedelta(hours=min_hours):
                return {
                    "should_execute": False,
                    "details": f"Last execution {time_since.total_seconds() / 3600:.1f} hours ago (minimum: {min_hours} hours)",
                }

            return {
                "should_execute": True,
                "details": f"Last execution {time_since.total_seconds() / 3600:.1f} hours ago",
            }

        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            return {"should_execute": True, "details": f"Error checking execution time: {e}"}

    def validate_wave_prerequisites(self, wave_name: str) -> dict[str, Any]:
        """Validate all prerequisites for wave execution."""
        validations = {
            "dependencies": self._check_dependencies(wave_name),
            "file_changes": self._check_target_files_changed(wave_name),
            "execution_frequency": self._check_execution_frequency(wave_name),
        }

        # Overall validation result
        all_satisfied = all(
            [
                validations["dependencies"]["satisfied"],
                validations["file_changes"]["changed"],
                validations["execution_frequency"]["should_execute"],
            ]
        )

        return {
            "wave_name": wave_name,
            "should_execute": all_satisfied,
            "validations": validations,
            "summary": {
                "dependencies_satisfied": validations["dependencies"]["satisfied"],
                "files_changed": validations["file_changes"]["changed"],
                "time_elapsed_sufficient": validations["execution_frequency"]["should_execute"],
            },
        }

    def generate_execution_plan(self, wave_names: list[str], force: bool = False) -> dict[str, Any]:
        """Generate execution plan for multiple waves."""
        plan = {
            "timestamp": datetime.now().isoformat(),
            "force_execution": force,
            "waves": {},
            "execution_order": [],
            "skipped_waves": [],
        }

        for wave_name in wave_names:
            validation = self.should_execute_wave(wave_name, force)

            plan["waves"][wave_name] = validation

            if validation["should_execute"]:
                plan["execution_order"].append(wave_name)
            else:
                plan["skipped_waves"].append(
                    {
                        "wave": wave_name,
                        "reason": validation["reason"],
                        "details": validation["details"],
                    }
                )

        return plan


def validate_before_execution(wave_name: str, force: bool = False) -> bool:
    """
    Validate and potentially skip wave execution.

    Args:
        wave_name: Name of the wave to validate
        force: Force execution regardless of conditions

    Returns:
        True if wave should execute, False if should skip
    """
    validator = PreExecutionValidator()
    result = validator.should_execute_wave(wave_name, force)

    if not result["should_execute"]:
        print(f"⚪ Skipping {wave_name}: {result['reason']}")
        print(f"   Details: {result['details']}")
        return False

    print(f"✅ Executing {wave_name}: {result['reason']}")
    return True


def main():
    """Example usage of pre-execution validation."""
    print("=== Pre-Execution Validation Demo ===")

    validator = PreExecutionValidator()

    # Validate specific wave
    wave_name = "wave5c_core_path_semantics"
    validation = validator.validate_wave_prerequisites(wave_name)

    print(f"\nValidation for {wave_name}:")
    print(f"Should execute: {validation['should_execute']}")
    print(f"Dependencies satisfied: {validation['summary']['dependencies_satisfied']}")
    print(f"Files changed: {validation['summary']['files_changed']}")
    print(f"Time elapsed sufficient: {validation['summary']['time_elapsed_sufficient']}")

    # Generate execution plan
    waves = ["wave2a_first_party", "wave3b_runtime_assertions", "wave5c_core_path_semantics"]
    plan = validator.generate_execution_plan(waves)

    print("\nExecution Plan:")
    print(f"Waves to execute: {plan['execution_order']}")
    print(f"Waves to skip: {len(plan['skipped_waves'])}")

    for skip in plan["skipped_waves"]:
        print(f"  - {skip['wave']}: {skip['reason']}")


if __name__ == "__main__":
    main()
