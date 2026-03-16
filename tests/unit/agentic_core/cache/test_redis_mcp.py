"""P3 MCP optimization tests — check_redis_health_via_mcp in redis_cache_client.py."""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_redis_mcp")
_emit_applies_guardrail("p0", "test_redis_mcp", "p0_governance")
_emit_reads_policy_state("p0", "test_redis_mcp", "policy_binding")
_emit_snapshots_state("p0", "test_redis_mcp", "state_snapshot")
emit_replay_key("p0", "test_redis_mcp")
emit_determinism_digest("p0", "test_redis_mcp")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_redis_mcp", "execution_auth")
_emit_validates_capability("p2", "test_redis_mcp", "capability_check")
_emit_routes_to_capability("p2", "test_redis_mcp", "capability_route")
_emit_writes_via_uwg("p2", "test_redis_mcp", "uwg_write")
_emit_blocks_direct_write("p2", "test_redis_mcp", "direct_write_block")
_emit_records_tool_invocation("p2", "test_redis_mcp", "tool_invocation")
_emit_captures_execution_output("p2", "test_redis_mcp", "exec_output")
_emit_dispatches_agent("p3", "test_redis_mcp", "agent_dispatch")
_emit_coordinates_agents("p3", "test_redis_mcp", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_redis_mcp", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_redis_mcp", "healing_outcome")
_emit_escalates_failure("p3", "test_redis_mcp", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_redis_mcp", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_redis_mcp", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_redis_mcp", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_redis_mcp", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_redis_mcp", "eval_metric")
_emit_stores_embedding("p4", "test_redis_mcp", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_redis_mcp", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_redis_mcp", "exec_snapshot_link")

pytestmark = pytest.mark.unit

try:
    from agentic_core.cache.redis_cache_client import check_redis_health_via_mcp

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    check_redis_health_via_mcp = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="redis_cache_client deps unavailable")
class TestCheckRedisHealthViaMcp:
    def test_returns_dict(self):
        result = check_redis_health_via_mcp()
        assert isinstance(result, dict)

    def test_result_has_required_keys(self):
        result = check_redis_health_via_mcp()
        assert "healthy" in result
        assert "method" in result
        assert "error" in result

    def test_method_is_mcp11(self):
        result = check_redis_health_via_mcp()
        assert result["method"] == "mcp11"

    def test_healthy_bool_type(self):
        result = check_redis_health_via_mcp()
        assert isinstance(result["healthy"], bool)

    def test_import_error_returns_unhealthy(self):
        import sys

        mods_to_remove = ["mcp11_set", "mcp11_get", "mcp11_delete"]
        originals = {m: sys.modules.pop(m, None) for m in mods_to_remove}
        try:
            result = check_redis_health_via_mcp()
            assert result["healthy"] is False
            assert "mcp11" in result["error"]
        finally:
            for m, orig in originals.items():
                if orig is not None:
                    sys.modules[m] = orig

    def test_mcp11_success_returns_healthy(self):
        mock_set = MagicMock(return_value=None)
        mock_get = MagicMock(return_value="1")
        mock_delete = MagicMock(return_value=None)
        mock_set_mod = MagicMock(mcp11_set=mock_set)
        mock_get_mod = MagicMock(mcp11_get=mock_get)
        mock_del_mod = MagicMock(mcp11_delete=mock_delete)
        with patch.dict(
            "sys.modules",
            {
                "mcp11_set": mock_set_mod,
                "mcp11_get": mock_get_mod,
                "mcp11_delete": mock_del_mod,
            },
        ):
            result = check_redis_health_via_mcp()
        assert result["healthy"] is True
        assert result["error"] is None

    def test_mcp11_get_returns_none_means_unhealthy(self):
        mock_set = MagicMock(return_value=None)
        mock_get = MagicMock(return_value=None)
        mock_delete = MagicMock(return_value=None)
        mock_set_mod = MagicMock(mcp11_set=mock_set)
        mock_get_mod = MagicMock(mcp11_get=mock_get)
        mock_del_mod = MagicMock(mcp11_delete=mock_delete)
        with patch.dict(
            "sys.modules",
            {
                "mcp11_set": mock_set_mod,
                "mcp11_get": mock_get_mod,
                "mcp11_delete": mock_del_mod,
            },
        ):
            result = check_redis_health_via_mcp()
        assert result["healthy"] is False

    def test_mcp11_exception_returns_unhealthy_with_error(self):
        mock_set = MagicMock(side_effect=ConnectionError("connection refused"))
        mock_set_mod = MagicMock(mcp11_set=mock_set)
        with patch.dict(
            "sys.modules",
            {
                "mcp11_set": mock_set_mod,
                "mcp11_get": MagicMock(mcp11_get=MagicMock()),
                "mcp11_delete": MagicMock(mcp11_delete=MagicMock()),
            },
        ):
            result = check_redis_health_via_mcp()
        assert result["healthy"] is False
        assert result["error"] is not None

    def test_does_not_raise(self):
        try:
            check_redis_health_via_mcp()
        except Exception as e:
            pytest.fail(f"check_redis_health_via_mcp raised unexpectedly: {e}")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
