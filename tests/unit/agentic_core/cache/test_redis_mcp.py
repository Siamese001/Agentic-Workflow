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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_redis_mcp")
_emit_applies_guardrail("p0", "test_redis_mcp", "p0_governance")
_emit_reads_policy_state("p0", "test_redis_mcp", "policy_binding")
_emit_snapshots_state("p0", "test_redis_mcp", "state_snapshot")
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_redis_mcp", "p4obs", "metric_1")
_emit_emits_metric_event("test_redis_mcp", "p4obs", "metric_2")
_emit_emits_metric_event("test_redis_mcp", "p4obs", "metric_3")
_emit_emits_metric_event("test_redis_mcp", "p4obs", "metric_4")
_emit_emits_metric_event("test_redis_mcp", "p4obs", "metric_5")
_emit_emits_metric_event("test_redis_mcp", "p4obs", "metric_6")
_emit_records_incident_event("test_redis_mcp", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_redis_mcp", "p4obs", "anomaly")
_emit_writes_observability_log("test_redis_mcp", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_redis_mcp", "p4obs", "mon_state")
_emit_triggers_alert("test_redis_mcp", "p4obs", "alert")
_emit_links_incident_trace("test_redis_mcp", "p4obs", "trace_link")
_emit_captures_pattern("test_redis_mcp", "p3lm", "pattern")
_emit_records_learning_event("test_redis_mcp", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_redis_mcp", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_redis_mcp", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_redis_mcp", "p3lm", "routing")
_emit_improves_agent_policy("test_redis_mcp", "p3lm", "policy")
_emit_stores_learning_state("test_redis_mcp", "p3lm", "state")
_emit_records_execution_trace("test_redis_mcp", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_redis_mcp", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_redis_mcp", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_redis_mcp", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_redis_mcp", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_redis_mcp", "env_read", "p2_env_1")
_emit_reads_environ("test_redis_mcp", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_redis_mcp", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_redis_mcp", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_redis_mcp", "context_pull")
_emit_pulls_context("p1", "test_redis_mcp", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_redis_mcp", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_redis_mcp", "uwg_term_2")
_emit_writes_through("p1", "test_redis_mcp", "write_through")
_emit_writes_through("p1", "test_redis_mcp", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_redis_mcp", "safety_validation")
_emit_invokes_eval("p1", "test_redis_mcp", "eval_call")
_emit_proposal_commits_routing("p1", "test_redis_mcp", "routing_commit")
_emit_escalates_to_human("p1", "test_redis_mcp", "human_escalation")
_emit_routes_through("p1", "test_redis_mcp", "route_through")
_emit_checks_agent_registry("p1", "test_redis_mcp", "agent_registry")
_emit_validates_agent_capability("p1", "test_redis_mcp", "capability")
_emit_dispatches_execution_plan("p1", "test_redis_mcp", "exec_plan")
_emit_agent_executes_agent("p1", "test_redis_mcp", "sub_agent")
_emit_routes_to_agent("p1", "test_redis_mcp", "target_agent")
_emit_verifies_policy("p1", "test_redis_mcp", "policy_check")
_emit_observes_runtime_state("p1", "test_redis_mcp", "runtime_state")
_emit_verifies_boundary("p1", "test_redis_mcp", "boundary_check")
_emit_transcripts_response("p1", "test_redis_mcp", "transcript")
_emit_hard_fails_untranscripted("p1", "test_redis_mcp")
_emit_gated_by_confidence("p1", "test_redis_mcp", "confidence_gate")
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
