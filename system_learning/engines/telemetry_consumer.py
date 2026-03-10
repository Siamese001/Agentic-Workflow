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

from system_learning.types.telemetry_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    TelemetryEvent,
    create_telemetry_slice,
)

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
