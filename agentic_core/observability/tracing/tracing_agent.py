"""
TracingAgent: Sovereign Distributed Tracing System

Provides span-based tracing for compliance missions and agent operations.
Features:
- Trace and span ID generation (UUID4)
- Hierarchical parent-child spans
- Start/end timing with duration calculation
- Status tracking (SUCCESS/ERROR)
- Attribute and event recording
- In-memory trace storage with export

Designed for integration with:
- ComplianceOrchestrator (root span)
- Individual agents (child spans)
- ReportingAgent (future trace visualization)

Placed in observability/tracing per SSOT semantic registry:
  "Span tracing, context propagation, and distributed trace ids"

Depth: agentic_core/observability/tracing/tracing_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant

Pure Python, no external dependencies.
Thread-safe via lock.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
from threading import Lock
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class span:
    """Represents a single tracing span."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.attributes = attributes or {}
        self.events: List[Dict[str, Any]] = []
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.status: str = "IN_PROGRESS"

    def start(self) -> None:
        self.start_time = datetime.now().isoformat(timespec="milliseconds")

    def end(self, status: str = "SUCCESS") -> None:
        self.end_time = datetime.now().isoformat(timespec="milliseconds")
        self.status = status

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "name": name,
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "attributes": attributes or {}
        }
        self.events.append(event)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def to_dict(self) -> Dict[str, Any]:
        duration_ms = 0.0
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            duration_ms = round((end - start).total_seconds() * 1000, 3)

        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events
        }


# Uppercase alias for backward compatibility
Span = span


class tracing_agent:
    """
    Autonomous distributed tracing agent.
    Manages trace context and span lifecycle.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root.resolve() if project_root else None
        self._lock = Lock()
        self._spans: Dict[str, span] = {}  # span_id → Span
        self._trace_map: Dict[str, List[str]] = {}  # trace_id → [span_ids]

    @contextmanager
    def create_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for creating and completing a span.

        Usage:
            with tracing_agent.create_span("location_validation") as span:
                span.set_attribute("file_count", 150)
                # do work
        """
        if not trace_id:
            trace_id = str(uuid.uuid4())

        span_id = str(uuid.uuid4())
        new_span = span(name, trace_id, span_id, parent_span_id, attributes)
        new_span.start()

        with self._lock:
            self._spans[span_id] = new_span
            self._trace_map.setdefault(trace_id, []).append(span_id)

        try:
            yield new_span
            new_span.end("SUCCESS")
        except Exception as e:
            new_span.end("ERROR")
            new_span.add_event("exception", {"error": str(e)})
            raise

    def set_attribute(self, span_id: str, key: str, value: Any) -> None:
        with self._lock:
            if span_id in self._spans:
                self._spans[span_id].attributes[key] = value

    def add_event(self, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            if span_id in self._spans:
                self._spans[span_id].add_event(name, attributes)

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Return all spans for a trace, ordered by start time."""
        with self._lock:
            span_ids = self._trace_map.get(trace_id, [])
            spans = [self._spans[sid] for sid in span_ids if sid in self._spans]
            spans.sort(key=lambda s: s.start_time or "")
            return [s.to_dict() for s in spans]

    def get_all_traces(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return all completed traces."""
        with self._lock:
            result = {}
            for trace_id, span_ids in self._trace_map.items():
                spans = []
                for sid in span_ids:
                    if sid in self._spans:
                        current_span = self._spans[sid]
                        if current_span.end_time:  # Only completed spans
                            spans.append(current_span.to_dict())
                if spans:
                    spans.sort(key=lambda s: s["start_time"])
                    result[trace_id] = spans
            return result

    def export_traces_json(self) -> str:
        """Export all traces as JSON string."""
        import json
        return json.dumps(self.get_all_traces(), indent=2)

    # === Compliance Mission Helpers ===

    @contextmanager
    def trace_compliance_mission(self, mission_id: str = "manual"):
        """High-level context for full compliance mission."""
        trace_id = str(uuid.uuid4())
        attributes = {"mission_id": mission_id, "agent": "ComplianceOrchestrator"}
        with self.create_span("full_compliance_mission", trace_id, attributes=attributes) as root_span:
            yield root_span, trace_id


# Uppercase alias for backward compatibility
TracingAgent = tracing_agent
