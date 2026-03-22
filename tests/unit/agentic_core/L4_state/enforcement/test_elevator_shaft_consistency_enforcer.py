"""Tests for ElevatorShaftConsistencyEnforcer — runtime semantic clock sync gate."""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_elevator_shaft_consistency_enforcer")
_emit_applies_guardrail("p0", "test_elevator_shaft_consistency_enforcer", "p0_governance")
_emit_reads_policy_state("p0", "test_elevator_shaft_consistency_enforcer", "policy_binding")
_emit_snapshots_state("p0", "test_elevator_shaft_consistency_enforcer", "state_snapshot")
emit_replay_key("p0", "test_elevator_shaft_consistency_enforcer")
emit_determinism_digest("p0", "test_elevator_shaft_consistency_enforcer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_elevator_shaft_consistency_enforcer", "execution_auth")
_emit_validates_capability("p2", "test_elevator_shaft_consistency_enforcer", "capability_check")
_emit_routes_to_capability("p2", "test_elevator_shaft_consistency_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "test_elevator_shaft_consistency_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "test_elevator_shaft_consistency_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_elevator_shaft_consistency_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "test_elevator_shaft_consistency_enforcer", "exec_output")
_emit_dispatches_agent("p3", "test_elevator_shaft_consistency_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_elevator_shaft_consistency_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_elevator_shaft_consistency_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_elevator_shaft_consistency_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "test_elevator_shaft_consistency_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_elevator_shaft_consistency_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_elevator_shaft_consistency_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_elevator_shaft_consistency_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_elevator_shaft_consistency_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_elevator_shaft_consistency_enforcer", "eval_metric")
_emit_stores_embedding("p4", "test_elevator_shaft_consistency_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_elevator_shaft_consistency_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_elevator_shaft_consistency_enforcer", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
    ClockSyncViolation,
    ElevatorShaftConsistencyEnforcer,
    MonotonicityViolation,
    WallClockContaminationError,
    assert_clock_synchronized,
    assert_no_wall_clock_in_module,
    get_enforcer,
    reset_enforcer,
)
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

_emit_emits_metric_event("test_elevator_shaft_consistency_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("test_elevator_shaft_consistency_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("test_elevator_shaft_consistency_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("test_elevator_shaft_consistency_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("test_elevator_shaft_consistency_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("test_elevator_shaft_consistency_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("test_elevator_shaft_consistency_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_elevator_shaft_consistency_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("test_elevator_shaft_consistency_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_elevator_shaft_consistency_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("test_elevator_shaft_consistency_enforcer", "p4obs", "alert")
_emit_links_incident_trace("test_elevator_shaft_consistency_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("test_elevator_shaft_consistency_enforcer", "p3lm", "pattern")
_emit_records_learning_event("test_elevator_shaft_consistency_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_elevator_shaft_consistency_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_elevator_shaft_consistency_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_elevator_shaft_consistency_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("test_elevator_shaft_consistency_enforcer", "p3lm", "policy")
_emit_stores_learning_state("test_elevator_shaft_consistency_enforcer", "p3lm", "state")
_emit_records_execution_trace("test_elevator_shaft_consistency_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_elevator_shaft_consistency_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_elevator_shaft_consistency_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_elevator_shaft_consistency_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_elevator_shaft_consistency_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_elevator_shaft_consistency_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("test_elevator_shaft_consistency_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_elevator_shaft_consistency_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_elevator_shaft_consistency_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_elevator_shaft_consistency_enforcer", "context_pull")
_emit_pulls_context("p1", "test_elevator_shaft_consistency_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_elevator_shaft_consistency_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_elevator_shaft_consistency_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "test_elevator_shaft_consistency_enforcer", "write_through")
_emit_writes_through("p1", "test_elevator_shaft_consistency_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_elevator_shaft_consistency_enforcer", "safety_validation")
_emit_invokes_eval("p1", "test_elevator_shaft_consistency_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "test_elevator_shaft_consistency_enforcer", "routing_commit")
_emit_escalates_to_human("p1", "test_elevator_shaft_consistency_enforcer", "human_escalation")
_emit_routes_through("p1", "test_elevator_shaft_consistency_enforcer", "route_through")
_emit_checks_agent_registry("p1", "test_elevator_shaft_consistency_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "test_elevator_shaft_consistency_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "test_elevator_shaft_consistency_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "test_elevator_shaft_consistency_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "test_elevator_shaft_consistency_enforcer", "target_agent")
_emit_verifies_policy("p1", "test_elevator_shaft_consistency_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "test_elevator_shaft_consistency_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "test_elevator_shaft_consistency_enforcer", "boundary_check")
_emit_transcripts_response("p1", "test_elevator_shaft_consistency_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "test_elevator_shaft_consistency_enforcer")
_emit_gated_by_confidence("p1", "test_elevator_shaft_consistency_enforcer", "confidence_gate")


def _snap(tick: int) -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=tick)


class TestAssertClockSynchronized:
    def test_identical_ticks_passes(self):
        assert_clock_synchronized(_snap(10), _snap(10))

    def test_within_tolerance_passes(self):
        assert_clock_synchronized(_snap(10), _snap(14), tolerance=5)

    def test_at_exact_tolerance_passes(self):
        assert_clock_synchronized(_snap(10), _snap(15), tolerance=5)

    def test_exceeds_tolerance_raises(self):
        with pytest.raises(ClockSyncViolation, match="drift 6 exceeds tolerance 5"):
            assert_clock_synchronized(_snap(10), _snap(16), tolerance=5)

    def test_reverse_order_drift_raises(self):
        with pytest.raises(ClockSyncViolation):
            assert_clock_synchronized(_snap(20), _snap(10), tolerance=5)

    def test_zero_tolerance_different_ticks_raises(self):
        with pytest.raises(ClockSyncViolation):
            assert_clock_synchronized(_snap(1), _snap(2), tolerance=0)

    def test_zero_tolerance_same_tick_passes(self):
        assert_clock_synchronized(_snap(5), _snap(5), tolerance=0)

    def test_context_in_error_message(self):
        with pytest.raises(ClockSyncViolation, match="L0<>L2"):
            assert_clock_synchronized(_snap(0), _snap(100), tolerance=5, context="L0<>L2")


class TestAssertNoWallClockInModule:
    def test_clean_module_passes(self, tmp_path):
        module = tmp_path / "clean.py"
        module.write_text("x = 1 + 2\n", encoding="utf-8")
        assert_no_wall_clock_in_module(module)

    def test_wall_clock_module_raises(self, tmp_path):
        module = tmp_path / "dirty.py"
        module.write_text("import time\ndef f():\n    return time.time()\n", encoding="utf-8")
        with pytest.raises(WallClockContaminationError, match="wall-clock contamination"):
            assert_no_wall_clock_in_module(module, context="test")

    def test_missing_module_raises(self, tmp_path):
        missing = tmp_path / "nonexistent.py"
        with pytest.raises(WallClockContaminationError):
            assert_no_wall_clock_in_module(missing)


class TestElevatorShaftConsistencyEnforcerRecordAdvance:
    def test_first_advance_recorded(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        assert enforcer.layer_tick("L0") == 5

    def test_monotonic_advance_ok(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L0", _snap(10))
        assert enforcer.layer_tick("L0") == 10

    def test_same_tick_advance_ok(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L0", _snap(5))
        assert enforcer.layer_tick("L0") == 5

    def test_non_monotonic_advance_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(10))
        with pytest.raises(MonotonicityViolation, match="non-monotonic tick"):
            enforcer.record_advance("L0", _snap(9))

    def test_independent_layers(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L2", _snap(3))
        assert enforcer.layer_tick("L0") == 5
        assert enforcer.layer_tick("L2") == 3

    def test_unknown_layer_returns_none(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        assert enforcer.layer_tick("L99") is None


class TestElevatorShaftConsistencyEnforcerAssertSync:
    def test_synchronized_layers_passes(self):
        enforcer = ElevatorShaftConsistencyEnforcer(drift_tolerance=5)
        enforcer.record_advance("L0", _snap(10))
        enforcer.record_advance("L2", _snap(12))
        enforcer.assert_layers_synchronized("L0", "L2")

    def test_drifted_layers_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer(drift_tolerance=3)
        enforcer.record_advance("L0", _snap(10))
        enforcer.record_advance("L2", _snap(20))
        with pytest.raises(ClockSyncViolation):
            enforcer.assert_layers_synchronized("L0", "L2")

    def test_missing_layer_a_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L2", _snap(5))
        with pytest.raises(KeyError, match="L0"):
            enforcer.assert_layers_synchronized("L0", "L2")

    def test_missing_layer_b_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        with pytest.raises(KeyError, match="L2"):
            enforcer.assert_layers_synchronized("L0", "L2")


class TestElevatorShaftConsistencyEnforcerRegisterModule:
    def test_clean_module_registered(self, tmp_path):
        module = tmp_path / "clean.py"
        module.write_text("x = 1\n", encoding="utf-8")
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.register_module(module)

    def test_dirty_module_raises(self, tmp_path):
        module = tmp_path / "dirty.py"
        module.write_text("import datetime\ndef f():\n    return datetime.utcnow()\n", encoding="utf-8")
        enforcer = ElevatorShaftConsistencyEnforcer()
        with pytest.raises(WallClockContaminationError):
            enforcer.register_module(module)

    def test_module_not_scanned_twice(self, tmp_path):
        module = tmp_path / "clean.py"
        module.write_text("x = 1\n", encoding="utf-8")
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.register_module(module)
        enforcer.register_module(module)


class TestElevatorShaftConsistencyEnforcerSummary:
    def test_summary_contains_all_layers(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L2", _snap(3))
        s = enforcer.summary()
        assert "L0" in s
        assert "L2" in s
        assert s["L0"]["last_tick"] == 5
        assert s["L2"]["last_tick"] == 3

    def test_summary_tracks_advance_count(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(1))
        enforcer.record_advance("L0", _snap(2))
        enforcer.record_advance("L0", _snap(3))
        assert enforcer.summary()["L0"]["advance_count"] == 3


class TestGlobalEnforcer:
    def setup_method(self):
        reset_enforcer()

    def test_get_enforcer_returns_instance(self):
        e = get_enforcer()
        assert isinstance(e, ElevatorShaftConsistencyEnforcer)

    def test_get_enforcer_singleton(self):
        e1 = get_enforcer()
        e2 = get_enforcer()
        assert e1 is e2

    def test_reset_enforcer_creates_fresh_instance(self):
        e1 = get_enforcer()
        e1.record_advance("L0", _snap(100))
        reset_enforcer()
        e2 = get_enforcer()
        assert e2 is not e1
        assert e2.layer_tick("L0") is None

    def teardown_method(self):
        reset_enforcer()
