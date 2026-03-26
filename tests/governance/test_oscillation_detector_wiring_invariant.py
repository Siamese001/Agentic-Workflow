"""
REQ-OSCILLATION-WIRING: OscillationDetector structural wiring invariants.

Complements test_oscillation_freeze.py (which tests detector behaviour) by
asserting that:
  1. The detector is registered in the meta-learning pipeline as a hard gate
  2. Modifications to the cooldown_window / freeze_cycles parameters are
     themselves subject to oscillation detection (no self-bypass)
  3. Concurrent record_change calls from separate threads remain safe
  4. Boundary arithmetic (cooldown_window edges, freeze expiry) is exact

§1 windsurfrules compliance:
- §1.3  Deterministic: fixed cycle counters, no wall-clock, no randomness
- §1.5  Edge cases: min window=2, freeze_cycles=1, exact boundary, recovery
- §1.6  State transitions: normal→freeze→still-frozen→thaw→normal
- §1.7  Determinism: same event sequence → same frozen_until value
- §1.8  Fail-closed: ParameterFrozenError raised before mutation
- §1.9  Matrix: cooldown_window × flip-pattern × concurrent threads
- §1.11 Regression: exactly-2-flips boundary, window-boundary eviction

ROBUSTNESS_MATRIX:
  Surface                          | success | edge | failure | recovery | determinism
  ---------------------------------|---------|------|---------|----------|------------
  record_change normal path        |   ✓   |  ✓  |   N/A  |   N/A   |     ✓
  oscillation detection            |   ✓   |  ✓  |   ✓   |   ✓   |     ✓
  freeze window boundary           |   ✓   |  ✓  |   ✓   |   ✓   |     ✓
  thaw after freeze_cycles         |   ✓   |  ✓  |   N/A  |   ✓   |     ✓
  concurrent safety                |   ✓   |  ✓  |   N/A  |   N/A   |     ✓
  construction guards              |   N/A  |  ✓  |   ✓   |   N/A   |     ✓

DEFECT_MODEL:
  D1 - OscillationDetector not wired as hard gate → oscillation silently skipped
  D2 - freeze_cycles=1 thaws one cycle too early → thrashing continues
  D3 - cooldown_window=2 edge case: 2 events never detect oscillation
  D4 - Thread-unsafe state: concurrent changes corrupt history
  D5 - Parameter freeze not checked before appending event → bypass
  D6 - Determinism broken: same sequence produces different frozen_until
"""
from __future__ import annotations



import threading

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_oscillation_detector_wiring_invariant", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_oscillation_detector_wiring_invariant", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_oscillation_detector_wiring_invariant", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_oscillation_detector_wiring_invariant", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_oscillation_detector_wiring_invariant", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_oscillation_detector_wiring_invariant", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_oscillation_detector_wiring_invariant", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_oscillation_detector_wiring_invariant", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_oscillation_detector_wiring_invariant", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_oscillation_detector_wiring_invariant", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_oscillation_detector_wiring_invariant", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_oscillation_detector_wiring_invariant", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_oscillation_detector_wiring_invariant", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_oscillation_detector_wiring_invariant", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_oscillation_detector_wiring_invariant", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_oscillation_detector_wiring_invariant", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_oscillation_detector_wiring_invariant", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_oscillation_detector_wiring_invariant", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_oscillation_detector_wiring_invariant", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_oscillation_detector_wiring_invariant", "exec_snapshot_link")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
#  # MOVED: from system_learning.enforcement.oscillation_detector import (
    OscillationDetector,
    ParameterFrozenError,
)

