"""Unit tests for system_learning.validators.oscillation_detector."""

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

_emit_authorize_and_execute("p2", "test_oscillation_detector", "execution_auth")
_emit_validates_capability("p2", "test_oscillation_detector", "capability_check")
_emit_routes_to_capability("p2", "test_oscillation_detector", "capability_route")
_emit_writes_via_uwg("p2", "test_oscillation_detector", "uwg_write")
_emit_blocks_direct_write("p2", "test_oscillation_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_oscillation_detector", "tool_invocation")
_emit_captures_execution_output("p2", "test_oscillation_detector", "exec_output")
_emit_dispatches_agent("p3", "test_oscillation_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_oscillation_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_oscillation_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_oscillation_detector", "healing_outcome")
_emit_escalates_failure("p3", "test_oscillation_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_oscillation_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_oscillation_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_oscillation_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_oscillation_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_oscillation_detector", "eval_metric")
_emit_stores_embedding("p4", "test_oscillation_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_oscillation_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_oscillation_detector", "exec_snapshot_link")
from system_learning.validators.oscillation_detector import (
    OscillationPolicy,
    compute_freeze_decision,
    detect_oscillation,
)

_emit_records_execution_trace("p0", "evidence", "test_oscillation_detector")
_emit_applies_guardrail("p0", "test_oscillation_detector", "p0_governance")
_emit_snapshots_state("p0", "test_oscillation_detector", "state_snapshot")
emit_replay_key("p0", "test_oscillation_detector")
emit_determinism_digest("p0", "test_oscillation_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestDetectOscillation:
    def test_oscillation_true_pattern(self):
        """Alternating values detected as oscillation."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.85, 0.8, 0.85, 0.8)
        assert detect_oscillation(values, policy) is True

    def test_oscillation_true_pattern_reverse(self):
        """Alternating values (reverse) detected as oscillation."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.85, 0.8, 0.85, 0.8, 0.85)
        assert detect_oscillation(values, policy) is True

    def test_non_oscillation_pattern(self):
        """Monotonic increasing values not detected as oscillation."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.81, 0.82, 0.83, 0.84)
        assert detect_oscillation(values, policy) is False

    def test_non_oscillation_all_same(self):
        """All same values not detected as oscillation."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.8, 0.8, 0.8, 0.8)
        assert detect_oscillation(values, policy) is False

    def test_insufficient_data(self):
        """Insufficient data returns False."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.85, 0.8)
        assert detect_oscillation(values, policy) is False

    def test_oscillation_with_epsilon_tolerance(self):
        """Values within epsilon tolerance detected as oscillation."""
        policy = OscillationPolicy(window=5, epsilon=0.02, freeze_seconds=3600)
        # 0.8 and 0.801 are within epsilon, 0.85 and 0.851 are within epsilon
        values = (0.8, 0.851, 0.801, 0.85, 0.8)
        assert detect_oscillation(values, policy) is True

    def test_non_oscillation_three_values(self):
        """Three distinct values not detected as oscillation."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.85, 0.9, 0.8, 0.85)
        assert detect_oscillation(values, policy) is False


class TestComputeFreezeDecision:
    def test_freeze_decision_on_oscillation(self):
        """Oscillation triggers freeze decision."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.85, 0.8, 0.85, 0.8)
        last_update_utc = 1700000000
        now_utc = 1700003600

        decision = compute_freeze_decision(values, last_update_utc, now_utc, policy)

        assert decision.should_freeze is True
        assert decision.freeze_until_utc == now_utc + policy.freeze_seconds

    def test_no_freeze_on_non_oscillation(self):
        """Non-oscillation does not trigger freeze."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.81, 0.82, 0.83, 0.84)
        last_update_utc = 1700000000
        now_utc = 1700003600

        decision = compute_freeze_decision(values, last_update_utc, now_utc, policy)

        assert decision.should_freeze is False
        assert decision.freeze_until_utc is None

    def test_freeze_until_utc_computation(self):
        """freeze_until_utc correctly computed."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=7200)
        values = (0.8, 0.85, 0.8, 0.85, 0.8)
        last_update_utc = 1700000000
        now_utc = 1700010000

        decision = compute_freeze_decision(values, last_update_utc, now_utc, policy)

        expected_freeze_until = 1700010000 + 7200
        assert decision.freeze_until_utc == expected_freeze_until

    def test_freeze_decision_deterministic(self):
        """compute_freeze_decision is deterministic."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.85, 0.8, 0.85, 0.8)
        last_update_utc = 1700000000
        now_utc = 1700003600

        decision1 = compute_freeze_decision(values, last_update_utc, now_utc, policy)
        decision2 = compute_freeze_decision(values, last_update_utc, now_utc, policy)
        decision3 = compute_freeze_decision(values, last_update_utc, now_utc, policy)

        assert decision1 == decision2 == decision3


class TestDeterminism:
    def test_detect_oscillation_deterministic(self):
        """detect_oscillation produces consistent results."""
        policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
        values = (0.8, 0.85, 0.8, 0.85, 0.8)

        result1 = detect_oscillation(values, policy)
        result2 = detect_oscillation(values, policy)
        result3 = detect_oscillation(values, policy)

        assert result1 == result2 == result3 is True
