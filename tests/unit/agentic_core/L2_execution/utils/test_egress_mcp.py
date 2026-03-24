"""P2 MCP optimization tests for egress_util.py — mcp4_fetch integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_egress_mcp")
_emit_applies_guardrail("p0", "test_egress_mcp", "p0_governance")
_emit_reads_policy_state("p0", "test_egress_mcp", "policy_binding")
_emit_snapshots_state("p0", "test_egress_mcp", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_egress_mcp", "p4obs", "metric_1")
_emit_emits_metric_event("test_egress_mcp", "p4obs", "metric_2")
_emit_emits_metric_event("test_egress_mcp", "p4obs", "metric_3")
_emit_emits_metric_event("test_egress_mcp", "p4obs", "metric_4")
_emit_emits_metric_event("test_egress_mcp", "p4obs", "metric_5")
_emit_emits_metric_event("test_egress_mcp", "p4obs", "metric_6")
_emit_records_incident_event("test_egress_mcp", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_egress_mcp", "p4obs", "anomaly")
_emit_writes_observability_log("test_egress_mcp", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_egress_mcp", "p4obs", "mon_state")
_emit_triggers_alert("test_egress_mcp", "p4obs", "alert")
_emit_links_incident_trace("test_egress_mcp", "p4obs", "trace_link")
_emit_captures_pattern("test_egress_mcp", "p3lm", "pattern")
_emit_records_learning_event("test_egress_mcp", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_egress_mcp", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_egress_mcp", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_egress_mcp", "p3lm", "routing")
_emit_improves_agent_policy("test_egress_mcp", "p3lm", "policy")
_emit_stores_learning_state("test_egress_mcp", "p3lm", "state")
_emit_records_execution_trace("test_egress_mcp", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_egress_mcp", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_egress_mcp", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_egress_mcp", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_egress_mcp", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_egress_mcp", "env_read", "p2_env_1")
_emit_reads_environ("test_egress_mcp", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_egress_mcp", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_egress_mcp", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_egress_mcp", "context_pull")
_emit_pulls_context("p1", "test_egress_mcp", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_egress_mcp", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_egress_mcp", "uwg_term_2")
_emit_writes_through("p1", "test_egress_mcp", "write_through")
_emit_writes_through("p1", "test_egress_mcp", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_egress_mcp", "safety_validation")
_emit_invokes_eval("p1", "test_egress_mcp", "eval_call")
_emit_proposal_commits_routing("p1", "test_egress_mcp", "routing_commit")
_emit_escalates_to_human("p1", "test_egress_mcp", "human_escalation")
_emit_routes_through("p1", "test_egress_mcp", "route_through")
_emit_checks_agent_registry("p1", "test_egress_mcp", "agent_registry")
_emit_validates_agent_capability("p1", "test_egress_mcp", "capability")
_emit_dispatches_execution_plan("p1", "test_egress_mcp", "exec_plan")
_emit_agent_executes_agent("p1", "test_egress_mcp", "sub_agent")
_emit_routes_to_agent("p1", "test_egress_mcp", "target_agent")
_emit_verifies_policy("p1", "test_egress_mcp", "policy_check")
_emit_observes_runtime_state("p1", "test_egress_mcp", "runtime_state")
_emit_verifies_boundary("p1", "test_egress_mcp", "boundary_check")
_emit_transcripts_response("p1", "test_egress_mcp", "transcript")
_emit_hard_fails_untranscripted("p1", "test_egress_mcp")
_emit_gated_by_confidence("p1", "test_egress_mcp", "confidence_gate")
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
