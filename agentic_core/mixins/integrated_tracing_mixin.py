"""Integrated Tracing Mixin - Bridges TracingMixin with OpenTelemetry Runtime ADG.

This mixin provides seamless integration between the existing TracingMixin
span management system and the OpenTelemetry Runtime ADG pipeline.

FEATURES:
- Automatic span collection from TracingMixin → OpenTelemetry adapter
- Runtime ADG materialization and storage integration
- Dual tracing: TracingMixin spans + OpenTelemetry spans
- Automatic persistence to L4/L6 storage
- Backward compatibility with existing TracingMixin usage

USAGE:
    class MyAgent(IntegratedTracingMixin):
        def __init__(self):
            super().__init__(service_name=self.__class__.__name__)

        def my_method(self):
            with self.start_span("my_operation"):
                # Your code here - automatically captured in Runtime ADG
                pass
"""

import logging
import time
from contextlib import contextmanager
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from agentic_core.mixins.tracing_mixin import SpanContext, TracingMixin


# Lazy imports to avoid L_SHARED->L_SL/L_APP gravity violations
def _get_tracer():
    from apps_shared.utils.open_telemetry_tracing_adapter_util import get_tracer
    return get_tracer()

def _get_auto_persistence_adapter():
    from system_learning.runtime_adg.auto_persistence import AutoPersistenceTracingAdapter
    return AutoPersistenceTracingAdapter

emit_determinism_digest("integrated_tracing_mixin", "integrated_tracing_mixin_digest")
record_execution_trace("integrated_tracing_mixin", "integrated_tracing_mixin_trace")

Logger = logging.getLogger(__name__)


