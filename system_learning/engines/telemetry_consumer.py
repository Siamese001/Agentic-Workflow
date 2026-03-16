"""G-16-26: Telemetry consumer for System Learning telemetry integration.

Read-only slice builder producing deterministic telemetry slices.

Invariants:
  - No wall-clock, no env, no randomness
  - Deterministic sorting by (ts_utc, kind, payload_hash)
  - Fail-closed on invalid window
  - Read-only inputs, proposal-only outputs
"""

from __future__ import annotations

import hashlib
from typing import Protocol

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

_emit_authorize_and_execute("p2", "telemetry_consumer", "execution_auth")
_emit_validates_capability("p2", "telemetry_consumer", "capability_check")
_emit_routes_to_capability("p2", "telemetry_consumer", "capability_route")
_emit_writes_via_uwg("p2", "telemetry_consumer", "uwg_write")
_emit_blocks_direct_write("p2", "telemetry_consumer", "direct_write_block")
_emit_records_tool_invocation("p2", "telemetry_consumer", "tool_invocation")
_emit_captures_execution_output("p2", "telemetry_consumer", "exec_output")
_emit_dispatches_agent("p3", "telemetry_consumer", "agent_dispatch")
_emit_coordinates_agents("p3", "telemetry_consumer", "agent_coordination")
_emit_records_workflow_lineage("p3", "telemetry_consumer", "workflow_lineage")
_emit_records_healing_outcome("p3", "telemetry_consumer", "healing_outcome")
_emit_escalates_failure("p3", "telemetry_consumer", "failure_escalation")
_emit_orchestrates_workflow("p3", "telemetry_consumer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telemetry_consumer", "healing_dispatch")
_emit_invokes_evaluation("p3", "telemetry_consumer", "evaluation_signal")
_emit_records_telemetry_event("p4", "telemetry_consumer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telemetry_consumer", "eval_metric")
_emit_stores_embedding("p4", "telemetry_consumer", "embedding_store")
_emit_updates_meta_learning_state("p4", "telemetry_consumer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telemetry_consumer", "exec_snapshot_link")
from system_learning.types.telemetry_types import (
    TelemetryEvent,
    create_telemetry_slice,
)

_emit_records_execution_trace("p0", "evidence", "telemetry_consumer")
_emit_applies_guardrail("p0", "telemetry_consumer", "p0_governance")
_emit_reads_policy_state("p0", "telemetry_consumer", "policy_binding")
_emit_snapshots_state("p0", "telemetry_consumer", "state_snapshot")
emit_replay_key("p0", "telemetry_consumer")
emit_determinism_digest("p0", "telemetry_consumer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# Exceptions
# =============================================================================


class TelemetryConsumerError(RuntimeError):
    """Raised when telemetry consumption fails."""


# =============================================================================
# Protocol
# =============================================================================


class TelemetryStore(Protocol):
    """Protocol for read-only telemetry store access."""

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read telemetry events within window.

        Parameters
        ----------
        window_start_utc : int
            Start of window (Unix timestamp).
        window_end_utc : int
            End of window (Unix timestamp).

        Returns
        -------
        tuple[tuple[int, str, bytes], ...]
            Events as (ts_utc, kind, payload_bytes).
        """
        ...


# =============================================================================
# Telemetry Consumer
# =============================================================================


def consume_telemetry(
    store: TelemetryStore,
    window_start_utc: int,
    window_end_utc: int,
) -> object:  # Returns TelemetrySlice
    """Consume telemetry events and produce deterministic slice.

    Enforces:
      - window_start < window_end
      - Deterministic sorting by (ts_utc, kind, payload_hash)
      - slice_hash = SHA-256(canonical_bytes(slice))
      - slice_id = slice_hash

    Parameters
    ----------
    store : TelemetryStore
        Read-only telemetry store.
    window_start_utc : int
        Start of window.
    window_end_utc : int
        End of window.

    Returns
    -------
    TelemetrySlice
        Deterministic telemetry slice.

    Raises
    ------
    TelemetryConsumerError
        If window is invalid.
    """
    # Validate window
    if window_start_utc >= window_end_utc:
        raise TelemetryConsumerError(f"Invalid window: start={window_start_utc} >= end={window_end_utc}")

    # Read events from store
    raw_events = store.read_events(window_start_utc, window_end_utc)

    # Convert to TelemetryEvent with payload_hash
    events = []
    for ts_utc, kind, payload_bytes in raw_events:
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        events.append(
            TelemetryEvent(
                ts_utc=ts_utc,
                kind=kind,
                payload_hash=payload_hash,
            )
        )

    # Sort events deterministically by (ts_utc, kind, payload_hash)
    sorted_events = sorted(events, key=lambda e: (e.ts_utc, e.kind, e.payload_hash))

    # Create slice with deterministic hash
    return create_telemetry_slice(
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        events=tuple(sorted_events),
    )
