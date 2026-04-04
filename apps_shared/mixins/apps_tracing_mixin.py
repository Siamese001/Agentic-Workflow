"""AppsTracingMixin - OpenTelemetry tracing for apps_* agent modules.

This mixin provides explicit OpenTelemetry span instrumentation for
all apps_* reasoning agents (apps_lic, apps_rg, apps_exec, apps_research).

BRIDGING:
- Bridges with agentic_core TracingMixin for cross-layer trace propagation
- Integrates with lifecycle_trace_contract emitters for ADG registration
- Supports both direct OTel SDK usage and higher-level span contexts

USAGE:
    from apps_shared.mixins.apps_tracing_mixin import AppsTracingMixin

    class MyAgent(AppsTracingMixin):
        def execute(self, request):
            with self.start_agent_span("execute", {"request_id": request.id}):
                # Your agent logic here
                result = self._process(request)
                return result
"""
# guardian: allow-silent-degradation - Tracing requires exception handling

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Import agentic_core tracing for cross-layer bridging
try:
    from agentic_core.mixins.tracing_mixin import SpanContext, TracingMixin
    AGENTIC_CORE_AVAILABLE = True
except ImportError:
    AGENTIC_CORE_AVAILABLE = False
    SpanContext = dict  # type: ignore

# Import lifecycle trace contract for ADG registration
try:
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
        _emit_records_execution_trace,
        _emit_records_telemetry_event,
    )
    LIFECYCLE_AVAILABLE = True
except ImportError:
    LIFECYCLE_AVAILABLE = False


logger = logging.getLogger(__name__)