class IntegratedTracingMixin(TracingMixin):
    """
    Integrated Tracing Mixin with Runtime ADG support.

    Extends TracingMixin to automatically bridge spans to OpenTelemetry
    and enable Runtime ADG collection and storage.

    INTEGRATION POINTS:
    1. TracingMixin spans → OpenTelemetry spans
    2. Automatic Runtime ADG materialization
    3. L4/L6 storage persistence
    4. Dual span export (TracingMixin + OpenTelemetry)

    BACKWARD COMPATIBILITY:
    - All existing TracingMixin methods work unchanged
    - Existing span management preserved
    - No breaking changes to agent code
    """

    def __init__(self, service_name: str | None = None, **kwargs: Any) -> None:
        """
        Initialize integrated tracing with OpenTelemetry bridge.

        Args:
            service_name: Service name for tracing
            **kwargs: Additional arguments passed to TracingMixin
        """
        # Initialize TracingMixin first
        super().__init__(service_name=service_name, **kwargs)

        # Initialize OpenTelemetry integration
        self._otel_service_name = service_name or self._tracing_service_name
        self._otel_tracer = None
        self._otel_enabled = False
        self._runtime_adg_enabled = False
        self._auto_persistence_enabled = False

        # Initialize OpenTelemetry tracer with auto-persistence
        try:
            self._otel_tracer = AutoPersistenceTracingAdapter(
                service_name=self._otel_service_name,
                enable_auto_persistence=True,
                enable_logging=True,
            )
            self._otel_enabled = self._otel_tracer.is_enabled()
            self._runtime_adg_enabled = True
            self._auto_persistence_enabled = True

            if self._otel_enabled:
                Logger.info(
                    f"[INTEGRATED_TRACING] {self._otel_service_name} - OpenTelemetry + Runtime ADG enabled"
                )
            else:
                Logger.warning(
                    f"[INTEGRATED_TRACING] {self._otel_service_name} - OpenTelemetry disabled, Runtime ADG only"
                )

        except Exception as e:
            Logger.error(
                f"[INTEGRATED_TRACING] {self._otel_service_name} - Failed to initialize OpenTelemetry: {e}"
            )
            self._otel_enabled = False
            self._runtime_adg_enabled = False
            self._auto_persistence_enabled = False

    @contextmanager
    def start_span(self, operation_name: str, attributes: dict[str, Any] | None = None):
        """
        Start an integrated span that bridges TracingMixin and OpenTelemetry.

        This context manager creates both a TracingMixin span and an OpenTelemetry span,
        automatically collecting data for Runtime ADG materialization.

        Args:
            operation_name: Name of the operation
            attributes: Additional span attributes

        Yields:
            IntegratedSpanContext with both TracingMixin and OpenTelemetry contexts
        """
        # Start TracingMixin span
        with super().start_span(operation_name, attributes) as tm_span:
            # Start OpenTelemetry span if enabled
            otel_span_context = None
            if self._otel_enabled and self._otel_tracer:
                # Map TracingMixin operation to appropriate OpenTelemetry span type
                otel_span_context = self._create_otel_span(operation_name, attributes)

            try:
                # Create integrated context and enter OpenTelemetry span
                integrated_span = IntegratedSpanContext(tm_span, otel_span_context, self)
                with integrated_span:
                    yield integrated_span
            except Exception as e:
                # Set error status on TracingMixin span
                tm_span.status = "ERROR"
                tm_span.attributes["error"] = str(e)
                tm_span.attributes["error_type"] = type(e).__name__
                raise

    def _create_otel_span(self, operation_name: str, attributes: dict[str, Any] | None):
        """Create appropriate OpenTelemetry span based on operation type."""
        # Determine span type based on operation name and context
        if "orchestrator" in operation_name.lower() or "mission" in operation_name.lower():
            return self._otel_tracer.trace_orchestrator(operation_name, attributes or {})
        elif "cognitive" in operation_name.lower() or "reasoning" in operation_name.lower():
            reasoning_mode = attributes.get("reasoning_mode", "react") if attributes else "react"
            return self._otel_tracer.trace_cognitive(operation_name, reasoning_mode=reasoning_mode, metadata=attributes)
        elif "action" in operation_name.lower():
            action_count = attributes.get("action_count", 1) if attributes else 1
            return self._otel_tracer.trace_action(action_count=action_count, metadata=attributes)
        elif "tool" in operation_name.lower():
            tool_name = attributes.get("tool_name", operation_name) if attributes else operation_name
            return self._otel_tracer.trace_tool(tool_name, attributes or {})
        else:
            # Default to orchestrator for unknown operations
            return self._otel_tracer.trace_orchestrator(operation_name, attributes or {})

    def flush_traces(self) -> list[dict[str, Any]]:
        """
        Flush all buffered traces from TracingMixin.

        Returns:
            List of flushed trace spans
        """
        tm_traces = super().flush_traces()

        # Get OpenTelemetry status if available
        otel_status = {}
        if self._otel_tracer and self._auto_persistence_enabled:
            otel_status = self._otel_tracer.get_auto_persistence_status()

        Logger.info(
            f"[INTEGRATED_TRACING] {self._otel_service_name} - Flushed {len(tm_traces)} TracingMixin traces",
            extra={"otel_status": otel_status}
        )

        return tm_traces

    def get_integrated_tracing_status(self) -> dict[str, Any]:
        """
        Get comprehensive status of integrated tracing system.

        Returns:
            Dictionary with status of all tracing components
        """
        status = {
            "service_name": self._otel_service_name,
            "tracing_mixin": {
                "enabled": self._trace_enabled,
                "initialized": self._tracing_initialized,
                "degraded": self._tracing_degraded,
                "buffer_size": len(self._trace_buffer),
                "current_trace_id": self._current_trace_id,
                "current_span_id": self._current_span_id,
            },
            "opentelemetry": {
                "enabled": self._otel_enabled,
                "service_name": self._otel_service_name,
            },
            "runtime_adg": {
                "enabled": self._runtime_adg_enabled,
                "auto_persistence": self._auto_persistence_enabled,
            },
        }

        # Add OpenTelemetry auto-persistence status if available
        if self._otel_tracer and self._auto_persistence_enabled:
            status["opentelemetry"]["auto_persistence"] = self._otel_tracer.get_auto_persistence_status()

        return status

    def force_runtime_adg_persistence(self, mission: str = "manual") -> dict[str, Any]:
        """
        Force immediate Runtime ADG persistence of current spans.

        Args:
            mission: Mission identifier for the manual persistence

        Returns:
            Persistence result from OpenTelemetry adapter
        """
        if self._otel_tracer and self._auto_persistence_enabled:
            result = self._otel_tracer.force_persist_current_spans(mission)
            Logger.info(
                f"[INTEGRATED_TRACING] {self._otel_service_name} - Forced Runtime ADG persistence",
                extra={"result": result}
            )
            return result
        else:
            return {
                "success": False,
                "reason": "Runtime ADG auto-persistence not enabled",
                "service_name": self._otel_service_name,
            }


