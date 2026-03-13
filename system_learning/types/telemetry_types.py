"""G-16-25: Telemetry types for System Learning telemetry integration.

Immutable, content-addressed telemetry slices with deterministic hashing.

Invariants:
  - All types are frozen dataclasses
  - Canonical byte serialization for hashing
  - Events sorted deterministically by (ts_utc, kind, payload_hash)
  - slice_id = slice_hash
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    """A single telemetry event.

    Fields
    ------
    ts_utc : int
        Event timestamp (Unix timestamp).
    kind : str
        Event kind/type.
    payload_hash : str
        SHA-256 hash of event payload bytes.
    """

    ts_utc: int
    kind: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class TelemetrySlice:
    """Immutable telemetry slice with content-addressed ID.

    Fields
    ------
    slice_id : str
        Content-addressed ID (SHA-256 hash of canonical bytes).
    window_start_utc : int
        Start of telemetry window (Unix timestamp).
    window_end_utc : int
        End of telemetry window (Unix timestamp).
    events : tuple[TelemetryEvent, ...]
        Events sorted deterministically by (ts_utc, kind, payload_hash).
    slice_hash : str
        SHA-256 hash of canonical bytes (same as slice_id).
    """

    slice_id: str
    window_start_utc: int
    window_end_utc: int
    events: tuple[TelemetryEvent, ...]
    slice_hash: str


def canonical_bytes(slice_obj: TelemetrySlice) -> bytes:
    """Return deterministic canonical byte representation of telemetry slice.

    Serialization rules:
      - Fields in fixed order
      - Events sorted by (ts_utc, kind, payload_hash)
      - Delimiter: ASCII unit separator (0x1F)

    Parameters
    ----------
    slice_obj : TelemetrySlice
        The telemetry slice to serialize.

    Returns
    -------
    bytes
        Canonical byte representation.
    """
    sorted_events = sorted(slice_obj.events, key=lambda e: (e.ts_utc, e.kind, e.payload_hash))
    parts = [str(slice_obj.window_start_utc).encode("utf-8"), str(slice_obj.window_end_utc).encode("utf-8")]
    for event in sorted_events:
        event_parts = [
            str(event.ts_utc).encode("utf-8"),
            event.kind.encode("utf-8"),
            event.payload_hash.encode("utf-8"),
        ]
        parts.append(b"\x1e".join(event_parts))
    return b"\x1f".join(parts)


def compute_slice_hash(slice_obj: TelemetrySlice) -> str:
    """Compute SHA-256 hash of canonical bytes.

    Parameters
    ----------
    slice_obj : TelemetrySlice
        The telemetry slice to hash.

    Returns
    -------
    str
        SHA-256 hex digest.
    """
    return hashlib.sha256(canonical_bytes(slice_obj)).hexdigest()


def create_telemetry_slice(
    window_start_utc: int, window_end_utc: int, events: tuple[TelemetryEvent, ...]
) -> TelemetrySlice:
    """Create a telemetry slice with content-addressed ID.

    Parameters
    ----------
    window_start_utc : int
        Start of telemetry window.
    window_end_utc : int
        End of telemetry window.
    events : tuple[TelemetryEvent, ...]
        Events (will be sorted deterministically).

    Returns
    -------
    TelemetrySlice
        Telemetry slice with slice_id = slice_hash.
    """
    temp_slice = TelemetrySlice(
        slice_id="",
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        events=events,
        slice_hash="",
    )
    slice_hash = compute_slice_hash(temp_slice)
    return TelemetrySlice(
        slice_id=slice_hash,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        events=events,
        slice_hash=slice_hash,
    )
