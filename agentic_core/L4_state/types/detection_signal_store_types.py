"""
L4 DetectionSignal Store — Phase 3

In-process persistence for L6 DetectionSignals.
Enforces strict prior-only semantics: fetch_latest returns only signals
committed BEFORE the given boundary tick, never same-cycle signals.

No external services. Pure in-memory store backed by a sorted list.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def _get_detection_signal_class():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_detection_signal_class", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_detection_signal_class", "p0_governance")
    from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal

    return DetectionSignal


@dataclass
class _StoredEntry:
    """Internal record: signal + the commit_tick at which it was stored."""

    signal: object
    commit_tick: int


@dataclass
class DetectionSignalStore:
    """
    L4 in-process store for DetectionSignals.

    Commit ticks are monotonically increasing integers supplied by the caller
    (typically the SemanticClock step_id or a simple counter).

    Same-cycle enforcement:
        fetch_latest(before_tick=T) returns the most recent signal whose
        commit_tick is STRICTLY LESS THAN T.  A signal stored at tick T
        is invisible to a fetch at boundary T — no same-cycle readback.
    """

    _entries: list[_StoredEntry] = field(default_factory=list)

    def store(self, signal: DetectionSignal, commit_tick: int) -> str:
        """
        Persist a DetectionSignal at the given commit_tick.

        Returns signal_hash for caller confirmation.
        Raises ValueError if commit_tick is not strictly greater than the
        last stored tick (monotonicity enforcement).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "DetectionSignalStore.store")

        if self._entries and commit_tick <= self._entries[-1].commit_tick:
            raise ValueError(
                f"commit_tick {commit_tick} must be strictly greater than last stored tick {self._entries[-1].commit_tick}"
            )
        self._entries.append(_StoredEntry(signal=signal, commit_tick=commit_tick))
        return signal.signal_hash

    def fetch_latest(self, before_tick: int) -> object | None:
        """
        Return the most recent signal with commit_tick STRICTLY < before_tick.

        Returns None if no qualifying signal exists.
        This is the no-same-cycle guarantee: a signal stored at before_tick
        is NOT returned.
        """
        result: object | None = None
        for entry in self._entries:
            if entry.commit_tick < before_tick:
                result = entry.signal
        return result

    def count(self) -> int:
        return len(self._entries)


_SIGNAL_STORE = DetectionSignalStore()


def get_signal_store() -> DetectionSignalStore:
    """Return the module-level L4 DetectionSignal store singleton."""
    return _SIGNAL_STORE


def store_detection_signal(signal: object, commit_tick: int) -> str:
    """Store a signal in the L4 SSOT store. Returns signal_hash."""
    return get_signal_store().store(signal, commit_tick)


def fetch_latest_detection_signal(before_tick: int) -> object | None:
    """
    Fetch the most recent signal committed before before_tick.

    Enforces no-same-cycle semantics: signals at before_tick are excluded.
    """
    return get_signal_store().fetch_latest(before_tick)


def get_prior_detection_signal(execution_start_tick: int) -> object | None:
    """
    Guaranteed prior-only accessor for routing decisions.

    Returns the most recent signal committed strictly before
    execution_start_tick. Signals emitted during the current execution
    cycle (at or after execution_start_tick) are invisible.
    """
    return fetch_latest_detection_signal(before_tick=execution_start_tick)
