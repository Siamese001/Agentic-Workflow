"""
Tests for ArchivalGatekeeper - Centralized Destructive File Operations Service

Tests cover:
1. Singleton pattern
2. safe_move operations
3. safe_archive operations
4. safe_delete (soft delete) operations
5. Audit logging
6. Path validation
7. Restore from archive
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (
    ArchivalGatekeeper,
    ArchivalOperation,
    ArchivalResult,
)
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR


@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def gatekeeper(temp_project):
    """Create a fresh ArchivalGatekeeper instance for each test."""
    # Reset singleton for clean test
    ArchivalGatekeeper.reset_instance()
    gk = ArchivalGatekeeper.get_instance(temp_project)
    # Disable approval requirement for backward compatibility in existing tests
    gk.set_require_approval(False)
    yield gk
    # Reset after test
    ArchivalGatekeeper.reset_instance()


class TestSingletonPattern:
    """Test singleton behavior."""

    def test_get_instance_returns_same_instance(self, temp_project):
        """Verify singleton returns same instance."""
        ArchivalGatekeeper.reset_instance()
        gk1 = ArchivalGatekeeper.get_instance(temp_project)
        gk2 = ArchivalGatekeeper.get_instance()
        assert gk1 is gk2
        ArchivalGatekeeper.reset_instance()

    def test_get_instance_requires_project_root_first_call(self):
        """Verify first call requires project_root."""
        ArchivalGatekeeper.reset_instance()
        with pytest.raises(ValueError, match="project_root must be provided"):
            ArchivalGatekeeper.get_instance()
        ArchivalGatekeeper.reset_instance()

    def test_reset_instance_clears_singleton(self, temp_project):
        """Verify reset clears the singleton."""
        ArchivalGatekeeper.reset_instance()
        ArchivalGatekeeper.get_instance(temp_project)
        ArchivalGatekeeper.reset_instance()

        # Should require project_root again
        with pytest.raises(ValueError):
            ArchivalGatekeeper.get_instance()
        ArchivalGatekeeper.reset_instance()


class TestSafeMove:
    """Test safe_move operations."""

    def test_safe_move_success(self, gatekeeper, temp_project):
        """Test successful file move."""
        # Create source file
        source = temp_project / "source.txt"
        source.write_text("test content")
        dest = temp_project / "subdir" / "dest.txt"

        result = gatekeeper.safe_move(source, dest, "TestAgent", "Test move")

        assert result.success is True
        assert result.operation == ArchivalOperation.MOVE
        assert not source.exists()
        assert dest.exists()
        assert dest.read_text() == "test content"

    def test_safe_move_creates_parent_dirs(self, gatekeeper, temp_project):
        """Test that parent directories are created."""
        source = temp_project / "source.txt"
        source.write_text("content")
        dest = temp_project / "a" / "b" / "c" / "dest.txt"

        result = gatekeeper.safe_move(source, dest, "TestAgent", "Deep move")

        assert result.success is True
        assert dest.exists()

    def test_safe_move_nonexistent_source(self, gatekeeper, temp_project):
        """Test move with nonexistent source fails."""
        source = temp_project / "nonexistent.txt"
        dest = temp_project / "dest.txt"

        result = gatekeeper.safe_move(source, dest, "TestAgent", "Bad move")

        assert result.success is False
        assert "does not exist" in result.error

    def test_safe_move_logs_operation(self, gatekeeper, temp_project):
        """Test that move is logged."""
        source = temp_project / "source.txt"
        source.write_text("content")
        dest = temp_project / "dest.txt"

        gatekeeper.safe_move(source, dest, "TestAgent", "Logged move")

        logs = gatekeeper.get_audit_log()
        assert len(logs) >= 1
        assert logs[0]["operation"] == "MOVE"
        assert logs[0]["requester_agent"] == "TestAgent"

    def test_safe_move_overwrite_protection_default(self, gatekeeper, temp_project):
        """Test that safe_move fails when destination exists and overwrite=False (default)."""
        # Create source and destination files
        source = temp_project / "source.txt"
        source.write_text("source content")
        dest = temp_project / "dest.txt"
        dest.write_text("existing content")

        # Attempt move without overwrite (default)
        result = gatekeeper.safe_move(source, dest, "TestAgent", "Overwrite attempt")

        # Should fail
        assert result.success is False
        assert "already exists" in result.error.lower()
        # Source should still exist
        assert source.exists()
        assert source.read_text() == "source content"
        # Destination should be unchanged
        assert dest.read_text() == "existing content"

    def test_safe_move_overwrite_allowed(self, gatekeeper, temp_project):
        """Test that safe_move succeeds when destination exists and overwrite=True."""
        # Create source and destination files
        source = temp_project / "source.txt"
        source.write_text("new content")
        dest = temp_project / "dest.txt"
        dest.write_text("old content")

        # Move with overwrite=True
        result = gatekeeper.safe_move(source, dest, "TestAgent", "Overwrite move", overwrite=True)

        # Should succeed
        assert result.success is True
        assert not source.exists()
        assert dest.exists()
        assert dest.read_text() == "new content"


class TestSafeArchive:
    """Test safe_archive operations."""

    def test_safe_archive_success(self, gatekeeper, temp_project):
        """Test successful file archive."""
        source = temp_project / "to_archive.txt"
        source.write_text("archive me")

        result = gatekeeper.safe_archive(source, "TestAgent", "Test archive")

        assert result.success is True
        assert result.operation == ArchivalOperation.ARCHIVE
        assert not source.exists()
        assert result.destination_path.exists()
        assert ARCHIVES_DIR in str(result.destination_path) and "gatekeeper" in str(result.destination_path)

    def test_safe_archive_preserves_relative_path(self, gatekeeper, temp_project):
        """Test that archive preserves relative path structure."""
        subdir = temp_project / "subdir" / "nested"
        subdir.mkdir(parents=True)
        source = subdir / "file.txt"
        source.write_text("nested content")

        result = gatekeeper.safe_archive(source, "TestAgent", "Archive nested")

        assert result.success is True
        # Check path contains original structure
        assert "subdir" in str(result.destination_path)
        assert "nested" in str(result.destination_path)

    def test_safe_archive_handles_collision(self, gatekeeper, temp_project):
        """Test archive handles filename collision."""
        # Create and archive first file
        source1 = temp_project / "file.txt"
        source1.write_text("first")
        result1 = gatekeeper.safe_archive(source1, "TestAgent", "First archive")

        # Create another file with same name
        source2 = temp_project / "file.txt"
        source2.write_text("second")
        result2 = gatekeeper.safe_archive(source2, "TestAgent", "Second archive")

        assert result1.success is True
        assert result2.success is True
        # Both should exist in archive with different names
        assert result1.destination_path != result2.destination_path


class TestSafeDelete:
    """Test safe_delete (soft delete) operations."""

    def test_safe_delete_is_soft_delete(self, gatekeeper, temp_project):
        """Test that delete is actually a soft delete (archive)."""
        source = temp_project / "to_delete.txt"
        source.write_text("delete me")

        result = gatekeeper.safe_delete(source, "TestAgent", "Test delete")

        assert result.success is True
        assert result.operation == ArchivalOperation.DELETE
        assert not source.exists()
        # File should be in archive, not permanently deleted
        assert result.destination_path.exists()
        assert ARCHIVES_DIR in str(result.destination_path) and "gatekeeper" in str(result.destination_path)

    def test_safe_delete_reason_prefixed(self, gatekeeper, temp_project):
        """Test that delete reason is prefixed with SOFT DELETE."""
        source = temp_project / "file.txt"
        source.write_text("content")

        result = gatekeeper.safe_delete(source, "TestAgent", "Removing duplicate")

        assert "[SOFT DELETE]" in result.reason


class TestPathValidation:
    """Test path validation logic."""

    def test_cannot_operate_on_archive_directory(self, gatekeeper, temp_project):
        """Test that operations on archive directory are blocked."""
        archive_file = gatekeeper.archive_root / "test.txt"
        archive_file.parent.mkdir(parents=True, exist_ok=True)
        archive_file.write_text("in archive")

        result = gatekeeper.safe_archive(archive_file, "TestAgent", "Bad archive")

        assert result.success is False
        assert "archive directory" in result.error.lower()

    def test_cannot_operate_on_git_directory(self, gatekeeper, temp_project):
        """Test that operations on .git are blocked."""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.write_text("git config")

        result = gatekeeper.safe_archive(git_file, "TestAgent", "Bad git archive")

        assert result.success is False
        assert ".git" in result.error


class TestAuditLog:
    """Test audit logging functionality."""

    def test_audit_log_created(self, gatekeeper, temp_project):
        """Test that audit log file is created."""
        source = temp_project / "file.txt"
        source.write_text("content")

        gatekeeper.safe_archive(source, "TestAgent", "Test")

        assert gatekeeper.audit_log_path.exists()

    def test_audit_log_contains_all_fields(self, gatekeeper, temp_project):
        """Test that audit log entries have all required fields."""
        source = temp_project / "file.txt"
        source.write_text("content")

        gatekeeper.safe_archive(source, "MyAgent", "My reason")

        logs = gatekeeper.get_audit_log()
        assert len(logs) >= 1

        entry = logs[0]
        assert "success" in entry
        assert "operation" in entry
        assert "source_path" in entry
        assert "destination_path" in entry
        assert "requester_agent" in entry
        assert "reason" in entry
        assert "timestamp" in entry

        assert entry["requester_agent"] == "MyAgent"
        assert entry["reason"] == "My reason"

    def test_get_audit_log_respects_limit(self, gatekeeper, temp_project):
        """Test that get_audit_log respects limit parameter."""
        # Create multiple operations
        for i in range(10):
            source = temp_project / f"file{i}.txt"
            source.write_text(f"content {i}")
            gatekeeper.safe_archive(source, "TestAgent", f"Archive {i}")

        logs = gatekeeper.get_audit_log(limit=LIMIT)
        assert len(logs) == 5


class TestRestoreFromArchive:
    """Test restore_from_archive functionality."""

    def test_restore_success(self, gatekeeper, temp_project):
        """Test successful restore from archive."""
        # Create and archive a file
        original = temp_project / "subdir" / "file.txt"
        original.parent.mkdir(parents=True)
        original.write_text("original content")

        archive_result = gatekeeper.safe_archive(original, "TestAgent", "Archive for restore test")
        assert archive_result.success is True

        # Restore it
        restore_result = gatekeeper.restore_from_archive(
            archive_result.destination_path,
            "TestAgent",
            "Restoring file",
        )

        assert restore_result.success is True
        # File should be back at original location
        assert original.exists()
        assert original.read_text() == "original content"

    def test_restore_fails_for_non_archive_path(self, gatekeeper, temp_project):
        """Test that restore fails for files not in archive."""
        non_archive = temp_project / "not_in_archive.txt"
        non_archive.write_text("content")

        result = gatekeeper.restore_from_archive(non_archive, "TestAgent", "Bad restore")

        assert result.success is False
        assert "not in archive" in result.error.lower()


class TestOperationCount:
    """Test operation counting."""

    def test_operation_count_increments(self, gatekeeper, temp_project):
        """Test that operation count increments correctly."""
        initial_count = gatekeeper.get_operation_count()

        # Perform some operations
        for i in range(3):
            source = temp_project / f"file{i}.txt"
            source.write_text(f"content {i}")
            gatekeeper.safe_archive(source, "TestAgent", f"Archive {i}")

        assert gatekeeper.get_operation_count() == initial_count + 3

    def test_failed_operations_not_counted(self, gatekeeper, temp_project):
        """Test that failed operations don't increment count."""
        initial_count = gatekeeper.get_operation_count()

        # Try to archive nonexistent file
        nonexistent = temp_project / "nonexistent.txt"
        gatekeeper.safe_archive(nonexistent, "TestAgent", "Bad archive")

        assert gatekeeper.get_operation_count() == initial_count


class TestArchivalResult:
    """Test ArchivalResult dataclass."""

    def test_to_dict(self):
        """Test ArchivalResult.to_dict() method."""
        result = ArchivalResult(
            success=True,
            operation=ArchivalOperation.ARCHIVE,
            source_path=Path("/test/source.txt"),
            destination_path=Path("/test/dest.txt"),
            requester_agent="TestAgent",
            reason="Test reason",
        )

        d = result.to_dict()

        assert d["success"] is True
        assert d["operation"] == "ARCHIVE"
        # Path separators vary by OS, just check the filename is present
        assert "source.txt" in d["source_path"]
        assert "dest.txt" in d["destination_path"]
        assert d["requester_agent"] == "TestAgent"
        assert d["reason"] == "Test reason"
        assert "timestamp" in d