class IntegratedSpanContext:
    """
    Combined context for TracingMixin and OpenTelemetry spans.

    Provides unified access to both tracing systems while maintaining
    backward compatibility with existing TracingMixin usage.
    """

    def __init__(
        self,
        tm_span: SpanContext,
        otel_span_context: Any,
        parent_mixin: IntegratedTracingMixin,
    ):
        """
        Initialize integrated span context.

        Args:
            tm_span: TracingMixin span context
            otel_span_context: OpenTelemetry span context manager
            parent_mixin: Parent IntegratedTracingMixin instance
        """
        self._tm_span = tm_span
        self._otel_span_context = otel_span_context
        self._otel_span = None  # Will be set when entering context
        self._parent_mixin = parent_mixin

    # TracingMixin compatibility methods
    @property
    def trace_id(self) -> str:
        """Get trace ID from TracingMixin span."""
        return self._tm_span.trace_id

    @property
    def span_id(self) -> str:
        """Get span ID from TracingMixin span."""
        return self._tm_span.span_id

    @property
    def service_name(self) -> str:
        """Get service name from TracingMixin span."""
        return self._tm_span.service_name

    @property
    def operation_name(self) -> str:
        """Get operation name from TracingMixin span."""
        return self._tm_span.operation_name

    @property
    def attributes(self) -> dict[str, Any]:
        """Get attributes from TracingMixin span."""
        return self._tm_span.attributes

    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set attribute on both TracingMixin and OpenTelemetry spans.

        Args:
            key: Attribute key
            value: Attribute value
        """
        # Set on TracingMixin span
        self._tm_span.attributes[key] = value

        # Set on OpenTelemetry span if available and if we have the actual span
        if self._otel_span and self._parent_mixin._otel_tracer:
            self._parent_mixin._otel_tracer.set_attribute(self._otel_span, key, value)

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """
        Add event to both TracingMixin and OpenTelemetry spans.

        Args:
            name: Event name
            attributes: Event attributes
        """
        # Add to TracingMixin span attributes
        if attributes:
            event_key = f"event_{name}_{int(time.time() * 1000)}"
            self._tm_span.attributes[event_key] = attributes

        # Add to OpenTelemetry span if available and if we have the actual span
        if self._otel_span and self._parent_mixin._otel_tracer:
            self._parent_mixin._otel_tracer.add_event(self._otel_span, name, attributes)

    def set_status(self, status: str) -> None:
        """
        Set status on both TracingMixin and OpenTelemetry spans.

        Args:
            status: Status string ("OK", "ERROR", etc.)
        """
        # Set on TracingMixin span
        self._tm_span.status = status

        # Set on OpenTelemetry span if available and if we have the actual span
        if self._otel_span and self._parent_mixin._otel_tracer:
            self._otel_span.set_status(status)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert integrated span to dictionary.

        Returns:
            Dictionary with both TracingMixin and OpenTelemetry span data
        """
        result = self._tm_span.to_dict()
        result["integrated_tracing"] = {
            "otel_span_available": self._otel_span is not None,
            "runtime_adg_enabled": self._parent_mixin._runtime_adg_enabled,
            "auto_persistence_enabled": self._parent_mixin._auto_persistence_enabled,
        }
        return result

    # Backward compatibility - behave like TracingMixin SpanContext
    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to TracingMixin span."""
        return getattr(self._tm_span, name)

    def __enter__(self):
        """Enter the OpenTelemetry span context."""
        if self._otel_span_context:
            self._otel_span = self._otel_span_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the OpenTelemetry span context."""
        if self._otel_span_context:
            self._otel_span_context.__exit__(exc_type, exc_val, exc_tb)
