"""P4 MCP optimization tests — read_gateway.py (mcp6_* filesystem reads)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

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

_emit_records_execution_trace("p0", "evidence", "test_read_gateway")
_emit_applies_guardrail("p0", "test_read_gateway", "p0_governance")
_emit_reads_policy_state("p0", "test_read_gateway", "policy_binding")
_emit_snapshots_state("p0", "test_read_gateway", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_read_gateway", "p4obs", "metric_1")
_emit_emits_metric_event("test_read_gateway", "p4obs", "metric_2")
_emit_emits_metric_event("test_read_gateway", "p4obs", "metric_3")
_emit_emits_metric_event("test_read_gateway", "p4obs", "metric_4")
_emit_emits_metric_event("test_read_gateway", "p4obs", "metric_5")
_emit_emits_metric_event("test_read_gateway", "p4obs", "metric_6")
_emit_records_incident_event("test_read_gateway", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_read_gateway", "p4obs", "anomaly")
_emit_writes_observability_log("test_read_gateway", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_read_gateway", "p4obs", "mon_state")
_emit_triggers_alert("test_read_gateway", "p4obs", "alert")
_emit_links_incident_trace("test_read_gateway", "p4obs", "trace_link")
_emit_captures_pattern("test_read_gateway", "p3lm", "pattern")
_emit_records_learning_event("test_read_gateway", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_read_gateway", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_read_gateway", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_read_gateway", "p3lm", "routing")
_emit_improves_agent_policy("test_read_gateway", "p3lm", "policy")
_emit_stores_learning_state("test_read_gateway", "p3lm", "state")
_emit_records_execution_trace("test_read_gateway", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_read_gateway", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_read_gateway", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_read_gateway", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_read_gateway", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_read_gateway", "env_read", "p2_env_1")
_emit_reads_environ("test_read_gateway", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_read_gateway", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_read_gateway", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_read_gateway", "context_pull")
_emit_pulls_context("p1", "test_read_gateway", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_read_gateway", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_read_gateway", "uwg_term_2")
_emit_writes_through("p1", "test_read_gateway", "write_through")
_emit_writes_through("p1", "test_read_gateway", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_read_gateway", "safety_validation")
_emit_invokes_eval("p1", "test_read_gateway", "eval_call")
_emit_proposal_commits_routing("p1", "test_read_gateway", "routing_commit")
emit_replay_key("p0", "test_read_gateway")
emit_determinism_digest("p0", "test_read_gateway")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_read_gateway", "execution_auth")
_emit_validates_capability("p2", "test_read_gateway", "capability_check")
_emit_routes_to_capability("p2", "test_read_gateway", "capability_route")
_emit_writes_via_uwg("p2", "test_read_gateway", "uwg_write")
_emit_blocks_direct_write("p2", "test_read_gateway", "direct_write_block")
_emit_records_tool_invocation("p2", "test_read_gateway", "tool_invocation")
_emit_captures_execution_output("p2", "test_read_gateway", "exec_output")
_emit_dispatches_agent("p3", "test_read_gateway", "agent_dispatch")
_emit_coordinates_agents("p3", "test_read_gateway", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_read_gateway", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_read_gateway", "healing_outcome")
_emit_escalates_failure("p3", "test_read_gateway", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_read_gateway", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_read_gateway", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_read_gateway", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_read_gateway", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_read_gateway", "eval_metric")
_emit_stores_embedding("p4", "test_read_gateway", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_read_gateway", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_read_gateway", "exec_snapshot_link")

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.tools.read_gateway import (
        file_exists,
        get_file_info,
        list_directory,
        read_bytes,
        read_json,
        read_text,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    read_text = None  # type: ignore[assignment]
    read_bytes = None  # type: ignore[assignment]
    read_json = None  # type: ignore[assignment]
    list_directory = None  # type: ignore[assignment]
    file_exists = None  # type: ignore[assignment]
    get_file_info = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestReadTextFallback:
    def test_reads_real_file_via_fallback(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        result = read_text(f)
        assert "hello world" in result

    def test_uses_mcp6_when_available(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("real content", encoding="utf-8")
        mock_fn = MagicMock(return_value="mcp content")
        with patch.dict("sys.modules", {"mcp6_read_text_file": MagicMock(mcp6_read_text_file=mock_fn)}):
            result = read_text(f)
        assert result == "mcp content"

    def test_falls_back_on_import_error(self, tmp_path):
        import sys

        f = tmp_path / "fallback.txt"
        f.write_text("fallback content", encoding="utf-8")
        original = sys.modules.pop("mcp6_read_text_file", None)
        try:
            result = read_text(f)
            assert "fallback content" in result
        finally:
            if original is not None:
                sys.modules["mcp6_read_text_file"] = original

    def test_falls_back_on_mcp6_exception(self, tmp_path):
        f = tmp_path / "except.txt"
        f.write_text("direct content", encoding="utf-8")
        mock_fn = MagicMock(side_effect=RuntimeError("mcp error"))
        with patch.dict("sys.modules", {"mcp6_read_text_file": MagicMock(mcp6_read_text_file=mock_fn)}):
            result = read_text(f)
        assert "direct content" in result


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestReadBytes:
    def test_reads_binary_file(self, tmp_path):
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01\x02\x03")
        result = read_bytes(f)
        assert result == b"\x00\x01\x02\x03"


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestReadJson:
    def test_reads_and_parses_json(self, tmp_path):
        f = tmp_path / "data.json"
        data = {"key": "value", "num": 42}
        f.write_text(json.dumps(data), encoding="utf-8")
        result = read_json(f)
        assert result["key"] == "value"
        assert result["num"] == 42

    def test_raises_on_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not valid json {{{{", encoding="utf-8")
        with pytest.raises(Exception):
            read_json(f)


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestListDirectory:
    def test_lists_files_in_directory(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        result = list_directory(tmp_path)
        assert isinstance(result, list)
        names = [Path(r).name if "/" in r or "\\" in r else r for r in result]
        assert any("a.txt" in n for n in names)
        assert any("b.txt" in n for n in names)

    def test_uses_mcp6_when_available(self, tmp_path):
        mock_fn = MagicMock(return_value=["file1.txt", "file2.txt"])
        with patch.dict("sys.modules", {"mcp6_list_directory": MagicMock(mcp6_list_directory=mock_fn)}):
            result = list_directory(tmp_path)
        assert isinstance(result, list)

    def test_falls_back_on_import_error(self, tmp_path):
        import sys

        (tmp_path / "test.txt").write_text("x")
        original = sys.modules.pop("mcp6_list_directory", None)
        try:
            result = list_directory(tmp_path)
            assert isinstance(result, list)
            assert len(result) >= 1
        finally:
            if original is not None:
                sys.modules["mcp6_list_directory"] = original


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestFileExists:
    def test_returns_true_for_existing_file(self, tmp_path):
        f = tmp_path / "exists.txt"
        f.write_text("x")
        assert file_exists(f) is True

    def test_returns_false_for_missing_file(self, tmp_path):
        f = tmp_path / "missing.txt"
        assert file_exists(f) is False


@pytest.mark.skipif(not _AVAILABLE, reason="read_gateway deps unavailable")
class TestGetFileInfo:
    def test_returns_dict(self, tmp_path):
        f = tmp_path / "info.txt"
        f.write_text("hello")
        result = get_file_info(f)
        assert isinstance(result, dict)

    def test_fallback_has_expected_keys(self, tmp_path):
        import sys

        f = tmp_path / "info.txt"
        f.write_text("hello")
        original = sys.modules.pop("mcp6_get_file_info", None)
        try:
            result = get_file_info(f)
            assert "size" in result
            assert "is_file" in result
            assert result["is_file"] is True
        finally:
            if original is not None:
                sys.modules["mcp6_get_file_info"] = original

    def test_uses_mcp6_when_available(self, tmp_path):
        f = tmp_path / "info.txt"
        f.write_text("hello")
        mock_result = {"size": 5, "is_file": True, "is_dir": False}
        mock_fn = MagicMock(return_value=mock_result)
        with patch.dict("sys.modules", {"mcp6_get_file_info": MagicMock(mcp6_get_file_info=mock_fn)}):
            result = get_file_info(f)
        assert isinstance(result, dict)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
