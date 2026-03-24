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
import json
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("telemetry_types", "telemetry_types_digest")
record_execution_trace("telemetry_types", "telemetry_types_trace")


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
    trace_id: str = ""
    span_id: str = ""
    parent_span_id: str = ""
    layer: str = ""
    component: str = ""
    name: str = ""


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

    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self)


def create_runtime_telemetry_event(record: Mapping[str, Any]) -> TelemetryEvent:
    payload = {
        "attributes": record.get("attributes", {}),
        "component": str(record.get("component", "")),
        "kind": str(record.get("kind", "span")),
        "layer": str(record.get("layer", "")),
        "name": str(record.get("name", "")),
        "parent_span_id": str(record.get("parent_span_id", "")),
        "span_id": str(record.get("span_id", "")),
        "trace_id": str(record.get("trace_id", "")),
    }
    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()
    return TelemetryEvent(
        ts_utc=int(record.get("ts_utc", 0)),
        kind=str(record.get("kind", "span")),
        payload_hash=payload_hash,
        trace_id=str(record.get("trace_id", "")),
        span_id=str(record.get("span_id", "")),
        parent_span_id=str(record.get("parent_span_id", "")),
        layer=str(record.get("layer", "")),
        component=str(record.get("component", "")),
        name=str(record.get("name", "")),
    )


def create_telemetry_slice_from_runtime_records(
    records: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> TelemetrySlice:
    events = tuple(create_runtime_telemetry_event(record) for record in records)
    sorted_events = tuple(
        sorted(
            events,
            key=lambda event: (
                event.ts_utc,
                event.kind,
                event.payload_hash,
                event.trace_id,
                event.span_id,
            ),
        )
    )
    if not sorted_events:
        return create_telemetry_slice(0, 0, ())
    return create_telemetry_slice(
        sorted_events[0].ts_utc,
        sorted_events[-1].ts_utc,
        sorted_events,
    )


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
    sorted_events = sorted(
        slice_obj.events,
        key=lambda e: (e.ts_utc, e.kind, e.payload_hash, e.trace_id, e.span_id),
    )
    parts = [str(slice_obj.window_start_utc).encode("utf-8"), str(slice_obj.window_end_utc).encode("utf-8")]
    for event in sorted_events:
        event_parts = [
            str(event.ts_utc).encode("utf-8"),
            event.kind.encode("utf-8"),
            event.payload_hash.encode("utf-8"),
            event.trace_id.encode("utf-8"),
            event.span_id.encode("utf-8"),
            event.parent_span_id.encode("utf-8"),
            event.layer.encode("utf-8"),
            event.component.encode("utf-8"),
            event.name.encode("utf-8"),
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
