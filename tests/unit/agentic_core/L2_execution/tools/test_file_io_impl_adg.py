"""ADG-driven tests for L2 execution file_io_impl — fan_in=1."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_file_io_impl_adg")
_emit_applies_guardrail("p0", "test_file_io_impl_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_file_io_impl_adg", "policy_binding")
_emit_snapshots_state("p0", "test_file_io_impl_adg", "state_snapshot")
emit_replay_key("p0", "test_file_io_impl_adg")
emit_determinism_digest("p0", "test_file_io_impl_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_file_io_impl_adg", "execution_auth")
_emit_validates_capability("p2", "test_file_io_impl_adg", "capability_check")
_emit_routes_to_capability("p2", "test_file_io_impl_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_file_io_impl_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_file_io_impl_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_file_io_impl_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_file_io_impl_adg", "exec_output")
_emit_dispatches_agent("p3", "test_file_io_impl_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_file_io_impl_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_file_io_impl_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_file_io_impl_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_file_io_impl_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_file_io_impl_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_file_io_impl_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_file_io_impl_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_file_io_impl_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_file_io_impl_adg", "eval_metric")
_emit_stores_embedding("p4", "test_file_io_impl_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_file_io_impl_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_file_io_impl_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.tools.file_io_impl import FileIo


class TestFileIoInit:
    def test_creates(self):
        fio = FileIo()
        assert fio is not None

    def test_has_read_file(self):
        assert hasattr(FileIo, "read_file")

    def test_has_save_file(self):
        assert hasattr(FileIo, "save_file")


class TestFileIoReadFile:
    def setup_method(self):
        self.fio = FileIo()

    def test_read_missing_file_returns_error_str(self):
        result = self.fio.read_file("/nonexistent_xyz/foo.txt")
        assert isinstance(result, str)
        assert "Error" in result or "error" in result.lower()

    def test_read_existing_text_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("hello world")
            tmp = f.name
        try:
            result = self.fio.read_file(tmp)
            assert result == "hello world"
        finally:
            Path(tmp).unlink(missing_ok=True)

    def test_read_md_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Title\ncontent")
            tmp = f.name
        try:
            result = self.fio.read_file(tmp)
            assert "Title" in result
        finally:
            Path(tmp).unlink(missing_ok=True)


class TestFileIoSaveFile:
    def setup_method(self):
        self.fio = FileIo()

    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "output.txt")
            result = self.fio.save_file("test content", path)
            assert isinstance(result, str)
            assert Path(path).exists()

    def test_save_writes_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "out.txt")
            self.fio.save_file("saved content", path)
            assert Path(path).read_text(encoding="utf-8") == "saved content"
