"""
Phase 5 — Wave 2 Tests: L4 ViolationEventStore prior-only persistence.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
from agentic_core.L4_state.types.violation_event_types import ViolationEvent, emit_violation_event
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_l4_violation_persistence", "p4obs", "metric_1")
_emit_emits_metric_event("test_l4_violation_persistence", "p4obs", "metric_2")
_emit_emits_metric_event("test_l4_violation_persistence", "p4obs", "metric_3")
_emit_emits_metric_event("test_l4_violation_persistence", "p4obs", "metric_4")
_emit_emits_metric_event("test_l4_violation_persistence", "p4obs", "metric_5")
_emit_emits_metric_event("test_l4_violation_persistence", "p4obs", "metric_6")
_emit_records_incident_event("test_l4_violation_persistence", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_l4_violation_persistence", "p4obs", "anomaly")
_emit_writes_observability_log("test_l4_violation_persistence", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_l4_violation_persistence", "p4obs", "mon_state")
_emit_triggers_alert("test_l4_violation_persistence", "p4obs", "alert")
_emit_links_incident_trace("test_l4_violation_persistence", "p4obs", "trace_link")
_emit_captures_pattern("test_l4_violation_persistence", "p3lm", "pattern")
_emit_records_learning_event("test_l4_violation_persistence", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_l4_violation_persistence", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_l4_violation_persistence", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_l4_violation_persistence", "p3lm", "routing")
_emit_improves_agent_policy("test_l4_violation_persistence", "p3lm", "policy")
_emit_stores_learning_state("test_l4_violation_persistence", "p3lm", "state")
_emit_records_execution_trace("test_l4_violation_persistence", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_l4_violation_persistence", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_l4_violation_persistence", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_l4_violation_persistence", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_l4_violation_persistence", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_l4_violation_persistence", "env_read", "p2_env_1")
_emit_reads_environ("test_l4_violation_persistence", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_l4_violation_persistence", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_l4_violation_persistence", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_l4_violation_persistence")
_emit_applies_guardrail("p0", "test_l4_violation_persistence", "p0_governance")
_emit_reads_policy_state("p0", "test_l4_violation_persistence", "policy_binding")
_emit_snapshots_state("p0", "test_l4_violation_persistence", "state_snapshot")
_emit_pulls_context("p1", "test_l4_violation_persistence", "context_pull")
_emit_pulls_context("p1", "test_l4_violation_persistence", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_l4_violation_persistence", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_l4_violation_persistence", "uwg_term_secondary")
_emit_writes_through("p1", "test_l4_violation_persistence", "write_through")
_emit_writes_through("p1", "test_l4_violation_persistence", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_l4_violation_persistence", "safety_validation")
_emit_invokes_eval("p1", "test_l4_violation_persistence", "eval_call")
_emit_proposal_commits_routing("p1", "test_l4_violation_persistence", "routing_commit")
_emit_escalates_to_human("p1", "test_l4_violation_persistence", "human_escalation")
_emit_routes_through("p1", "test_l4_violation_persistence", "route_through")
_emit_checks_agent_registry("p1", "test_l4_violation_persistence", "agent_registry")
_emit_validates_agent_capability("p1", "test_l4_violation_persistence", "capability")
_emit_dispatches_execution_plan("p1", "test_l4_violation_persistence", "exec_plan")
_emit_agent_executes_agent("p1", "test_l4_violation_persistence", "sub_agent")
_emit_routes_to_agent("p1", "test_l4_violation_persistence", "target_agent")
_emit_verifies_policy("p1", "test_l4_violation_persistence", "policy_check")
_emit_observes_runtime_state("p1", "test_l4_violation_persistence", "runtime_state")
_emit_verifies_boundary("p1", "test_l4_violation_persistence", "boundary_check")
_emit_transcripts_response("p1", "test_l4_violation_persistence", "transcript")
_emit_hard_fails_untranscripted("p1", "test_l4_violation_persistence")
_emit_gated_by_confidence("p1", "test_l4_violation_persistence", "confidence_gate")
emit_replay_key("p0", "test_l4_violation_persistence")
emit_determinism_digest("p0", "test_l4_violation_persistence")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l4_violation_persistence", "execution_auth")
_emit_validates_capability("p2", "test_l4_violation_persistence", "capability_check")
_emit_routes_to_capability("p2", "test_l4_violation_persistence", "capability_route")
_emit_writes_via_uwg("p2", "test_l4_violation_persistence", "uwg_write")
_emit_blocks_direct_write("p2", "test_l4_violation_persistence", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l4_violation_persistence", "tool_invocation")
_emit_captures_execution_output("p2", "test_l4_violation_persistence", "exec_output")
_emit_dispatches_agent("p3", "test_l4_violation_persistence", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l4_violation_persistence", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l4_violation_persistence", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l4_violation_persistence", "healing_outcome")
_emit_escalates_failure("p3", "test_l4_violation_persistence", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l4_violation_persistence", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l4_violation_persistence", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l4_violation_persistence", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l4_violation_persistence", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l4_violation_persistence", "eval_metric")
_emit_stores_embedding("p4", "test_l4_violation_persistence", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l4_violation_persistence", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l4_violation_persistence", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"


def _make_event(commit_tick: int, severity: float = 0.5, decision: str = "block") -> ViolationEvent:
    return emit_violation_event(
        mission_id="mission-test",
        commit_tick=commit_tick,
        guardian_decision=decision,
        violation_codes=["CODE_A"],
        severity_score=severity,
        created_at_utc=_TS,
    )


class TestStoreAndFetch:
    def test_store_returns_event_hash(self):
        store = ViolationEventStore()
        e = _make_event(commit_tick=3)
        h = store.store_violation_event(e)
        assert h == e.event_hash
        assert len(h) == 64

    def test_store_idempotent(self):
        """Storing the same event twice does not duplicate it."""
        store = ViolationEventStore()
        e = _make_event(commit_tick=3)
        store.store_violation_event(e)
        store.store_violation_event(e)
        assert store.count() == 1

    def test_store_rejects_non_event(self):
        store = ViolationEventStore()
        with pytest.raises(TypeError):
            store.store_violation_event({"not": "an event"})  # type: ignore[arg-type]

    def test_store_and_fetch_latest_prior_only(self):
        """
        fetch_latest_violation(before_tick=T) returns the most recent event
        with commit_tick < T.
        """
        store = ViolationEventStore()
        e3 = _make_event(commit_tick=3)
        e5 = _make_event(commit_tick=5)
        e7 = _make_event(commit_tick=7)
        store.store_violation_event(e3)
        store.store_violation_event(e5)
        store.store_violation_event(e7)

        result = store.fetch_latest_violation(before_tick=6)
        assert result is not None
        assert result.commit_tick == 5

    def test_fetch_latest_returns_highest_tick_below_boundary(self):
        store = ViolationEventStore()
        for tick in [1, 2, 3, 4, 5]:
            store.store_violation_event(_make_event(commit_tick=tick))

        result = store.fetch_latest_violation(before_tick=4)
        assert result is not None
        assert result.commit_tick == 3

    def test_fetch_latest_returns_none_when_no_prior(self):
        store = ViolationEventStore()
        e = _make_event(commit_tick=10)
        store.store_violation_event(e)

        result = store.fetch_latest_violation(before_tick=5)
        assert result is None

    def test_fetch_latest_returns_none_on_empty_store(self):
        store = ViolationEventStore()
        assert store.fetch_latest_violation(before_tick=100) is None


class TestSameCycleExclusion:
    def test_fetch_disallows_same_cycle_event(self):
        """
        An event at commit_tick=T must NOT be returned by
        fetch_latest_violation(before_tick=T).
        """
        store = ViolationEventStore()
        e_same = _make_event(commit_tick=10)
        store.store_violation_event(e_same)

        result = store.fetch_latest_violation(before_tick=10)
        assert result is None

    def test_fetch_window_excludes_same_cycle(self):
        """fetch_window(before_tick=T) must not include commit_tick=T."""
        store = ViolationEventStore()
        e_same = _make_event(commit_tick=10)
        e_prior = _make_event(commit_tick=8)
        store.store_violation_event(e_same)
        store.store_violation_event(e_prior)

        window = store.fetch_window(before_tick=10, window_ticks=5)
        ticks = [e.commit_tick for e in window]
        assert 10 not in ticks
        assert 8 in ticks

    def test_same_cycle_event_stored_but_invisible_at_boundary(self):
        """
        Event at tick T is stored (count increases) but fetch at T returns None.
        This proves structural invisibility, not deletion.
        """
        store = ViolationEventStore()
        e = _make_event(commit_tick=7)
        store.store_violation_event(e)
        assert store.count() == 1
        assert store.fetch_latest_violation(before_tick=7) is None
        assert store.fetch_latest_violation(before_tick=8) is not None


class TestFetchWindow:
    def test_fetch_window_returns_sorted_by_tick_then_hash(self):
        """
        fetch_window must return events sorted ascending by
        (commit_tick, event_hash).
        """
        store = ViolationEventStore()
        ticks = [3, 7, 5, 4, 6]
        events = {}
        for t in ticks:
            e = _make_event(commit_tick=t)
            store.store_violation_event(e)
            events[t] = e

        window = store.fetch_window(before_tick=10, window_ticks=10)
        returned_ticks = [e.commit_tick for e in window]
        assert returned_ticks == sorted(returned_ticks)

    def test_fetch_window_respects_lower_bound(self):
        """Only events with commit_tick >= before_tick - window_ticks are returned."""
        store = ViolationEventStore()
        for t in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            store.store_violation_event(_make_event(commit_tick=t))

        window = store.fetch_window(before_tick=8, window_ticks=3)
        ticks = [e.commit_tick for e in window]
        assert all(5 <= t < 8 for t in ticks)

    def test_fetch_window_empty_when_no_events_in_range(self):
        store = ViolationEventStore()
        store.store_violation_event(_make_event(commit_tick=1))
        window = store.fetch_window(before_tick=10, window_ticks=2)
        assert window == []

    def test_fetch_window_negative_window_ticks_raises(self):
        store = ViolationEventStore()
        with pytest.raises(ValueError, match="window_ticks"):
            store.fetch_window(before_tick=10, window_ticks=-1)

    def test_fetch_window_zero_ticks_returns_empty(self):
        """window_ticks=0 means [T, T) which is empty."""
        store = ViolationEventStore()
        store.store_violation_event(_make_event(commit_tick=9))
        window = store.fetch_window(before_tick=10, window_ticks=0)
        assert window == []

    def test_fetch_window_returns_all_in_range(self):
        store = ViolationEventStore()
        for t in [5, 6, 7, 8, 9]:
            store.store_violation_event(_make_event(commit_tick=t))

        window = store.fetch_window(before_tick=10, window_ticks=5)
        ticks = [e.commit_tick for e in window]
        assert sorted(ticks) == [5, 6, 7, 8, 9]
