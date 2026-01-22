
import time
import uuid

# from archives.legacy_root_folders.core.models.models import TelemetryEvent  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.runtime.observability.collectors import append_event, push_span, pop_span  # DEPRECATED: Archive import removed to protect archives from validation edits


def _now_ms() -> int:
    return int(time.time() * 1000)


def start_span(name: str, ctx: dict[str, object] | None = None) -> dict[str, object]:
    """Create a uniquely identified span and record the start time."""

    span_id = str(uuid.uuid4())
    record: dict[str, object] = {
        "span_id": span_id,
        "name": name,
        "start_ms": _now_ms(),
        "ctx": ctx or {},
    }
    push_span(record)

    append_event(
        TelemetryEvent(
            name=name,
            span_id=span_id,
            ts_ms=record["start_ms"],
            attributes={
                "event_type": "span_start",
                "span_id": span_id,
                "ctx": ctx or {},
            },
        )
    )

    return record


def end_span(span_record: dict[str, object]) -> None:
    """Close a previously-started span; no-op if unknown."""

    #     from archives.legacy_root_folders.runtime.observability.collectors import span_stack  # DEPRECATED: Archive import removed to protect archives from validation edits

    if span_record not in span_stack():
        return

    pop_span(span_record)
    end_ms = _now_ms()
    duration = end_ms - span_record["start_ms"]

    append_event(
        TelemetryEvent(
            name=span_record["name"],
            span_id=span_record["span_id"],
            ts_ms=end_ms,
            attributes={
                "event_type": "span_end",
                "span_id": span_record["span_id"],
                "duration_ms": duration,
                "ctx": span_record.get("ctx", {}),
            },
        )
    )