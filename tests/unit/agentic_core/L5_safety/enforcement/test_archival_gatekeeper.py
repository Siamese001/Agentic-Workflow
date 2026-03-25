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

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (
    ArchivalGatekeeper,
    ArchivalOperation,
    ArchivalResult,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_archival_gatekeeper", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_archival_gatekeeper", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_archival_gatekeeper", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_archival_gatekeeper", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_archival_gatekeeper", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_archival_gatekeeper", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_archival_gatekeeper", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_archival_gatekeeper", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_archival_gatekeeper", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_archival_gatekeeper", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_archival_gatekeeper", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_archival_gatekeeper", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_archival_gatekeeper", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_archival_gatekeeper", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_archival_gatekeeper", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_archival_gatekeeper", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_archival_gatekeeper", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_archival_gatekeeper", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_archival_gatekeeper", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_archival_gatekeeper", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_archival_gatekeeper", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_archival_gatekeeper", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_archival_gatekeeper", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_archival_gatekeeper", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_archival_gatekeeper", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_archival_gatekeeper", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_archival_gatekeeper", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_archival_gatekeeper", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_archival_gatekeeper")
# REMOVED: _emit_applies_guardrail("p0", "test_archival_gatekeeper", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_archival_gatekeeper", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_archival_gatekeeper", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_archival_gatekeeper", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_archival_gatekeeper", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_archival_gatekeeper", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_archival_gatekeeper", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_archival_gatekeeper", "write_through")
# REMOVED: _emit_writes_through("p1", "test_archival_gatekeeper", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_archival_gatekeeper", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_archival_gatekeeper", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_archival_gatekeeper", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_archival_gatekeeper", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_archival_gatekeeper", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_archival_gatekeeper", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_archival_gatekeeper", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_archival_gatekeeper", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_archival_gatekeeper", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_archival_gatekeeper", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_archival_gatekeeper", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_archival_gatekeeper", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_archival_gatekeeper", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_archival_gatekeeper", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_archival_gatekeeper")
# REMOVED: _emit_gated_by_confidence("p1", "test_archival_gatekeeper", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_archival_gatekeeper")
# REMOVED: emit_determinism_digest("p0", "test_archival_gatekeeper")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_archival_gatekeeper", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_archival_gatekeeper", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_archival_gatekeeper", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_archival_gatekeeper", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_archival_gatekeeper", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_archival_gatekeeper", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_archival_gatekeeper", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_archival_gatekeeper", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_archival_gatekeeper", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_archival_gatekeeper", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_archival_gatekeeper", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_archival_gatekeeper", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_archival_gatekeeper", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_archival_gatekeeper", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_archival_gatekeeper", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_archival_gatekeeper", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_archival_gatekeeper", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_archival_gatekeeper", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_archival_gatekeeper", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_archival_gatekeeper", "exec_snapshot_link")

LIMIT = 5


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
    """Test get_instance_requires_project_root_first_call runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute get_instance_requires_project_root_first_call
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
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
