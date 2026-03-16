"""Concrete TelemetryStore — reads telemetry events for the meta-learning pipeline.

Provides file-backed and in-memory implementations of the ``TelemetryStore``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_writes_through,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "telemetry_store", "p0_governance")
_emit_reads_policy_state("p0", "telemetry_store", "policy_binding")
_emit_snapshots_state("p0", "telemetry_store", "state_snapshot")
emit_replay_key("p0", "telemetry_store")
emit_determinism_digest("p0", "telemetry_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class FileBackedTelemetryStore:
    """File-backed telemetry store reading from a JSONL telemetry log.

    Each line in the telemetry file is expected to be a JSON object with at
    least ``timestamp_utc`` (int), ``event_type`` (str), and ``payload``
    (JSON-serializable) fields.

    Parameters
    ----------
    telemetry_path : Path
        Path to the JSONL telemetry log file.
    """

    def __init__(self, telemetry_path: Path) -> None:
        self._path = Path(telemetry_path)

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read telemetry events within the given time window.

        Returns
        -------
        tuple[tuple[int, str, bytes], ...]
            Tuple of ``(timestamp_utc, event_type, payload_bytes)`` triples.
        """
        _emit_writes_through(str(uuid.uuid4()), "FileBackedTelemetryStore.read_events", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedTelemetryStore.read_events")

        if not self._path.exists():
            return ()
        events: list[tuple[int, str, bytes]] = []
        try:
            for line in self._path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    ts = int(obj.get("timestamp_utc", 0))
                    if window_start_utc <= ts <= window_end_utc:
                        event_type = str(obj.get("event_type", "unknown"))
                        payload = json.dumps(
                            obj.get("payload", {}), separators=(",", ":"), sort_keys=True
                        ).encode("utf-8")
                        events.append((ts, event_type, payload))
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
        except OSError as exc:
            logger.debug("Failed to read telemetry file %s: %s", self._path, exc)
        return tuple(events)


class InMemoryTelemetryStore:
    """In-memory telemetry store for testing."""

    def __init__(self) -> None:
        self._events: list[tuple[int, str, bytes]] = []

    def add_event(self, timestamp_utc: int, event_type: str, payload_bytes: bytes) -> None:
        self._events.append((timestamp_utc, event_type, payload_bytes))

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        return tuple(e for e in self._events if window_start_utc <= e[0] <= window_end_utc)


__all__ = ["FileBackedTelemetryStore", "InMemoryTelemetryStore"]