class AppsTracingMixin:
    """OpenTelemetry tracing mixin for apps_* agent modules.

    Provides explicit span instrumentation that bridges with agentic_core
    infrastructure for comprehensive distributed tracing.

    FEATURES:
    - Explicit OTel span creation for agent operations
    - Automatic bridging to TracingMixin (if available)
    - ADG lifecycle trace contract emission
    - Graceful degradation when OTel unavailable

    SPAN TYPES:
    - AGENT_EXECUTE: Agent execution spans
    - AGENT_REASON: Agent reasoning spans
    - AGENT_CALL_TOOL: Tool invocation spans
    - AGENT_VALIDATE: Validation spans
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize tracing mixin."""
        super().__init__(*args, **kwargs)
        self._apps_tracer: Any = None
        self._apps_tracing_enabled = False
        self._service_name = getattr(self, '__class__.__name__', 'unknown_agent')

        # Initialize OpenTelemetry tracer
        self._init_apps_tracer()

    def _init_apps_tracer(self) -> None:
        """Initialize OpenTelemetry tracer for apps_* agent."""
        if not OTEL_AVAILABLE:
            logger.debug(f"[{self._service_name}] OpenTelemetry not available")
            return

        try:
            # Get or create tracer for this agent
            self._apps_tracer = trace.get_tracer(
                instrumenting_module_name=f"apps.{self._service_name}",
                instrumenting_library_version="1.0.0"
            )
            self._apps_tracing_enabled = True
            logger.info(f"[{self._service_name}] AppsTracingMixin initialized")
        except Exception as e:
            logger.warning(f"[{self._service_name}] Failed to initialize tracer: {e}")

    @contextmanager
    def start_agent_span(
        self,
        operation: str,
        attributes: dict[str, Any] | None = None,
        span_kind: str = "AGENT_EXECUTE"
    ) -> Generator[SpanContext | dict, None, None]:
        """Start an agent operation span with OTel instrumentation.

        Args:
            operation: Name of the operation (e.g., "execute", "reason", "validate")
            attributes: Additional span attributes
            span_kind: Type of span (AGENT_EXECUTE, AGENT_REASON, AGENT_CALL_TOOL, AGENT_VALIDATE)

        Yields:
            Span context (SpanContext if available, else dict)

        Usage:
            with self.start_agent_span("execute", {"request_id": "123"}):
                result = self.process(request)
        """
        span_name = f"{self._service_name}.{operation}"
        start_time = time.time()

        # Emit lifecycle trace for ADG registration
        if LIFECYCLE_AVAILABLE:
            try:
                _emit_records_execution_trace(
                    self._service_name,
                    "L_APP",
                    span_name
                )
            except Exception:
                pass  # Silent degradation

        # Create OpenTelemetry span if available
        otel_span = None
        if self._apps_tracing_enabled and self._apps_tracer:
            try:
                # Build span attributes
                span_attrs = {
                    "agent.name": self._service_name,
                    "agent.operation": operation,
                    "agent.span_kind": span_kind,
                    "agent.layer": "L_APP",
                }
                if attributes:
                    span_attrs.update(attributes)

                # Start OTel span
                otel_span = self._apps_tracer.start_span(
                    name=span_name,
                    attributes=span_attrs
                )

                # Set span status to OK initially
                otel_span.set_status(Status(StatusCode.OK))

            except Exception as e:
                logger.debug(f"[{self._service_name}] Failed to create OTel span: {e}")
                otel_span = None

        # Create fallback span context
        if AGENTIC_CORE_AVAILABLE:
            ctx = SpanContext(
                trace_id=self._generate_trace_id(),
                span_id=self._generate_span_id(),
                service_name=self._service_name,
                operation_name=operation,
                attributes=attributes or {}
            )
        else:
            ctx = {
                "trace_id": self._generate_trace_id(),
                "span_id": self._generate_span_id(),
                "service_name": self._service_name,
                "operation_name": operation,
                "attributes": attributes or {}
            }

        try:
            yield ctx

            # Mark span as successful
            if otel_span:
                otel_span.set_status(Status(StatusCode.OK))

        except Exception as e:
            # Mark span as error
            if otel_span:
                otel_span.set_status(Status(StatusCode.ERROR, str(e)))
                otel_span.record_exception(e)
            raise
        finally:
            # End span
            duration_ms = (time.time() - start_time) * 1000

            if otel_span:
                otel_span.set_attribute("duration_ms", duration_ms)
                otel_span.end()

            # Emit telemetry event
            if LIFECYCLE_AVAILABLE:
                try:
                    _emit_records_telemetry_event(
                        self._service_name,
                        span_name,
                        f"span_completed_duration_ms={duration_ms:.2f}"
                    )
                except Exception:
                    pass

            logger.debug(f"[{self._service_name}] Span {span_name} completed in {duration_ms:.2f}ms")

    def start_reasoning_span(
        self,
        reasoning_type: str,
        attributes: dict[str, Any] | None = None
    ) -> Generator[SpanContext | dict, None, None]:
        """Start a reasoning-specific span.

        Args:
            reasoning_type: Type of reasoning (e.g., "planning", "analysis", "synthesis")
            attributes: Additional span attributes

        Usage:
            with self.start_reasoning_span("planning"):
                plan = self.create_plan()
        """
        attrs = {"reasoning.type": reasoning_type}
        if attributes:
            attrs.update(attributes)
        return self.start_agent_span("reason", attrs, span_kind="AGENT_REASON")

    def start_tool_span(
        self,
        tool_name: str,
        attributes: dict[str, Any] | None = None
    ) -> Generator[SpanContext | dict, None, None]:
        """Start a tool invocation span.

        Args:
            tool_name: Name of the tool being called
            attributes: Additional span attributes

        Usage:
            with self.start_tool_span("search", {"query": "example"}):
                results = self.call_search_tool(query)
        """
        attrs = {"tool.name": tool_name}
        if attributes:
            attrs.update(attributes)
        return self.start_agent_span(f"tool.{tool_name}", attrs, span_kind="AGENT_CALL_TOOL")

    def start_validation_span(
        self,
        validation_type: str,
        attributes: dict[str, Any] | None = None
    ) -> Generator[SpanContext | dict, None, None]:
        """Start a validation span.

        Args:
            validation_type: Type of validation (e.g., "output", "safety", "quality")
            attributes: Additional span attributes

        Usage:
            with self.start_validation_span("safety"):
                self.validate_output_safety(content)
        """
        attrs = {"validation.type": validation_type}
        if attributes:
            attrs.update(attributes)
        return self.start_agent_span(f"validate.{validation_type}", attrs, span_kind="AGENT_VALIDATE")

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID."""
        import uuid
        return str(uuid.uuid4())

    def _generate_span_id(self) -> str:
        """Generate unique span ID."""
        import uuid
        return str(uuid.uuid4())[:16]

    def get_tracing_status(self) -> dict[str, Any]:
        """Get current tracing status."""
        return {
            "service_name": self._service_name,
            "otel_available": OTEL_AVAILABLE,
            "agentic_core_available": AGENTIC_CORE_AVAILABLE,
            "lifecycle_available": LIFECYCLE_AVAILABLE,
            "tracing_enabled": self._apps_tracing_enabled,
            "tracer_initialized": self._apps_tracer is not None,
        }


__all__ = ["AppsTracingMixin", "OTEL_AVAILABLE", "AGENTIC_CORE_AVAILABLE", "LIFECYCLE_AVAILABLE"]
