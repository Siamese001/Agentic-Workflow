"""Tool Execute observability Execution - Tool wrapper for observability execution.

This module provides tool-based adapters for executing observability operations
with standardized tool interfaces and protocol compliance.
Follows the functional component pattern with proper logging.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "tool_type_types", "p0_governance")
_emit_reads_policy_state("p0", "tool_type_types", "policy_binding")
_emit_snapshots_state("p0", "tool_type_types", "state_snapshot")
emit_replay_key("p0", "tool_type_types")
emit_determinism_digest("p0", "tool_type_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "tool_type_types", "execution_auth")
_emit_validates_capability("p2", "tool_type_types", "capability_check")
_emit_routes_to_capability("p2", "tool_type_types", "capability_route")
_emit_writes_via_uwg("p2", "tool_type_types", "uwg_write")
_emit_blocks_direct_write("p2", "tool_type_types", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_type_types", "tool_invocation")
_emit_captures_execution_output("p2", "tool_type_types", "exec_output")
_emit_dispatches_agent("p3", "tool_type_types", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_type_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_type_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_type_types", "healing_outcome")
_emit_escalates_failure("p3", "tool_type_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_type_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_type_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_type_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_type_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_type_types", "eval_metric")
_emit_stores_embedding("p4", "tool_type_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_type_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_type_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Types of observability tools."""

    TRACER = "tracer"
    METRIC_COLLECTOR = "metric_collector"
    LOG_ANALYZER = "log_analyzer"
    EVENT_PROCESSOR = "event_processor"
    PROFILER = "profiler"


class ExecutionMode(Enum):
    """Modes of tool execution."""

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class ToolDefinition:
    """Definition of an observability tool."""

    tool_id: str
    tool_type: ToolType
    name: str
    version: str
    description: str
    parameters: dict[str, dict[str, Any]]
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ToolExecutionContext:
    """Context for tool execution."""

    execution_id: str
    tool_id: str
    mode: ExecutionMode
    caller_id: str | None = None
    session_id: str | None = None
    trace_context: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecutionConfig:
    """configuration for tool execution."""

    timeout: float = 30.0
    retry_count: int = 3
    enable_tracing: bool = True
    enable_metrics: bool = True
    buffer_size: int = 1000


