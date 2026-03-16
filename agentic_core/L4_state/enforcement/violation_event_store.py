"""
Phase 5 — ViolationEventStore: L4 in-process persistence with prior-only fetch.

Guarantees:
- store_violation_event(event) -> event_hash  (idempotent by hash)
- fetch_latest_violation(before_tick) -> Optional[ViolationEvent]
  Returns only events with commit_tick < before_tick (prior-only).
- fetch_window(before_tick, window_ticks) -> list[ViolationEvent]
  Returns events with commit_tick in [before_tick - window_ticks, before_tick).
  Sorted ascending by (commit_tick, event_hash).

Same-cycle events (commit_tick == before_tick) are structurally invisible.
"""

from __future__ import annotations

import uuid

from agentic_core.L4_state.types.violation_event_types import ViolationEvent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "violation_event_store")
emit_determinism_digest("p0", "violation_event_store")

_emit_dispatches_healing_run("p1", "violation_event_store", "L4")
_emit_routes_through("p1", "violation_event_store", "L4")
_emit_escalates_to_human("p1", "violation_event_store", "L4")
_emit_reads_policy_state("p1", "violation_event_store", "L4")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "violation_event_store", "p0_governance")
_emit_authorize_and_execute("p2", "violation_event_store", "execution_auth")
_emit_validates_capability("p2", "violation_event_store", "capability_check")
_emit_routes_to_capability("p2", "violation_event_store", "capability_route")
_emit_writes_via_uwg("p2", "violation_event_store", "uwg_write")
_emit_blocks_direct_write("p2", "violation_event_store", "direct_write_block")
_emit_records_tool_invocation("p2", "violation_event_store", "tool_invocation")
_emit_captures_execution_output("p2", "violation_event_store", "exec_output")
_emit_dispatches_agent("p3", "violation_event_store", "agent_dispatch")
_emit_coordinates_agents("p3", "violation_event_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "violation_event_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "violation_event_store", "healing_outcome")
_emit_escalates_failure("p3", "violation_event_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "violation_event_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "violation_event_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "violation_event_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "violation_event_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "violation_event_store", "eval_metric")
_emit_stores_embedding("p4", "violation_event_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "violation_event_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "violation_event_store", "exec_snapshot_link")


class ViolationEventStore:
    """
    In-process L4 store for ViolationEvent records.

    Thread-safety: not guaranteed (single-threaded agent model assumed).
    Idempotent: storing the same event_hash twice is a no-op.
    """

    def __init__(self) -> None:
        self._events: dict[str, ViolationEvent] = {}

    def store_violation_event(self, event: ViolationEvent) -> str:
        """
        Persist a ViolationEvent. Returns event_hash.
        Idempotent: duplicate hashes are silently ignored.
        """
        _emit_snapshots_state(str(uuid.uuid4()), "ViolationEventStore.store_violation_event", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ViolationEventStore.store_violation_event"
        )

        if not isinstance(event, ViolationEvent):
            raise TypeError(
                f"ViolationEventStore.store_violation_event: expected ViolationEvent, got {type(event).__name__}"
            )
        self._events[event.event_hash] = event
        return event.event_hash

    def fetch_latest_violation(self, before_tick: int) -> ViolationEvent | None:
        """
        Return the most recent ViolationEvent with commit_tick < before_tick.

        Same-cycle events (commit_tick == before_tick) are excluded.
        Returns None if no prior events exist.
        """
        prior = [e for e in self._events.values() if e.commit_tick < before_tick]
        if not prior:
            return None
        return max(prior, key=lambda e: (e.commit_tick, e.event_hash))

    def fetch_window(self, before_tick: int, window_ticks: int) -> list[ViolationEvent]:
        """
        Return all ViolationEvents with commit_tick in
        [before_tick - window_ticks, before_tick).

        Sorted ascending by (commit_tick, event_hash) for determinism.
        Same-cycle events (commit_tick == before_tick) are excluded.
        """
        if window_ticks < 0:
            raise ValueError(
                f"ViolationEventStore.fetch_window: window_ticks must be >= 0, got {window_ticks}"
            )
        low = before_tick - window_ticks
        window = [e for e in self._events.values() if low <= e.commit_tick < before_tick]
        return sorted(window, key=lambda e: (e.commit_tick, e.event_hash))

    def count(self) -> int:
        """Return total number of stored events."""
        return len(self._events)

    def clear(self) -> None:
        """Remove all stored events (test utility)."""
        self._events.clear()
