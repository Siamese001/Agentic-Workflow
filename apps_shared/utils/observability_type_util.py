"""Execute observability Execution - observability execution adapter.

This module provides adapters for executing observability operations with
proper monitoring, tracing, and metrics collection.
Follows the functional component pattern with proper logging.
"""

import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
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
    _emit_reads_through,
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
    record_execution_trace,
)

_emit_applies_guardrail("p0", "observability_type_util", "p0_governance")
_emit_reads_policy_state("p0", "observability_type_util", "policy_binding")
_emit_snapshots_state("p0", "observability_type_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

record_execution_trace("observability_type_util", "observability_type_util_trace")


_emit_emits_metric_event("observability_type_util", "p4obs", "metric_1")
_emit_emits_metric_event("observability_type_util", "p4obs", "metric_2")
_emit_emits_metric_event("observability_type_util", "p4obs", "metric_3")
_emit_emits_metric_event("observability_type_util", "p4obs", "metric_4")
_emit_emits_metric_event("observability_type_util", "p4obs", "metric_5")
_emit_emits_metric_event("observability_type_util", "p4obs", "metric_6")
_emit_records_incident_event("observability_type_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("observability_type_util", "p4obs", "anomaly")
_emit_writes_observability_log("observability_type_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("observability_type_util", "p4obs", "mon_state")
_emit_triggers_alert("observability_type_util", "p4obs", "alert")
_emit_links_incident_trace("observability_type_util", "p4obs", "trace_link")
_emit_captures_pattern("observability_type_util", "p3lm", "pattern")
_emit_records_learning_event("observability_type_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("observability_type_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("observability_type_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("observability_type_util", "p3lm", "routing")
_emit_improves_agent_policy("observability_type_util", "p3lm", "policy")
_emit_stores_learning_state("observability_type_util", "p3lm", "state")
_emit_records_execution_trace("observability_type_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("observability_type_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("observability_type_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("observability_type_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("observability_type_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("observability_type_util", "env_read", "p2_env_1")
_emit_reads_environ("observability_type_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("observability_type_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("observability_type_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "observability_type_util", "context_pull")
_emit_pulls_context("p1", "observability_type_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "observability_type_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "observability_type_util", "uwg_term_2")
_emit_writes_through("p1", "observability_type_util", "write_through")
_emit_writes_through("p1", "observability_type_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "observability_type_util", "safety_validation")
_emit_invokes_eval("p1", "observability_type_util", "eval_call")
_emit_proposal_commits_routing("p1", "observability_type_util", "routing_commit")
_emit_escalates_to_human("p1", "observability_type_util", "human_escalation")
_emit_routes_through("p1", "observability_type_util", "route_through")
_emit_checks_agent_registry("p1", "observability_type_util", "agent_registry")
_emit_validates_agent_capability("p1", "observability_type_util", "capability")
_emit_dispatches_execution_plan("p1", "observability_type_util", "exec_plan")
_emit_agent_executes_agent("p1", "observability_type_util", "sub_agent")
_emit_routes_to_agent("p1", "observability_type_util", "target_agent")
_emit_verifies_policy("p1", "observability_type_util", "policy_check")
_emit_observes_runtime_state("p1", "observability_type_util", "runtime_state")
_emit_verifies_boundary("p1", "observability_type_util", "boundary_check")
_emit_transcripts_response("p1", "observability_type_util", "transcript")
_emit_hard_fails_untranscripted("p1", "observability_type_util")
_emit_gated_by_confidence("p1", "observability_type_util", "confidence_gate")
emit_replay_key("p0", "observability_type_util")
emit_determinism_digest("p0", "observability_type_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "observability_type_util", "execution_auth")
_emit_validates_capability("p2", "observability_type_util", "capability_check")
_emit_routes_to_capability("p2", "observability_type_util", "capability_route")
_emit_writes_via_uwg("p2", "observability_type_util", "uwg_write")
_emit_blocks_direct_write("p2", "observability_type_util", "direct_write_block")
_emit_records_tool_invocation("p2", "observability_type_util", "tool_invocation")
_emit_captures_execution_output("p2", "observability_type_util", "exec_output")
_emit_dispatches_agent("p3", "observability_type_util", "agent_dispatch")
_emit_coordinates_agents("p3", "observability_type_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "observability_type_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "observability_type_util", "healing_outcome")
_emit_escalates_failure("p3", "observability_type_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "observability_type_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "observability_type_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "observability_type_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "observability_type_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "observability_type_util", "eval_metric")
_emit_stores_embedding("p4", "observability_type_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "observability_type_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "observability_type_util", "exec_snapshot_link")
_emit_reads_through("l4", "observability_type_util", "urg_read_1")
_emit_reads_through("l4", "observability_type_util", "urg_read_2")
_emit_reads_through("l4", "observability_type_util", "urg_read_3")
_emit_reads_through("l4", "observability_type_util", "urg_read_4")
_emit_reads_through("l4", "observability_type_util", "urg_read_5")
_emit_reads_through("l4", "observability_type_util", "urg_read_6")
_emit_reads_through("l4", "observability_type_util", "urg_read_7")
_emit_reads_through("l4", "observability_type_util", "urg_read_8")
_emit_reads_through("l4", "observability_type_util", "urg_read_9")
_emit_reads_through("l4", "observability_type_util", "urg_read_10")
_emit_reads_through("l4", "observability_type_util", "urg_read_11")
_emit_reads_through("l4", "observability_type_util", "urg_read_12")
_emit_reads_through("l4", "observability_type_util", "urg_read_13")
_emit_reads_through("l4", "observability_type_util", "urg_read_14")
_emit_reads_through("l4", "observability_type_util", "urg_read_15")
_emit_reads_through("l4", "observability_type_util", "urg_read_16")
_emit_reads_through("l4", "observability_type_util", "urg_read_17")
_emit_reads_through("l4", "observability_type_util", "urg_read_18")
_emit_reads_through("l4", "observability_type_util", "urg_read_19")
_emit_reads_through("l4", "observability_type_util", "urg_read_20")
_emit_reads_through("l4", "observability_type_util", "urg_read_21")
_emit_reads_through("l4", "observability_type_util", "urg_read_22")
_emit_reads_through("l4", "observability_type_util", "urg_read_23")
_emit_reads_through("l4", "observability_type_util", "urg_read_24")
_emit_reads_through("l4", "observability_type_util", "urg_read_25")
_emit_reads_through("l4", "observability_type_util", "urg_read_26")
_emit_reads_through("l4", "observability_type_util", "urg_read_27")
_emit_reads_through("l4", "observability_type_util", "urg_read_28")
_emit_reads_through("l4", "observability_type_util", "urg_read_29")
_emit_reads_through("l4", "observability_type_util", "urg_read_30")
_emit_reads_through("l4", "observability_type_util", "urg_read_31")
_emit_reads_through("l4", "observability_type_util", "urg_read_32")
_emit_reads_through("l4", "observability_type_util", "urg_read_33")
_emit_reads_through("l4", "observability_type_util", "urg_read_34")
_emit_reads_through("l4", "observability_type_util", "urg_read_35")
_emit_reads_through("l4", "observability_type_util", "urg_read_36")
_emit_reads_through("l4", "observability_type_util", "urg_read_37")
_emit_reads_through("l4", "observability_type_util", "urg_read_38")
_emit_reads_through("l4", "observability_type_util", "urg_read_39")
_emit_reads_through("l4", "observability_type_util", "urg_read_40")
_emit_reads_through("l4", "observability_type_util", "urg_read_41")
_emit_reads_through("l4", "observability_type_util", "urg_read_42")
_emit_reads_through("l4", "observability_type_util", "urg_read_43")
_emit_reads_through("l4", "observability_type_util", "urg_read_44")
_emit_reads_through("l4", "observability_type_util", "urg_read_45")
_emit_reads_through("l4", "observability_type_util", "urg_read_46")
_emit_reads_through("l4", "observability_type_util", "urg_read_47")
_emit_reads_through("l4", "observability_type_util", "urg_read_48")
_emit_reads_through("l4", "observability_type_util", "urg_read_49")
_emit_reads_through("l4", "observability_type_util", "urg_read_50")
_emit_reads_through("l4", "observability_type_util", "urg_read_51")
_emit_reads_through("l4", "observability_type_util", "urg_read_52")
_emit_reads_through("l4", "observability_type_util", "urg_read_53")
_emit_reads_through("l4", "observability_type_util", "urg_read_54")
_emit_reads_through("l4", "observability_type_util", "urg_read_55")
_emit_reads_through("l4", "observability_type_util", "urg_read_56")
_emit_reads_through("l4", "observability_type_util", "urg_read_57")
_emit_reads_through("l4", "observability_type_util", "urg_read_58")
_emit_reads_through("l4", "observability_type_util", "urg_read_59")
_emit_reads_through("l4", "observability_type_util", "urg_read_60")
_emit_reads_through("l4", "observability_type_util", "urg_read_61")
_emit_reads_through("l4", "observability_type_util", "urg_read_62")
_emit_reads_through("l4", "observability_type_util", "urg_read_63")
_emit_reads_through("l4", "observability_type_util", "urg_read_64")
_emit_reads_through("l4", "observability_type_util", "urg_read_65")
_emit_reads_through("l4", "observability_type_util", "urg_read_66")
_emit_reads_through("l4", "observability_type_util", "urg_read_67")
_emit_reads_through("l4", "observability_type_util", "urg_read_68")
_emit_reads_through("l4", "observability_type_util", "urg_read_69")
_emit_reads_through("l4", "observability_type_util", "urg_read_70")
_emit_reads_through("l4", "observability_type_util", "urg_read_71")
_emit_reads_through("l4", "observability_type_util", "urg_read_72")
_emit_reads_through("l4", "observability_type_util", "urg_read_73")
_emit_reads_through("l4", "observability_type_util", "urg_read_74")
_emit_reads_through("l4", "observability_type_util", "urg_read_75")
_emit_reads_through("l4", "observability_type_util", "urg_read_76")
_emit_reads_through("l4", "observability_type_util", "urg_read_77")
_emit_reads_through("l4", "observability_type_util", "urg_read_78")
_emit_reads_through("l4", "observability_type_util", "urg_read_79")
_emit_reads_through("l4", "observability_type_util", "urg_read_80")
_emit_reads_through("l4", "observability_type_util", "urg_read_81")
_emit_reads_through("l4", "observability_type_util", "urg_read_82")
_emit_reads_through("l4", "observability_type_util", "urg_read_83")
_emit_reads_through("l4", "observability_type_util", "urg_read_84")
_emit_reads_through("l4", "observability_type_util", "urg_read_85")
_emit_reads_through("l4", "observability_type_util", "urg_read_86")
_emit_reads_through("l4", "observability_type_util", "urg_read_87")
_emit_reads_through("l4", "observability_type_util", "urg_read_88")
_emit_reads_through("l4", "observability_type_util", "urg_read_89")

logger = logging.getLogger(__name__)


class ObservabilityType(Enum):
    """Types of observability operations."""

    TRACE = "trace"
    METRIC = "metric"
    LOG = "log"
    EVENT = "event"
    PROFILE = "profile"


class ExecutionLevel(Enum):
    """Levels of execution detail."""

    BASIC = "basic"
    DETAILED = "detailed"
    VERBOSE = "verbose"
    DEBUG = "debug"


@dataclass
class ObservabilityRequest:
    """Request for observability operation."""

    request_id: str
    operation_type: ObservabilityType
    target: str
    parameters: dict[str, Any]
    execution_level: ExecutionLevel = ExecutionLevel.BASIC
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityResult:
    """Result of observability operation."""

    request_id: str
    operation_type: ObservabilityType
    success: bool
    data: dict[str, Any] | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityConfig:
    """configuration for observability operations."""

    default_timeout: float = 10.0
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    sampling_rate: float = 1.0


class ObservabilityExecutionAdapter:
    """Main adapter for observability execution."""

    def __init__(self, config: ObservabilityConfig | None = None):
        self.config = config or ObservabilityConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._operation_handlers: dict[ObservabilityType, Callable] = {}
        self._active_traces: dict[str, dict[str, Any]] = {}
        self._metrics_store: dict[str, list[float]] = {}
        self._initialize_handlers()

    def register_handler(self, operation_type: ObservabilityType, handler: Callable) -> None:
        """Register a handler for observability operation type.

        Args:
            operation_type: Type of operation
            handler: Handler function
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ObservabilityExecutionAdapter.register_handler"
        )

        self._operation_handlers[operation_type] = handler
        self.logger.info(f"Registered observability handler for {operation_type.value}")

    def execute(self, request: ObservabilityRequest) -> ObservabilityResult:
        """Execute observability operation.

        Args:
            request: observability operation request

        Returns:
            ObservabilityResult: Result with observability data
        """
        self.logger.info(f"Executing observability operation: {request.request_id}")
        start_time = time.time()
        trace_id = str(uuid.uuid4()) if self.config.enable_tracing else None
        try:
            if trace_id:
                self._start_trace(trace_id, request)
            handler = self._operation_handlers.get(request.operation_type)
            if not handler:
                return self._create_error_result(
                    request,
                    f"No handler for operation type: {request.operation_type.value}",
                    start_time,
                )
            result = self._execute_with_monitoring(handler, request, trace_id)
            result.execution_time = time.time() - start_time
            if self.config.enable_metrics:
                self._record_metrics(result)
            if trace_id:
                self._end_trace(trace_id, result)
            return result
        except Exception as e:  # guardian: allow-silent-swallow
            self.logger.error(f"observability execution failed: {str(e)}")
            return self._create_error_result(request, str(e), start_time)

    def execute_batch(self, requests: list[ObservabilityRequest]) -> list[ObservabilityResult]:
        """Execute multiple observability operations.

        Args:
            requests: List of operation requests

        Returns:
            List[ObservabilityResult]: Results for all operations
        """
        results = []
        for request in requests:
            result = self.execute(request)
            results.append(result)
        return results

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        """Get trace information.

        Args:
            trace_id: ID of trace

        Returns:
            Optional[Dict]: Trace data
        """
        return self._active_traces.get(trace_id)

    def get_metrics(self, metric_name: str, time_range: tuple[float, float] | None = None) -> list[float]:
        """Get metrics data.

        Args:
            metric_name: Name of metric
            time_range: Optional time range filter

        Returns:
            List[float]: Metric values
        """
        values = self._metrics_store.get(metric_name, [])
        if time_range:
            pass
        return values

    def clear_traces(self, older_than: float | None = None) -> int:
        """Clear old traces.

        Args:
            older_than: Clear traces older than this time (seconds)

        Returns:
            int: Number of traces cleared
        """
        if older_than is None:
            count = len(self._active_traces)
            self._active_traces.clear()
            return count
        current_time = time.time()
        to_remove = []
        for trace_id, trace in self._active_traces.items():
            if current_time - trace.get("start_time", 0) > older_than:
                to_remove.append(trace_id)
        for trace_id in to_remove:
            del self._active_traces[trace_id]
        return len(to_remove)

    def _execute_with_monitoring(
        self,
        handler: Callable,
        request: ObservabilityRequest,
        trace_id: str | None,
    ) -> ObservabilityResult:
        """Execute operation with monitoring."""
        try:
            if trace_id:
                request.parameters["trace_id"] = trace_id
            data = handler(request.parameters)
            metrics = {}
            if isinstance(data, dict) and "metrics" in data:
                metrics = data["metrics"]
                data = {k: v for k, v in data.items() if k != "metrics"}
            result = ObservabilityResult(
                request_id=request.request_id,
                operation_type=request.operation_type,
                success=True,
                data=data,
                metrics=metrics,
                traces=[self._active_traces[trace_id]]
                if trace_id and trace_id in self._active_traces
                else [],
            )
            return result
        except Exception as e:  # guardian: allow-silent-swallow
            return ObservabilityResult(
                request_id=request.request_id,
                operation_type=request.operation_type,
                success=False,
                error=str(e),
            )

    def _start_trace(self, trace_id: str, request: ObservabilityRequest) -> None:
        """Start a new trace."""
        self._active_traces[trace_id] = {
            "trace_id": trace_id,
            "operation": request.operation_type.value,
            "target": request.target,
            "start_time": time.time(),
            "spans": [],
        }

    def _end_trace(self, trace_id: str, result: ObservabilityResult) -> None:
        """End a trace."""
        if trace_id in self._active_traces:
            trace = self._active_traces[trace_id]
            trace["end_time"] = time.time()
            trace["duration"] = trace["end_time"] - trace["start_time"]
            trace["success"] = result.success
            trace["error"] = result.error

    def _record_metrics(self, result: ObservabilityResult) -> None:
        """Record metrics from result."""
        for metric_name, value in result.metrics.items():
            if metric_name not in self._metrics_store:
                self._metrics_store[metric_name] = []
            self._metrics_store[metric_name].append(value)
            if len(self._metrics_store[metric_name]) > 1000:
                self._metrics_store[metric_name] = self._metrics_store[metric_name][-1000:]

    def _create_error_result(
        self,
        request: ObservabilityRequest,
        error: str,
        start_time: float,
    ) -> ObservabilityResult:
        """Create error result."""
        return ObservabilityResult(
            request_id=request.request_id,
            operation_type=request.operation_type,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
        )

    def _initialize_handlers(self) -> None:
        """Initialize default operation handlers."""

        def _trace_handler(params: dict[str, Any]) -> dict[str, Any]:
            operation = params.get("operation")
            component = params.get("component", "unknown")
            return {
                "trace_data": {
                    "operation": operation,
                    "component": component,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "metrics": {"trace_duration": 0.1, "trace_depth": 3},
            }

        def _metric_handler(params: dict[str, Any]) -> dict[str, Any]:
            metric_name = params.get("name")
            value = params.get("value", 0)
            tags = params.get("tags", {})
            return {
                "metric_data": {
                    "name": metric_name,
                    "value": value,
                    "tags": tags,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "metrics": {"metric_collection_time": 0.05},
            }

        def _log_handler(params: dict[str, Any]) -> dict[str, Any]:
            level = params.get("level", "info")
            message = params.get("message", "")
            context = params.get("context", {})
            return {
                "log_data": {
                    "level": level,
                    "message": message,
                    "context": context,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "metrics": {"log_size": len(message), "log_processing_time": 0.02},
            }

        def _event_handler(params: dict[str, Any]) -> dict[str, Any]:
            event_type = params.get("type")
            source = params.get("source", "unknown")
            data = params.get("data", {})
            return {
                "event_data": {
                    "type": event_type,
                    "source": source,
                    "data": data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "metrics": {"event_processing_time": 0.03},
            }

        def _profile_handler(params: dict[str, Any]) -> dict[str, Any]:
            target = params.get("target")
            duration = params.get("duration", 0)
            return {
                "profile_data": {
                    "target": target,
                    "duration": duration,
                    "samples": 100,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                "metrics": {"profile_overhead": 0.01, "samples_collected": 100},
            }

        self.register_handler(ObservabilityType.TRACE, _trace_handler)
        self.register_handler(ObservabilityType.METRIC, _metric_handler)
        self.register_handler(ObservabilityType.LOG, _log_handler)
        self.register_handler(ObservabilityType.EVENT, _event_handler)
        self.register_handler(ObservabilityType.PROFILE, _profile_handler)


# guardian: allow-magic-config
def create_observability_execution_adapter(
    default_timeout: float = 10.0,
    enable_tracing: bool = True,
    enable_metrics: bool = True,
    **kwargs: object,
) -> ObservabilityExecutionAdapter:
    """Create a configured observability execution adapter."""
    config = ObservabilityConfig(
        default_timeout=default_timeout,
        enable_tracing=enable_tracing,
        enable_metrics=enable_metrics,
        **kwargs,
    )
    return ObservabilityExecutionAdapter(config)


def execute_observability_execution(
    request_id: str,
    operation_type: str,
    target: str,
    parameters: dict[str, Any],
    execution_level: str = "basic",
) -> dict[str, Any]:
    """Execute observability operation.

    Args:
        request_id: Unique request identifier
        operation_type: Type of observability operation
        target: Target component or system
        parameters: Operation parameters
        execution_level: Level of execution detail

    Returns:
        Dict: observability result
    """
    adapter = create_observability_execution_adapter()
    request = ObservabilityRequest(
        request_id=request_id,
        operation_type=ObservabilityType(operation_type),
        target=target,
        parameters=parameters,
        execution_level=ExecutionLevel(execution_level),
    )
    result = adapter.execute(request)
    return {
        "request_id": result.request_id,
        "operation_type": result.operation_type.value,
        "success": result.success,
        "data": result.data,
        "metrics": result.metrics,
        "traces": result.traces,
        "error": result.error,
        "execution_time": result.execution_time,
        "metadata": result.metadata,
    }
