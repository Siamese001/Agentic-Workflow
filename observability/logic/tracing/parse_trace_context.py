"""
w3c_trace_context.py - Tracing Module

Domain: tracing
Generated: 2025-12-07T12:07:59.861451
"""

import logging
import time
import uuid
from typing import Generator, Dict, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class Span:
    """A trace span."""
    trace_id: str
    span_id: str
    name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: Dict[str, object] = field(default_factory=dict)
    events: List[Dict] = field(default_factory=list)
    parent_id: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        """Execute duration_ms operation."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


class W3cTraceContext:
    """Tracer for tracing domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        self.config = config or {}
        self.spans: List[Span] = []
        self._current_span: Optional[Span] = None
        logger.info(f"Initialized {self.__class__.__name__}")

    @contextmanager
    def start_span(self, name: str, attributes: Optional[Dict] = None) -> Generator[Span, None, None]:
        """Start a new span."""
        trace_id = self._current_span.trace_id if self._current_span else str(uuid.uuid4())
        parent_id = self._current_span.span_id if self._current_span else None

        span = Span(
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            name=name,
            attributes=attributes or {},
            parent_id=parent_id
        )

        prev_span = self._current_span
        self._current_span = span

        try:
            yield span
        finally:
            span.end_time = time.time()
            self.spans.append(span)
            self._current_span = prev_span

    def add_event(self, name: str, attributes: Optional[Dict] = None) -> None:
        """Add event to current span."""
        if self._current_span:
            self._current_span.events.append({
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {}
            })

    def get_spans(self) -> List[Span]:
        """Get all recorded spans."""
        return self.spans


# Global tracer
_tracer = W3cTraceContext()


@contextmanager
def trace(name: str, attributes: Optional[Dict] = None) -> Generator[Span, None, None]:
    """Create a trace span."""
    with _tracer.start_span(name, attributes) as span:
        yield span