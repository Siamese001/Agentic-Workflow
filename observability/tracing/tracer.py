"""
Distributed Tracer Implementation

Provides distributed tracing capabilities for monitoring and debugging
agentic workflows across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, AsyncGenerator
from enum import Enum

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Context variables for trace propagation
current_span: ContextVar[Optional["Span"]] = ContextVar("current_span", default=None)
trace_context: ContextVar[Dict[str, Any]] = ContextVar("trace_context", default={})


class SpanKind(str, Enum):
    """Types of spans for different operations."""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


@dataclass
class SpanContext:
    """Context for trace propagation across service boundaries."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)
    flags: int = 0

    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers for propagation."""
        return {
            "x-trace-id": self.trace_id,
            "x-span-id": self.span_id,
            "x-parent-span-id": self.parent_span_id or "",
            "x-trace-flags": str(self.flags),
        }

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> SpanContext:
        """Create from HTTP headers."""
        return cls(
            trace_id=headers.get("x-trace-id", ""),
            span_id=headers.get("x-span-id", ""),
            parent_span_id=headers.get("x-parent-span-id") or None,
            flags=int(headers.get("x-trace-flags", "0")),
        )


@dataclass
class Span:
    """Represents a single span in a distributed trace."""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = "ok"
    kind: SpanKind = SpanKind.INTERNAL
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        event = {
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        }
        self.events.append(event)

    def set_error(self, error: Exception) -> None:
        """Mark span as errored."""
        self.status = "error"
        self.set_attribute("error.message", str(error))
        self.set_attribute("error.type", type(error).__name__)

    def finish(self) -> None:
        """Finish the span."""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.set_attribute("duration_ms", duration * 1000)


class Tracer:
    """Distributed tracer for agentic workflow monitoring."""

    def __init__(self, service_name: str = "agentic-workflow", jaeger_endpoint: Optional[str] = None):
        self.service_name = service_name
        self.spans: Dict[str, Span] = {}
        self.active_spans: List[str] = []

        # Initialize OpenTelemetry if Jaeger endpoint provided
        if jaeger_endpoint:
            self._init_opentelemetry(jaeger_endpoint)
        else:
            self._tracer = None

    def _init_opentelemetry(self, jaeger_endpoint: str) -> None:
        """Initialize OpenTelemetry with Jaeger exporter."""
        resource = Resource.create({"service.name": self.service_name})

        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer_provider = trace.get_tracer_provider()

        jaeger_exporter = JaegerExporter(
            endpoint=jaeger_endpoint,
            collector_endpoint=jaeger_endpoint,
        )

        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)

        self._tracer = trace.get_tracer(__name__)

    def start_span(self, name: str, parent: Optional[Span] = None, kind: SpanKind = SpanKind.INTERNAL) -> Span:
        """Start a new span."""
        span_id = str(uuid.uuid4())

        # Get trace ID from parent or create new
        if parent:
            trace_id = parent.trace_id
            parent_span_id = parent.span_id
        else:
            trace_id = str(uuid.uuid4())
            parent_span_id = None

        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            kind=kind,
        )

        self.spans[span_id] = span
        self.active_spans.append(span_id)

        # Set current span context
        current_span.set(span)

        # Also create OpenTelemetry span if available
        if self._tracer:
            ot_span = self._tracer.start_span(name)
            span.set_attribute("otel_span_id", ot_span.get_span_context().span_id)

        return span

    def finish_span(self, span: Span) -> None:
        """Finish a span."""
        span.finish()
        if span.span_id in self.active_spans:
            self.active_spans.remove(span.span_id)

    def get_current_span(self) -> Optional[Span]:
        """Get the currently active span."""
        return current_span.get()

    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace."""
        return [span for span in self.spans.values() if span.trace_id == trace_id]

    @asynccontextmanager
    async def trace(self, operation_name: str, kind: SpanKind = SpanKind.INTERNAL) -> AsyncGenerator[Span, None]:
        """Context manager for automatic span lifecycle management."""
        parent = self.get_current_span()
        span = self.start_span(operation_name, parent=parent, kind=kind)

        try:
            yield span
        except Exception as e:
            span.set_error(e)
            raise
        finally:
            self.finish_span(span)

    def trace_function(self, operation_name: str, kind: SpanKind = SpanKind.INTERNAL):
        """Decorator for automatic function tracing."""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    async with self.trace(f"{operation_name}:{func.__name__}", kind) as span:
                        span.set_attribute("function.name", func.__name__)
                        span.set_attribute("function.args_count", len(args))
                        return await func(*args, **kwargs)
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs):
                    with asyncio.Runner() as runner:
                        return runner.run(self._trace_sync(func, operation_name, kind, *args, **kwargs))
                return sync_wrapper
        return decorator

    async def _trace_sync(self, func, operation_name: str, kind: SpanKind, *args, **kwargs):
        """Helper for tracing synchronous functions."""
        async with self.trace(f"{operation_name}:{func.__name__}", kind) as span:
            span.set_attribute("function.name", func.__name__)
            span.set_attribute("function.args_count", len(args))
            return func(*args, **kwargs)

    def inject_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Inject trace context into HTTP headers."""
        span = self.get_current_span()
        if span:
            context = SpanContext(
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
            )
            headers.update(context.to_headers())
        return headers

    def extract_context(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        """Extract trace context from HTTP headers."""
        try:
            return SpanContext.from_headers(headers)
        except (KeyError, ValueError):
            return None

    def get_metrics(self) -> Dict[str, Any]:
        """Get tracer metrics."""
        return {
            "total_spans": len(self.spans),
            "active_spans": len(self.active_spans),
            "completed_spans": len(self.spans) - len(self.active_spans),
            "error_spans": len([s for s in self.spans.values() if s.status == "error"]),
        }


# Global tracer instance
_tracer: Optional[Tracer] = None


def get_tracer() -> Tracer:
    """Get the global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer


def init_tracer(service_name: str, jaeger_endpoint: Optional[str] = None) -> Tracer:
    """Initialize the global tracer."""
    global _tracer
    _tracer = Tracer(service_name=service_name, jaeger_endpoint=jaeger_endpoint)
    return _tracer


# Convenience functions
async def trace(operation_name: str, kind: SpanKind = SpanKind.INTERNAL) -> AsyncGenerator[Span, None]:
    """Trace an operation using the global tracer."""
    async with get_tracer().trace(operation_name, kind) as span:
        yield span


def trace_function(operation_name: str, kind: SpanKind = SpanKind.INTERNAL):
    """Decorator for function tracing using global tracer."""
    return get_tracer().trace_function(operation_name, kind)


__all__ = [
    "Tracer",
    "Span",
    "SpanContext",
    "SpanKind",
    "get_tracer",
    "init_tracer",
    "trace",
    "trace_function",
]
