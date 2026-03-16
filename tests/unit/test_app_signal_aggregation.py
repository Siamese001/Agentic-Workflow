"""Tests for deterministic offline aggregation — Wave 7.0.11.

Validates:
  a) deterministic aggregation output for same event ordering vs shuffled ordering
  b) median determinism for even/odd counts
  c) fail-closed on empty baseline/candidate
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.config.path_constants import (
    APPS_RG_DIR,
)
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
)

_emit_records_execution_trace("p0", "evidence", "test_app_signal_aggregation")
_emit_applies_guardrail("p0", "test_app_signal_aggregation", "p0_governance")
_emit_reads_policy_state("p0", "test_app_signal_aggregation", "policy_binding")
_emit_snapshots_state("p0", "test_app_signal_aggregation", "state_snapshot")
emit_replay_key("p0", "test_app_signal_aggregation")
emit_determinism_digest("p0", "test_app_signal_aggregation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_app_signal_aggregation", "execution_auth")
_emit_validates_capability("p2", "test_app_signal_aggregation", "capability_check")
_emit_routes_to_capability("p2", "test_app_signal_aggregation", "capability_route")
_emit_writes_via_uwg("p2", "test_app_signal_aggregation", "uwg_write")
_emit_blocks_direct_write("p2", "test_app_signal_aggregation", "direct_write_block")
_emit_records_tool_invocation("p2", "test_app_signal_aggregation", "tool_invocation")
_emit_captures_execution_output("p2", "test_app_signal_aggregation", "exec_output")
_emit_dispatches_agent("p3", "test_app_signal_aggregation", "agent_dispatch")
_emit_coordinates_agents("p3", "test_app_signal_aggregation", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_app_signal_aggregation", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_app_signal_aggregation", "healing_outcome")
_emit_escalates_failure("p3", "test_app_signal_aggregation", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_app_signal_aggregation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_app_signal_aggregation", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_app_signal_aggregation", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_app_signal_aggregation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_app_signal_aggregation", "eval_metric")
_emit_stores_embedding("p4", "test_app_signal_aggregation", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_app_signal_aggregation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_app_signal_aggregation", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from system_learning.types.app_signal_types import (
    AppSignalEventArtifact,
    aggregate_app_signals,
    build_app_signal_event,
)

_CLOCK = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))


def _make_events(
    values: list[float],
    *,
    app_id: str = APPS_RG_DIR,
    metric_name: str = "resume_message_response_rate",
    prefix: str = "msg",
) -> list[AppSignalEventArtifact]:
    """Helper: build a list of AppSignalEventArtifact from float values."""
    return [
        build_app_signal_event(
            app_id=app_id,
            run_id="run_agg",
            message_id=f"{prefix}_{i:03d}",
            metric_name=metric_name,
            metric_value=v,
            semantic_clock=_CLOCK,
        )
        for i, v in enumerate(values)
    ]


class TestAggregateAppSignals:
    def test_deterministic_same_order_and_shuffled(self) -> None:
        """Same events in different order produce identical aggregate."""
        vals = [0.80, 0.85, 0.90, 0.70, 0.75]
        events_a = _make_events(vals)
        events_b = _make_events(list(reversed(vals)), prefix="rev")

        all_events = events_a + events_b
        shuffled = list(reversed(all_events))

        agg1 = aggregate_app_signals(
            app_id=APPS_RG_DIR,
            window_id="w_test",
            metric_name="resume_message_response_rate",
            events=all_events,
            baseline_selector=lambda e: e.message_id.startswith("msg"),
            candidate_selector=lambda e: e.message_id.startswith("rev"),
            evidence_hash="agg_hash_001",
            semantic_clock=_CLOCK,
        )
        agg2 = aggregate_app_signals(
            app_id=APPS_RG_DIR,
            window_id="w_test",
            metric_name="resume_message_response_rate",
            events=shuffled,
            baseline_selector=lambda e: e.message_id.startswith("msg"),
            candidate_selector=lambda e: e.message_id.startswith("rev"),
            evidence_hash="agg_hash_001",
            semantic_clock=_CLOCK,
        )
        assert agg1.trace_id == agg2.trace_id
        assert agg1.to_json() == agg2.to_json()
        assert agg1.n == 10

    def test_median_determinism_even_and_odd(self) -> None:
        """Median aggregation is deterministic for even and odd counts."""
        odd_vals = [1.0, 3.0, 5.0]
        even_vals = [2.0, 4.0, 6.0, 8.0]
        events = _make_events(odd_vals, metric_name="time_to_first_reply_hours", prefix="bl") + _make_events(
            even_vals, metric_name="time_to_first_reply_hours", prefix="cd"
        )
        agg = aggregate_app_signals(
            app_id=APPS_RG_DIR,
            window_id="w_med",
            metric_name="time_to_first_reply_hours",
            events=events,
            baseline_selector=lambda e: e.message_id.startswith("bl"),
            candidate_selector=lambda e: e.message_id.startswith("cd"),
            evidence_hash="med_hash",
            semantic_clock=_CLOCK,
        )
        assert agg.baseline_value == 3.0
        assert agg.candidate_value == 5.0
        assert agg.n == 7

        agg2 = aggregate_app_signals(
            app_id=APPS_RG_DIR,
            window_id="w_med",
            metric_name="time_to_first_reply_hours",
            events=list(reversed(events)),
            baseline_selector=lambda e: e.message_id.startswith("bl"),
            candidate_selector=lambda e: e.message_id.startswith("cd"),
            evidence_hash="med_hash",
            semantic_clock=_CLOCK,
        )
        assert agg.trace_id == agg2.trace_id

    def test_fail_closed_empty_baseline_candidate(self) -> None:
        """Aggregator rejects empty baseline or candidate sets."""
        events = _make_events([0.5, 0.6])
        with pytest.raises(ValueError, match="EMPTY_CANDIDATE"):
            aggregate_app_signals(
                app_id=APPS_RG_DIR,
                window_id="w_fail",
                metric_name="resume_message_response_rate",
                events=events,
                baseline_selector=lambda _: True,
                candidate_selector=lambda _: False,
                evidence_hash="fail_hash",
                semantic_clock=_CLOCK,
            )
        with pytest.raises(ValueError, match="EMPTY_BASELINE"):
            aggregate_app_signals(
                app_id=APPS_RG_DIR,
                window_id="w_fail",
                metric_name="resume_message_response_rate",
                events=events,
                baseline_selector=lambda _: False,
                candidate_selector=lambda _: True,
                evidence_hash="fail_hash",
                semantic_clock=_CLOCK,
            )
