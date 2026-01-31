"""
Test suite for RuntimeStateGuard corruption recovery and atomic persistence.

Verifies that the state guard can recover from corrupted JSON files
and maintains atomic writes to prevent data loss.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L4_state.validation_context.RuntimeStateGuard import RuntimeStateGuard


class TestRuntimeStateGuard:
    """100% PASS: Ensures RuntimeStateGuard handles corruption and atomic operations."""

    def test_state_corruption_recovery(self):
        """
        Verifies that RuntimeStateGuard detects corrupted JSON
        and restores the state from the .bak file.
        """
        import tempfile

        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_file = root / "runtime_state.json"
            backup_file = root / "runtime_state.json.bak"

            # 1. Create a valid backup
            valid_data = {"shared_alignment_metrics": {"upgrade_count": 8}}
            with open(backup_file, "w") as f:
                json.dump(valid_data, f)

            # 2. Create a CORRUPTED state file (half-written)
            with open(state_file, "w") as f:
                f.write("{'shared_alignment_metrics': ")  # Missing closing brace

            # 3. Initialize Guard
            guard = RuntimeStateGuard(root)

            # 4. Verify auto-recovery
            count = guard.get_metric("upgrade_count")
            assert count == 8, f"Failed to recover from backup. Got {count}, expected 8."

            # 5. Verify state file was repaired
            with open(state_file) as f:
                repaired_data = json.load(f)
            assert repaired_data == valid_data

        print("✅ test_state_corruption_recovery: 100% PASS")

    def test_atomic_persist_creates_backup(self):
        """
        Verifies that atomic persist creates backup before writing.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_file = root / "runtime_state.json"
            backup_file = root / "runtime_state.json.bak"

            # 1. Create initial state
            initial_data = {"shared_alignment_metrics": {"upgrade_count": 3}}
            with open(state_file, "w") as f:
                json.dump(initial_data, f)

            # 2. Initialize guard and increment
            guard = RuntimeStateGuard(root)
            guard.increment_metric("upgrade_count")

            # 3. Verify backup exists and contains original data
            assert backup_file.exists(), "Backup file was not created"
            with open(backup_file) as f:
                backup_data = json.load(f)
            assert backup_data == initial_data, "Backup does not contain original data"

            # 4. Verify main file has updated data
            with open(state_file) as f:
                main_data = json.load(f)
            expected_data = {"shared_alignment_metrics": {"upgrade_count": 4}}
            assert main_data == expected_data, "Main file not updated correctly"

        print("✅ test_atomic_persist_creates_backup: 100% PASS")

    def test_no_backup_available_resets_state(self):
        """
        Verifies that when no backup exists for corrupted file,
        the guard resets to empty state.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_file = root / "runtime_state.json"
            root / "runtime_state.json.bak"

            # 1. Create corrupted state file with no backup
            with open(state_file, "w") as f:
                f.write("invalid json content")

            # 2. Initialize guard (should reset state)
            with patch("builtins.print") as mock_print:
                guard = RuntimeStateGuard(root)

                # Verify warning was printed
                mock_print.assert_any_call("[StateGuard] No backup found. Resetting state.")

            # 3. Verify state is empty
            count = guard.get_metric("upgrade_count")
            assert count == 0, "State should be reset to empty"

        print("✅ test_no_backup_available_resets_state: 100% PASS")

    def test_missing_state_file_creates_empty_state(self):
        """
        Verifies that missing state file results in empty initial state.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_file = root / "runtime_state.json"

            # Ensure state file doesn't exist
            assert not state_file.exists()

            # Initialize guard
            guard = RuntimeStateGuard(root)

            # Verify state is empty
            count = guard.get_metric("upgrade_count")
            assert count == 0, "Missing file should result in empty state"

            # Verify state file is created after first operation
            guard.increment_metric("upgrade_count")
            assert state_file.exists(), "State file should be created after operation"

        print("✅ test_missing_state_file_creates_empty_state: 100% PASS")

    def test_increment_metric_accumulates_correctly(self):
        """
        Verifies that increment_metric correctly accumulates values.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize guard
            guard = RuntimeStateGuard(root)

            # Test multiple increments
            assert guard.get_metric("counter") == 0
            guard.increment_metric("counter", 1)
            assert guard.get_metric("counter") == 1
            guard.increment_metric("counter", 5)
            assert guard.get_metric("counter") == 6
            guard.increment_metric("counter")
            assert guard.get_metric("counter") == 7

            # Test different metrics
            guard.increment_metric("other_counter", 10)
            assert guard.get_metric("other_counter") == 10
            assert guard.get_metric("counter") == 7  # Original unchanged

        print("✅ test_increment_metric_accumulates_correctly: 100% PASS")

    def test_get_metric_with_default_values(self):
        """
        Verifies get_metric returns correct default values.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Initialize guard
            guard = RuntimeStateGuard(root)

            # Test default values
            assert guard.get_metric("nonexistent") == 0
            assert guard.get_metric("nonexistent", 42) == 42
            assert guard.get_metric("nonexistent", "default") == "default"

            # Test after setting value
            guard.increment_metric("test_metric", 5)
            assert guard.get_metric("test_metric") == 5
            assert guard.get_metric("test_metric", 999) == 5  # Default ignored when value exists

        print("✅ test_get_metric_with_default_values: 100% PASS")

    def test_persistence_failure_cleanup(self):
        """
        Verifies that temporary files are cleaned up on persistence failure.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_file = root / "runtime_state.json"
            temp_file = root / "runtime_state.json.tmp"

            # Create initial state
            with open(state_file, "w") as f:
                json.dump({"test": "initial"}, f)

            # Initialize guard
            guard = RuntimeStateGuard(root)

            # Mock os.replace to raise exception
            with (
                patch("os.replace", side_effect=OSError("Permission denied")),
                patch("builtins.print") as mock_print,
            ):
                # Attempt increment (should fail gracefully)
                guard.increment_metric("upgrade_count")

                # Verify error was logged
                mock_print.assert_any_call("[StateGuard] PERSISTENCE FAILURE: Permission denied")

                # Verify temp file was cleaned up
                assert not temp_file.exists(), "Temporary file should be cleaned up on failure"

                # Verify original state file is unchanged
                with open(state_file) as f:
                    data = json.load(f)
                assert data == {"test": "initial"}, "Original file should be unchanged on failure"

        print("✅ test_persistence_failure_cleanup: 100% PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