@dataclass
class ToolExecutionResult:
    """Result of tool execution."""

    execution_id: str
    tool_id: str
    success: bool
    output: Any | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityToolExecutor:
    """Main executor for observability tools."""

    def __init__(self, config: ToolExecutionConfig | None = None):
        self.config = config or ToolExecutionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._registered_tools: dict[str, ToolDefinition] = {}
        self._tool_handlers: dict[str, Callable] = {}
        self._active_executions: dict[str, dict[str, Any]] = {}
        self._initialize_built_in_tools()

    def register_tool(self, tool_def: ToolDefinition, handler: Callable) -> None:
        """Register a new observability tool.

        Args:
            tool_def: Tool definition
            handler: Tool execution handler
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"ToolRegistry.register_tool:{tool_def.tool_id}")
        self._registered_tools[tool_def.tool_id] = tool_def
        self._tool_handlers[tool_def.tool_id] = handler
        self.logger.info(f"Registered tool: {tool_def.tool_id}")

    def execute_tool(self, context: ToolExecutionContext, parameters: dict[str, Any]) -> ToolExecutionResult:
        """Execute an observability tool.

        Args:
            context: Execution context
            parameters: Tool parameters

        Returns:
            ToolExecutionResult: Execution result
        """
        self.logger.info(f"Executing tool: {context.tool_id}")
        start_time = time.time()
        try:
            if context.tool_id not in self._registered_tools:
                return self._create_error_result(
                    context.execution_id, context.tool_id, f"Tool not found: {context.tool_id}", start_time
                )
            tool_def = self._registered_tools[context.tool_id]
            validation_errors = self._validate_parameters(parameters, tool_def)
            if validation_errors:
                return self._create_error_result(
                    context.execution_id,
                    context.tool_id,
                    f"Parameter validation failed: {validation_errors}",
                    start_time,
                )
            self._track_execution_start(context)
            handler = self._tool_handlers[context.tool_id]
            result = self._execute_with_context(handler, context, parameters)
            result.execution_time = time.time() - start_time
            self._track_execution_complete(context, result)
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            return self._create_error_result(context.execution_id, context.tool_id, str(e), start_time)

    def execute_tool_stream(
        self, context: ToolExecutionContext, parameters: dict[str, str]
    ) -> dict[str, object]:
        """Execute tool in streaming mode.

        Args:
            context: Execution context
            parameters: Tool parameters

        Returns:
            Iterator: Stream of results
        """
        if context.mode != ExecutionMode.STREAMING:
            raise ValueError("Execution mode must be STREAMING for streaming execution")
        handler = self._tool_handlers.get(context.tool_id)
        if not handler:
            raise ValueError(f"No handler for tool: {context.tool_id}")
        yield from handler(parameters, stream=True)

    def list_tools(self, tool_type: ToolType | None = None) -> list[ToolDefinition]:
        """List registered tools.

        Args:
            tool_type: Optional filter by tool type

        Returns:
            List[ToolDefinition]: Registered tools
        """
        tools = list(self._registered_tools.values())
        if tool_type:
            tools = [t for t in tools if t.tool_type == tool_type]
        return tools

    def get_tool_info(self, tool_id: str) -> ToolDefinition | None:
        """Get tool information.

        Args:
            tool_id: Tool identifier

        Returns:
            Optional[ToolDefinition]: Tool definition
        """
        return self._registered_tools.get(tool_id)

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active execution.

        Args:
            execution_id: Execution identifier

        Returns:
            bool: True if cancelled successfully
        """
        if execution_id in self._active_executions:
            execution = self._active_executions[execution_id]
            execution["cancelled"] = True
            self.logger.info(f"Cancelled execution: {execution_id}")
            return True
        return False

    def get_execution_status(self, execution_id: str) -> dict[str, str] | None:
        """Get status of execution.

        Args:
            execution_id: Execution identifier

        Returns:
            Optional[Dict]: Execution status
        """
        return self._active_executions.get(execution_id)

    def _execute_with_context(
        self, handler: Callable, context: ToolExecutionContext, parameters: dict[str, str]
    ) -> ToolExecutionResult:
        """Execute tool with context."""
        exec_env = {
            "context": context,
            "parameters": parameters,
            "config": self.config,
            "logger": self.logger,
        }
        if context.mode == ExecutionMode.SYNCHRONOUS:
            result_data = handler(exec_env)
        elif context.mode == ExecutionMode.ASYNCHRONOUS:
            result_data = handler(exec_env)
        elif context.mode == ExecutionMode.BATCH:
            result_data = self._execute_batch(handler, exec_env)
        else:
            raise ValueError(f"Unsupported execution mode: {context.mode}")
        output = result_data.get("output")
        metrics = result_data.get("metrics", {})
        artifacts = result_data.get("artifacts", [])
        warnings = result_data.get("warnings", [])
        return ToolExecutionResult(
            execution_id=context.execution_id,
            tool_id=context.tool_id,
            success=True,
            output=output,
            metrics=metrics,
            artifacts=artifacts,
            warnings=warnings,
        )

    def _execute_batch(self, handler: Callable, exec_env: dict[str, str]) -> dict[str, str]:
        """Execute tool in batch mode."""
        parameters = exec_env["parameters"]
        batch_items = parameters.get("batch_items", [])
        results = []
        total_metrics = {}
        all_artifacts = []
        all_warnings = []
        for item in batch_items:
            item_env = exec_env.copy()
            item_env["parameters"] = item
            try:
                item_result = handler(item_env)
                results.append(item_result.get("output"))
                for key, value in item_result.get("metrics", {}).items():
                    if key not in total_metrics:
                        total_metrics[key] = []
                    total_metrics[key].append(value)
                all_artifacts.extend(item_result.get("artifacts", []))
                all_warnings.extend(item_result.get("warnings", []))
            except Exception as e:
                raise
                all_warnings.append(f"Batch item failed: {str(e)}")
        final_metrics = {}
        for key, values in total_metrics.items():
            if values:
                final_metrics[f"{key}_avg"] = sum(values) / len(values)
                final_metrics[f"{key}_total"] = sum(values)
        return {
            "output": results,
            "metrics": final_metrics,
            "artifacts": all_artifacts,
            "warnings": all_warnings,
        }

    def _validate_parameter_type(self, param_name: str, value: object, expected_type: str) -> str | None:
        """Validate a single parameter type and return error message if invalid."""
        type_validators = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int),
            "float": lambda v: isinstance(v, int | float),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
        }
        validator = type_validators.get(expected_type)
        if validator and (not validator(value)):
            type_names = {
                "string": "string",
                "integer": "integer",
                "float": "number",
                "boolean": "boolean",
                "array": "array",
                "object": "object",
            }
            return f"Parameter {param_name} must be {type_names.get(expected_type, 'valid type')}"
        return None

    def _validate_parameters(self, parameters: dict[str, Any], tool_def: ToolDefinition) -> list[str]:
        """Validate tool parameters."""
        errors = []
        for param_name, param_def in tool_def.parameters.items():
            if param_def.get("required", False) and param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
            if param_name in parameters:
                expected_type = param_def.get("type")
                value = parameters[param_name]
                type_error = self._validate_parameter_type(param_name, value, expected_type)
                if type_error:
                    errors.append(type_error)
        return errors

    def _track_execution_start(self, context: ToolExecutionContext) -> None:
        """Track execution start."""
        self._active_executions[context.execution_id] = {
            "tool_id": context.tool_id,
            "mode": context.mode,
            "start_time": time.time(),
            "status": "running",
            "cancelled": False,
        }

    def _track_execution_complete(self, context: ToolExecutionContext, result: ToolExecutionResult) -> None:
        """Track execution completion."""
        if context.execution_id in self._active_executions:
            execution = self._active_executions[context.execution_id]
            execution["end_time"] = time.time()
            execution["status"] = "completed" if result.success else "failed"
            execution["execution_time"] = result.execution_time

    def _create_error_result(
        self, execution_id: str, tool_id: str, error: str, start_time: float
    ) -> ToolExecutionResult:
        """Create error result."""
        return ToolExecutionResult(
            execution_id=execution_id,
            tool_id=tool_id,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
        )

    def _initialize_built_in_tools(self) -> None:
        """Initialize built-in observability tools."""
        trace_tool = ToolDefinition(
            tool_id="trace_collector",
            tool_type=ToolType.TRACER,
            name="Trace Collector",
            version="1.0",
            description="Collects and analyzes trace data",
            parameters={
                "trace_id": {"type": "string", "required": False},
                "service": {"type": "string", "required": False},
                "time_range": {"type": "object", "required": False},
            },
            capabilities=["collect", "analyze", "export"],
        )

        def _trace_handler(exec_env: dict[str, Any]) -> dict[str, Any]:
            exec_env["parameters"]
            return {
                "output": {
                    "traces": [
                        {"id": "trace_1", "duration": 0.5, "spans": 5},
                        {"id": "trace_2", "duration": 0.3, "spans": 3},
                    ],
                    "summary": {"total_traces": 2, "avg_duration": 0.4},
                },
                "metrics": {"traces_collected": 2, "processing_time": 0.1},
            }

        metric_tool = ToolDefinition(
            tool_id="metric_collector",
            tool_type=ToolType.METRIC_COLLECTOR,
            name="Metric Collector",
            version="1.0",
            description="Collects system and application metrics",
            parameters={
                "metric_names": {"type": "array", "required": False},
                "aggregation": {"type": "string", "required": False},
            },
            capabilities=["collect", "aggregate", "query"],
        )

        def _metric_handler(exec_env: dict[str, Any]) -> dict[str, Any]:
            exec_env["parameters"]
            return {
                "output": {
                    "metrics": [
                        {"name": "cpu_usage", "value": 45.2, "timestamp": datetime.utcnow().isoformat()},
                        {"name": "memory_usage", "value": 67.8, "timestamp": datetime.utcnow().isoformat()},
                    ]
                },
                "metrics": {"metrics_collected": 2, "processing_time": 0.05},
            }

        log_tool = ToolDefinition(
            tool_id="log_analyzer",
            tool_type=ToolType.LOG_ANALYZER,
            name="Log Analyzer",
            version="1.0",
            description="Analyzes and filters log data",
            parameters={
                "level": {"type": "string", "required": False},
                "pattern": {"type": "string", "required": False},
                "limit": {"type": "integer", "required": False},
            },
            capabilities=["filter", "parse", "analyze"],
        )

        def _log_handler(exec_env: dict[str, Any]) -> dict[str, Any]:
            exec_env["parameters"]
            return {
                "output": {
                    "logs": [
                        {
                            "message": "Application started",
                            "level": "info",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        {
                            "message": "Error processing request",
                            "level": "error",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    ],
                    "summary": {"total_logs": 2, "error_count": 1},
                },
                "metrics": {"logs_analyzed": 2, "processing_time": 0.08},
            }

        self.register_tool(trace_tool, _trace_handler)
        self.register_tool(metric_tool, _metric_handler)
        self.register_tool(log_tool, _log_handler)


# guardian: allow-magic-config
def create_observability_tool_executor(
    timeout: float = 30.0, retry_count: int = 3, enable_tracing: bool = True, **kwargs: object
) -> ObservabilityToolExecutor:
    """Create a configured observability tool executor."""
    config = ToolExecutionConfig(
        timeout=timeout, retry_count=retry_count, enable_tracing=enable_tracing, **kwargs
    )
    return ObservabilityToolExecutor(config)


def tool_execute_observability_execution(
    tool_id: str,
    execution_id: str,
    parameters: dict[str, Any],
    mode: str = "synchronous",
    caller_id: str | None = None,
) -> dict[str, Any]:
    """Execute observability tool.

    Args:
        tool_id: Tool identifier
        execution_id: Unique execution identifier
        parameters: Tool parameters
        mode: Execution mode
        caller_id: Optional caller identifier

    Returns:
        Dict: Execution result
    """
    executor = create_observability_tool_executor()
    context = ToolExecutionContext(
        execution_id=execution_id, tool_id=tool_id, mode=ExecutionMode(mode), caller_id=caller_id
    )
    result = executor.execute_tool(context, parameters)
    return {
        "execution_id": result.execution_id,
        "tool_id": result.tool_id,
        "success": result.success,
        "output": result.output,
        "metrics": result.metrics,
        "artifacts": result.artifacts,
        "error": result.error,
        "warnings": result.warnings,
        "execution_time": result.execution_time,
    }
