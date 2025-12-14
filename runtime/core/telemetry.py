import duckdb
import json
import time
from dataclasses import dataclass, asdict

@dataclass
class TraceEvent:
    trace_id: str
    span_id: str
    role: str
    event_type: str
    payload: dict
    timestamp: float

class TelemetryRecorder:
    def __init__(self, db_path="flight_recorder.duckdb"):
        self.conn = duckdb.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS traces 
            (trace_id VARCHAR, span_id VARCHAR, role VARCHAR, event_type VARCHAR, payload JSON, timestamp DOUBLE)
        """)

    def record(self, event: TraceEvent):
        self.conn.execute(
            "INSERT INTO traces VALUES (?, ?, ?, ?, ?, ?)",
            (event.trace_id, event.span_id, event.role, event.event_type, json.dumps(event.payload), event.timestamp)
        )
