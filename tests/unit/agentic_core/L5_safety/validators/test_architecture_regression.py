"""
Architecture Regression Test Suite - Phase 4 Integration Tests

Validates the complete safety stack integration:
1. HygieneGuardian → ArchivalGatekeeper delegation
2. GovernanceAgent → ArchivalGatekeeper delegation
3. Audit trail integrity

Scenarios:
- Scenario 1 (Happy Path): HygieneGuardian detects copy pattern → Gatekeeper archives
- Scenario 2 (Blocked Path): GovernanceAgent tries protected path → Gatekeeper rejects
- Scenario 3 (Audit Trail): Valid operation → Audit log contains correct entry
"""

import json

import pytest

from agentic_core.L5_safety.core.ArchivalGatekeeper import (
    ArchivalGatekeeper,
)
from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent
from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
    HygieneGuardianAgent,
)


class TestScenario1HappyPath:
    """
    Scenario 1: The Happy Path

    Simulate HygieneGuardian detecting a "copy pattern" file.
    Assert it calls Gatekeeper.
    Assert Gatekeeper logs to archival_audit.jsonl.
    Assert file is moved to archives/.
    """

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure with archives directory."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        # Disable approval prompts for testing
        gk.set_require_approval(False)
        yield gk
        ArchivalGatekeeper.reset_instance()

    @pytest.fixture
    def hygiene_agent(self, temp_project, gatekeeper):
        """Create HygieneGuardianAgent with dry_run=False for actual operations."""
        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=False)
        return agent

    def test_copy_pattern_detected_and_archived(self, hygiene_agent, temp_project, gatekeeper):
        """
        Full integration: HygieneGuardian detects copy pattern → Gatekeeper archives.
        """
        # Create a file with copy pattern (e.g., "file (1).py")
        copy_file = temp_project / "module (1).py"
        copy_file.write_text("# This is a copy pattern file")

        # Scan for violations
        hygiene_agent._scan_directory(temp_project)

        # Verify copy pattern was detected
        copy_violations = [
            v for v in hygiene_agent.violations if v.violation_type == "copy_pattern"
        ]
        assert len(copy_violations) == 1, "Should detect exactly one copy pattern violation"
        assert copy_violations[0].file_path == copy_file

        # Fix violations (this should call Gatekeeper)
        fixed_count = hygiene_agent._fix_violations()

        # Verify file was archived (no longer at original location)
        assert not copy_file.exists(), "Copy pattern file should be archived"

        # Verify file is in archives
        archive_dir = temp_project / "archives" / "gatekeeper"
        archived_files = list(archive_dir.rglob("module (1).py"))
        assert len(archived_files) == 1, "File should exist in archives"

        # Verify audit log was written
        audit_log = archive_dir / "archival_audit.jsonl"
        assert audit_log.exists(), "Audit log should exist"

        # Verify audit log contains the operation
        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        # Find the entry for our file
        relevant_entries = [e for e in log_entries if "module (1).py" in e.get("source_path", "")]
        assert len(relevant_entries) >= 1, "Audit log should contain entry for archived file"

        entry = relevant_entries[-1]  # Get the most recent
        assert entry["success"] is True
        assert entry["requester_agent"] == "HygieneGuardianAgent"
        assert entry["operation"] == "DELETE"  # safe_delete is a soft delete

    def test_repeated_filename_detected_and_archived(self, hygiene_agent, temp_project, gatekeeper):
        """
        Integration: HygieneGuardian detects repeated filename → Gatekeeper archives.
        """
        # Create a file with repeated string pattern
        repeated_file = temp_project / "enums_enums_enums.py"
        repeated_file.write_text("# This has repeated strings in filename")

        # Scan for violations
        hygiene_agent._scan_directory(temp_project)

        # Verify repeated filename was detected
        repeated_violations = [
            v for v in hygiene_agent.violations if v.violation_type == "repeated_filename"
        ]
        assert len(repeated_violations) == 1, "Should detect repeated filename violation"

        # Fix violations
        hygiene_agent._fix_violations()

        # Verify file was archived
        assert not repeated_file.exists(), "Repeated filename file should be archived"

        # Verify audit log entry
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        relevant_entries = [
            e for e in log_entries if "enums_enums_enums.py" in e.get("source_path", "")
        ]
        assert len(relevant_entries) >= 1


