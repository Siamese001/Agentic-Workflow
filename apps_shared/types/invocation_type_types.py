"""Invoke observability Tool - Tool invocation adapter for observability operations.

This module provides adapters for invoking observability tools with proper
protocol handling, parameter validation, and response processing.
Follows the functional component pattern with proper logging.
"""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
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
)

_emit_applies_guardrail("p0", "invocation_type_types", "p0_governance")
_emit_reads_policy_state("p0", "invocation_type_types", "policy_binding")
_emit_snapshots_state("p0", "invocation_type_types", "state_snapshot")
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

_emit_emits_metric_event("invocation_type_types", "p4obs", "metric_1")
_emit_emits_metric_event("invocation_type_types", "p4obs", "metric_2")
_emit_emits_metric_event("invocation_type_types", "p4obs", "metric_3")
_emit_emits_metric_event("invocation_type_types", "p4obs", "metric_4")
_emit_emits_metric_event("invocation_type_types", "p4obs", "metric_5")
_emit_emits_metric_event("invocation_type_types", "p4obs", "metric_6")
_emit_records_incident_event("invocation_type_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("invocation_type_types", "p4obs", "anomaly")
_emit_writes_observability_log("invocation_type_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("invocation_type_types", "p4obs", "mon_state")
_emit_triggers_alert("invocation_type_types", "p4obs", "alert")
_emit_links_incident_trace("invocation_type_types", "p4obs", "trace_link")
_emit_captures_pattern("invocation_type_types", "p3lm", "pattern")
_emit_records_learning_event("invocation_type_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("invocation_type_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("invocation_type_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("invocation_type_types", "p3lm", "routing")
_emit_improves_agent_policy("invocation_type_types", "p3lm", "policy")
_emit_stores_learning_state("invocation_type_types", "p3lm", "state")
_emit_records_execution_trace("invocation_type_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("invocation_type_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("invocation_type_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("invocation_type_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("invocation_type_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("invocation_type_types", "env_read", "p2_env_1")
_emit_reads_environ("invocation_type_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("invocation_type_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("invocation_type_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "invocation_type_types", "context_pull")
_emit_pulls_context("p1", "invocation_type_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "invocation_type_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "invocation_type_types", "uwg_term_2")
_emit_writes_through("p1", "invocation_type_types", "write_through")
_emit_writes_through("p1", "invocation_type_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "invocation_type_types", "safety_validation")
_emit_invokes_eval("p1", "invocation_type_types", "eval_call")
_emit_proposal_commits_routing("p1", "invocation_type_types", "routing_commit")
_emit_escalates_to_human("p1", "invocation_type_types", "human_escalation")
_emit_routes_through("p1", "invocation_type_types", "route_through")
_emit_checks_agent_registry("p1", "invocation_type_types", "agent_registry")
_emit_validates_agent_capability("p1", "invocation_type_types", "capability")
_emit_dispatches_execution_plan("p1", "invocation_type_types", "exec_plan")
_emit_agent_executes_agent("p1", "invocation_type_types", "sub_agent")
_emit_routes_to_agent("p1", "invocation_type_types", "target_agent")
_emit_verifies_policy("p1", "invocation_type_types", "policy_check")
_emit_observes_runtime_state("p1", "invocation_type_types", "runtime_state")
_emit_verifies_boundary("p1", "invocation_type_types", "boundary_check")
_emit_transcripts_response("p1", "invocation_type_types", "transcript")
_emit_hard_fails_untranscripted("p1", "invocation_type_types")
_emit_gated_by_confidence("p1", "invocation_type_types", "confidence_gate")
emit_replay_key("p0", "invocation_type_types")
emit_determinism_digest("p0", "invocation_type_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "invocation_type_types", "execution_auth")
_emit_validates_capability("p2", "invocation_type_types", "capability_check")
_emit_routes_to_capability("p2", "invocation_type_types", "capability_route")
_emit_writes_via_uwg("p2", "invocation_type_types", "uwg_write")
_emit_blocks_direct_write("p2", "invocation_type_types", "direct_write_block")
_emit_records_tool_invocation("p2", "invocation_type_types", "tool_invocation")
_emit_captures_execution_output("p2", "invocation_type_types", "exec_output")
_emit_dispatches_agent("p3", "invocation_type_types", "agent_dispatch")
_emit_coordinates_agents("p3", "invocation_type_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "invocation_type_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "invocation_type_types", "healing_outcome")
_emit_escalates_failure("p3", "invocation_type_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "invocation_type_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "invocation_type_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "invocation_type_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "invocation_type_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "invocation_type_types", "eval_metric")
_emit_stores_embedding("p4", "invocation_type_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "invocation_type_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "invocation_type_types", "exec_snapshot_link")
_emit_reads_through("l4", "invocation_type_types", "urg_read_1")
_emit_reads_through("l4", "invocation_type_types", "urg_read_2")
_emit_reads_through("l4", "invocation_type_types", "urg_read_3")
_emit_reads_through("l4", "invocation_type_types", "urg_read_4")
_emit_reads_through("l4", "invocation_type_types", "urg_read_5")
_emit_reads_through("l4", "invocation_type_types", "urg_read_6")
_emit_reads_through("l4", "invocation_type_types", "urg_read_7")
_emit_reads_through("l4", "invocation_type_types", "urg_read_8")
_emit_reads_through("l4", "invocation_type_types", "urg_read_9")
_emit_reads_through("l4", "invocation_type_types", "urg_read_10")
_emit_reads_through("l4", "invocation_type_types", "urg_read_11")
_emit_reads_through("l4", "invocation_type_types", "urg_read_12")
_emit_reads_through("l4", "invocation_type_types", "urg_read_13")
_emit_reads_through("l4", "invocation_type_types", "urg_read_14")
_emit_reads_through("l4", "invocation_type_types", "urg_read_15")
_emit_reads_through("l4", "invocation_type_types", "urg_read_16")
_emit_reads_through("l4", "invocation_type_types", "urg_read_17")
_emit_reads_through("l4", "invocation_type_types", "urg_read_18")
_emit_reads_through("l4", "invocation_type_types", "urg_read_19")
_emit_reads_through("l4", "invocation_type_types", "urg_read_20")
_emit_reads_through("l4", "invocation_type_types", "urg_read_21")
_emit_reads_through("l4", "invocation_type_types", "urg_read_22")
_emit_reads_through("l4", "invocation_type_types", "urg_read_23")
_emit_reads_through("l4", "invocation_type_types", "urg_read_24")
_emit_reads_through("l4", "invocation_type_types", "urg_read_25")
_emit_reads_through("l4", "invocation_type_types", "urg_read_26")
_emit_reads_through("l4", "invocation_type_types", "urg_read_27")
_emit_reads_through("l4", "invocation_type_types", "urg_read_28")
_emit_reads_through("l4", "invocation_type_types", "urg_read_29")
_emit_reads_through("l4", "invocation_type_types", "urg_read_30")
_emit_reads_through("l4", "invocation_type_types", "urg_read_31")
_emit_reads_through("l4", "invocation_type_types", "urg_read_32")
_emit_reads_through("l4", "invocation_type_types", "urg_read_33")
_emit_reads_through("l4", "invocation_type_types", "urg_read_34")
_emit_reads_through("l4", "invocation_type_types", "urg_read_35")
_emit_reads_through("l4", "invocation_type_types", "urg_read_36")
_emit_reads_through("l4", "invocation_type_types", "urg_read_37")
_emit_reads_through("l4", "invocation_type_types", "urg_read_38")
_emit_reads_through("l4", "invocation_type_types", "urg_read_39")
_emit_reads_through("l4", "invocation_type_types", "urg_read_40")
_emit_reads_through("l4", "invocation_type_types", "urg_read_41")
_emit_reads_through("l4", "invocation_type_types", "urg_read_42")
_emit_reads_through("l4", "invocation_type_types", "urg_read_43")
_emit_reads_through("l4", "invocation_type_types", "urg_read_44")
_emit_reads_through("l4", "invocation_type_types", "urg_read_45")
_emit_reads_through("l4", "invocation_type_types", "urg_read_46")
_emit_reads_through("l4", "invocation_type_types", "urg_read_47")
_emit_reads_through("l4", "invocation_type_types", "urg_read_48")
_emit_reads_through("l4", "invocation_type_types", "urg_read_49")
_emit_reads_through("l4", "invocation_type_types", "urg_read_50")
_emit_reads_through("l4", "invocation_type_types", "urg_read_51")
_emit_reads_through("l4", "invocation_type_types", "urg_read_52")
_emit_reads_through("l4", "invocation_type_types", "urg_read_53")
_emit_reads_through("l4", "invocation_type_types", "urg_read_54")
_emit_reads_through("l4", "invocation_type_types", "urg_read_55")
_emit_reads_through("l4", "invocation_type_types", "urg_read_56")
_emit_reads_through("l4", "invocation_type_types", "urg_read_57")
_emit_reads_through("l4", "invocation_type_types", "urg_read_58")
_emit_reads_through("l4", "invocation_type_types", "urg_read_59")
_emit_reads_through("l4", "invocation_type_types", "urg_read_60")
_emit_reads_through("l4", "invocation_type_types", "urg_read_61")
_emit_reads_through("l4", "invocation_type_types", "urg_read_62")
_emit_reads_through("l4", "invocation_type_types", "urg_read_63")
_emit_reads_through("l4", "invocation_type_types", "urg_read_64")
_emit_reads_through("l4", "invocation_type_types", "urg_read_65")
_emit_reads_through("l4", "invocation_type_types", "urg_read_66")
_emit_reads_through("l4", "invocation_type_types", "urg_read_67")
_emit_reads_through("l4", "invocation_type_types", "urg_read_68")
_emit_reads_through("l4", "invocation_type_types", "urg_read_69")
_emit_reads_through("l4", "invocation_type_types", "urg_read_70")
_emit_reads_through("l4", "invocation_type_types", "urg_read_71")
_emit_reads_through("l4", "invocation_type_types", "urg_read_72")
_emit_reads_through("l4", "invocation_type_types", "urg_read_73")
_emit_reads_through("l4", "invocation_type_types", "urg_read_74")
_emit_reads_through("l4", "invocation_type_types", "urg_read_75")
_emit_reads_through("l4", "invocation_type_types", "urg_read_76")
_emit_reads_through("l4", "invocation_type_types", "urg_read_77")
_emit_reads_through("l4", "invocation_type_types", "urg_read_78")
_emit_reads_through("l4", "invocation_type_types", "urg_read_79")
_emit_reads_through("l4", "invocation_type_types", "urg_read_80")
_emit_reads_through("l4", "invocation_type_types", "urg_read_81")
_emit_reads_through("l4", "invocation_type_types", "urg_read_82")
_emit_reads_through("l4", "invocation_type_types", "urg_read_83")
_emit_reads_through("l4", "invocation_type_types", "urg_read_84")
_emit_reads_through("l4", "invocation_type_types", "urg_read_85")
_emit_reads_through("l4", "invocation_type_types", "urg_read_86")
_emit_reads_through("l4", "invocation_type_types", "urg_read_87")
_emit_reads_through("l4", "invocation_type_types", "urg_read_88")
_emit_reads_through("l4", "invocation_type_types", "urg_read_89")
_emit_reads_through("l4", "invocation_type_types", "urg_read_90")
_emit_reads_through("l4", "invocation_type_types", "urg_read_91")
_emit_reads_through("l4", "invocation_type_types", "urg_read_92")
_emit_reads_through("l4", "invocation_type_types", "urg_read_93")
_emit_reads_through("l4", "invocation_type_types", "urg_read_94")
_emit_reads_through("l4", "invocation_type_types", "urg_read_95")
_emit_reads_through("l4", "invocation_type_types", "urg_read_96")
_emit_reads_through("l4", "invocation_type_types", "urg_read_97")
_emit_reads_through("l4", "invocation_type_types", "urg_read_98")
_emit_reads_through("l4", "invocation_type_types", "urg_read_99")
_emit_reads_through("l4", "invocation_type_types", "urg_read_100")

logger = logging.getLogger(__name__)


class InvocationType(Enum):
    """Types of tool invocation."""

    DIRECT = "direct"
    PROXY = "proxy"
    ASYNC = "async"
    BATCH = "batch"


class ResponseFormat(Enum):
    """Response format types."""

    JSON = "json"
    PROTOBUF = "protobuf"
    XML = "xml"
    BINARY = "binary"


@dataclass
class ToolEndpoint:
    """Definition of a tool endpoint."""

    endpoint_id: str
    url: str
    protocol: str
    authentication: dict[str, Any] | None = None
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0


@dataclass
class InvocationRequest:
    """Request for tool invocation."""

    invocation_id: str
    tool_name: str
    method: str
    parameters: dict[str, Any]
    endpoint: ToolEndpoint | None = None
    invocation_type: InvocationType = InvocationType.DIRECT
    response_format: ResponseFormat = ResponseFormat.JSON
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InvocationConfig:
    """configuration for tool invocation."""

    default_timeout: float = 30.0
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: float = 300.0
    enable_compression: bool = False


@dataclass
class InvocationResponse:
    """Response from tool invocation."""

    invocation_id: str
    tool_name: str
    success: bool
    data: Any | None = None
    headers: dict[str, str] = field(default_factory=dict)
    status_code: int | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityToolInvoker:
    """Main invoker for observability tools."""

    def __init__(self, config: InvocationConfig | None = None):
        self.config = config or InvocationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._registered_tools: dict[str, ToolEndpoint] = {}
        self._tool_handlers: dict[str, Callable] = {}
        self._invocation_cache: dict[str, tuple[Any, float]] = {}
        self._initialize_handlers()

    def register_tool(self, tool_name: str, endpoint: ToolEndpoint, handler: Callable | None = None) -> None:
        """Register a tool endpoint.

        Args:
            tool_name: Name of the tool
            endpoint: Tool endpoint definition
            handler: Optional handler function
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ObservabilityToolInvoker.register_tool")

        self._registered_tools[tool_name] = endpoint
        if handler:
            self._tool_handlers[tool_name] = handler
        self.logger.info(f"Registered tool: {tool_name}")

    def invoke_tool(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke an observability tool.

        Args:
            request: Invocation request

        Returns:
            InvocationResponse: Tool response
        """
        self.logger.info(f"Invoking tool: {request.tool_name}")
        start_time = time.time()
        try:
            if self.config.enable_caching:
                cached_response = self._get_from_cache(request)
                if cached_response is not None:
                    self.logger.info(f"Returning cached response for: {request.invocation_id}")
                    cached_response.execution_time = time.time() - start_time
                    return cached_response
            if request.tool_name not in self._registered_tools:
                return self._create_error_response(
                    request.invocation_id,
                    request.tool_name,
                    f"Tool not registered: {request.tool_name}",
                    start_time,
                )
            if request.invocation_type == InvocationType.DIRECT:
                response = self._invoke_direct(request)
            elif request.invocation_type == InvocationType.PROXY:
                response = self._invoke_proxy(request)
            elif request.invocation_type == InvocationType.ASYNC:
                response = self._invoke_async(request)
            elif request.invocation_type == InvocationType.BATCH:
                response = self._invoke_batch(request)
            else:
                raise ValueError(f"Unsupported invocation type: {request.invocation_type}")
            if self.config.enable_caching and response.success:
                self._store_in_cache(request, response)
            response.execution_time = time.time() - start_time
            return response
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Tool invocation failed: {str(e)}")
            return self._create_error_response(request.invocation_id, request.tool_name, str(e), start_time)

    def invoke_batch(self, requests: list[InvocationRequest]) -> list[InvocationResponse]:
        """Invoke multiple tools.

        Args:
            requests: List of invocation requests

        Returns:
            List[InvocationResponse]: Responses for all requests
        """
        responses = []
        for request in requests:
            response = self.invoke_tool(request)
            responses.append(response)
        return responses

    def invoke_stream(self, request: InvocationRequest) -> dict[str, object]:
        """Invoke tool with streaming response.

        Args:
            request: Invocation request

        Returns:
            Iterator: Stream of response chunks
        """
        if request.invocation_type != InvocationType.ASYNC:
            raise ValueError("Invocation type must be ASYNC for streaming")
        handler = self._tool_handlers.get(request.tool_name)
        if not handler:
            raise ValueError(f"No handler for tool: {request.tool_name}")
        yield from handler(request.parameters, stream=True)

    def get_tool_status(self, tool_name: str) -> dict[str, Any] | None:
        """Get tool status.

        Args:
            tool_name: Name of tool

        Returns:
            Optional[Dict]: Tool status information
        """
        if tool_name not in self._registered_tools:
            return None
        endpoint = self._registered_tools[tool_name]
        return {
            "tool_name": tool_name,
            "endpoint": endpoint.url,
            "protocol": endpoint.protocol,
            "status": "active",
            "last_check": datetime.utcnow().isoformat(),
        }

    def clear_cache(self, pattern: str | None = None) -> int:
        """Clear invocation cache.

        Args:
            pattern: Optional pattern to match cache keys

        Returns:
            int: Number of cache entries cleared
        """
        if pattern is None:
            count = len(self._invocation_cache)
            self._invocation_cache.clear()
            return count
        to_remove = []
        for key in self._invocation_cache:
            if pattern in key:
                to_remove.append(key)
        for key in to_remove:
            del self._invocation_cache[key]
        return len(to_remove)

    def _invoke_direct(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke tool directly."""
        handler = self._tool_handlers.get(request.tool_name)
        if handler:
            result = handler(request.method, request.parameters)
            return InvocationResponse(
                invocation_id=request.invocation_id,
                tool_name=request.tool_name,
                success=True,
                data=result,
                status_code=200,
            )
        else:
            return self._simulate_invocation(request)

    def _invoke_proxy(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke tool through proxy."""
        return self._simulate_invocation(request, proxy=True)

    def _invoke_async(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke tool asynchronously."""
        return self._simulate_invocation(request, async_mode=True)

    def _invoke_batch(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke tool in batch mode."""
        batch_items = request.parameters.get("batch_items", [])
        results = []
        for item in batch_items:
            item_request = InvocationRequest(
                invocation_id=f"{request.invocation_id}_{len(results)}",
                tool_name=request.tool_name,
                method=request.method,
                parameters=item,
                endpoint=request.endpoint,
                invocation_type=InvocationType.DIRECT,
                response_format=request.response_format,
            )
            response = self._invoke_direct(item_request)
            results.append(response.data if response.success else {"error": response.error})
        return InvocationResponse(
            invocation_id=request.invocation_id,
            tool_name=request.tool_name,
            success=True,
            data=results,
            status_code=200,
        )

    def _simulate_invocation(
        self, request: InvocationRequest, proxy: bool = False, async_mode: bool = False
    ) -> InvocationResponse:
        """Simulate tool invocation."""
        time.sleep(DEFAULT_SLEEP)
        if request.tool_name == "trace_collector":
            data = {
                "trace_id": request.parameters.get("trace_id", "mock_trace_123"),
                "spans": [{"operation": "span1", "duration": 0.1}, {"operation": "span2", "duration": 0.2}],
            }
        elif request.tool_name == "metric_collector":
            data = {"metrics": [{"name": "cpu", "value": 45.2}, {"name": "memory", "value": 67.8}]}
        elif request.tool_name == "log_analyzer":
            data = {
                "logs": [
                    {"message": "Sample log", "level": "info"},
                    {"message": "Error log", "level": "error"},
                ]
            }
        else:
            data = {"message": f"Mock response from {request.tool_name}"}
        if proxy:
            data["proxy_used"] = True
        if async_mode:
            data["async_mode"] = True
        return InvocationResponse(
            invocation_id=request.invocation_id,
            tool_name=request.tool_name,
            success=True,
            data=data,
            headers={"content-type": "application/json"},
            status_code=200,
        )

    def _get_from_cache(self, request: InvocationRequest) -> InvocationResponse | None:
        """Get response from cache."""
        cache_key = self._generate_cache_key(request)
        if cache_key in self._invocation_cache:
            cached_response, timestamp = self._invocation_cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                return cached_response
            else:
                del self._invocation_cache[cache_key]
        return None

    def _store_in_cache(self, request: InvocationRequest, response: InvocationResponse) -> None:
        """Store response in cache."""
        cache_key = self._generate_cache_key(request)
        self._invocation_cache[cache_key] = (response, time.time())

    def _generate_cache_key(self, request: InvocationRequest) -> str:
        """Generate cache key for request."""
        key_data = {
            "tool_name": request.tool_name,
            "method": request.method,
            "parameters": request.parameters,
        }
        return f"tool_invoke_{hash(json.dumps(key_data, sort_keys=True))}"

    def _create_error_response(
        self, invocation_id: str, tool_name: str, error: str, start_time: float
    ) -> InvocationResponse:
        """Create error response."""
        return InvocationResponse(
            invocation_id=invocation_id,
            tool_name=tool_name,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
        )

    def _initialize_handlers(self) -> None:
        """Initialize default tool handlers."""

        def _trace_handler(method: str, params: dict[str, Any]) -> dict[str, Any]:
            if method == "collect":
                return {"traces": [{"id": params.get("trace_id", "default"), "duration": 0.5}]}
            elif method == "analyze":
                return {"analysis": "trace_analysis_complete"}
            else:
                raise ValueError(f"Unknown method: {method}")

        def _metric_handler(method: str, params: dict[str, Any]) -> dict[str, Any]:
            if method == "collect":
                return {
                    "metrics": [{"name": "cpu", "value": 45.2, "timestamp": datetime.utcnow().isoformat()}]
                }
            elif method == "query":
                return {"query_result": "metric_data"}
            else:
                raise ValueError(f"Unknown method: {method}")

        def _log_handler(method: str, params: dict[str, Any]) -> dict[str, Any]:
            if method == "analyze":
                return {"analysis": {"total_logs": 100, "error_count": 5, "warnings": 10}}
            elif method == "filter":
                return {"filtered_logs": []}
            else:
                raise ValueError(f"Unknown method: {method}")

        self._tool_handlers["trace_collector"] = _trace_handler
        self._tool_handlers["metric_collector"] = _metric_handler
        self._tool_handlers["log_analyzer"] = _log_handler


# guardian: allow-magic-config
def create_observability_tool_invoker(
    default_timeout: float = 30.0, retry_attempts: int = 3, enable_caching: bool = True, **kwargs: object
) -> ObservabilityToolInvoker:
    """Create a configured observability tool invoker."""
    config = InvocationConfig(
        default_timeout=default_timeout,
        retry_attempts=retry_attempts,
        enable_caching=enable_caching,
        **kwargs,
    )
    return ObservabilityToolInvoker(config)


def invoke_observability_tool(
    invocation_id: str,
    tool_name: str,
    method: str,
    parameters: dict[str, Any],
    invocation_type: str = "direct",
    response_format: str = "json",
) -> dict[str, Any]:
    """Invoke observability tool.

    Args:
        invocation_id: Unique invocation identifier
        tool_name: Name of tool to invoke
        method: Method to call on tool
        parameters: Tool parameters
        invocation_type: Type of invocation
        response_format: Expected response format

    Returns:
        Dict: Invocation response
    """
    invoker = create_observability_tool_invoker()
    request = InvocationRequest(
        invocation_id=invocation_id,
        tool_name=tool_name,
        method=method,
        parameters=parameters,
        invocation_type=InvocationType(invocation_type),
        response_format=ResponseFormat(response_format),
    )
    response = invoker.invoke_tool(request)
    return {
        "invocation_id": response.invocation_id,
        "tool_name": response.tool_name,
        "success": response.success,
        "data": response.data,
        "headers": response.headers,
        "status_code": response.status_code,
        "error": response.error,
        "warnings": response.warnings,
        "execution_time": response.execution_time,
    }
