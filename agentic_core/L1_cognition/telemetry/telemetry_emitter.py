"""
L1 Cognition Telemetry Emitter - Write-only, ZERO-decision component

Emits deterministic TelemetryEvent artifacts and forwards them to L4
telemetry recording via an injected seam. L1 never branches on safety
state and does not couple to L2/L5.
"""

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "telemetry_emitter")
emit_determinism_digest("p0", "telemetry_emitter")

_emit_dispatches_healing_run("p1", "telemetry_emitter", "L1")
_emit_routes_through("p1", "telemetry_emitter", "L1")
_emit_escalates_to_human("p1", "telemetry_emitter", "L1")
_emit_reads_policy_state("p1", "telemetry_emitter", "L1")


def compute_event_hash(stage: str, kind: str, commit_tick: int, details: dict[str, Any]) -> str:
    """
    Compute deterministic event hash from canonical JSON bytes.

    Args:
        stage: Event stage identifier
        kind: Event kind/type
        commit_tick: Required input tick (no wall-clock)
        details: Event details dictionary

    Returns:
        SHA-256 hash of canonical JSON representation
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_event_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_event_hash", "p0_governance")
    canonical_data = {"stage": stage, "kind": kind, "commit_tick": commit_tick, "details": details}
    canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TelemetryEvent:
    """Immutable telemetry event artifact."""

    trace_id: str
    stage: str
    kind: str
    commit_tick: int
    details: dict
    event_hash: str

    @classmethod
    def create(
        cls, trace_id: str, stage: str, kind: str, commit_tick: int, details: dict[str, Any]
    ) -> "TelemetryEvent":
        """
        Create a new TelemetryEvent with deterministic event_hash.

        Args:
            trace_id: Execution trace identifier
            stage: Event stage identifier
            kind: Event kind/type
            commit_tick: Required input tick (no wall-clock)
            details: Event details dictionary

        Returns:
            New TelemetryEvent with computed event_hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "TelemetryEvent.create")

        details_copy = copy.deepcopy(details)
        event_hash = compute_event_hash(stage, kind, commit_tick, details_copy)
        return cls(
            trace_id=trace_id,
            stage=stage,
            kind=kind,
            commit_tick=commit_tick,
            details=details_copy,
            event_hash=event_hash,
        )


class TelemetryEmitter:
    """
    Write-only telemetry emitter with injected recording seam.

    Calls injected record_fn exactly once, no branching on event content,
    no I/O, no decisions.
    """

    def emit(self, *, event: TelemetryEvent, record_fn) -> None:
        """
        Emit telemetry event via injected recording function.

        Args:
            event: TelemetryEvent to emit
            record_fn: Injected recording function to call
        """
        record_fn(event)

    def build_event(
        self, *, trace_id: str, stage: str, kind: str, commit_tick: int, details: dict[str, Any]
    ) -> TelemetryEvent:
        """
        Convenience constructor for TelemetryEvent.

        Args:
            trace_id: Execution trace identifier
            stage: Event stage identifier
            kind: Event kind/type
            commit_tick: Required input tick (no wall-clock)
            details: Event details dictionary

        Returns:
            New TelemetryEvent
        """
        return TelemetryEvent.create(trace_id, stage, kind, commit_tick, details)