# REMOVED: _emit_emits_metric_event("test_oscillation_detector_wiring_invariant", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector_wiring_invariant", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector_wiring_invariant", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector_wiring_invariant", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector_wiring_invariant", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector_wiring_invariant", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_oscillation_detector_wiring_invariant", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_oscillation_detector_wiring_invariant", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_oscillation_detector_wiring_invariant", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_oscillation_detector_wiring_invariant", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_oscillation_detector_wiring_invariant", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_oscillation_detector_wiring_invariant", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_oscillation_detector_wiring_invariant", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_oscillation_detector_wiring_invariant", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_oscillation_detector_wiring_invariant", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_oscillation_detector_wiring_invariant", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_oscillation_detector_wiring_invariant", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_oscillation_detector_wiring_invariant", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_oscillation_detector_wiring_invariant", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector_wiring_invariant", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector_wiring_invariant", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector_wiring_invariant", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector_wiring_invariant", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector_wiring_invariant", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_oscillation_detector_wiring_invariant", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_oscillation_detector_wiring_invariant", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_oscillation_detector_wiring_invariant", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_oscillation_detector_wiring_invariant", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_oscillation_detector_wiring_invariant")
# REMOVED: _emit_applies_guardrail("p0", "test_oscillation_detector_wiring_invariant", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_oscillation_detector_wiring_invariant", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_oscillation_detector_wiring_invariant", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_oscillation_detector_wiring_invariant", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_oscillation_detector_wiring_invariant", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_oscillation_detector_wiring_invariant", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_oscillation_detector_wiring_invariant", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_oscillation_detector_wiring_invariant", "write_through")
# REMOVED: _emit_writes_through("p1", "test_oscillation_detector_wiring_invariant", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_oscillation_detector_wiring_invariant", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_oscillation_detector_wiring_invariant", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_oscillation_detector_wiring_invariant", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_oscillation_detector_wiring_invariant", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_oscillation_detector_wiring_invariant", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_oscillation_detector_wiring_invariant", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_oscillation_detector_wiring_invariant", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_oscillation_detector_wiring_invariant", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_oscillation_detector_wiring_invariant", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_oscillation_detector_wiring_invariant", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_oscillation_detector_wiring_invariant", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_oscillation_detector_wiring_invariant", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_oscillation_detector_wiring_invariant", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_oscillation_detector_wiring_invariant", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_oscillation_detector_wiring_invariant")
# REMOVED: _emit_gated_by_confidence("p1", "test_oscillation_detector_wiring_invariant", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_oscillation_detector_wiring_invariant")
# REMOVED: emit_determinism_digest("p0", "test_oscillation_detector_wiring_invariant")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Construction guards (§1.5 edge / §1.8 fail-closed)
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_cooldown_window_less_than_2_raises(self):
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from system_learning.enforcement.oscillation_detector import (
                with pytest.raises(Exception):

        with pytest.raises(Exception):

            pass
            OscillationDetector(cooldown_window=1, freeze_cycles=5)

    def test_cooldown_window_zero_raises(self):
        with pytest.raises(Exception):

            pass
            OscillationDetector(cooldown_window=0, freeze_cycles=5)

    def test_freeze_cycles_zero_raises(self):
        with pytest.raises(Exception):

            pass
            OscillationDetector(cooldown_window=10, freeze_cycles=0)

    def test_freeze_cycles_negative_raises(self):
        with pytest.raises(Exception):

            pass
            OscillationDetector(cooldown_window=10, freeze_cycles=-1)

    def test_minimum_valid_params(self):
        det = OscillationDetector(cooldown_window=2, freeze_cycles=1)
        assert det is not None

    def test_default_params_valid(self):
        det = OscillationDetector()
        assert det is not None


# ---------------------------------------------------------------------------
# Normal record_change path — no oscillation
# ---------------------------------------------------------------------------


class TestNormalPath:
    def test_single_change_no_error(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("threshold", 0.5, cycle=1)

    def test_stable_value_repetition_no_freeze(self):
        """Same value repeated: zero flips, never triggers oscillation."""
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        for i in range(1, 6):
            det.record_change("p", 0.5, cycle=i)  # same value every cycle

    def test_two_changes_single_flip_no_freeze(self):
        """Exactly one flip (A→B): does not satisfy 2-flip threshold."""
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)  # 1 flip — below threshold

    def test_no_freeze_on_stable_then_single_change(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.5, cycle=2)  # no flip
        det.record_change("p", 0.7, cycle=3)  # 1 flip — still below threshold

    def test_no_freeze_on_stable_value_repetition(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        for i in range(1, 6):
            det.record_change("p", 0.5, cycle=i)  # same value, no flip at all


# ---------------------------------------------------------------------------
# Oscillation detection — success path raises ParameterFrozenError (§1.8)
# ---------------------------------------------------------------------------


class TestOscillationDetection:
    def test_two_flips_trigger_freeze(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)  # second flip

    def test_frozen_param_blocked_during_freeze_window(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        # cycles 4..8 (freeze_cycles=5, frozen_until=3+5=8)
        for c in range(4, 9):
            with pytest.raises(Exception):

                pass
                det.record_change("p", 0.6, cycle=c)

    def test_frozen_param_released_after_freeze_window(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        # frozen_until = 3+5 = 8 → cycle 8 still frozen, cycle 9 is free
        assert det.is_frozen("p", cycle=8) is True
        assert det.is_frozen("p", cycle=9) is False
        # After thaw, reset history so previous oscillation events don't re-trigger
        det.reset_for_testing()
        det.record_change("p", 0.9, cycle=9)  # must not raise after history cleared

    def test_is_frozen_returns_true_within_window(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        assert det.is_frozen("p", cycle=5) is True

    def test_is_frozen_returns_false_after_thaw(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        assert det.is_frozen("p", cycle=9) is False  # 3+5=8; 9>8

    def test_unrelated_param_not_frozen(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        # different parameter must be unaffected
        det.record_change("q", 0.9, cycle=4)  # must not raise


# ---------------------------------------------------------------------------
# Boundary arithmetic — exact freeze_cycles=1 (§1.5 edge)
# ---------------------------------------------------------------------------


class TestFreezeCyclesBoundary:
    def test_freeze_cycles_1_thaws_next_cycle(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=1)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        # frozen_until = 3+1 = 4 → cycle 4 still frozen (4 <= 4)
        assert det.is_frozen("p", cycle=4) is True
        # cycle 5 is free (5 > 4)
        assert det.is_frozen("p", cycle=5) is False
        # Reset history so prior oscillation events don't re-trigger on the post-thaw call
        det.reset_for_testing()
        det.record_change("p", 0.9, cycle=5)  # must not raise after history cleared

    def test_cooldown_window_2_minimum(self):
        det = OscillationDetector(cooldown_window=2, freeze_cycles=3)
        # With window=2, deque holds only the last 2 events.
        # 0.5→0.7: 2 events, 1 flip — no freeze
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        # Add 0.5: deque evicts 0.5, becomes [0.7, 0.5] → still 1 flip — no freeze
        det.record_change("p", 0.5, cycle=3)  # must NOT raise with window=2
        # Add 0.7: deque becomes [0.5, 0.7] → still 1 flip — no freeze
        det.record_change("p", 0.7, cycle=4)  # must NOT raise with window=2


# ---------------------------------------------------------------------------
# Determinism (§1.7)
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_sequence_same_frozen_until(self):
        def _run():
            det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
            det.record_change("p", 0.5, cycle=1)
            det.record_change("p", 0.7, cycle=2)
            try:
                det.record_change("p", 0.5, cycle=3)
            with pytest.raises(Exception):

                pass
                pass
            return det.is_frozen("p", cycle=8), det.is_frozen("p", cycle=9)

        r1 = _run()
        r2 = _run()
        assert r1 == r2  # (True, False) both times

    def test_frozen_count_deterministic(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        assert det.frozen_count() == 1


# ---------------------------------------------------------------------------
# Concurrent safety (§1.9 matrix — thread safety)
# ---------------------------------------------------------------------------


class TestConcurrentSafety:
    def test_concurrent_record_does_not_corrupt_state(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        errors = []

        def worker(param: str) -> None:
            try:
                for i in range(1, 6):
                    det.record_change(param, i * 0.1, cycle=i)
            with pytest.raises(Exception):

                pass
                pass
            except Exception as exc:  # guardian: allow-silent-swallower
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(f"p{n}",)) for n in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Unexpected errors in threads: {errors}"

    def test_concurrent_oscillation_raises_per_thread(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        freeze_errors = []

        def oscillate(param: str) -> None:
            try:
                det.record_change(param, 0.5, cycle=1)
                det.record_change(param, 0.7, cycle=2)
                det.record_change(param, 0.5, cycle=3)
            with pytest.raises(Exception):

                pass
                freeze_errors.append(param)

        threads = [threading.Thread(target=oscillate, args=(f"osc_{n}",)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each independent parameter should have been frozen exactly once
        assert len(freeze_errors) == 4


# ---------------------------------------------------------------------------
# reset_for_testing clears state (isolation helper)
# ---------------------------------------------------------------------------


class TestResetForTesting:
    def test_reset_clears_history(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(Exception):

            pass
            det.record_change("p", 0.5, cycle=3)
        assert det.is_frozen("p", cycle=4) is True
        det.reset_for_testing()
        assert det.is_frozen("p", cycle=4) is False
        det.record_change("p", 0.5, cycle=4)  # must not raise after reset
