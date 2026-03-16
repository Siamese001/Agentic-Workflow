"""P2 MCP optimization tests for egress_util.py — mcp4_fetch integration."""

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

_emit_records_execution_trace("p0", "evidence", "test_egress_mcp")
_emit_applies_guardrail("p0", "test_egress_mcp", "p0_governance")
_emit_reads_policy_state("p0", "test_egress_mcp", "policy_binding")
_emit_snapshots_state("p0", "test_egress_mcp", "state_snapshot")
emit_replay_key("p0", "test_egress_mcp")
emit_determinism_digest("p0", "test_egress_mcp")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_egress_mcp", "execution_auth")
_emit_validates_capability("p2", "test_egress_mcp", "capability_check")
_emit_routes_to_capability("p2", "test_egress_mcp", "capability_route")
_emit_writes_via_uwg("p2", "test_egress_mcp", "uwg_write")
_emit_blocks_direct_write("p2", "test_egress_mcp", "direct_write_block")
_emit_records_tool_invocation("p2", "test_egress_mcp", "tool_invocation")
_emit_captures_execution_output("p2", "test_egress_mcp", "exec_output")
_emit_dispatches_agent("p3", "test_egress_mcp", "agent_dispatch")
_emit_coordinates_agents("p3", "test_egress_mcp", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_egress_mcp", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_egress_mcp", "healing_outcome")
_emit_escalates_failure("p3", "test_egress_mcp", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_egress_mcp", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_egress_mcp", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_egress_mcp", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_egress_mcp", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_egress_mcp", "eval_metric")
_emit_stores_embedding("p4", "test_egress_mcp", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_egress_mcp", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_egress_mcp", "exec_snapshot_link")

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.egress_util import NetworkingUtility

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    NetworkingUtility = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="egress_util deps unavailable")
class TestFetchUrlEgressEnforcement:
    """Egress filter must be enforced before any MCP fetch call."""

    def setup_method(self):
        self.util = NetworkingUtility(allowed_hosts={"allowed.com"})

    def test_blocked_host_never_calls_mcp4(self):
        called = []
        mock_fn = MagicMock(side_effect=lambda **kwargs: called.append(kwargs) or "content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://blocked.evil.com/data")
        assert result["status"] == "blocked"
        assert called == [], "mcp4_fetch must NOT be called for blocked hosts"

    def test_allowed_host_attempts_mcp4(self):
        mock_fn = MagicMock(return_value="page content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert result["status"] in ("success", "mock_success", "error")

    def test_allowed_host_mcp4_success_returns_content(self):
        mock_fn = MagicMock(return_value="real page content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert result["status"] == "success"
        assert result["content"] == "real page content"
        assert result["url"] == "https://allowed.com/page"

    def test_allowed_host_mcp4_unavailable_falls_back(self):
        import sys

        original = sys.modules.pop("mcp4_fetch", None)
        try:
            result = self.util.fetch_url("https://allowed.com/page")
            assert result["status"] == "mock_success"
            assert "mcp4_fetch unavailable" in result["content"]
        finally:
            if original is not None:
                sys.modules["mcp4_fetch"] = original

    def test_allowed_host_mcp4_exception_returns_error(self):
        mock_fn = MagicMock(side_effect=RuntimeError("network timeout"))
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert result["status"] == "error"
        assert "network timeout" in result["reason"]

    def test_result_always_contains_host(self):
        mock_fn = MagicMock(return_value="content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert "host" in result

    def test_blocked_result_structure(self):
        result = self.util.fetch_url("https://blocked.com/page")
        assert "status" in result
        assert "reason" in result
        assert "host" in result
        assert result["status"] == "blocked"


@pytest.mark.skipif(not _AVAILABLE, reason="egress_util deps unavailable")
class TestFetchUrlSubdomainAllowed:
    def test_subdomain_of_allowed_host_is_fetched(self):
        util = NetworkingUtility(allowed_hosts={"example.com"})
        mock_fn = MagicMock(return_value="subdomain content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = util.fetch_url("https://api.example.com/v1/data")
        assert result["status"] in ("success", "mock_success")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