class TestScenario2BlockedPath:
    """
    Scenario 2: The Blocked Path

    Simulate GovernanceAgent trying to move a protected file (e.g., inside .git).
    Assert Gatekeeper rejects it.
    Assert GovernanceAgent handles the rejection gracefully (no crash).
    """

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure with .git directory."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        (tmp_path / ".git" / "objects").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        gk.set_require_approval(False)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_protected_git_file_rejected(self, temp_project, gatekeeper):
        """
        Gatekeeper must reject operations on files inside .git directory.
        """
        # Create a file inside .git
        git_file = temp_project / ".git" / "config"
        git_file.write_text("[core]\nrepositoryformatversion = 0")

        # Attempt to archive the file
        result = gatekeeper.safe_archive(git_file, "TestAgent", "Attempting to archive git file")

        # Verify operation was rejected
        assert result.success is False, "Operation on .git file should fail"
        assert ".git" in result.error, "Error should mention .git"

        # Verify file was NOT moved
        assert git_file.exists(), "Git file must still exist after rejection"

    def test_protected_venv_file_rejected(self, temp_project, gatekeeper):
        """
        Gatekeeper must reject operations on files inside venv directory.
        """
        # Create venv directory and file
        venv_dir = temp_project / "venv" / "lib"
        venv_dir.mkdir(parents=True)
        venv_file = venv_dir / "python3.11"
        venv_file.write_text("# venv file")

        # Attempt to delete the file
        result = gatekeeper.safe_delete(venv_file, "TestAgent", "Attempting to delete venv file")

        # Verify operation was rejected
        assert result.success is False
        assert "venv" in result.error

        # Verify file was NOT moved
        assert venv_file.exists()

    def test_governance_agent_handles_rejection_gracefully(self, temp_project, gatekeeper):
        """
        GovernanceAgent must handle Gatekeeper rejection without crashing.
        """
        # Create a file inside .git
        git_file = temp_project / ".git" / "test_config"
        git_file.write_text("test content")

        # Create GovernanceAgent
        governance = GovernanceAgent(str(temp_project))

        # Attempt to sanitize the file (should be rejected by Gatekeeper)
        # This should NOT raise an exception
        try:
            # Directly call gatekeeper through governance
            result = governance.gatekeeper.safe_delete(
                git_file, "GovernanceAgent", "Test deletion of protected file"
            )

            # Verify rejection was handled
            assert result.success is False
            assert git_file.exists()

        except Exception as e:
            pytest.fail(f"GovernanceAgent should handle rejection gracefully, but raised: {e}")

    def test_archive_directory_protected(self, temp_project, gatekeeper):
        """
        Gatekeeper must reject operations on files already in archives directory.
        """
        # Create a file inside archives
        archive_file = temp_project / "archives" / "gatekeeper" / "test_archived.py"
        archive_file.parent.mkdir(parents=True, exist_ok=True)
        archive_file.write_text("# Already archived")

        # Attempt to archive it again
        result = gatekeeper.safe_archive(archive_file, "TestAgent", "Re-archiving")

        # Verify operation was rejected
        assert result.success is False
        assert "archive" in result.error.lower()


