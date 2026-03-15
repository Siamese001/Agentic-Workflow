"""
L6 Observability Vigilance Dispatcher - Pure Event Dispatch

Emits immutable VigilanceEvent artifacts and routes via injected enqueue seams.
L6 has ZERO authority: no decisions, no direct L4 mutation, no L2/L5 coupling.
"""

from dataclasses import dataclass
from typing import Callable
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True)
class VigilanceEventArtifact:
    """Immutable vigilance event artifact."""

    trace_id: str
    signals: tuple[str, ...]
    summary: str

    @classmethod
    def create(cls, trace_id: str, signals: tuple[str, ...], summary: str) -> "VigilanceEventArtifact":
        """
        Create a new VigilanceEventArtifact with normalized signals.

        Args:
            trace_id: Unique trace identifier
            signals: Raw signals tuple
            summary: Event summary

        Returns:
            New VigilanceEventArtifact with sorted unique signals
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "VigilanceEventArtifact.create")

        unique_signals = tuple(sorted(set(signals)))
        return cls(trace_id=trace_id, signals=unique_signals, summary=summary)


class VigilanceDispatcher:
    """
    Pure vigilance event dispatcher.

    Routes events via injected enqueue function only.
    No branching, no scoring, no routing logic, no state mutation.
    """

    def dispatch(
        self, *, event: VigilanceEventArtifact, enqueue_fn: Callable[[VigilanceEventArtifact], None]
    ) -> None:
        """
        Dispatch event using injected enqueue function.

        Calls enqueue_fn(event) exactly once.
        No branching, no scoring, no routing logic.

        Args:
            event: Event to dispatch
            enqueue_fn: Function to enqueue the event
        """
        enqueue_fn(event)


def to_meta_payload(event: VigilanceEventArtifact) -> dict:
    """
    Convert VigilanceEventArtifact to meta-learning payload.

    Args:
        event: Event artifact to convert

    Returns:
        Dictionary with trace_id, signals list, and summary
    """
    return {"trace_id": event.trace_id, "signals": list(event.signals), "summary": event.summary}
