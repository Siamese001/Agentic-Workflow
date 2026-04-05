import time
import uuid

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from apps_shared.config import pipeline_constants_config as _pipeline_constants
from apps_shared.utils.runtime_observability_collectors_util import (
    TelemetryEvent,
    append_event,
    pop_span,
    push_span,
    span_stack,
)

emit_determinism_digest("runtime_observability_spans_util", "runtime_observability_spans_util_digest")
record_execution_trace("runtime_observability_spans_util", "runtime_observability_spans_util_trace")

MAX_RETRIES = _pipeline_constants.MAX_RETRIES
DEFAULT_SLEEP = _pipeline_constants.DEFAULT_SLEEP
THRESHOLD = _pipeline_constants.THRESHOLD
BUFFER_SIZE = _pipeline_constants.BUFFER_SIZE
BATCH_SIZE = _pipeline_constants.BATCH_SIZE
MAX_DEPTH = _pipeline_constants.MAX_DEPTH


def _now_ms() -> int:
    return int(time.time() * 1000)


def start_span(name: str, ctx: dict[str, object] | None = None) -> dict[str, object]:
    """Create a uniquely identified span and record the start time."""
    span_id = str(uuid.uuid4())
    record: dict[str, object] = {"span_id": span_id, "name": name, "start_ms": _now_ms(), "ctx": ctx or {}}
    push_span(record)
    append_event(
        TelemetryEvent(
            name=name,
            data={"event_type": "span_start", "span_id": span_id, "ctx": ctx or {}},
        )
    )
    return record


def end_span(span_record: dict[str, object]) -> None:
    """Close a previously-started span; no-op if unknown."""
    if span_record not in span_stack():
        return
    pop_span(span_record)
    end_ms = _now_ms()
    duration = end_ms - int(span_record.get("start_ms", end_ms))
    append_event(
        TelemetryEvent(
            name=str(span_record.get("name", "")),
            data={
                "event_type": "span_end",
                "span_id": span_record.get("span_id", ""),
                "duration_ms": duration,
                "ctx": span_record.get("ctx", {}),
            },
        )
    )
