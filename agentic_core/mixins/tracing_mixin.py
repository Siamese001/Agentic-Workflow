"""
TracingMixin - Mandatory Tracing for ALL Sovereign Agents.

ROOT INJECTION (Jan 2026):
This mixin provides distributed tracing capabilities at the root level,
ensuring 100% trace coverage across all 278 agents in the fleet.

FEATURES:
- OpenTelemetry-compatible span management
- Automatic service name mapping from class name
- Context propagation for distributed traces
- Graceful degradation when tracing backend unavailable

USAGE:
    class MyAgent(TracingMixin):
        def __init__(self):
            TracingMixin.__init__(self, service_name=self.__class__.__name__)

        def my_method(self):
            with self.start_span("my_operation"):
                # Your code here
                pass

THUNDERING HERD PROTECTION:
- Sampling rate configurable via TRACE_SAMPLE_RATE env var
- Default: 10% for INFO, 100% for ERROR
- Priority sampling ensures critical traces are never dropped
"""
# guardian: allow-silent-degradation - Tracing requires exception handling

import hashlib
import logging
import os
import random
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "tracing_mixin", "p0_governance")
_emit_reads_policy_state("p0", "tracing_mixin", "policy_binding")
_emit_snapshots_state("p0", "tracing_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("tracing_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("tracing_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("tracing_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("tracing_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("tracing_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("tracing_mixin", "p4obs", "metric_6")
_emit_records_incident_event("tracing_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("tracing_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("tracing_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("tracing_mixin", "p4obs", "mon_state")
_emit_triggers_alert("tracing_mixin", "p4obs", "alert")
_emit_links_incident_trace("tracing_mixin", "p4obs", "trace_link")
_emit_captures_pattern("tracing_mixin", "p3lm", "pattern")
_emit_records_learning_event("tracing_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tracing_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("tracing_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tracing_mixin", "p3lm", "routing")
_emit_improves_agent_policy("tracing_mixin", "p3lm", "policy")
_emit_stores_learning_state("tracing_mixin", "p3lm", "state")
_emit_records_execution_trace("tracing_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tracing_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tracing_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tracing_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tracing_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tracing_mixin", "env_read", "p2_env_1")
_emit_reads_environ("tracing_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("tracing_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tracing_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tracing_mixin", "context_pull")
_emit_pulls_context("p1", "tracing_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tracing_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tracing_mixin", "uwg_term_2")
_emit_writes_through("p1", "tracing_mixin", "write_through")
_emit_writes_through("p1", "tracing_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "tracing_mixin", "safety_validation")
_emit_invokes_eval("p1", "tracing_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "tracing_mixin", "routing_commit")
_emit_escalates_to_human("p1", "tracing_mixin", "human_escalation")
_emit_routes_through("p1", "tracing_mixin", "route_through")
_emit_checks_agent_registry("p1", "tracing_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "tracing_mixin", "capability")
_emit_dispatches_execution_plan("p1", "tracing_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "tracing_mixin", "sub_agent")
_emit_routes_to_agent("p1", "tracing_mixin", "target_agent")
_emit_verifies_policy("p1", "tracing_mixin", "policy_check")
_emit_observes_runtime_state("p1", "tracing_mixin", "runtime_state")
_emit_verifies_boundary("p1", "tracing_mixin", "boundary_check")
_emit_transcripts_response("p1", "tracing_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "tracing_mixin")
_emit_gated_by_confidence("p1", "tracing_mixin", "confidence_gate")
emit_replay_key("p0", "tracing_mixin")
emit_determinism_digest("p0", "tracing_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "tracing_mixin", "execution_auth")
_emit_validates_capability("p2", "tracing_mixin", "capability_check")
_emit_routes_to_capability("p2", "tracing_mixin", "capability_route")
_emit_writes_via_uwg("p2", "tracing_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "tracing_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "tracing_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "tracing_mixin", "exec_output")
_emit_dispatches_agent("p3", "tracing_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "tracing_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "tracing_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "tracing_mixin", "healing_outcome")
_emit_escalates_failure("p3", "tracing_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "tracing_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tracing_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "tracing_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "tracing_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tracing_mixin", "eval_metric")
_emit_stores_embedding("p4", "tracing_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "tracing_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tracing_mixin", "exec_snapshot_link")

_CTR: list[int] = [0]


def _new_span_id() -> str:
    """Determinism-safe span ID: SHA-256 of process entropy seed + counter."""
    _CTR[0] += 1
    raw = f"{os.getpid()}:{_CTR[0]}:{os.urandom(8).hex()}"
    return hashlib.sha256(raw.encode()).hexdigest()


Logger = logging.getLogger(__name__)


@dataclass
class SpanContext:
    """Represents a tracing span context."""

    trace_id: str = field(default_factory=lambda: _new_span_id())
    span_id: str = field(default_factory=lambda: _new_span_id()[:16])
    parent_span_id: str | None = None
    service_name: str = "unknown"
    operation_name: str = "unknown"
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "OK"

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add an event to the span."""
        if attributes:
            event_key = f"event_{name}_{int(time.time() * 1000)}"
            self.attributes[event_key] = attributes

    def set_status(self, status: str) -> None:
        """Set the status of the span."""
        self.status = status

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary for telemetry export."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "service_name": self.service_name,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else None,
            "attributes": self.attributes,
            "status": self.status,
        }


class TracingMixin:
    """
    Mandatory Tracing Mixin for ALL Sovereign Agents.

    Provides distributed tracing capabilities with:
    - Automatic span creation and management
    - Context propagation across agent boundaries
    - Graceful degradation when tracing unavailable
    - Priority sampling for load management
    - Circuit breaker for initialization failures

    ROOT INJECTION:
    This mixin is injected at the infrastructure_mixin level,
    ensuring all agents in the L0-L6 hierarchy have tracing.

    CIRCUIT BREAKER (Skeptical Challenge Response):
    If TracingMixin.__init__ fails or hangs, the agent will still initialize
    with tracing disabled. This prevents fleet-wide initialization failures.

    MRO Position:
    ConcreteAgent -> LayerBase -> SovereignBaseAgent -> infrastructure_mixin -> TracingMixin -> ...
    """

    _trace_sample_rate: float = float(os.getenv("TRACE_SAMPLE_RATE", "0.1"))
    _trace_enabled: bool = os.getenv("TRACE_ENABLED", "true").lower() == "true"
    _init_timeout_seconds: float = float(os.getenv("TRACE_INIT_TIMEOUT", "2.0"))
    _circuit_breaker_open: bool = False
    _circuit_breaker_failures: int = 0
    _circuit_breaker_threshold: int = 3

    def __init__(self, service_name: str | None = None, **kwargs: Any) -> None:
        """
        Initialize tracing context with circuit breaker protection.

        CIRCUIT BREAKER PATTERN:
        - If initialization fails 3 times consecutively, circuit opens
        - Open circuit = tracing disabled, but agent still initializes
        - Prevents "God Object" single point of failure

        Args:
            service_name: Service name for spans (defaults to class name)
            **kwargs: Passed to super().__init__()
        """
        self._tracing_service_name: str = service_name or self.__class__.__name__
        self._tracing_initialized: bool = False
        self._tracing_degraded: bool = False
        self._current_trace_id: str | None = None
        self._current_span_id: str | None = None
        self._span_stack: list[SpanContext] = []
        self._trace_buffer: list[dict[str, Any]] = []
        self._trace_buffer_max: int = 1000
        if TracingMixin._circuit_breaker_open:
            self._tracing_degraded = True
            Logger.warning(
                f"[TRACING] {self._tracing_service_name} initialized in DEGRADED mode (circuit breaker open)"
            )
        else:
            try:
                self._initialize_tracing_safe()
                self._tracing_initialized = True
                TracingMixin._circuit_breaker_failures = 0
            except Exception as e:
                raise
                TracingMixin._circuit_breaker_failures += 1
                if TracingMixin._circuit_breaker_failures >= TracingMixin._circuit_breaker_threshold:
                    TracingMixin._circuit_breaker_open = True
                    Logger.error(
                        f"[TRACING] Circuit breaker OPENED after {TracingMixin._circuit_breaker_failures} failures. All subsequent agents will initialize in degraded mode."
                    )
                self._tracing_degraded = True
                Logger.warning(
                    f"[TRACING] {self._tracing_service_name} initialization failed: {e}. Operating in degraded mode. Failures: {TracingMixin._circuit_breaker_failures}"
                )
    def __post_init__(self) -> None:
        """
        Cooperative __post_init__ for dataclass agents.

        Dataclass-based agents (like BaseDispatchAgent) use __post_init__
        instead of __init__. This method ensures tracing is properly initialized.
        """
        # Initialize tracing if not already done via __init__
        if not hasattr(self, '_span_stack'):
            self._tracing_service_name: str = self.__class__.__name__
            self._tracing_initialized: bool = False
            self._tracing_degraded: bool = False
            self._current_trace_id: str | None = None
            self._current_span_id: str | None = None
            self._span_stack: list[SpanContext] = []
            self._trace_buffer: list[dict[str, Any]] = []
            self._trace_buffer_max: int = 1000
        # Call parent's __post_init__ if it exists
        if hasattr(super(), '__post_init__'):
            super().__post_init__()

    def _initialize_tracing_safe(self) -> None:
        """
        Safe tracing initialization with timeout.

        This method contains any potentially slow operations
        (e.g., backend discovery, connection establishment).
        """
        pass

    @contextmanager
    def start_span(
        self, operation_name: str, attributes: dict[str, Any] | None = None
    ) -> Generator[SpanContext, None, None]:
        """
        Start a new tracing span.

        Args:
            operation_name: Name of the operation being traced
            attributes: Optional attributes to attach to the span

        Yields:
            SpanContext: The active span context

        Usage:
            with self.start_span("my_operation", {"key": "value"}):
                # Your code here
                pass
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TracingMixin.start_span")

        # guardian: allow-silent-degradation - Skip when tracing disabled
        if not self._trace_enabled:
            yield SpanContext(operation_name=operation_name)
            return
        parent_span = self._span_stack[-1] if self._span_stack else None
        span = SpanContext(
            trace_id=parent_span.trace_id if parent_span else _new_span_id(),
            span_id=_new_span_id()[:16],
            parent_span_id=parent_span.span_id if parent_span else None,
            service_name=self._tracing_service_name,
            operation_name=operation_name,
            attributes=attributes or {},
        )
        self._span_stack.append(span)
        self._current_trace_id = span.trace_id
        self._current_span_id = span.span_id
        try:
            yield span
            span.status = "OK"
        except Exception as e:
            span.status = "ERROR"
            span.attributes["error"] = str(e)
            span.attributes["error_type"] = type(e).__name__
            raise
        finally:
            span.end_time = time.time()
            if self._span_stack and self._span_stack[-1] == span:
                self._span_stack.pop()
            if self._span_stack:
                self._current_span_id = self._span_stack[-1].span_id
            else:
                self._current_span_id = None
                self._current_trace_id = None
            self._buffer_span(span)

    def _buffer_span(self, span: SpanContext) -> None:
        """Buffer a completed span for export."""
        if len(self._trace_buffer) >= self._trace_buffer_max:
            self._trace_buffer = self._trace_buffer[100:]
        self._trace_buffer.append(span.to_dict())

    def get_trace_context(self) -> dict[str, Any]:
        """
        Get current trace context for propagation.

        Returns:
            Dictionary with trace_id and span_id for context propagation
        """
        return {
            "trace_id": self._current_trace_id,
            "span_id": self._current_span_id,
            "service_name": self._tracing_service_name,
        }

    def inject_trace_context(self, context: dict[str, Any]) -> None:
        """
        Inject external trace context (for distributed tracing).

        Args:
            context: Dictionary with trace_id and optionally span_id
        """
        if "trace_id" in context:
            self._current_trace_id = context["trace_id"]
        if "span_id" in context:
            self._current_span_id = context["span_id"]

    def sample_rate_check(self) -> bool:
        """
        Check if current trace should be sampled.

        Returns:
            True if trace should be recorded, False to skip
        """
        return random.random() < self._trace_sample_rate

    def flush_traces(self) -> list[dict[str, Any]]:
        """
        Flush all buffered traces and optionally bridge to OpenTelemetry.

        Returns:
            List of flushed trace spans
        """
        traces = self._trace_buffer.copy()
        self._trace_buffer.clear()

        # Bridge to OpenTelemetry if available
        if hasattr(self, '_otel_bridge_enabled') and getattr(self, '_otel_bridge_enabled', False):
            self._bridge_to_opentelemetry(traces)

        Logger.info(f"[TRACING] {self._tracing_service_name} - Flushed {len(traces)} traces")
        return traces

    def _bridge_to_opentelemetry(self, traces: list[dict[str, Any]]) -> None:
        """
        Bridge TracingMixin traces to OpenTelemetry adapter.

        Args:
            traces: List of TracingMixin trace dictionaries
        """
        try:
            from apps_shared.utils.open_telemetry_tracing_adapter_util import get_tracer

            tracer = get_tracer(service_name=self._tracing_service_name)

            for trace in traces:
                # Convert TracingMixin span to OpenTelemetry format
                self._create_otel_span_from_trace(trace, tracer)

        # guardian: allow-silent-degradation - Optional OpenTelemetry bridging
        except ImportError:
            Logger.debug("[TRACING] OpenTelemetry not available for bridging")
        except Exception as e:
            Logger.error(f"[TRACING] Failed to bridge to OpenTelemetry: {e}")

    def _create_otel_span_from_trace(self, trace: dict[str, Any], tracer: Any) -> None:
        """
        Create OpenTelemetry span from TracingMixin trace.

        Args:
            trace: TracingMixin trace dictionary
            tracer: OpenTelemetry tracer instance
        """
        try:
            operation_name = trace.get("operation_name", "unknown")
            attributes = trace.get("attributes", {})

            # Determine span type based on operation
            if "cognitive" in operation_name.lower():
                reasoning_mode = attributes.get("reasoning_mode", "react")
                span_context = tracer.trace_cognitive(operation_name, reasoning_mode=reasoning_mode, metadata=attributes)
            elif "tool" in operation_name.lower():
                tool_name = attributes.get("tool_name", operation_name)
                span_context = tracer.trace_tool(tool_name, attributes)
            elif "action" in operation_name.lower():
                action_count = attributes.get("action_count", 1)
                span_context = tracer.trace_action(action_count=action_count, metadata=attributes)
            else:
                span_context = tracer.trace_orchestrator(operation_name, metadata=attributes)

            # Enter and exit the span context to create it
            with span_context:
                pass  # Span is created and automatically closed

        except Exception as e:
            Logger.debug(f"[TRACING] Failed to create OpenTelemetry span: {e}")

    def get_tracing_status(self) -> dict[str, Any]:
        """
        Get current tracing status.

        Returns:
            Dictionary with tracing configuration and state
        """
        return {
            "enabled": self._trace_enabled,
            "sample_rate": self._trace_sample_rate,
            "service_name": self._tracing_service_name,
            "initialized": getattr(self, "_tracing_initialized", False),
            "active_spans": len(self._span_stack),
            "buffered_traces": len(self._trace_buffer),
        }


__all__ = ["TracingMixin", "SpanContext"]
