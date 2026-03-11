"""
opentelemetry_tracing_adapter.py - function Module

Domain: tracing
Generated: 2025-12-07T12:07:59.858910
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.trace import Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

logger = logging.getLogger(__name__)


class SpanType(Enum):
    """Types of execution spans."""

    ORCHESTRATOR = "orchestrator"
    COGNITIVE = "cognitive"
    ACTION = "action"
    TOOL = "tool"
    DAG_NODE = "dag_node"
    REASONING = "reasoning"


@dataclass
class SpanMetadata:
    """Metadata attached to a span."""

    span_type: SpanType
    component: str
    layer: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for span attributes."""
        return {
            "span.type": self.span_type.value,
            "component": self.component,
            "layer": self.layer,
            **self.attributes,
        }


@dataclass
class CostMetrics:
    """Cost and token metrics for LLM calls."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model: str = "unknown"
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tokens.prompt": self.prompt_tokens,
            "tokens.completion": self.completion_tokens,
            "tokens.total": self.total_tokens,
            "cost.usd": self.estimated_cost_usd,
            "llm.model": self.model,
            "llm.latency_ms": self.latency_ms,
        }


@dataclass
class ResilienceMetrics:
    """Resilience metrics for action execution."""

    retry_attempts: int = 0
    circuit_breaker_state: str = "CLOSED"
    rate_limit_status: str = "OK"
    backoff_ms: float = 0.0
    success: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resilience.retry_attempts": self.retry_attempts,
            "resilience.circuit_breaker": self.circuit_breaker_state,
            "resilience.rate_limit": self.rate_limit_status,
            "resilience.backoff_ms": self.backoff_ms,
            "resilience.success": self.success,
        }


class OpenTelemetryTracingAdapter:
    """Full OpenTelemetry tracing adapter for agentic execution.

    Provides hierarchical tracing:
    - Orchestrator span (root) - Full agent run
    - Cognitive spans - Think/reasoning phases
    - Action spans - Tool execution phases
    - Tool spans - Individual tool calls
    - DAG node spans - Workflow task execution

    Integrates with Phase 1 components:
    - TokenBudget for cost tracking
    - ErrorRecoveryManager for resilience metrics
    - ReActEngine for reasoning traces
    """

    def __init__(
        self,
        service_name: str = "agentic-workflow",
        enable_console_export: bool = False,
        enable_logging: bool = True,
    ):
        """Initialize tracing adapter.

        Args:
            service_name: Name of the service for tracing
            enable_console_export: Export spans to console
            enable_logging: Enable logging of span events
        """
        self.service_name = service_name
        self.enable_logging = enable_logging

        if OTEL_AVAILABLE:
            # Create tracer provider
            resource = Resource.create({"service.name": service_name})
            provider = TracerProvider(resource=resource)

            # Add console exporter if enabled
            if enable_console_export:
                processor = BatchSpanProcessor(ConsoleSpanExporter())
                provider.add_span_processor(processor)

            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(__name__)
            self._enabled = True

            if self.enable_logging:
                logger.info("opentelemetry_initialized", extra={"service_name": service_name})
        else:
            self.tracer = None
            self._enabled = False

            if self.enable_logging:
                logger.warning(
                    "opentelemetry_not_available",
                    extra={"message": "Install opentelemetry-api and opentelemetry-sdk"},
                )

    @contextmanager
    def trace_orchestrator(
        self,
        mission: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Trace orchestrator execution (L3 - Root span).

        Args:
            mission: Mission being executed
            metadata: Additional metadata

        Yields:
            Span context
        """
        span_metadata = SpanMetadata(
            span_type=SpanType.ORCHESTRATOR,
            component="NervousSystem",
            layer="L3_Orchestration",
            attributes={
                "mission": mission,
                **(metadata or {}),
            },
        )

        with self._create_span(
            name="orchestrator.execute",
            metadata=span_metadata,
        ) as span:
            yield span

    @contextmanager
    def trace_cognitive(
        self,
        task: str,
        reasoning_mode: str = "react",
        cost_metrics: CostMetrics | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Trace cognitive plane execution (L1 - Think phase).

        Args:
            task: Task being planned
            reasoning_mode: Reasoning mode (react, cot, etc.)
            cost_metrics: Token and cost metrics
            metadata: Additional metadata

        Yields:
            Span context
        """
        attributes = {
            "task": task,
            "reasoning.mode": reasoning_mode,
            **(metadata or {}),
        }

        # Add cost metrics if provided
        if cost_metrics:
            attributes.update(cost_metrics.to_dict())

        span_metadata = SpanMetadata(
            span_type=SpanType.COGNITIVE,
            component="CognitivePlane",
            layer="L1_Cognition",
            attributes=attributes,
        )

        with self._create_span(
            name="cognitive.think",
            metadata=span_metadata,
        ) as span:
            yield span

    @contextmanager
    def trace_action(
        self,
        action_count: int,
        resilience_metrics: ResilienceMetrics | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Trace action plane execution (L2 - Act phase).

        Args:
            action_count: Number of actions being executed
            resilience_metrics: Resilience metrics
            metadata: Additional metadata

        Yields:
            Span context
        """
        attributes = {
            "action.count": action_count,
            **(metadata or {}),
        }

        # Add resilience metrics if provided
        if resilience_metrics:
            attributes.update(resilience_metrics.to_dict())

        span_metadata = SpanMetadata(
            span_type=SpanType.ACTION,
            component="ActionPlane",
            layer="L2_Execution",
            attributes=attributes,
        )

        with self._create_span(
            name="action.execute",
            metadata=span_metadata,
        ) as span:
            yield span

    @contextmanager
    def trace_tool(
        self,
        tool_name: str,
        parameters: dict[str, Any] | None = None,
        resilience_metrics: ResilienceMetrics | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Trace individual tool execution (L2 - Leaf span).

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            resilience_metrics: Resilience metrics
            metadata: Additional metadata

        Yields:
            Span context
        """
        attributes = {
            "tool.name": tool_name,
            "tool.parameters": str(parameters or {}),
            **(metadata or {}),
        }

        # Add resilience metrics if provided
        if resilience_metrics:
            attributes.update(resilience_metrics.to_dict())

        span_metadata = SpanMetadata(
            span_type=SpanType.TOOL,
            component=f"Tool.{tool_name}",
            layer="L2_Execution",
            attributes=attributes,
        )

        with self._create_span(
            name=f"tool.{tool_name}",
            metadata=span_metadata,
        ) as span:
            yield span

    @contextmanager
    def trace_dag_node(
        self,
        task_id: str,
        task_type: str,
        dependencies: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Trace DAG node execution (Pillar 4).

        Args:
            task_id: Task ID
            task_type: Task type
            dependencies: Task dependencies
            metadata: Additional metadata

        Yields:
            Span context
        """
        span_metadata = SpanMetadata(
            span_type=SpanType.DAG_NODE,
            component="DAGEngine",
            layer="L3_Orchestration",
            attributes={
                "dag.task_id": task_id,
                "dag.task_type": task_type,
                "dag.dependencies": str(dependencies or []),
                **(metadata or {}),
            },
        )

        with self._create_span(
            name=f"dag.task.{task_id}",
            metadata=span_metadata,
        ) as span:
            yield span

    @contextmanager
    def trace_reasoning(
        self,
        step_number: int,
        step_type: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Trace reasoning step (ReAct integration).

        Args:
            step_number: Step number in reasoning trace
            step_type: Type of step (think, action, observation)
            metadata: Additional metadata

        Yields:
            Span context
        """
        span_metadata = SpanMetadata(
            span_type=SpanType.REASONING,
            component="ReActEngine",
            layer="L1_Cognition",
            attributes={
                "reasoning.step": step_number,
                "reasoning.type": step_type,
                **(metadata or {}),
            },
        )

        with self._create_span(
            name=f"reasoning.step.{step_number}",
            metadata=span_metadata,
        ) as span:
            yield span

    @contextmanager
    def _create_span(
        self,
        name: str,
        metadata: SpanMetadata,
    ):
        """Create a span with metadata.

        Args:
            name: Span name
            metadata: Span metadata

        Yields:
            Span or None if tracing disabled
        """
        if not self._enabled or not self.tracer:
            # Tracing disabled, yield None
            yield None
            return

        start_time = time.time()

        with self.tracer.start_as_current_span(name) as span:
            # Set attributes
            for key, value in metadata.to_dict().items():
                span.set_attribute(key, value)

            try:
                yield span

                # Mark as successful
                span.set_status(Status(StatusCode.OK))

                if self.enable_logging:
                    logger.debug(
                        "span_completed",
                        extra={
                            "span_name": name,
                            "span_type": metadata.span_type.value,
                            "duration_ms": (time.time() - start_time) * 1000,
                        },
                    )

            except Exception as e:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                # Mark as failed
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)

                if self.enable_logging:
                    logger.error(
                        "span_failed",
                        extra={
                            "span_name": name,
                            "error": str(e),
                        },
                        exc_info=True,
                    )

                raise

    def add_event(self, span: Any, name: str, attributes: dict[str, Any] | None = None):
        """Add an event to a span.

        Args:
            span: Span to add event to
            name: Event name
            attributes: Event attributes
        """
        if span and self._enabled:
            span.add_event(name, attributes=attributes or {})

    def set_attribute(self, span: Any, key: str, value: Any):
        """Set an attribute on a span.

        Args:
            span: Span to set attribute on
            key: Attribute key
            value: Attribute value
        """
        if span and self._enabled:
            span.set_attribute(key, value)

    def is_enabled(self) -> bool:
        """Check if tracing is enabled.

        Returns:
            True if tracing is enabled
        """
        return self._enabled


# Global tracer instance
_global_tracer: OpenTelemetryTracingAdapter | None = None


def get_tracer(
    service_name: str = "agentic-workflow",
    enable_console_export: bool = False,
) -> OpenTelemetryTracingAdapter:
    """Get or create global tracer instance.

    Args:
        service_name: Service name
        enable_console_export: Enable console export

    Returns:
        OpenTelemetryTracingAdapter instance
    """
    global _global_tracer

    if _global_tracer is None:
        _global_tracer = OpenTelemetryTracingAdapter(
            service_name=service_name,
            enable_console_export=enable_console_export,
        )

    return _global_tracer


def reset_tracer():
    """Reset global tracer instance."""
    global _global_tracer
    _global_tracer = None
