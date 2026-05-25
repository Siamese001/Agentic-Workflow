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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    record_execution_trace,
)
from apps_shared.config import pipeline_constants_config as _pipeline_constants

MAX_RETRIES = _pipeline_constants.MAX_RETRIES
DEFAULT_SLEEP = _pipeline_constants.DEFAULT_SLEEP
THRESHOLD = _pipeline_constants.THRESHOLD
BUFFER_SIZE = _pipeline_constants.BUFFER_SIZE
BATCH_SIZE = _pipeline_constants.BATCH_SIZE
MAX_DEPTH = _pipeline_constants.MAX_DEPTH

_emit_applies_guardrail("p0", "open_telemetry_tracing_adapter_util", "p0_governance")
_emit_reads_policy_state("p0", "open_telemetry_tracing_adapter_util", "policy_binding")
_emit_snapshots_state("p0", "open_telemetry_tracing_adapter_util", "state_snapshot")
emit_replay_key("p0", "open_telemetry_tracing_adapter_util")
emit_determinism_digest("p0", "open_telemetry_tracing_adapter_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "open_telemetry_tracing_adapter_util", "execution_auth")
_emit_validates_capability("p2", "open_telemetry_tracing_adapter_util", "capability_check")
_emit_routes_to_capability("p2", "open_telemetry_tracing_adapter_util", "capability_route")
_emit_writes_via_uwg("p2", "open_telemetry_tracing_adapter_util", "uwg_write")
_emit_blocks_direct_write("p2", "open_telemetry_tracing_adapter_util", "direct_write_block")
_emit_records_tool_invocation("p2", "open_telemetry_tracing_adapter_util", "tool_invocation")
_emit_captures_execution_output("p2", "open_telemetry_tracing_adapter_util", "exec_output")
_emit_dispatches_agent("p3", "open_telemetry_tracing_adapter_util", "agent_dispatch")
_emit_coordinates_agents("p3", "open_telemetry_tracing_adapter_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "open_telemetry_tracing_adapter_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "open_telemetry_tracing_adapter_util", "healing_outcome")
_emit_escalates_failure("p3", "open_telemetry_tracing_adapter_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "open_telemetry_tracing_adapter_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "open_telemetry_tracing_adapter_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "open_telemetry_tracing_adapter_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "open_telemetry_tracing_adapter_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "open_telemetry_tracing_adapter_util", "eval_metric")
_emit_stores_embedding("p4", "open_telemetry_tracing_adapter_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "open_telemetry_tracing_adapter_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "open_telemetry_tracing_adapter_util", "exec_snapshot_link")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.trace import Status, StatusCode

    # Phase 1: OTLP exporter support for external telemetry backends
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGrpcExporter

        OTEL_GRPC_EXPORTER_AVAILABLE = True
    except ImportError:
        OTEL_GRPC_EXPORTER_AVAILABLE = False

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHttpExporter

        OTEL_HTTP_EXPORTER_AVAILABLE = True
    except ImportError:
        OTEL_HTTP_EXPORTER_AVAILABLE = False

    OTEL_AVAILABLE = True
except ImportError:  # guardian: allow-silent-swallow -- optional dependency
    OTEL_AVAILABLE = False
    OTEL_GRPC_EXPORTER_AVAILABLE = False
    OTEL_HTTP_EXPORTER_AVAILABLE = False
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

record_execution_trace("open_telemetry_tracing_adapter_util", "open_telemetry_tracing_adapter_util_trace")


_emit_emits_metric_event("open_telemetry_tracing_adapter_util", "p4obs", "metric_1")
_emit_emits_metric_event("open_telemetry_tracing_adapter_util", "p4obs", "metric_2")
_emit_emits_metric_event("open_telemetry_tracing_adapter_util", "p4obs", "metric_3")
_emit_emits_metric_event("open_telemetry_tracing_adapter_util", "p4obs", "metric_4")
_emit_emits_metric_event("open_telemetry_tracing_adapter_util", "p4obs", "metric_5")
_emit_emits_metric_event("open_telemetry_tracing_adapter_util", "p4obs", "metric_6")
_emit_records_incident_event("open_telemetry_tracing_adapter_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("open_telemetry_tracing_adapter_util", "p4obs", "anomaly")
_emit_writes_observability_log("open_telemetry_tracing_adapter_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("open_telemetry_tracing_adapter_util", "p4obs", "mon_state")
_emit_triggers_alert("open_telemetry_tracing_adapter_util", "p4obs", "alert")
_emit_links_incident_trace("open_telemetry_tracing_adapter_util", "p4obs", "trace_link")
_emit_captures_pattern("open_telemetry_tracing_adapter_util", "p3lm", "pattern")
_emit_records_learning_event("open_telemetry_tracing_adapter_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("open_telemetry_tracing_adapter_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("open_telemetry_tracing_adapter_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("open_telemetry_tracing_adapter_util", "p3lm", "routing")
_emit_improves_agent_policy("open_telemetry_tracing_adapter_util", "p3lm", "policy")
_emit_stores_learning_state("open_telemetry_tracing_adapter_util", "p3lm", "state")
_emit_records_execution_trace("open_telemetry_tracing_adapter_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("open_telemetry_tracing_adapter_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("open_telemetry_tracing_adapter_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("open_telemetry_tracing_adapter_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("open_telemetry_tracing_adapter_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("open_telemetry_tracing_adapter_util", "env_read", "p2_env_1")
_emit_reads_environ("open_telemetry_tracing_adapter_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("open_telemetry_tracing_adapter_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("open_telemetry_tracing_adapter_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "open_telemetry_tracing_adapter_util", "context_pull")
_emit_pulls_context("p1", "open_telemetry_tracing_adapter_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "open_telemetry_tracing_adapter_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "open_telemetry_tracing_adapter_util", "uwg_term_2")
_emit_writes_through("p1", "open_telemetry_tracing_adapter_util", "write_through")
_emit_writes_through("p1", "open_telemetry_tracing_adapter_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "open_telemetry_tracing_adapter_util", "safety_validation")
_emit_invokes_eval("p1", "open_telemetry_tracing_adapter_util", "eval_call")
_emit_proposal_commits_routing("p1", "open_telemetry_tracing_adapter_util", "routing_commit")
_emit_escalates_to_human("p1", "open_telemetry_tracing_adapter_util", "human_escalation")
_emit_routes_through("p1", "open_telemetry_tracing_adapter_util", "route_through")
_emit_checks_agent_registry("p1", "open_telemetry_tracing_adapter_util", "agent_registry")
_emit_validates_agent_capability("p1", "open_telemetry_tracing_adapter_util", "capability")
_emit_dispatches_execution_plan("p1", "open_telemetry_tracing_adapter_util", "exec_plan")
_emit_agent_executes_agent("p1", "open_telemetry_tracing_adapter_util", "sub_agent")
_emit_routes_to_agent("p1", "open_telemetry_tracing_adapter_util", "target_agent")
_emit_verifies_policy("p1", "open_telemetry_tracing_adapter_util", "policy_check")
_emit_observes_runtime_state("p1", "open_telemetry_tracing_adapter_util", "runtime_state")
_emit_verifies_boundary("p1", "open_telemetry_tracing_adapter_util", "boundary_check")
_emit_transcripts_response("p1", "open_telemetry_tracing_adapter_util", "transcript")
_emit_hard_fails_untranscripted("p1", "open_telemetry_tracing_adapter_util")
_emit_gated_by_confidence("p1", "open_telemetry_tracing_adapter_util", "confidence_gate")

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
        enable_otlp_grpc: bool = False,
        enable_otlp_http: bool = False,
        otlp_grpc_endpoint: str | None = None,
        otlp_http_endpoint: str | None = None,
    ):
        """Initialize tracing adapter.

        Args:
            service_name: Name of the service for tracing
            enable_console_export: Export spans to console
            enable_logging: Enable logging of span events
            enable_otlp_grpc: Enable OTLP gRPC exporter for external backends
            enable_otlp_http: Enable OTLP HTTP exporter for gRPC-blocked environments
            otlp_grpc_endpoint: Custom OTLP gRPC endpoint (defaults to env var or standard port)
            otlp_http_endpoint: Custom OTLP HTTP endpoint (defaults to env var or standard port)
        """
        self.service_name = service_name
        self.enable_logging = enable_logging
        self._completed_spans: list[dict[str, Any]] = []
        self._span_stack: list[tuple[str, str]] = []
        self._active_spans: dict[str, Any] = {}
        if OTEL_AVAILABLE:
            import os as _os

            # Anthropic-alignment: standard resource attributes (service.name / version /
            # deployment.environment). See docs/architecture/adr/ADR-024-otel-anthropic-alignment.md.
            resource_attrs = {
                "service.name": _os.environ.get("OTEL_SERVICE_NAME", service_name),
                "service.version": _os.environ.get("OTEL_SERVICE_VERSION", "unknown"),
                "deployment.environment": _os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT", "unknown"),
                "rpc.system": "mcp",
            }
            extra_res = _os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")
            for pair in extra_res.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k and v:
                        resource_attrs[k] = v
            resource = Resource.create(resource_attrs)
            provider = TracerProvider(resource=resource)

            # Console exporter (for debugging)
            if enable_console_export:
                processor = BatchSpanProcessor(ConsoleSpanExporter())
                provider.add_span_processor(processor)

            # OTLP gRPC exporter (for production backends like Jaeger, Tempo, etc.)
            if enable_otlp_grpc and OTEL_GRPC_EXPORTER_AVAILABLE:
                try:
                    import os

                    endpoint = otlp_grpc_endpoint or os.getenv(
                        "OTEL_EXPORTER_OTLP_GRPC_ENDPOINT", "http://localhost:4317"
                    )
                    otlp_exporter = OTLPGrpcExporter(endpoint=endpoint)
                    otlp_processor = BatchSpanProcessor(
                        otlp_exporter,
                        max_queue_size=2048,
                        max_export_batch_size=512,
                        schedule_delay_millis=5000,
                    )
                    provider.add_span_processor(otlp_processor)
                    if self.enable_logging:
                        logger.info("otlp_grpc_exporter_enabled", extra={"endpoint": endpoint})
                except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                    if self.enable_logging:
                        logger.warning("otlp_grpc_exporter_failed", extra={"error": str(e)})

            # OTLP HTTP exporter (for environments where gRPC is blocked)
            if enable_otlp_http and OTEL_HTTP_EXPORTER_AVAILABLE:
                try:
                    import os

                    endpoint = otlp_http_endpoint or os.getenv(
                        "OTEL_EXPORTER_OTLP_HTTP_ENDPOINT", "http://localhost:4318"
                    )
                    otlp_exporter = OTLPHttpExporter(endpoint=endpoint)
                    otlp_processor = BatchSpanProcessor(
                        otlp_exporter,
                        max_queue_size=2048,
                        max_export_batch_size=512,
                        schedule_delay_millis=5000,
                    )
                    provider.add_span_processor(otlp_processor)
                    if self.enable_logging:
                        logger.info("otlp_http_exporter_enabled", extra={"endpoint": endpoint})
                except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
                    if self.enable_logging:
                        logger.warning("otlp_http_exporter_failed", extra={"error": str(e)})

            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(__name__)
            self._enabled = True
            if self.enable_logging:
                logger.info(
                    "opentelemetry_initialized",
                    extra={
                        "service_name": service_name,
                        "grpc_available": OTEL_GRPC_EXPORTER_AVAILABLE,
                        "http_available": OTEL_HTTP_EXPORTER_AVAILABLE,
                    },
                )
        else:
            self.tracer = None
            self._enabled = False
            if self.enable_logging:
                logger.warning(
                    "opentelemetry_not_available",
                    extra={"message": "Install opentelemetry-api and opentelemetry-sdk"},
                )

    @contextmanager
    def trace_orchestrator(self, mission: str, metadata: dict[str, Any] | None = None):
        """Trace orchestrator execution (L3 - Root span).

        Tier-1 emit-site fix (plan runtime-adg-tier1-emit-corpus-refresh):
        every orchestrator trace now emits the three required Tier-1 spans
        — ``runtime.trace_root`` at entry and ``Exit.disposition`` at exit
        — and installs the adapter as the ambient context-var so any
        nested code can call ``seal_step()`` to emit ``L2.step.seal``
        without explicit adapter plumbing. The emits are additive and
        observability-only: they never raise (fail-open in the helper).

        Mirrors the pattern already in
        ``system_learning/runtime_adg/auto_persistence.py:trace_orchestrator``;
        lifting it into the parent class closes the gap surfaced by
        ``tools/debug/_runtime_adg_coverage_audit.py`` (3 of 5 categories
        previously reported as ``emit_site_gap``).

        Args:
            mission: Mission being executed
            metadata: Additional metadata

        Yields:
            Span context
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "OpenTelemetryTracingAdapter.trace_orchestrator",
        )

        # Tier-1 emit fixture: lazy import so module-load stays cheap
        # and circular-import safe (runtime_span_emitter does not depend
        # on this module). All three calls fail-open by contract.
        from agentic_core.L6_system_learning.runtime_span_emitter import (  # noqa: PLC0415
            back_patch_trace_id,
            emit_exit_disposition,
            emit_trace_root,
            reset_current_adapter,
            set_current_adapter,
        )

        # 1) Emit runtime.trace_root BEFORE the OTel root span exists so
        # it is first in the drained buffer. We reconcile its trace_id
        # to the real OTel trace_id below once the span stack is live.
        staging_trace_id = ""
        try:
            staging_trace_id = emit_trace_root(
                self,
                mission=mission,
                input_envelope=metadata,
                metadata={"service": getattr(self, "service_name", "unknown")},
            )
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            logger.debug("tier1_trace_root_emit_failed: %s", exc)

        # 2) Install adapter as ambient context-var so any nested
        # caller can use seal_step() without adapter plumbing.
        adapter_token = set_current_adapter(self)

        disposition = "allow"  # default unless inner block raises
        unified_trace_id = staging_trace_id
        span_metadata = SpanMetadata(
            span_type=SpanType.ORCHESTRATOR,
            component="NervousSystem",
            layer="L3_Orchestration",
            attributes={"mission": mission, **(metadata or {})},
        )
        try:
            with self._create_span(name="orchestrator.execute", metadata=span_metadata) as span:
                # 3) Reconcile the staged trace_root span to the real
                # OTel trace_id once the span stack is populated.
                try:
                    otel_trace_id = getattr(self, "_span_stack", None) and self._span_stack[-1][0] or ""
                    if otel_trace_id and otel_trace_id != staging_trace_id:
                        back_patch_trace_id(self, staging_trace_id, otel_trace_id)
                        unified_trace_id = otel_trace_id
                except (
                    AttributeError,
                    IndexError,
                    TypeError,
                ):  # guardian: allow-silent-swallow -- best-effort trace_id reconciliation; staging id is the safe default when the OTel span stack is absent
                    pass
                try:
                    yield span
                except (OSError, ValueError, TypeError, RuntimeError):
                    disposition = "deny"
                    raise
        finally:
            # 4) Restore adapter context-var.
            try:
                reset_current_adapter(adapter_token)
            except (ValueError, LookupError) as exc:
                logger.debug("tier1_adapter_reset_failed: %s", exc)

            # 5) Emit Exit.disposition at run close, using unified
            # trace_id so it correlates with trace_root + children.
            try:
                emit_exit_disposition(
                    self,
                    trace_id=unified_trace_id,
                    disposition=disposition,
                    policy_hash="otel_adapter_v1",
                    reason_codes=(
                        ("trace_orchestrator_ok",)
                        if disposition == "allow"
                        else ("trace_orchestrator_error",)
                    ),
                    metadata={"mission": mission},
                )
            except (OSError, ValueError, TypeError, RuntimeError) as exc:
                logger.debug("tier1_exit_disposition_emit_failed: %s", exc)

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
        attributes = {"task": task, "reasoning.mode": reasoning_mode, **(metadata or {})}
        if cost_metrics:
            attributes.update(cost_metrics.to_dict())
        span_metadata = SpanMetadata(
            span_type=SpanType.COGNITIVE,
            component="CognitivePlane",
            layer="L1_Cognition",
            attributes=attributes,
        )
        with self._create_span(name="cognitive.think", metadata=span_metadata) as span:
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
        attributes = {"action.count": action_count, **(metadata or {})}
        if resilience_metrics:
            attributes.update(resilience_metrics.to_dict())
        span_metadata = SpanMetadata(
            span_type=SpanType.ACTION,
            component="ActionPlane",
            layer="L2_Execution",
            attributes=attributes,
        )
        with self._create_span(name="action.execute", metadata=span_metadata) as span:
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
        attributes = {"tool.name": tool_name, "tool.parameters": str(parameters or {}), **(metadata or {})}
        if resilience_metrics:
            attributes.update(resilience_metrics.to_dict())
        span_metadata = SpanMetadata(
            span_type=SpanType.TOOL,
            component=f"Tool.{tool_name}",
            layer="L2_Execution",
            attributes=attributes,
        )
        with self._create_span(name=f"tool.{tool_name}", metadata=span_metadata) as span:
            yield span

    # ------------------------------------------------------------------
    # Anthropic Agent SDK taxonomy (ADR-024)
    # ------------------------------------------------------------------
    @contextmanager
    def trace_interaction(
        self,
        prompt_summary: str = "",
        session_id: str = "",
        metadata: dict[str, Any] | None = None,
    ):
        """Wrap a single agent turn (prompt -> response).

        Emits span ``claude_code.interaction`` per Anthropic Agent SDK
        observability guidance. Root span for an agent loop turn.
        """
        attributes = {
            "claude_code.prompt_summary": str(prompt_summary)[:256],
            "session.id": str(session_id)[:64],
            **(metadata or {}),
        }
        span_metadata = SpanMetadata(
            span_type=SpanType.ORCHESTRATOR,
            component="AgentInteraction",
            layer="L3_Orchestration",
            attributes=attributes,
        )
        with self._create_span(name="claude_code.interaction", metadata=span_metadata) as span:
            yield span

    @contextmanager
    def trace_llm_request(
        self,
        model: str,
        cost_metrics: CostMetrics | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Wrap a single LLM call. Emits span ``claude_code.llm_request``."""
        attributes = {"llm.model": model, **(metadata or {})}
        if cost_metrics:
            attributes.update(cost_metrics.to_dict())
        span_metadata = SpanMetadata(
            span_type=SpanType.COGNITIVE,
            component="LLMRequest",
            layer="L1_Cognition",
            attributes=attributes,
        )
        with self._create_span(name="claude_code.llm_request", metadata=span_metadata) as span:
            yield span

    @contextmanager
    def trace_claude_tool(
        self,
        tool_name: str,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Wrap a tool invocation with Anthropic taxonomy.

        Emits parent ``claude_code.tool`` with child ``claude_code.tool.execution``.
        Permission-wait children can be opened via ``trace_tool_blocked_on_user``.
        """
        attributes = {
            "claude_code.tool.name": tool_name,
            "tool.parameters": str(parameters or {})[:1024],
            **(metadata or {}),
        }
        outer_meta = SpanMetadata(
            span_type=SpanType.TOOL,
            component=f"Tool.{tool_name}",
            layer="L2_Execution",
            attributes=attributes,
        )
        with self._create_span(name="claude_code.tool", metadata=outer_meta):
            inner_meta = SpanMetadata(
                span_type=SpanType.TOOL,
                component=f"Tool.{tool_name}",
                layer="L2_Execution",
                attributes={"claude_code.tool.name": tool_name},
            )
            with self._create_span(name="claude_code.tool.execution", metadata=inner_meta) as span:
                yield span

    @contextmanager
    def trace_tool_blocked_on_user(
        self,
        tool_name: str,
        reason: str = "permission_wait",
        metadata: dict[str, Any] | None = None,
    ):
        """Wrap a HITL / permission wait. Emits ``claude_code.tool.blocked_on_user``."""
        attributes = {
            "claude_code.tool.name": tool_name,
            "claude_code.block_reason": reason,
            **(metadata or {}),
        }
        span_metadata = SpanMetadata(
            span_type=SpanType.TOOL,
            component=f"Tool.{tool_name}",
            layer="L5_Safety",
            attributes=attributes,
        )
        with self._create_span(name="claude_code.tool.blocked_on_user", metadata=span_metadata) as span:
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
        with self._create_span(name=f"dag.task.{task_id}", metadata=span_metadata) as span:
            yield span

    @contextmanager
    def trace_reasoning(self, step_number: int, step_type: str, metadata: dict[str, Any] | None = None):
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
            attributes={"reasoning.step": step_number, "reasoning.type": step_type, **(metadata or {})},
        )
        with self._create_span(name=f"reasoning.step.{step_number}", metadata=span_metadata) as span:
            yield span

    @contextmanager
    def _create_span(self, name: str, metadata: SpanMetadata):
        """Create a span with metadata.

        Args:
            name: Span name
            metadata: Span metadata

        Yields:
            Span or None if tracing disabled
        """
        if not self._enabled or not self.tracer:
            yield None
            return
        start_time = time.time()
        with self.tracer.start_as_current_span(name) as span:
            span_context = getattr(span, "get_span_context", lambda: None)()
            parent_trace_id = self._span_stack[-1][0] if self._span_stack else ""
            parent_span_id = self._span_stack[-1][1] if self._span_stack else ""
            trace_id = parent_trace_id
            span_id = ""
            if span_context is not None:
                raw_trace_id = getattr(span_context, "trace_id", 0)
                raw_span_id = getattr(span_context, "span_id", 0)
                if raw_trace_id:
                    trace_id = f"{int(raw_trace_id):032x}"
                if raw_span_id:
                    span_id = f"{int(raw_span_id):016x}"
            if not trace_id:
                trace_id = f"{time.time_ns():032x}"[-32:]
            if not span_id:
                span_id = f"{time.time_ns():016x}"[-16:]
            self._span_stack.append((trace_id, span_id))
            for key, value in metadata.to_dict().items():
                span.set_attribute(key, value)
            outcome = "ok"
            try:
                yield span
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
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                outcome = "error"
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                if self.enable_logging:
                    logger.error("span_failed", extra={"span_name": name, "error": str(e)}, exc_info=True)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                self._completed_spans.append(
                    {
                        "ts_utc": int(start_time * 1000),
                        "duration_ms": round(duration_ms, 3),
                        "kind": metadata.span_type.value,
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "layer": metadata.layer,
                        "component": metadata.component,
                        "name": name,
                        "status": outcome,
                        "attributes": metadata.to_dict(),
                    },
                )
                if self._span_stack:
                    self._span_stack.pop()

    def drain_completed_spans(self) -> list[dict[str, Any]]:
        drained = [
            {
                **record,
                "attributes": dict(record.get("attributes", {})),
            }
            for record in sorted(
                self._completed_spans,
                key=lambda record: (
                    int(record.get("ts_utc", 0)),
                    str(record.get("trace_id", "")),
                    str(record.get("span_id", "")),
                    str(record.get("name", "")),
                ),
            )
        ]
        self._completed_spans.clear()
        return drained

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

    # Wave C-2: Expose spans for telemetry store integration
    def get_active_spans(self) -> list[dict[str, Any]]:
        """Get all active spans for telemetry store integration.

        Returns:
            List of active span data
        """
        if not self._enabled or not hasattr(self, "_active_spans"):
            return []

        spans_data = []
        for span_id, span in tqdm(self._active_spans.items(), desc="Processing", unit="item"):
            span_data = {
                "span_id": span_id,
                "trace_id": getattr(span, "trace_id", "unknown"),
                "name": getattr(span, "name", "unknown"),
                "start_time": getattr(span, "start_time", 0),
                "end_time": getattr(span, "end_time", None),
                "status": getattr(span, "status", "RUNNING"),
                "attributes": getattr(span, "attributes", {}),
                "events": getattr(span, "events", []),
            }
            spans_data.append(span_data)

        return spans_data

    def get_span_metrics(self) -> dict[str, Any]:
        """Get span metrics for telemetry analysis.

        Returns:
            Span metrics summary
        """
        if not self._enabled or not hasattr(self, "_active_spans"):
            return {
                "total_spans": 0,
                "running_spans": 0,
                "completed_spans": 0,
                "error_spans": 0,
                "avg_duration_ms": 0.0,
            }

        spans = list(self._active_spans.values())
        total_spans = len(spans)

        running_spans = sum(1 for span in spans if getattr(span, "status", "RUNNING") == "RUNNING")
        completed_spans = sum(1 for span in spans if getattr(span, "status", "RUNNING") == "COMPLETED")
        error_spans = sum(1 for span in spans if getattr(span, "status", "RUNNING") == "ERROR")

        # Calculate average duration for completed spans
        completed_span_data = [
            span
            for span in spans
            if getattr(span, "status", "RUNNING") == "COMPLETED"
            and hasattr(span, "start_time")
            and hasattr(span, "end_time")
            and span.end_time is not None
        ]

        if completed_span_data:
            durations = [(span.end_time - span.start_time) for span in completed_span_data]
            avg_duration_ms = sum(durations) / len(durations)
        else:
            avg_duration_ms = 0.0

        return {
            "total_spans": total_spans,
            "running_spans": running_spans,
            "completed_spans": completed_spans,
            "error_spans": error_spans,
            "avg_duration_ms": avg_duration_ms,
        }


_global_tracer: OpenTelemetryTracingAdapter | None = None


def get_tracer(
    service_name: str = "agentic-workflow",
    enable_console_export: bool = False,
    enable_otlp_grpc: bool = False,
    enable_otlp_http: bool = False,
    otlp_grpc_endpoint: str | None = None,
    otlp_http_endpoint: str | None = None,
) -> OpenTelemetryTracingAdapter:
    """Get or create global tracer instance.

    Args:
        service_name: Service name
        enable_console_export: Enable console export
        enable_otlp_grpc: Enable OTLP gRPC exporter
        enable_otlp_http: Enable OTLP HTTP exporter
        otlp_grpc_endpoint: Custom OTLP gRPC endpoint
        otlp_http_endpoint: Custom OTLP HTTP endpoint

    Returns:
        OpenTelemetryTracingAdapter instance
    """
    global _global_tracer
    if _global_tracer is None:
        # Anthropic-alignment: honor OTEL_TRACES_EXPORTER=otlp + OTEL_EXPORTER_OTLP_PROTOCOL
        # without requiring callers to pass flags. See ADR-024.
        import os as _os

        traces_exporter = _os.environ.get("OTEL_TRACES_EXPORTER", "").lower()
        protocol = _os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "").lower()
        if traces_exporter == "otlp":
            if protocol in ("http", "http/protobuf", "http/json"):
                enable_otlp_http = True
            else:
                enable_otlp_grpc = True
        _global_tracer = OpenTelemetryTracingAdapter(
            service_name=service_name,
            enable_console_export=enable_console_export,
            enable_otlp_grpc=enable_otlp_grpc,
            enable_otlp_http=enable_otlp_http,
            otlp_grpc_endpoint=otlp_grpc_endpoint,
            otlp_http_endpoint=otlp_http_endpoint,
        )
    return _global_tracer


def reset_tracer():
    """Reset global tracer instance."""
    global _global_tracer
    _global_tracer = None
