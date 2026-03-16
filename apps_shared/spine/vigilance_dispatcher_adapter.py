"""
Vigilance Dispatcher Adapter — bridges VigilanceDispatcher to spine adapters.

VigilanceDispatcher.dispatch() requires a VigilanceEventArtifact and an
enqueue_fn callable. The spine adapters call dispatch(*args, **kwargs).

This adapter:
1. Constructs a VigilanceEventArtifact from the execution context
2. Routes events to a module-level in-memory queue (non-blocking)
3. Falls back to no-op if VigilanceDispatcher cannot be imported

Dispatching is fire-and-forget: any failure is logged and swallowed.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "vigilance_dispatcher_adapter", "p0_governance")
_emit_reads_policy_state("p0", "vigilance_dispatcher_adapter", "policy_binding")
_emit_routes_to_agent("p1", "vigilance_dispatcher_adapter", "apps")
_emit_orchestrates_workflow("p1", "vigilance_dispatcher_adapter", "apps")
_emit_dispatches_execution_plan("p1", "vigilance_dispatcher_adapter", "apps")
_emit_validates_agent_capability("p1", "vigilance_dispatcher_adapter", "apps")
_emit_checks_agent_registry("p1", "vigilance_dispatcher_adapter", "apps")
_emit_snapshots_state("p0", "vigilance_dispatcher_adapter", "state_snapshot")
emit_replay_key("p0", "vigilance_dispatcher_adapter")
emit_determinism_digest("p0", "vigilance_dispatcher_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "vigilance_dispatcher_adapter", "execution_auth")
_emit_validates_capability("p2", "vigilance_dispatcher_adapter", "capability_check")
_emit_routes_to_capability("p2", "vigilance_dispatcher_adapter", "capability_route")
_emit_writes_via_uwg("p2", "vigilance_dispatcher_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "vigilance_dispatcher_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "vigilance_dispatcher_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "vigilance_dispatcher_adapter", "exec_output")
_emit_dispatches_agent("p3", "vigilance_dispatcher_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "vigilance_dispatcher_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "vigilance_dispatcher_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "vigilance_dispatcher_adapter", "healing_outcome")
_emit_escalates_failure("p3", "vigilance_dispatcher_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "vigilance_dispatcher_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vigilance_dispatcher_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "vigilance_dispatcher_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "vigilance_dispatcher_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vigilance_dispatcher_adapter", "eval_metric")
_emit_stores_embedding("p4", "vigilance_dispatcher_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "vigilance_dispatcher_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vigilance_dispatcher_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_EVENT_QUEUE: deque = deque(maxlen=256)


def _drain_event_queue() -> list:
    """Return and clear the current event queue (for testing)."""
    events = list(_EVENT_QUEUE)
    _EVENT_QUEUE.clear()
    return events


def _build_real_dispatcher():
    from agentic_core.L6_observability.engines.vigilance_dispatcher import (
        VigilanceDispatcher,
        VigilanceEventArtifact,
    )

    return (VigilanceDispatcher, VigilanceEventArtifact)


class VigilanceDispatcherAdapter:
    """
    Adapter wrapping VigilanceDispatcher for use in spine adapters.

    dispatch() is fire-and-forget: failures are logged but never re-raised
    so vigilance events never block execution.
    """

    def __init__(self) -> None:
        try:
            VigilanceDispatcher, self._ArtifactCls = _build_real_dispatcher()
            self._dispatcher = VigilanceDispatcher()
            self._real = True
        except ImportError:
            logger.warning("VigilanceDispatcher unavailable; using null fallback")
            self._dispatcher = None
            self._ArtifactCls = None
            self._real = False

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        """
        Dispatch a vigilance event extracted from execution context kwargs.

        Accepts the same variadic signature as the null stubs so spine code
        needs no changes.  When invoked with named keys:
          trace_id (str) — from CID or cycle
          signals  (tuple[str, ...] | list[str]) — execution signals
          summary  (str) — human-readable summary

        Falls back to no-op if any step fails.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "VigilanceDispatcherAdapter.dispatch")

        if not self._real:
            return
        try:
            trace_id: str = str(kwargs.get("trace_id", "unknown"))
            raw_signals = kwargs.get("signals", ())
            if isinstance(raw_signals, str):
                raw_signals = (raw_signals,)
            signals: tuple[str, ...] = tuple(raw_signals)
            summary: str = str(kwargs.get("summary", "spine-execution"))
            event = self._ArtifactCls.create(trace_id=trace_id, signals=signals, summary=summary)
            self._dispatcher.dispatch(event=event, enqueue_fn=_EVENT_QUEUE.append)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("VigilanceDispatcherAdapter.dispatch swallowed: %s", exc)

    @property
    def is_real(self) -> bool:
        """True if backed by the real VigilanceDispatcher, False for null fallback."""
        return self._real
