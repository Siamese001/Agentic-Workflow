#!/usr/bin/env python3
"""
Test Suite: Gatekeeper Governance Layer

Verifies that ArchivalGatekeeper properly implements:
1. Interactive user approval flow
2. Batch mode (ARCHIVE_BATCH_ACCEPT=1) auto-approval
3. L4 Ledger integration hooks
4. Denial handling (operation fails when user denies)

REQUIREMENTS:
- 100% pass rate required
- All tests must verify governance before file system changes
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.core.ArchivalGatekeeper import (
    ARCHIVE_BATCH_ACCEPT_ENV,
    ArchivalGatekeeper,
    ArchivalOperation,
    ArchivalResult,
)


class TestApprovalDenied:
    """Test that operations fail when user denies approval."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_safe_delete_denied_does_not_move_file(self, gatekeeper, temp_project):
        """
        CRITICAL TEST: When user denies approval, safe_delete must NOT move the file.

        This verifies the governance layer prevents unauthorized operations.
        """
        # Create test file
        test_file = temp_project / "test_file_to_delete.py"
        test_file.write_text("# This file should NOT be moved")

        # Mock input to return 'n' (deny)
        gatekeeper.set_input_function(lambda prompt: "n")

        # Attempt delete
        result = gatekeeper.safe_delete(test_file, "TestAgent", "Test deletion")

        # Verify operation failed
        assert result.success is False, "Operation should fail when user denies"
        assert result.error == "User denied approval", "Error should indicate denial"
        assert result.approval_status == "DENIED", "Approval status should be DENIED"

        # CRITICAL: Verify file was NOT moved
        assert test_file.exists(), "File must still exist after denial"

    def test_safe_move_denied_does_not_move_file(self, gatekeeper, temp_project):
        """When user denies approval, safe_move must NOT move the file."""
        # Create test file
        test_file = temp_project / "test_file_to_move.py"
        test_file.write_text("# This file should NOT be moved")
        dest = temp_project / "new_location" / "test_file_to_move.py"

        # Mock input to return 'n' (deny)
        gatekeeper.set_input_function(lambda prompt: "n")

        # Attempt move
        result = gatekeeper.safe_move(test_file, dest, "TestAgent", "Test move")

        # Verify operation failed
        assert result.success is False
        assert result.error == "User denied approval"
        assert result.approval_status == "DENIED"

        # CRITICAL: Verify file was NOT moved
        assert test_file.exists(), "Source file must still exist after denial"
        assert not dest.exists(), "Destination must not exist after denial"

    def test_safe_archive_denied_does_not_archive_file(self, gatekeeper, temp_project):
        """When user denies approval, safe_archive must NOT archive the file."""
        # Create test file
        test_file = temp_project / "test_file_to_archive.py"
        test_file.write_text("# This file should NOT be archived")

        # Mock input to return 'no' (deny - full word)
        gatekeeper.set_input_function(lambda prompt: "no")

        # Attempt archive
        result = gatekeeper.safe_archive(test_file, "TestAgent", "Test archive")

        # Verify operation failed
        assert result.success is False
        assert result.error == "User denied approval"
        assert result.approval_status == "DENIED"

        # CRITICAL: Verify file was NOT archived
        assert test_file.exists(), "File must still exist after denial"


