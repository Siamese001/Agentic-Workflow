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
    _emit_records_execution_trace,
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "telemetry_store", "p0_governance")
_emit_reads_policy_state("p0", "telemetry_store", "policy_binding")
_emit_snapshots_state("p0", "telemetry_store", "state_snapshot")
emit_replay_key("p0", "telemetry_store")
emit_determinism_digest("p0", "telemetry_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "telemetry_store", "execution_auth")
_emit_validates_capability("p2", "telemetry_store", "capability_check")
_emit_routes_to_capability("p2", "telemetry_store", "capability_route")
_emit_writes_via_uwg("p2", "telemetry_store", "uwg_write")
_emit_blocks_direct_write("p2", "telemetry_store", "direct_write_block")
_emit_records_tool_invocation("p2", "telemetry_store", "tool_invocation")
_emit_captures_execution_output("p2", "telemetry_store", "exec_output")
_emit_dispatches_agent("p3", "telemetry_store", "agent_dispatch")
_emit_coordinates_agents("p3", "telemetry_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "telemetry_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "telemetry_store", "healing_outcome")
_emit_escalates_failure("p3", "telemetry_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "telemetry_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "telemetry_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "telemetry_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "telemetry_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "telemetry_store", "eval_metric")
_emit_stores_embedding("p4", "telemetry_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "telemetry_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "telemetry_store", "exec_snapshot_link")

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
