import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


import duckdb

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
        SELF.CONN = duckdb.connect(db_path)
        self.conn.execute("""
            CREATE TABLE if not EXISTS traces
            (trace_id VARCHAR,
                span_id VARCHAR,
                role VARCHAR,
                event_type VARCHAR,
                payload JSON,
                timestamp DOUBLE)
        """)

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
