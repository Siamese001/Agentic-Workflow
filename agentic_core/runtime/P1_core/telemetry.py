from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field

import json
import logging
from typing import Any

import duckdb

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


LOGGER = logging.getLogger(__name__)


@dataclass
class TraceEvent:
    trace_id: str
    span_id: str
    role: str
    event_type: str
    payload: dict
    timestamp: float


class TelemetryRecorder:
    def __init__(self: Any, db_path: Any) -> None:
        self.conn = duckdb.connect(db_path)
        self.conn.execute(""" """)

    def record(self: Any, event: TraceEvent) -> None:
        self.conn.execute(
            "INSERT INTO traces VALUES (?, ?, ?, ?, ?, ?)",
            (event.trace_id,
                event.span_id,
                event.role,
                event.event_type,
                json.dumps(event.payload),
                event.timestamp)
        )

