import logging
import time
import uuid
from typing import Dict, Optional

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


LOGGER = logging.getLogger(__name__)
# from archives.legacy_root_folders.core.models.models import TelemetryEvent  # DEPRECATED: Archi...
# from archives.legacy_root_folders.runtime.observability.collectors import append_event, push_span


def _now_ms() -> int:
    return int(time.time() * 1000)


def start_span(name: str, ctx: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Create a uniquely identified span and record the start time."""

    span_id = str(uuid.uuid4())
    record: Dict[str, object] = {
        "span_id": span_id,
        "name": name,
        "start_ms": _now_ms(),
        "ctx": ctx or {},
    }
    # Assuming push_span and append_event are defined elsewhere
    # push_span(record)
    # append_event(
    #     TelemetryEvent(
    #         NAME=name,
    #         span_id=span_id,
    #         ts_ms=record["start_ms"],
    #         ATTRIBUTES={
    #             "event_type": "span_start",
    #             "span_id": span_id,
    #             "ctx": ctx or {},
    #         },
    #     )
    # )

    return record


def end_span(span_record: Dict[str, object]) -> None:
    """Close a previously-started span; no-op if unknown."""

    # from archives.legacy_root_folders.runtime.observability.collectors import span_stack, pop_span  # DEP.
    # Assuming span_stack and pop_span are defined elsewhere
    # if span_record not in span_stack():
    #     return

    # pop_span(span_record)
    end_ms = _now_ms()
    duration = end_ms - span_record["start_ms"]

    # Assuming TelemetryEvent is defined elsewhere
    # append_event(
    #     TelemetryEvent(
    #         NAME=span_record["name"],
    #         span_id=span_record["span_id"],
    #         ts_ms=end_ms,
    #         ATTRIBUTES={
    #             "event_type": "span_end",
    #             "span_id": span_record["span_id"],
    #             "duration_ms": duration,
    #             "ctx": span_record.get("ctx", {}),
    #         },
    #     )
    # )

