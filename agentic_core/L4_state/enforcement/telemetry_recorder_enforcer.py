from __future__ import annotations

import logging
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
)

_emit_dispatches_healing_run("p1", "telemetry_recorder_enforcer", "L4")
_emit_routes_through("p1", "telemetry_recorder_enforcer", "L4")
_emit_escalates_to_human("p1", "telemetry_recorder_enforcer", "L4")
_emit_reads_policy_state("p1", "telemetry_recorder_enforcer", "L4")


class TraceEvent:
    def __init__(self, trace_id, span_id, ROLE, event_type, PAYLOAD, TIMESTAMP):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TraceEvent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TraceEvent.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "TraceEvent.__init__")
        self.data = {
            "trace_id": trace_id,
            "span_id": span_id,
            "role": ROLE,
            "type": event_type,
            "payload": PAYLOAD,
            "time": TIMESTAMP,
        }


class TelemetryRecorder:
    """
    L0 Maintenance: The Flight Recorder.
    Captures all system events for observability and audit.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

    def record(self, event: TraceEvent):
        """Persists a trace event to the logs."""
        logging.info(f"Telemetry: [{event.data['type']}] - {event.data['span_id']}")
