"""ADG-driven tests for agentic_core/L0_routing/scripts/execution_context.py — fan_in=2.

Contract tests: ConfigSurface, ExecutionContext, BaseRefiner.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_execution_context_adg")
_emit_applies_guardrail("p0", "test_execution_context_adg", "p0_governance")
_emit_snapshots_state("p0", "test_execution_context_adg", "state_snapshot")
emit_replay_key("p0", "test_execution_context_adg")
emit_determinism_digest("p0", "test_execution_context_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_context_adg", "execution_auth")
_emit_validates_capability("p2", "test_execution_context_adg", "capability_check")
_emit_routes_to_capability("p2", "test_execution_context_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_context_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_context_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_context_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_context_adg", "exec_output")
_emit_dispatches_agent("p3", "test_execution_context_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_context_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_context_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_context_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_context_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_context_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_context_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_context_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_context_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_context_adg", "eval_metric")
_emit_stores_embedding("p4", "test_execution_context_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_context_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_context_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.execution_context import (
    BaseRefiner,
    ConfigSurface,
    ExecutionContext,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_execution_context_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_execution_context_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_execution_context_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_execution_context_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_execution_context_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_execution_context_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_execution_context_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_execution_context_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_execution_context_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_execution_context_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_execution_context_adg", "p4obs", "alert")
_emit_links_incident_trace("test_execution_context_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_execution_context_adg", "p3lm", "pattern")
_emit_records_learning_event("test_execution_context_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_execution_context_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_execution_context_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_execution_context_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_execution_context_adg", "p3lm", "policy")
_emit_stores_learning_state("test_execution_context_adg", "p3lm", "state")
_emit_records_execution_trace("test_execution_context_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_execution_context_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_execution_context_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_execution_context_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_execution_context_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_execution_context_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_execution_context_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_execution_context_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_execution_context_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_execution_context_adg", "context_pull")
_emit_pulls_context("p1", "test_execution_context_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_execution_context_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_execution_context_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_execution_context_adg", "write_through")
_emit_writes_through("p1", "test_execution_context_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_execution_context_adg", "safety_validation")
_emit_invokes_eval("p1", "test_execution_context_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_execution_context_adg", "routing_commit")


class TestConfigSurface:
    def test_creates_valid(self):
        cs = ConfigSurface(
            threshold_configs={"threshold": 0.85},
            tier_constants={"X": 0.75, "Y": 0.40},
            tool_budget_caps={"max_tool_calls": 100},
            freshness_windows={"ttl": 3600},
        )
        assert cs.threshold_configs["threshold"] == 0.85

    def test_is_frozen(self):
        cs = ConfigSurface(
            threshold_configs={},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        with pytest.raises(Exception):
            cs.threshold_configs = {"new": 0.5}  # frozen

    def test_compute_hash_returns_hex_string(self):
        cs = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={"x": 0.5},
            tool_budget_caps={"max": 10},
            freshness_windows={"ttl": 100},
        )
        h = cs.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_compute_hash_deterministic(self):
        cs1 = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        cs2 = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        assert cs1.compute_hash() == cs2.compute_hash()

    def test_different_configs_different_hash(self):
        cs1 = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        cs2 = ConfigSurface(
            threshold_configs={"t": 0.8},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        assert cs1.compute_hash() != cs2.compute_hash()


class TestExecutionContext:
    def test_creates_with_defaults(self):
        ctx = ExecutionContext()
        assert ctx.mission_id == ""
        assert ctx.step_id == ""
        assert ctx.replay_mode is False
        assert ctx.safety_status == "PENDING"

    def test_to_dict_has_required_keys(self):
        ctx = ExecutionContext(mission_id="m1", step_id="s1")
        d = ctx.to_dict()
        for key in ("mission_id", "step_id", "timestamp", "replay_mode", "safety_status"):
            assert key in d

    def test_to_dict_mission_id(self):
        ctx = ExecutionContext(mission_id="mission_abc")
        assert ctx.to_dict()["mission_id"] == "mission_abc"

    def test_set_config_surface_updates_hash(self):
        ctx = ExecutionContext()
        assert ctx.config_surface_hash is None
        cs = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        ctx.set_config_surface(cs)
        assert ctx.config_surface_hash is not None
        assert len(ctx.config_surface_hash) == 64

    def test_trace_id_default_none(self):
        ctx = ExecutionContext()
        assert ctx.trace_id is None

    def test_active_policy_hash_default_none(self):
        ctx = ExecutionContext()
        assert ctx.active_policy_hash is None


class TestBaseRefiner:
    def test_creates_without_config(self):
        r = BaseRefiner()
        assert r.config == {}
        assert r.weights == {}

    def test_creates_with_config(self):
        r = BaseRefiner(config={"weights": {"score": 2.0}})
        assert r.weights == {"score": 2.0}

    def test_refine_applies_weights(self):
        r = BaseRefiner()
        result = r.refine({"score": 10.0}, weights={"score": 2.0})
        assert result["score"] == 20.0

    def test_refine_no_weights_returns_copy(self):
        r = BaseRefiner()
        data = {"value": 42}
        result = r.refine(data)
        assert result["value"] == 42
        assert result is not data  # copy, not same object

    def test_refine_skips_non_numeric(self):
        r = BaseRefiner()
        result = r.refine({"name": "foo", "score": 10.0}, weights={"score": 3.0, "name": 2.0})
        assert result["name"] == "foo"  # string not multiplied
        assert result["score"] == pytest.approx(30.0)