class TestScenario3AuditTrail:
    """
    Scenario 3: The Audit Trail

    Perform a valid move.
    Read archival_audit.jsonl.
    Assert the entry contains requester="HygieneGuardianAgent" and operation="DELETE".
    """

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
        gk.set_require_approval(False)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_audit_log_contains_correct_requester(self, temp_project, gatekeeper):
        """
        Audit log must contain the correct requester agent name.
        """
        # Create test file
        test_file = temp_project / "test_audit_file.py"
        test_file.write_text("# Test file for audit")

        # Perform delete operation
        result = gatekeeper.safe_delete(
            test_file, "HygieneGuardianAgent", "Test deletion for audit verification"
        )

        assert result.success is True

        # Read audit log
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        assert audit_log.exists()

        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        # Find our entry
        relevant_entries = [
            e for e in log_entries if "test_audit_file.py" in e.get("source_path", "")
        ]

        assert len(relevant_entries) >= 1
        entry = relevant_entries[-1]

        # Verify requester
        assert entry["requester_agent"] == "HygieneGuardianAgent"

    def test_audit_log_contains_correct_operation(self, temp_project, gatekeeper):
        """
        Audit log must contain the correct operation type.
        """
        # Create test file
        test_file = temp_project / "test_operation_file.py"
        test_file.write_text("# Test file for operation check")

        # Perform delete operation (soft delete)
        result = gatekeeper.safe_delete(test_file, "TestAgent", "Testing operation logging")

        assert result.success is True

        # Read audit log
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        relevant_entries = [
            e for e in log_entries if "test_operation_file.py" in e.get("source_path", "")
        ]

        assert len(relevant_entries) >= 1
        entry = relevant_entries[-1]

        # Verify operation is DELETE (soft delete)
        assert entry["operation"] == "DELETE"

    def test_audit_log_contains_timestamp(self, temp_project, gatekeeper):
        """
        Audit log entries must contain timestamps.
        """
        # Create test file
        test_file = temp_project / "test_timestamp_file.py"
        test_file.write_text("# Test file for timestamp check")

        # Perform operation
        gatekeeper.safe_archive(test_file, "TestAgent", "Testing timestamp")

        # Read audit log
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        relevant_entries = [
            e for e in log_entries if "test_timestamp_file.py" in e.get("source_path", "")
        ]

        assert len(relevant_entries) >= 1
        entry = relevant_entries[-1]

        # Verify timestamp exists and is ISO format
        assert "timestamp" in entry
        assert "2026" in entry["timestamp"]  # Should be current year

    def test_audit_log_contains_reason(self, temp_project, gatekeeper):
        """
        Audit log entries must contain the reason for the operation.
        """
        # Create test file
        test_file = temp_project / "test_reason_file.py"
        test_file.write_text("# Test file for reason check")

        # Perform operation with specific reason
        reason = "Duplicate file removal - test case"
        gatekeeper.safe_delete(test_file, "TestAgent", reason)

        # Read audit log
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        relevant_entries = [
            e for e in log_entries if "test_reason_file.py" in e.get("source_path", "")
        ]

        assert len(relevant_entries) >= 1
        entry = relevant_entries[-1]

        # Verify reason contains our text (may be prefixed with [SOFT DELETE])
        assert "Duplicate file removal" in entry["reason"]

    def test_audit_log_contains_destination_path(self, temp_project, gatekeeper):
        """
        Audit log entries must contain the destination path for archive operations.
        """
        # Create test file
        test_file = temp_project / "test_destination_file.py"
        test_file.write_text("# Test file for destination check")

        # Perform archive operation
        gatekeeper.safe_archive(test_file, "TestAgent", "Testing destination logging")

        # Read audit log
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        with open(audit_log, encoding="utf-8") as f:
            log_entries = [json.loads(line) for line in f.readlines()]

        relevant_entries = [
            e for e in log_entries if "test_destination_file.py" in e.get("source_path", "")
        ]

        assert len(relevant_entries) >= 1
        entry = relevant_entries[-1]

        # Verify destination path exists and points to archives
        assert entry["destination_path"] is not None
        assert "archives" in entry["destination_path"]
        assert "gatekeeper" in entry["destination_path"]


class TestIntegrationEndToEnd:
    """
    End-to-end integration tests for the complete safety stack.
    """

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a complete temporary project structure."""
        (tmp_path / "archives" / "gatekeeper").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / ".git").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def gatekeeper(self, temp_project):
        """Create a fresh gatekeeper instance."""
        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(temp_project)
        gk.set_require_approval(False)
        yield gk
        ArchivalGatekeeper.reset_instance()

    def test_full_hygiene_workflow(self, temp_project, gatekeeper):
        """
        Complete workflow: Create violations → Detect → Fix → Verify audit.
        """
        # Create multiple violation types
        (temp_project / "empty.py").write_text("")
        (temp_project / "backup.bak").write_text("backup content")
        (temp_project / "file_copy.py").write_text("# copy pattern")

        # Create HygieneGuardian
        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=False)

        # Scan
        agent._scan_directory(temp_project)

        # Should detect multiple violations
        assert len(agent.violations) >= 2

        # Fix
        fixed = agent._fix_violations()

        # Verify files are archived
        assert not (temp_project / "empty.py").exists()
        assert not (temp_project / "backup.bak").exists()
        assert not (temp_project / "file_copy.py").exists()

        # Verify audit log has entries
        audit_log = temp_project / "archives" / "gatekeeper" / "archival_audit.jsonl"
        with open(audit_log, encoding="utf-8") as f:
            entries = f.readlines()

        assert len(entries) >= 2, "Should have multiple audit entries"

    def test_delegation_chain_integrity(self, temp_project, gatekeeper):
        """
        Verify that all agents delegate to Gatekeeper (no direct file ops).
        """
        # Create test file
        test_file = temp_project / "delegation_test.bak"
        test_file.write_text("test content")

        # Track Gatekeeper calls
        original_safe_delete = gatekeeper.safe_delete
        call_count = [0]

        def tracking_safe_delete(*args, **kwargs):
            call_count[0] += 1
            return original_safe_delete(*args, **kwargs)

        gatekeeper.safe_delete = tracking_safe_delete

        # Create and run HygieneGuardian
        agent = HygieneGuardianAgent(temp_project, ctx=None, dry_run=False)
        agent._scan_directory(temp_project)
        agent._fix_violations()

        # Verify Gatekeeper was called
        assert call_count[0] >= 1, "HygieneGuardian must delegate to Gatekeeper"

        # Restore original method
        gatekeeper.safe_delete = original_safe_delete
