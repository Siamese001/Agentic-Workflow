#!/usr/bin/env python3
"""
Idempotent Wave Template - Base class for truly idempotent wave executions.

This template demonstrates how to implement proper idempotency
using the WaveStateManager.
"""

import sys
from pathlib import Path
from typing import Any

# Add tools to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from wave_state_manager import (
    check_file_idempotency,
    check_pattern_idempotency,
    complete_wave,
    get_state_manager,
    start_wave,
)


class IdempotentWave:
    """Base class for idempotent wave executions."""

    def __init__(self, wave_name: str):
        self.wave_name = wave_name
        self.execution_id = None
        self.metrics = {}
        self.state_manager = get_state_manager()

    def execute(self) -> dict[str, Any]:
        """Execute the wave idempotently."""
        # Start wave with idempotency check
        self.execution_id = start_wave(self.wave_name)
        if self.execution_id is None:
            # Wave already completed, return previous results
            return self._get_previous_results()

        try:
            # Execute wave logic
            results = self._execute_wave_logic()

            # Record metrics and complete wave
            complete_wave(self.wave_name, self.metrics)

            return results

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            print(f"❌ Wave {self.wave_name} failed: {e}")
            raise

    def _get_previous_results(self) -> dict[str, Any]:
        """Get results from previous wave execution."""
        state = self.state_manager.get_wave_state(self.wave_name)
        if state:
            print(f"📋 Using previous results for {self.wave_name}")
            return {
                'wave_name': self.wave_name,
                'execution_id': state.execution_id,
                'timestamp': state.timestamp,
                'metrics': state.metrics,
                'files_modified': list(state.files_modified.keys()),
                'patterns_applied': {
                    pattern_type: list(patterns)
                    for pattern_type, patterns in state.patterns_applied.items()
                },
                'idempotent': True,
            }
        return {}

    def _execute_wave_logic(self) -> dict[str, Any]:
        """Override this method in subclasses to implement wave logic."""
        raise NotImplementedError("Subclasses must implement _execute_wave_logic")

    def modify_file_idempotently(self, file_path: Path, modification_func) -> bool:
        """Modify a file idempotently."""
        return check_file_idempotency(self.wave_name, file_path, modification_func)

    def apply_pattern_idempotently(self, pattern_type: str, pattern: str, application_func) -> bool:
        """Apply a pattern idempotently."""
        return check_pattern_idempotency(self.wave_name, pattern_type, pattern, application_func)

    def record_metric(self, key: str, value: Any):
        """Record a metric for this wave execution."""
        self.metrics[key] = value


# Example: Idempotent Wave 2a Implementation
class IdempotentWave2a(IdempotentWave):
    """Example: Idempotent Wave 2a - Remove First-Party Skips."""

    def __init__(self):
        super().__init__("wave2a_first_party")

    def _execute_wave_logic(self) -> dict[str, Any]:
        """Execute Wave 2a logic idempotently."""
        print(f"=== {self.wave_name}: Remove First-Party Skips ===")

        # Find target files
        target_files = self._find_target_files()
        self.record_metric('target_files', len(target_files))

        files_modified = 0
        skips_removed = 0

        for file_path in target_files:
            # Apply file modifications idempotently
            was_modified = self.modify_file_idempotently(file_path, lambda: self._remove_first_party_skips(file_path))

            if was_modified:
                files_modified += 1
                skips_removed += self._count_removed_skips(file_path)

        self.record_metric('files_modified', files_modified)
        self.record_metric('skips_removed', skips_removed)

        return {
            'wave_name': self.wave_name,
            'target_files': len(target_files),
            'files_modified': files_modified,
            'skips_removed': skips_removed,
            'idempotent': True,
        }

    def _find_target_files(self) -> list[Path]:
        """Find files with first-party skip patterns."""
        # Implementation would scan for files with skip patterns
        # This is just an example
        return []

    def _remove_first_party_skips(self, file_path: Path) -> bool:
        """Remove first-party skip patterns from file."""
        # Implementation would remove skip patterns
        # Return True if modifications were made
        return False

    def _count_removed_skips(self, file_path: Path) -> int:
        """Count number of skips removed from file."""
        # Implementation would count removed skips
        return 0


# Example: Idempotent Wave 5c Implementation
class IdempotentWave5c(IdempotentWave):
    """Example: Idempotent Wave 5c - Core Path Semantics."""

    def __init__(self):
        super().__init__("wave5c_core_path_semantics")

    def _execute_wave_logic(self) -> dict[str, Any]:
        """Execute Wave 5c logic idempotently."""
        print(f"=== {self.wave_name}: Core Path Semantics Hardening ===")

        # Find conftest.py files
        conftest_files = list(Path("tests").rglob("conftest.py"))
        conftest_files.append(Path("conftest.py"))

        self.record_metric('target_files', len(conftest_files))

        files_modified = 0
        improvements_added = 0

        for conftest_file in conftest_files:
            if conftest_file.exists():
                # Apply modifications idempotently
                was_modified = self.modify_file_idempotently(conftest_file, lambda: self._harden_conftest(conftest_file))

                if was_modified:
                    files_modified += 1
                    improvements_added += self._count_improvements(conftest_file)

        self.record_metric('files_modified', files_modified)
        self.record_metric('improvements_added', improvements_added)

        return {
            'wave_name': self.wave_name,
            'target_files': len(conftest_files),
            'files_modified': files_modified,
            'improvements_added': improvements_added,
            'idempotent': True,
        }

    def _harden_conftest(self, conftest_file: Path) -> bool:
        """Harden conftest.py file with path semantics."""
        # Check if already hardened
        content = conftest_file.read_text() if conftest_file.exists() else ""

        # Look for existing hardening patterns
        if "pytest_plugins" in content and "testpaths" in content:
            return False  # Already hardened

        # Apply hardening
        hardening_content = '''"""pytest configuration."""
import pytest

pytest_plugins = []

# Test path configuration
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
norecursedirs = [".git", ".tox", "dist", "build", "__pycache__"]
'''

        conftest_file.parent.mkdir(parents=True, exist_ok=True)
        conftest_file.write_text(hardening_content + "\n" + content)

        return True

    def _count_improvements(self, conftest_file: Path) -> int:
        """Count improvements added to conftest file."""
        content = conftest_file.read_text() if conftest_file.exists() else ""

        improvements = 0
        if "pytest_plugins" in content:
            improvements += 1
        if "testpaths" in content:
            improvements += 1
        if "python_files" in content:
            improvements += 1
        if "norecursedirs" in content:
            improvements += 1

        return improvements


def main():
    """Example usage of idempotent waves."""
    print("=== Idempotent Wave Execution Demo ===")

    # Execute Wave 2a idempotently
    wave2a = IdempotentWave2a()
    result2a = wave2a.execute()
    print(f"Wave 2a result: {result2a}")

    # Execute Wave 5c idempotently
    wave5c = IdempotentWave5c()
    result5c = wave5c.execute()
    print(f"Wave 5c result: {result5c}")

    # Show execution summary
    state_manager = get_state_manager()
    summary = state_manager.get_execution_summary()
    print(f"\nExecution Summary: {summary}")


if __name__ == '__main__':
    main()