class TestApprovalApproved:
    """Test that operations succeed when user approves."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_safe_delete_approved_moves_file(self, gatekeeper, temp_project):
        """When user approves, safe_delete should move file to archive."""
        # Create test file
        test_file = temp_project / "approved_delete.py"
        test_file.write_text("# This file should be archived")

        # Mock input to return 'y' (approve)
        gatekeeper.set_input_function(lambda prompt: "y")

        # Attempt delete
        result = gatekeeper.safe_delete(test_file, "TestAgent", "Approved deletion")

        # Verify operation succeeded
        assert result.success is True, f"Operation should succeed: {result.error}"
        assert result.approval_status == "APPROVED"

        # Verify file was moved
        assert not test_file.exists(), "Source file should be moved"
        assert result.destination_path.exists(), "File should exist in archive"

    def test_safe_move_approved_moves_file(self, gatekeeper, temp_project):
        """When user approves, safe_move should move the file."""
        # Create test file
        test_file = temp_project / "approved_move.py"
        test_file.write_text("# This file should be moved")
        dest = temp_project / "new_location" / "approved_move.py"

        # Mock input to return 'yes' (approve - full word)
        gatekeeper.set_input_function(lambda prompt: "yes")

        # Attempt move
        result = gatekeeper.safe_move(test_file, dest, "TestAgent", "Approved move")

        # Verify operation succeeded
        assert result.success is True, f"Operation should succeed: {result.error}"
        assert result.approval_status == "APPROVED"

        # Verify file was moved
        assert not test_file.exists(), "Source file should be moved"
        assert dest.exists(), "Destination file should exist"


class TestBatchMode:
    """Test ARCHIVE_BATCH_ACCEPT=1 auto-approval mode."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_batch_mode_auto_approves_without_input(self, gatekeeper, temp_project):
        """
        CRITICAL TEST: With ARCHIVE_BATCH_ACCEPT=1, operations should auto-approve
        without calling the input function.
        """
        # Create test file
        test_file = temp_project / "batch_delete.py"
        test_file.write_text("# Batch mode test")

        # Set up a mock input that should NOT be called
        input_called = []
        def mock_input(prompt):
            input_called.append(prompt)
            return "n"  # Would deny if called

        gatekeeper.set_input_function(mock_input)

        # Enable batch mode
        with patch.dict(os.environ, {ARCHIVE_BATCH_ACCEPT_ENV: "1"}):
            result = gatekeeper.safe_delete(test_file, "TestAgent", "Batch delete")

        # Verify operation succeeded without input
        assert result.success is True, f"Batch mode should auto-approve: {result.error}"
        assert result.approval_status == "BATCH_APPROVED"
        assert len(input_called) == 0, "Input function should NOT be called in batch mode"

        # Verify file was moved
        assert not test_file.exists(), "File should be archived in batch mode"

    def test_batch_mode_disabled_requires_input(self, gatekeeper, temp_project):
        """Without ARCHIVE_BATCH_ACCEPT=1, operations should require input."""
        # Create test file
        test_file = temp_project / "non_batch_delete.py"
        test_file.write_text("# Non-batch mode test")

        # Set up a mock input that will be called
        input_called = []
        def mock_input(prompt):
            input_called.append(prompt)
            return "y"

        gatekeeper.set_input_function(mock_input)

        # Ensure batch mode is disabled
        with patch.dict(os.environ, {ARCHIVE_BATCH_ACCEPT_ENV: "0"}, clear=False):
            # Remove the env var if it exists
            os.environ.pop(ARCHIVE_BATCH_ACCEPT_ENV, None)
            result = gatekeeper.safe_delete(test_file, "TestAgent", "Non-batch delete")

        # Verify input was called
        assert len(input_called) > 0, "Input function should be called without batch mode"
        assert result.approval_status == "APPROVED"

    def test_batch_mode_with_empty_value_disabled(self, gatekeeper, temp_project):
        """ARCHIVE_BATCH_ACCEPT with empty value should NOT enable batch mode."""
        # Create test file
        test_file = temp_project / "empty_batch.py"
        test_file.write_text("# Empty batch test")

        input_called = []
        def mock_input(prompt):
            input_called.append(prompt)
            return "y"

        gatekeeper.set_input_function(mock_input)

        # Set empty value
        with patch.dict(os.environ, {ARCHIVE_BATCH_ACCEPT_ENV: ""}):
            result = gatekeeper.safe_delete(test_file, "TestAgent", "Empty batch test")

        # Verify input was called (batch mode disabled)
        assert len(input_called) > 0, "Empty value should not enable batch mode"


