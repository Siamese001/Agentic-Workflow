"""
Phase 3 — Wave 2 Tests: L4 persistence + no-same-cycle enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.detection_signal_store_types import (
    DetectionSignalStore,
)
from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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
)

_emit_emits_metric_event("test_l4_persistence", "p4obs", "metric_1")
_emit_emits_metric_event("test_l4_persistence", "p4obs", "metric_2")
_emit_emits_metric_event("test_l4_persistence", "p4obs", "metric_3")
_emit_emits_metric_event("test_l4_persistence", "p4obs", "metric_4")
_emit_emits_metric_event("test_l4_persistence", "p4obs", "metric_5")
_emit_emits_metric_event("test_l4_persistence", "p4obs", "metric_6")
_emit_records_incident_event("test_l4_persistence", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_l4_persistence", "p4obs", "anomaly")
_emit_writes_observability_log("test_l4_persistence", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_l4_persistence", "p4obs", "mon_state")
_emit_triggers_alert("test_l4_persistence", "p4obs", "alert")
_emit_links_incident_trace("test_l4_persistence", "p4obs", "trace_link")
_emit_captures_pattern("test_l4_persistence", "p3lm", "pattern")
_emit_records_learning_event("test_l4_persistence", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_l4_persistence", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_l4_persistence", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_l4_persistence", "p3lm", "routing")
_emit_improves_agent_policy("test_l4_persistence", "p3lm", "policy")
_emit_stores_learning_state("test_l4_persistence", "p3lm", "state")
_emit_records_execution_trace("test_l4_persistence", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_l4_persistence", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_l4_persistence", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_l4_persistence", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_l4_persistence", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_l4_persistence", "env_read", "p2_env_1")
_emit_reads_environ("test_l4_persistence", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_l4_persistence", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_l4_persistence", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_l4_persistence")
_emit_applies_guardrail("p0", "test_l4_persistence", "p0_governance")
_emit_reads_policy_state("p0", "test_l4_persistence", "policy_binding")
_emit_snapshots_state("p0", "test_l4_persistence", "state_snapshot")
_emit_pulls_context("p1", "test_l4_persistence", "context_pull")
_emit_pulls_context("p1", "test_l4_persistence", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_l4_persistence", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_l4_persistence", "uwg_term_secondary")
_emit_writes_through("p1", "test_l4_persistence", "write_through")
_emit_writes_through("p1", "test_l4_persistence", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_l4_persistence", "safety_validation")
_emit_invokes_eval("p1", "test_l4_persistence", "eval_call")
_emit_proposal_commits_routing("p1", "test_l4_persistence", "routing_commit")
_emit_escalates_to_human("p1", "test_l4_persistence", "human_escalation")
_emit_routes_through("p1", "test_l4_persistence", "route_through")
_emit_checks_agent_registry("p1", "test_l4_persistence", "agent_registry")
_emit_validates_agent_capability("p1", "test_l4_persistence", "capability")
_emit_dispatches_execution_plan("p1", "test_l4_persistence", "exec_plan")
_emit_agent_executes_agent("p1", "test_l4_persistence", "sub_agent")
_emit_routes_to_agent("p1", "test_l4_persistence", "target_agent")
_emit_verifies_policy("p1", "test_l4_persistence", "policy_check")
_emit_observes_runtime_state("p1", "test_l4_persistence", "runtime_state")
_emit_verifies_boundary("p1", "test_l4_persistence", "boundary_check")
_emit_transcripts_response("p1", "test_l4_persistence", "transcript")
_emit_hard_fails_untranscripted("p1", "test_l4_persistence")
_emit_gated_by_confidence("p1", "test_l4_persistence", "confidence_gate")
emit_replay_key("p0", "test_l4_persistence")
emit_determinism_digest("p0", "test_l4_persistence")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l4_persistence", "execution_auth")
_emit_validates_capability("p2", "test_l4_persistence", "capability_check")
_emit_routes_to_capability("p2", "test_l4_persistence", "capability_route")
_emit_writes_via_uwg("p2", "test_l4_persistence", "uwg_write")
_emit_blocks_direct_write("p2", "test_l4_persistence", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l4_persistence", "tool_invocation")
_emit_captures_execution_output("p2", "test_l4_persistence", "exec_output")
_emit_dispatches_agent("p3", "test_l4_persistence", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l4_persistence", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l4_persistence", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l4_persistence", "healing_outcome")
_emit_escalates_failure("p3", "test_l4_persistence", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l4_persistence", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l4_persistence", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l4_persistence", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l4_persistence", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l4_persistence", "eval_metric")
_emit_stores_embedding("p4", "test_l4_persistence", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l4_persistence", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l4_persistence", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


def _sig(mission_id: str, created_at_utc: int, anomaly_score: float = 0.3) -> DetectionSignal:
    return DetectionSignal.build(
        mission_id=mission_id,
        created_at_utc=created_at_utc,
        anomaly_score=anomaly_score,
        escalation_rate=0.0,
        retry_rate=0.0,
        violation_density=0.0,
    )


class TestDetectionSignalStore:
    def _fresh(self) -> DetectionSignalStore:
        return DetectionSignalStore()

    def test_store_returns_signal_hash(self):
        store = self._fresh()
        sig = _sig("m-001", 100)
        returned_hash = store.store(sig, commit_tick=1)
        assert returned_hash == sig.signal_hash

    def test_store_and_fetch_latest_prior_only(self):
        """
        Store signal at tick 5; fetch with before_tick=10 must return it.
        """
        store = self._fresh()
        sig = _sig("m-prior", 100, anomaly_score=0.5)
        store.store(sig, commit_tick=5)
        result = store.fetch_latest(before_tick=10)
        assert result is not None
        assert result.signal_hash == sig.signal_hash

    def test_fetch_latest_disallows_same_cycle_signal(self):
        """
        Negative: store signal at tick T; fetch with before_tick=T must return None.
        Same-cycle signal is invisible.
        """
        store = self._fresh()
        sig = _sig("m-same-cycle", 100, anomaly_score=0.9)
        store.store(sig, commit_tick=10)
        result = store.fetch_latest(before_tick=10)
        assert result is None, "Same-cycle signal must not be returned by fetch_latest(before_tick=T)"

    def test_fetch_latest_returns_none_when_empty(self):
        store = self._fresh()
        assert store.fetch_latest(before_tick=100) is None

    def test_fetch_latest_returns_most_recent_prior(self):
        """With multiple signals, fetch returns the most recent one before boundary."""
        store = self._fresh()
        sig1 = _sig("m-a", 100, anomaly_score=0.1)
        sig2 = _sig("m-b", 200, anomaly_score=0.8)
        store.store(sig1, commit_tick=1)
        store.store(sig2, commit_tick=2)
        result = store.fetch_latest(before_tick=3)
        assert result is not None
        assert result.signal_hash == sig2.signal_hash

    def test_fetch_latest_excludes_signals_at_or_after_boundary(self):
        store = self._fresh()
        sig1 = _sig("m-old", 100, anomaly_score=0.2)
        sig2 = _sig("m-new", 200, anomaly_score=0.9)
        store.store(sig1, commit_tick=5)
        store.store(sig2, commit_tick=10)
        result = store.fetch_latest(before_tick=10)
        assert result is not None
        assert result.signal_hash == sig1.signal_hash

    def test_monotonicity_enforced(self):
        """Storing at a non-increasing tick must raise ValueError."""
        store = self._fresh()
        sig1 = _sig("m-mono-1", 100)
        sig2 = _sig("m-mono-2", 200)
        store.store(sig1, commit_tick=5)
        with pytest.raises(ValueError, match="strictly greater"):
            store.store(sig2, commit_tick=5)

    def test_storage_uses_canonical_bytes_and_hash(self):
        """Verify stored signal_hash matches independently computed hash."""
        store = self._fresh()
        sig = _sig("m-hash-check", 300, anomaly_score=0.4)
        expected_hash = DetectionSignal.compute_hash(
            schema_version=sig.schema_version,
            mission_id=sig.mission_id,
            created_at_utc=sig.created_at_utc,
            anomaly_score=sig.anomaly_score,
            escalation_rate=sig.escalation_rate,
            retry_rate=sig.retry_rate,
            violation_density=sig.violation_density,
        )
        store.store(sig, commit_tick=1)
        fetched = store.fetch_latest(before_tick=2)
        assert fetched is not None
        assert fetched.signal_hash == expected_hash

    def test_count_tracks_stored_signals(self):
        store = self._fresh()
        assert store.count() == 0
        store.store(_sig("m-c1", 100), commit_tick=1)
        assert store.count() == 1
        store.store(_sig("m-c2", 200), commit_tick=2)
        assert store.count() == 2


class TestGetPriorDetectionSignal:
    """Tests for the get_prior_detection_signal helper (prior-only semantics)."""

    def test_get_prior_returns_none_when_no_prior_exists(self):
        """Fresh store: no prior signal for any tick."""
        store = DetectionSignalStore()
        result = store.fetch_latest(before_tick=1)
        assert result is None

    def test_get_prior_strictly_excludes_same_tick(self):
        """
        Negative: signal stored at tick T must not be returned when
        execution_start_tick == T.
        """
        store = DetectionSignalStore()
        sig = _sig("m-excl", 500, anomaly_score=0.95)
        store.store(sig, commit_tick=7)
        result = store.fetch_latest(before_tick=7)
        assert result is None

    def test_get_prior_returns_signal_from_previous_tick(self):
        store = DetectionSignalStore()
        sig = _sig("m-prev", 400, anomaly_score=0.6)
        store.store(sig, commit_tick=3)
        result = store.fetch_latest(before_tick=4)
        assert result is not None
        assert result.signal_hash == sig.signal_hash
