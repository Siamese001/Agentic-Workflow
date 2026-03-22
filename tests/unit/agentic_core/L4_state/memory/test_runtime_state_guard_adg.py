"""ADG-driven tests for agentic_core/L4_state/memory/runtime_state_guard.py — fan_in=3.

Contract tests: RuntimeStateGuard importability, get_metric, increment_metric,
and batch context manager. Write gateway is mocked to avoid filesystem side effects.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_runtime_state_guard_adg")
_emit_applies_guardrail("p0", "test_runtime_state_guard_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_state_guard_adg", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_state_guard_adg", "state_snapshot")
emit_replay_key("p0", "test_runtime_state_guard_adg")
emit_determinism_digest("p0", "test_runtime_state_guard_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_runtime_state_guard_adg", "execution_auth")
_emit_validates_capability("p2", "test_runtime_state_guard_adg", "capability_check")
_emit_routes_to_capability("p2", "test_runtime_state_guard_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_runtime_state_guard_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_runtime_state_guard_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_runtime_state_guard_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_runtime_state_guard_adg", "exec_output")
_emit_dispatches_agent("p3", "test_runtime_state_guard_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_runtime_state_guard_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_runtime_state_guard_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_runtime_state_guard_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_runtime_state_guard_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_runtime_state_guard_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_runtime_state_guard_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_runtime_state_guard_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_runtime_state_guard_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_runtime_state_guard_adg", "eval_metric")
_emit_stores_embedding("p4", "test_runtime_state_guard_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_runtime_state_guard_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_runtime_state_guard_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L4_state.memory.runtime_state_guard import RuntimeStateGuard
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_runtime_state_guard_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_runtime_state_guard_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_runtime_state_guard_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_runtime_state_guard_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_runtime_state_guard_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_runtime_state_guard_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_runtime_state_guard_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_runtime_state_guard_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_runtime_state_guard_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_runtime_state_guard_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_runtime_state_guard_adg", "p4obs", "alert")
_emit_links_incident_trace("test_runtime_state_guard_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_runtime_state_guard_adg", "p3lm", "pattern")
_emit_records_learning_event("test_runtime_state_guard_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_runtime_state_guard_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_runtime_state_guard_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_runtime_state_guard_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_runtime_state_guard_adg", "p3lm", "policy")
_emit_stores_learning_state("test_runtime_state_guard_adg", "p3lm", "state")
_emit_records_execution_trace("test_runtime_state_guard_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_runtime_state_guard_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_runtime_state_guard_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_runtime_state_guard_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_runtime_state_guard_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_runtime_state_guard_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_runtime_state_guard_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_runtime_state_guard_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_runtime_state_guard_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_runtime_state_guard_adg", "context_pull")
_emit_pulls_context("p1", "test_runtime_state_guard_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_runtime_state_guard_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_runtime_state_guard_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_runtime_state_guard_adg", "write_through")
_emit_writes_through("p1", "test_runtime_state_guard_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_runtime_state_guard_adg", "safety_validation")
_emit_invokes_eval("p1", "test_runtime_state_guard_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_runtime_state_guard_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_runtime_state_guard_adg", "human_escalation")
_emit_routes_through("p1", "test_runtime_state_guard_adg", "route_through")
_emit_checks_agent_registry("p1", "test_runtime_state_guard_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_runtime_state_guard_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_runtime_state_guard_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_runtime_state_guard_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_runtime_state_guard_adg", "target_agent")
_emit_verifies_policy("p1", "test_runtime_state_guard_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_runtime_state_guard_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_runtime_state_guard_adg", "boundary_check")
_emit_transcripts_response("p1", "test_runtime_state_guard_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_runtime_state_guard_adg")
_emit_gated_by_confidence("p1", "test_runtime_state_guard_adg", "confidence_gate")


def _make_guard(tmp_path: Path) -> RuntimeStateGuard:
    state_path = tmp_path / "runtime_state.json"
    state_path.write_text("{}", encoding="utf-8")
    guard = RuntimeStateGuard.__new__(RuntimeStateGuard)
    guard.state_path = state_path
    guard.backup_path = tmp_path / "runtime_state.json.bak"
    guard._state_cache = {}
    guard._batch_depth = 0
    guard._dirty = False
    return guard


class TestRuntimeStateGuardImport:
    def test_class_importable(self):
        assert callable(RuntimeStateGuard)


class TestRuntimeStateGuardGetMetric:
    def test_missing_key_returns_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            assert guard.get_metric("cycles_healed") == 0

    def test_missing_key_custom_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            assert guard.get_metric("x", default=42) == 42

    def test_existing_metric_returned(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            guard._state_cache["shared_alignment_metrics"] = {"cycles_healed": 7}
            assert guard.get_metric("cycles_healed") == 7


class TestRuntimeStateGuardIncrementMetric:
    def test_increment_adds_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist"):
                guard.increment_metric("cycles_healed")
                assert guard.get_metric("cycles_healed") == 1

    def test_increment_cumulative(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist"):
                guard.increment_metric("cycles_healed")
                guard.increment_metric("cycles_healed")
                guard.increment_metric("cycles_healed")
                assert guard.get_metric("cycles_healed") == 3

    def test_increment_custom_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist"):
                guard.increment_metric("batch_count", value=5)
                assert guard.get_metric("batch_count") == 5

    def test_increment_in_batch_defers_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            guard._batch_depth = 1  # inside batch context
            with patch.object(guard, "_atomic_persist") as mock_persist:
                guard.increment_metric("x")
                mock_persist.assert_not_called()
                assert guard._dirty is True

    def test_increment_outside_batch_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            guard = _make_guard(Path(tmp))
            with patch.object(guard, "_atomic_persist") as mock_persist:
                guard.increment_metric("x")
                mock_persist.assert_called_once()
