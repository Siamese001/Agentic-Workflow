"""
Telemetry Recorder - The Black Box

High-performance event ingestion engine for agent cognition tracking.
Writes to an append-only DuckDB database for real-time analytics.
"""

import time
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    logger.warning("DuckDB not available. Install with: pip install duckdb")


@dataclass
class TraceEvent:
    """Structured event in the agent's execution trace."""
    trace_id: str
    span_id: str
    agent_role: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: float


class TelemetryRecorder:
    """
    High-performance event ingestion engine.
    Writes to an append-only DuckDB database for real-time analytics.
    """
    
    def __init__(self, db_path: str = "flight_recorder.duckdb"):
        """
        Initialize the telemetry recorder.
        
        Args:
            db_path: Path to the DuckDB database file
        """
        if not DUCKDB_AVAILABLE:
            raise ImportError("DuckDB not installed. Run: pip install duckdb")
        
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._init_schema()
        
        logger.info(f"Telemetry recorder initialized (db={db_path})")

    def _init_schema(self):
        """Initialize the database schema."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id VARCHAR,
                span_id VARCHAR,
                agent_role VARCHAR,
                event_type VARCHAR,
                payload JSON,
                timestamp DOUBLE
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_trace_id ON traces(trace_id)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_span_id ON traces(span_id)
        """)
        
        logger.debug("Database schema initialized")

    def record_event(self, event: TraceEvent):
        """
        Record a single event.
        
        Args:
            event: TraceEvent to record
        """
        try:
            self.conn.execute(
                "INSERT INTO traces VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event.trace_id,
                    event.span_id,
                    event.agent_role,
                    event.event_type,
                    json.dumps(event.payload),
                    event.timestamp
                )
            )
            logger.debug(f"Recorded event: {event.event_type} for {event.span_id}")
        except Exception as e:
            logger.error(f"Failed to record event: {e}")

    def record_batch(self, events: List[TraceEvent]):
        """
        Record multiple events in a batch for better performance.
        
        Args:
            events: List of TraceEvents to record
        """
        try:
            data = [
                (e.trace_id, e.span_id, e.agent_role, e.event_type, 
                 json.dumps(e.payload), e.timestamp)
                for e in events
            ]
            
            self.conn.executemany(
                "INSERT INTO traces VALUES (?, ?, ?, ?, ?, ?)",
                data
            )
            logger.debug(f"Recorded batch of {len(events)} events")
        except Exception as e:
            logger.error(f"Failed to record batch: {e}")

    def get_trace_gantt(self, trace_id: str):
        """
        Query for visualization: Start/End times of spans.
        
        Args:
            trace_id: Trace ID to query
            
        Returns:
            DataFrame with gantt chart data
        """
        return self.conn.execute("""
            SELECT span_id, agent_role, 
                   MIN(timestamp) as start_time, 
                   MAX(timestamp) as end_time,
                   MAX(timestamp) - MIN(timestamp) as duration
            FROM traces 
            WHERE trace_id = ? 
            GROUP BY span_id, agent_role
            ORDER BY start_time ASC
        """, [trace_id]).df()

    def get_trace_events(self, trace_id: str):
        """
        Get all events for a trace.
        
        Args:
            trace_id: Trace ID to query
            
        Returns:
            DataFrame with all events
        """
        return self.conn.execute("""
            SELECT span_id, event_type, timestamp, payload 
            FROM traces 
            WHERE trace_id = ? 
            ORDER BY timestamp ASC
        """, [trace_id]).df()

    def get_tool_stats(self, trace_id: str):
        """
        Get MCP tool usage statistics for a trace.
        
        Args:
            trace_id: Trace ID to query
            
        Returns:
            DataFrame with tool usage stats
        """
        return self.conn.execute("""
            SELECT json_extract_string(payload, '$.tool') as tool_name, 
                   COUNT(*) as calls,
                   AVG(json_extract(payload, '$.duration_ms')) as avg_duration_ms
            FROM traces 
            WHERE trace_id = ? AND event_type = 'MCP_CALL'
            GROUP BY tool_name
        """, [trace_id]).df()

    def get_recent_traces(self, limit: int = 20):
        """
        Get list of recent trace IDs.
        
        Args:
            limit: Maximum number of traces to return
            
        Returns:
            DataFrame with trace IDs and metadata
        """
        return self.conn.execute("""
            SELECT DISTINCT trace_id,
                   MIN(timestamp) as start_time,
                   MAX(timestamp) as end_time,
                   COUNT(*) as event_count
            FROM traces 
            GROUP BY trace_id
            ORDER BY start_time DESC 
            LIMIT ?
        """, [limit]).df()

    def get_error_events(self, trace_id: Optional[str] = None):
        """
        Get all error events, optionally filtered by trace.
        
        Args:
            trace_id: Optional trace ID to filter by
            
        Returns:
            DataFrame with error events
        """
        if trace_id:
            return self.conn.execute("""
                SELECT trace_id, span_id, agent_role, timestamp, payload
                FROM traces 
                WHERE trace_id = ? AND event_type LIKE '%ERROR%'
                ORDER BY timestamp DESC
            """, [trace_id]).df()
        else:
            return self.conn.execute("""
                SELECT trace_id, span_id, agent_role, timestamp, payload
                FROM traces 
                WHERE event_type LIKE '%ERROR%'
                ORDER BY timestamp DESC
                LIMIT 100
            """).df()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Telemetry recorder closed")


class TelemetryContext:
    """
    Context manager for telemetry recording within a span.
    """
    
    def __init__(
        self, 
        recorder: TelemetryRecorder,
        trace_id: str,
        span_id: str,
        agent_role: str
    ):
        self.recorder = recorder
        self.trace_id = trace_id
        self.span_id = span_id
        self.agent_role = agent_role
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.log_event("SPAN_START", {})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.log_event("SPAN_ERROR", {
                "error_type": exc_type.__name__,
                "error_message": str(exc_val),
                "duration_ms": duration
            })
        else:
            self.log_event("SPAN_END", {"duration_ms": duration})

    def log_event(self, event_type: str, payload: Dict[str, Any]):
        """Log an event within this span."""
        event = TraceEvent(
            trace_id=self.trace_id,
            span_id=self.span_id,
            agent_role=self.agent_role,
            event_type=event_type,
            payload=payload,
            timestamp=time.time()
        )
        self.recorder.record_event(event)


def create_telemetry_recorder(db_path: str = "flight_recorder.duckdb") -> TelemetryRecorder:
    """
    Factory function to create a telemetry recorder.
    
    Args:
        db_path: Path to the DuckDB database
        
    Returns:
        TelemetryRecorder instance
    """
    return TelemetryRecorder(db_path)
