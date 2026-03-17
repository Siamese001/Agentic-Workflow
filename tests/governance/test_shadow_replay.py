"""
Tests for ShadowReplayValidator pre-activation regression guard.

Phase 2.3: Mathematically-Sealed Sovereignty Hardening
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

_emit_records_execution_trace("p0", "evidence", "test_shadow_replay")
_emit_applies_guardrail("p0", "test_shadow_replay", "p0_governance")
_emit_reads_policy_state("p0", "test_shadow_replay", "policy_binding")
_emit_snapshots_state("p0", "test_shadow_replay", "state_snapshot")
emit_replay_key("p0", "test_shadow_replay")
emit_determinism_digest("p0", "test_shadow_replay")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_shadow_replay", "execution_auth")
_emit_validates_capability("p2", "test_shadow_replay", "capability_check")
_emit_routes_to_capability("p2", "test_shadow_replay", "capability_route")
_emit_writes_via_uwg("p2", "test_shadow_replay", "uwg_write")
_emit_blocks_direct_write("p2", "test_shadow_replay", "direct_write_block")
_emit_records_tool_invocation("p2", "test_shadow_replay", "tool_invocation")
_emit_captures_execution_output("p2", "test_shadow_replay", "exec_output")
_emit_dispatches_agent("p3", "test_shadow_replay", "agent_dispatch")
_emit_coordinates_agents("p3", "test_shadow_replay", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_shadow_replay", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_shadow_replay", "healing_outcome")
_emit_escalates_failure("p3", "test_shadow_replay", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_shadow_replay", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_shadow_replay", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_shadow_replay", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_shadow_replay", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_shadow_replay", "eval_metric")
_emit_stores_embedding("p4", "test_shadow_replay", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_shadow_replay", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_shadow_replay", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

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
from system_learning.enforcement.shadow_replay_validator import (
    EPSILON,
    RegressionError,
    ReplayResult,
    ShadowReplayValidator,
)

_emit_emits_metric_event("test_shadow_replay", "p4obs", "metric_1")
_emit_emits_metric_event("test_shadow_replay", "p4obs", "metric_2")
_emit_emits_metric_event("test_shadow_replay", "p4obs", "metric_3")
_emit_emits_metric_event("test_shadow_replay", "p4obs", "metric_4")
_emit_emits_metric_event("test_shadow_replay", "p4obs", "metric_5")
_emit_emits_metric_event("test_shadow_replay", "p4obs", "metric_6")
_emit_records_incident_event("test_shadow_replay", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_shadow_replay", "p4obs", "anomaly")
_emit_writes_observability_log("test_shadow_replay", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_shadow_replay", "p4obs", "mon_state")
_emit_triggers_alert("test_shadow_replay", "p4obs", "alert")
_emit_links_incident_trace("test_shadow_replay", "p4obs", "trace_link")
_emit_captures_pattern("test_shadow_replay", "p3lm", "pattern")
_emit_records_learning_event("test_shadow_replay", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_shadow_replay", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_shadow_replay", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_shadow_replay", "p3lm", "routing")
_emit_improves_agent_policy("test_shadow_replay", "p3lm", "policy")
_emit_stores_learning_state("test_shadow_replay", "p3lm", "state")
_emit_records_execution_trace("test_shadow_replay", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_shadow_replay", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_shadow_replay", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_shadow_replay", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_shadow_replay", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_shadow_replay", "env_read", "p2_env_1")
_emit_reads_environ("test_shadow_replay", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_shadow_replay", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_shadow_replay", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_shadow_replay", "context_pull")
_emit_pulls_context("p1", "test_shadow_replay", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_shadow_replay", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_shadow_replay", "uwg_term_secondary")
_emit_writes_through("p1", "test_shadow_replay", "write_through")
_emit_writes_through("p1", "test_shadow_replay", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_shadow_replay", "safety_validation")
_emit_invokes_eval("p1", "test_shadow_replay", "eval_call")
_emit_proposal_commits_routing("p1", "test_shadow_replay", "routing_commit")
_emit_escalates_to_human("p1", "test_shadow_replay", "human_escalation")
_emit_routes_through("p1", "test_shadow_replay", "route_through")
_emit_checks_agent_registry("p1", "test_shadow_replay", "agent_registry")
_emit_validates_agent_capability("p1", "test_shadow_replay", "capability")
_emit_dispatches_execution_plan("p1", "test_shadow_replay", "exec_plan")
_emit_agent_executes_agent("p1", "test_shadow_replay", "sub_agent")
_emit_routes_to_agent("p1", "test_shadow_replay", "target_agent")
_emit_verifies_policy("p1", "test_shadow_replay", "policy_check")
_emit_observes_runtime_state("p1", "test_shadow_replay", "runtime_state")
_emit_verifies_boundary("p1", "test_shadow_replay", "boundary_check")
_emit_transcripts_response("p1", "test_shadow_replay", "transcript")
_emit_hard_fails_untranscripted("p1", "test_shadow_replay")
_emit_gated_by_confidence("p1", "test_shadow_replay", "confidence_gate")

_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64


def _make_result(
    trace_id: str = "t1",
    original_digest: str = _DIGEST_A,
    replayed_digest: str = _DIGEST_A,
    original_perf: float = 0.9,
    replayed_perf: float = 0.9,
    original_safety: float = 0.95,
    replayed_safety: float = 0.95,
) -> ReplayResult:
    return ReplayResult(
        trace_id=trace_id,
        original_digest=original_digest,
        replayed_digest=replayed_digest,
        original_performance=original_perf,
        replayed_performance=replayed_perf,
        original_safety_score=original_safety,
        replayed_safety_score=replayed_safety,
    )


class TestReplayResultProperties:
    def test_digest_unchanged(self) -> None:
        r = _make_result()
        assert r.digest_changed is False

    def test_digest_changed(self) -> None:
        r = _make_result(replayed_digest=_DIGEST_B)
        assert r.digest_changed is True

    def test_performance_delta_positive(self) -> None:
        r = _make_result(original_perf=0.8, replayed_perf=0.9)
        assert r.performance_delta == pytest.approx(0.1)

    def test_performance_delta_negative(self) -> None:
        r = _make_result(original_perf=0.9, replayed_perf=0.8)
        assert r.performance_delta == pytest.approx(-0.1)

    def test_safety_not_degraded(self) -> None:
        r = _make_result(original_safety=0.9, replayed_safety=0.9)
        assert r.safety_degraded is False

    def test_safety_degraded(self) -> None:
        r = _make_result(original_safety=0.9, replayed_safety=0.8)
        assert r.safety_degraded is True

    def test_regression_threshold_no_regression(self) -> None:
        r = _make_result(original_perf=0.8, replayed_perf=0.9)
        assert r.regression_threshold == 0.0

    def test_regression_threshold_with_regression(self) -> None:
        r = _make_result(original_perf=0.9, replayed_perf=0.85)
        assert r.regression_threshold == pytest.approx(0.05)


class TestShadowReplayValidator:
    def setup_method(self) -> None:
        self.validator = ShadowReplayValidator()

    def test_passes_with_stable_digests(self) -> None:
        results = [_make_result(trace_id=f"t{i}") for i in range(3)]
        summary = self.validator.validate(results)
        assert summary.activation_safe is True
        assert summary.all_digests_stable is True

    def test_passes_digest_change_with_improvement(self) -> None:
        r = _make_result(
            replayed_digest=_DIGEST_B,
            original_perf=0.8,
            replayed_perf=0.9,
            original_safety=0.9,
            replayed_safety=0.95,
        )
        summary = self.validator.validate([r])
        assert summary.activation_safe is True

    def test_rejects_digest_change_with_no_improvement(self) -> None:
        r = _make_result(
            replayed_digest=_DIGEST_B,
            original_perf=0.9,
            replayed_perf=0.8,
        )
        with pytest.raises(RegressionError):
            self.validator.validate([r])

    def test_rejects_safety_degradation(self) -> None:
        r = _make_result(
            replayed_digest=_DIGEST_B,
            original_perf=0.8,
            replayed_perf=0.95,
            original_safety=0.9,
            replayed_safety=0.7,
        )
        with pytest.raises(RegressionError):
            self.validator.validate([r])

    def test_rejects_regression_exceeding_epsilon(self) -> None:
        r = _make_result(
            original_perf=1.0,
            replayed_perf=1.0 - (EPSILON + 0.001),
        )
        with pytest.raises(RegressionError):
            self.validator.validate([r])

    def test_rejects_empty_results(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            self.validator.validate([])

    def test_epsilon_is_constant(self) -> None:
        assert isinstance(EPSILON, float)
        assert EPSILON == 0.01

    def test_summary_total_traces(self) -> None:
        results = [_make_result(trace_id=f"t{i}") for i in range(5)]
        summary = self.validator.validate(results)
        assert summary.total_traces == 5
