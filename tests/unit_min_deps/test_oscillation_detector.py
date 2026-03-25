"""Unit tests for system_learning.validators.oscillation_detector."""

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

# REMOVED: _emit_authorize_and_execute("p2", "test_oscillation_detector", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_oscillation_detector", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_oscillation_detector", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_oscillation_detector", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_oscillation_detector", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_oscillation_detector", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_oscillation_detector", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_oscillation_detector", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_oscillation_detector", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_oscillation_detector", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_oscillation_detector", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_oscillation_detector", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_oscillation_detector", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_oscillation_detector", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_oscillation_detector", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_oscillation_detector", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_oscillation_detector", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_oscillation_detector", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_oscillation_detector", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_oscillation_detector", "exec_snapshot_link")
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
from system_learning.validators.oscillation_detector import (
    OscillationPolicy,
    compute_freeze_decision,
    detect_oscillation,
)

# REMOVED: _emit_emits_metric_event("test_oscillation_detector", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_oscillation_detector", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_oscillation_detector", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_oscillation_detector", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_oscillation_detector", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_oscillation_detector", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_oscillation_detector", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_oscillation_detector", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_oscillation_detector", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_oscillation_detector", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_oscillation_detector", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_oscillation_detector", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_oscillation_detector", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_oscillation_detector", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_oscillation_detector", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_oscillation_detector", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_oscillation_detector", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_oscillation_detector", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_oscillation_detector", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_oscillation_detector", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_oscillation_detector")
# REMOVED: _emit_applies_guardrail("p0", "test_oscillation_detector", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_oscillation_detector", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_oscillation_detector", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_oscillation_detector", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_oscillation_detector", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_oscillation_detector", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_oscillation_detector", "write_through")
# REMOVED: _emit_writes_through("p1", "test_oscillation_detector", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_oscillation_detector", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_oscillation_detector", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_oscillation_detector", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_oscillation_detector", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_oscillation_detector", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_oscillation_detector", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_oscillation_detector", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_oscillation_detector", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_oscillation_detector", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_oscillation_detector", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_oscillation_detector", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_oscillation_detector", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_oscillation_detector", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_oscillation_detector", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_oscillation_detector")
# REMOVED: _emit_gated_by_confidence("p1", "test_oscillation_detector", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_oscillation_detector")
# REMOVED: emit_determinism_digest("p0", "test_oscillation_detector")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