class TestL4LedgerIntegration:
    """Test L4 Ledger hook integration."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_l4_ledger_hook_called_on_success(self, gatekeeper, temp_project):
        """L4 Ledger hook should be called after successful operation."""
        # Create test file
        test_file = temp_project / "ledger_test.py"
        test_file.write_text("# Ledger test")

        # Set up mock L4 ledger hook
        ledger_entries = []
        def mock_ledger_hook(result: ArchivalResult):
            ledger_entries.append(result)

        gatekeeper.set_l4_ledger_hook(mock_ledger_hook)
        gatekeeper.set_input_function(lambda prompt: "y")

        # Perform operation
        result = gatekeeper.safe_delete(test_file, "TestAgent", "Ledger test")

        # Verify ledger was notified
        assert len(ledger_entries) == 1, "L4 Ledger should be notified once"
        assert ledger_entries[0].success is True
        assert ledger_entries[0].operation == ArchivalOperation.DELETE

    def test_l4_ledger_hook_called_on_denial(self, gatekeeper, temp_project):
        """L4 Ledger hook should be called even when operation is denied."""
        # Create test file
        test_file = temp_project / "ledger_denial_test.py"
        test_file.write_text("# Ledger denial test")

        # Set up mock L4 ledger hook
        ledger_entries = []
        def mock_ledger_hook(result: ArchivalResult):
            ledger_entries.append(result)

        gatekeeper.set_l4_ledger_hook(mock_ledger_hook)
        gatekeeper.set_input_function(lambda prompt: "n")

        # Perform operation (will be denied)
        result = gatekeeper.safe_delete(test_file, "TestAgent", "Ledger denial test")

        # Verify ledger was notified of denial
        assert len(ledger_entries) == 1, "L4 Ledger should be notified of denial"
        assert ledger_entries[0].success is False
        assert ledger_entries[0].approval_status == "DENIED"

    def test_l4_ledger_hook_receives_complete_result(self, gatekeeper, temp_project):
        """L4 Ledger hook should receive complete ArchivalResult with all fields."""
        # Create test file
        test_file = temp_project / "complete_result_test.py"
        test_file.write_text("# Complete result test")

        # Set up mock L4 ledger hook
        ledger_entries = []
        def mock_ledger_hook(result: ArchivalResult):
            ledger_entries.append(result)

        gatekeeper.set_l4_ledger_hook(mock_ledger_hook)
        gatekeeper.set_input_function(lambda prompt: "y")

        # Perform operation
        gatekeeper.safe_delete(test_file, "TestAgent", "Complete result test")

        # Verify all fields are present
        entry = ledger_entries[0]
        assert entry.source_path is not None
        assert entry.destination_path is not None
        assert entry.requester_agent == "TestAgent"
        assert "Complete result test" in entry.reason
        assert entry.timestamp is not None
        assert entry.approval_status in ("APPROVED", "BATCH_APPROVED")


class TestApprovalStatusTracking:
    """Test that approval_status is properly tracked in results."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_approval_status_in_audit_log(self, gatekeeper, temp_project):
        """Approval status should be recorded in audit log."""
        # Create test file
        test_file = temp_project / "audit_status_test.py"
        test_file.write_text("# Audit status test")

        gatekeeper.set_input_function(lambda prompt: "y")

        # Perform operation
        gatekeeper.safe_delete(test_file, "TestAgent", "Audit status test")

        # Check audit log
        audit_entries = gatekeeper.get_audit_log(limit=1)
        assert len(audit_entries) > 0
        assert "approval_status" in audit_entries[0]
        assert audit_entries[0]["approval_status"] == "APPROVED"

    def test_result_to_dict_includes_approval_status(self, gatekeeper, temp_project):
        """ArchivalResult.to_dict() should include approval_status."""
        result = ArchivalResult(
            success=True,
            operation=ArchivalOperation.DELETE,
            source_path=Path("/test/path"),
            destination_path=Path("/archive/path"),
            requester_agent="TestAgent",
            reason="Test reason",
            approval_status="APPROVED",
        )

        result_dict = result.to_dict()
        assert "approval_status" in result_dict
        assert result_dict["approval_status"] == "APPROVED"


class TestRequireApprovalSetting:
    """Test the set_require_approval configuration."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_disable_approval_skips_input(self, gatekeeper, temp_project):
        """When approval is disabled, input should not be called."""
        # Create test file
        test_file = temp_project / "no_approval_test.py"
        test_file.write_text("# No approval test")

        input_called = []
        def mock_input(prompt):
            input_called.append(prompt)
            return "n"

        gatekeeper.set_input_function(mock_input)
        gatekeeper.set_require_approval(False)  # Disable approval

        # Perform operation
        result = gatekeeper.safe_delete(test_file, "TestAgent", "No approval test")

        # Verify input was NOT called
        assert len(input_called) == 0, "Input should not be called when approval disabled"
        assert result.success is True
        assert result.approval_status == "APPROVED"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
