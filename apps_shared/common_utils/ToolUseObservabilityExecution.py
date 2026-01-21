"""Tool Use Observability Execution - Tool-based execution adapter for observability.

This module provides tool-based adapters for executing observability operations
with standardized tool interfaces, execution management, and error handling.
Follows the functional component pattern with proper logging.
"""

import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ExecutionType(Enum):
    """Types of tool execution."""
    SYNC = "sync"
    ASYNC = "async"
    STREAMING = "streaming"
    BATCH = "batch"


class ToolStatus(Enum):
    """Status of tools."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ToolDefinition:
    """Definition of an observability tool."""
    tool_id: str
    name: str
    version: str
    description: str
    execution_type: ExecutionType
    capabilities: list[str]
    configuration: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ToolExecutionRequest:
    """Request for tool execution."""
    execution_id: str
    tool_id: str
    command: str
    parameters: dict[str, Any]
    execution_type: ExecutionType
    timeout: float = 30.0
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecutionConfig:
    """Configuration for tool execution."""
    default_timeout: float = 30.0
    max_retries: int = 3
    enable_health_checks: bool = True
    health_check_interval: float = 60.0
    enable_metrics: bool = True
    enable_tracing: bool = True


@dataclass
class ToolExecutionResult:
    """Result of tool execution."""
    execution_id: str
    tool_id: str
    command: str
    success: bool
    output: Any | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityToolExecutor:
    """Main executor for observability tools."""

    def __init__(self, config: ToolExecutionConfig | None = None):
        self.config = config or ToolExecutionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._registered_tools: dict[str, ToolDefinition] = {}
        self._tool_implementations: dict[str, Callable] = {}
        self._tool_status: dict[str, ToolStatus] = {}
        self._active_executions: dict[str, dict[str, Any]] = {}
        self._initialize_tools()

    def register_tool(self, tool_def: ToolDefinition,
                     implementation: Callable) -> None:
        """Register an observability tool.

        Args:
            tool_def: Tool definition
            implementation: Tool implementation function
        """
        self._registered_tools[tool_def.tool_id] = tool_def
        self._tool_implementations[tool_def.tool_id] = implementation
        self._tool_status[tool_def.tool_id] = ToolStatus.ACTIVE
        self.logger.info(f"Registered tool: {tool_def.tool_id}")

    def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute an observability tool.

        Args:
            request: Tool execution request

        Returns:
            ToolExecutionResult: Execution result
        """
        self.logger.info(f"Executing tool: {request.tool_id}, command: {request.command}")

        start_time = time.time()

        try:
            # Validate tool exists and is active
            if request.tool_id not in self._registered_tools:
                return self._create_error_result(
                    request.execution_id,
                    request.tool_id,
                    request.command,
                    f"Tool not registered: {request.tool_id}",
                    start_time
                )

            if self._tool_status[request.tool_id] != ToolStatus.ACTIVE:
                return self._create_error_result(
                    request.execution_id,
                    request.tool_id,
                    request.command,
                    f"Tool not active: {self._tool_status[request.tool_id].value}",
                    start_time
                )

            # Track execution
            self._track_execution_start(request)

            # Execute based on execution type
            if request.execution_type == ExecutionType.SYNC:
                result = self._execute_sync(request)
            elif request.execution_type == ExecutionType.ASYNC:
                result = self._execute_async(request)
            elif request.execution_type == ExecutionType.STREAMING:
                result = self._execute_streaming(request)
            elif request.execution_type == ExecutionType.BATCH:
                result = self._execute_batch(request)
            else:
                raise ValueError(f"Unsupported execution type: {request.execution_type}")

            # Calculate execution time
            result.execution_time = time.time() - start_time

            # Update execution tracking
            self._track_execution_complete(request, result)

            return result

        except Exception as e:
            self.logger.error(f"Tool execution failed: {str(e)}")
            return self._create_error_result(
                request.execution_id,
                request.tool_id,
                request.command,
                str(e),
                start_time
            )

    def execute_tool_stream(self, request: ToolExecutionRequest) -> object:
        """Execute tool with streaming output.

        Args:
            request: Tool execution request

        Returns:
            Iterator: Stream of output chunks
        """
        if request.execution_type != ExecutionType.STREAMING:
            raise ValueError("Execution type must be STREAMING for streaming execution")

        implementation = self._tool_implementations.get(request.tool_id)
        if not implementation:
            raise ValueError(f"No implementation for tool: {request.tool_id}")

        # Execute and stream
        for chunk in implementation(request.command, request.parameters, stream=True):
            yield chunk

    def execute_tools_batch(self, requests: list[ToolExecutionRequest]) -> list[ToolExecutionResult]:
        """Execute multiple tools.

        Args:
            requests: List of execution requests

        Returns:
            List[ToolExecutionResult]: Results for all executions
        """
        results = []

        for request in requests:
            result = self.execute_tool(request)
            results.append(result)

        return results

    def list_tools(self, status: ToolStatus | None = None) -> list[ToolDefinition]:
        """List registered tools.

        Args:
            status: Optional filter by status

        Returns:
            List[ToolDefinition]: Registered tools
        """
        tools = list(self._registered_tools.values())

        if status:
            tools = [t for t in tools if self._tool_status.get(t.tool_id) == status]

        return tools

    def get_tool_definition(self, tool_id: str) -> ToolDefinition | None:
        """Get tool definition.

        Args:
            tool_id: Tool identifier

        Returns:
            Optional[ToolDefinition]: Tool definition
        """
        return self._registered_tools.get(tool_id)

    def get_tool_status(self, tool_id: str) -> ToolStatus | None:
        """Get tool status.

        Args:
            tool_id: Tool identifier

        Returns:
            Optional[ToolStatus]: Tool status
        """
        return self._tool_status.get(tool_id)

    def set_tool_status(self, tool_id: str, status: ToolStatus) -> None:
        """Set tool status.

        Args:
            tool_id: Tool identifier
            status: New status
        """
        if tool_id in self._tool_status:
            self._tool_status[tool_id] = status
            self.logger.info(f"Updated tool {tool_id} status to: {status.value}")

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

    def get_execution_status(self, execution_id: str) -> dict[str, Any] | None:
        """Get execution status.

        Args:
            execution_id: Execution identifier

        Returns:
            Optional[Dict]: Execution status
        """
        return self._active_executions.get(execution_id)

    def _execute_sync(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute tool synchronously."""
        implementation = self._tool_implementations[request.tool_id]

        # Execute implementation
        output = implementation(request.command, request.parameters)

        # Extract stdout/stderr if available
        stdout = output.get("stdout") if isinstance(output, dict) else None
        stderr = output.get("stderr") if isinstance(output, dict) else None
        exit_code = output.get("exit_code", 0) if isinstance(output, dict) else 0

        return ToolExecutionResult(
            execution_id=request.execution_id,
            tool_id=request.tool_id,
            command=request.command,
            success=exit_code == 0,
            output=output,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr
        )

    def _execute_async(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute tool asynchronously."""
        implementation = self._tool_implementations[request.tool_id]

        # Execute with async simulation
        output = implementation(request.command, request.parameters, async_mode=True)

        return ToolExecutionResult(
            execution_id=request.execution_id,
            tool_id=request.tool_id,
            command=request.command,
            success=True,
            output=output,
            exit_code=0
        )

    def _execute_streaming(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute tool in streaming mode."""
        # For streaming mode, we return a result indicating streaming is active
        return ToolExecutionResult(
            execution_id=request.execution_id,
            tool_id=request.tool_id,
            command=request.command,
            success=True,
            output={"status": "streaming_active"},
            exit_code=0
        )

    def _execute_batch(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute tool in batch mode."""
        batch_commands = request.parameters.get("batch_commands", [])
        results = []
        total_exit_code = 0

        for command in batch_commands:
            implementation = self._tool_implementations[request.tool_id]

            try:
                output = implementation(command, request.parameters)
                results.append(output)

                if isinstance(output, dict) and output.get("exit_code", 0) != 0:
                    total_exit_code = output["exit_code"]

            except Exception as e:
                self.logger.warning(f"Batch command failed: {str(e)}")
                results.append({"error": str(e)})
                total_exit_code = 1

        return ToolExecutionResult(
            execution_id=request.execution_id,
            tool_id=request.tool_id,
            command=request.command,
            success=total_exit_code == 0,
            output=results,
            exit_code=total_exit_code
        )

    def _track_execution_start(self, request: ToolExecutionRequest) -> None:
        """Track execution start."""
        self._active_executions[request.execution_id] = {
            "tool_id": request.tool_id,
            "command": request.command,
            "execution_type": request.execution_type.value,
            "start_time": time.time(),
            "status": "running",
            "cancelled": False
        }

    def _track_execution_complete(self, request: ToolExecutionRequest,
                                 result: ToolExecutionResult) -> None:
        """Track execution completion."""
        if request.execution_id in self._active_executions:
            execution = self._active_executions[request.execution_id]
            execution["end_time"] = time.time()
            execution["status"] = "completed" if result.success else "failed"
            execution["execution_time"] = result.execution_time

    def _create_error_result(self, execution_id: str, tool_id: str,
                            command: str, error: str, start_time: float) -> ToolExecutionResult:
        """Create error result."""
        return ToolExecutionResult(
            execution_id=execution_id,
            tool_id=tool_id,
            command=command,
            success=False,
            error=error,
            exit_code=1,
            execution_time=time.time() - start_time
        )

    def _initialize_tools(self) -> None:
        """Initialize built-in tools."""
        # Log collector tool
        log_tool = ToolDefinition(
            tool_id="log_collector",
            name="Log Collector",
            version="1.0",
            description="Collects and processes log data",
            execution_type=ExecutionType.SYNC,
            capabilities=["collect", "filter", "parse"]
        )

        def _log_collector_impl(command: str, params: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            if command == "collect":
                return {
                    "stdout": "Collected 100 log entries",
                    "exit_code": 0,
                    "logs": [
                        {"timestamp": datetime.utcnow().isoformat(), "level": "info", "message": "Sample log"}
                    ]
                }
            elif command == "filter":
                level = params.get("level", "info")
                return {
                    "stdout": f"Filtered logs by level: {level}",
                    "exit_code": 0,
                    "filtered_count": 50
                }
            else:
                return {
                    "stderr": f"Unknown command: {command}",
                    "exit_code": 1
                }

        # Metric collector tool
        metric_tool = ToolDefinition(
            tool_id="metric_collector",
            name="Metric Collector",
            version="1.0",
            description="Collects system and application metrics",
            execution_type=ExecutionType.SYNC,
            capabilities=["collect", "aggregate", "query"]
        )

        def _metric_collector_impl(command: str, params: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            if command == "collect":
                return {
                    "stdout": "Collected system metrics",
                    "exit_code": 0,
                    "metrics": {
                        "cpu": 45.2,
                        "memory": 67.8,
                        "disk": 23.5
                    }
                }
            elif command == "aggregate":
                return {
                    "stdout": "Aggregated metrics over time window",
                    "exit_code": 0,
                    "aggregated": {"avg_cpu": 42.1, "max_memory": 78.9}
                }
            else:
                return {
                    "stderr": f"Unknown command: {command}",
                    "exit_code": 1
                }

        # Trace analyzer tool
        trace_tool = ToolDefinition(
            tool_id="trace_analyzer",
            name="Trace Analyzer",
            version="1.0",
            description="Analyzes distributed trace data",
            execution_type=ExecutionType.ASYNC,
            capabilities=["analyze", "correlate", "visualize"]
        )

        def _trace_analyzer_impl(command: str, params: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            trace_id = params.get("trace_id", "default")
            return {
                "stdout": f"Analyzed trace: {trace_id}",
                "exit_code": 0,
                "analysis": {
                    "trace_id": trace_id,
                    "span_count": 10,
                    "total_duration": 0.5,
                    "errors": 0
                }
            }

        # Register built-in tools
        self.register_tool(log_tool, _log_collector_impl)
        self.register_tool(metric_tool, _metric_collector_impl)
        self.register_tool(trace_tool, _trace_analyzer_impl)


# Factory function for easy instantiation
def create_observability_tool_executor(
    default_timeout: float = 30.0,
    max_retries: int = 3,
    enable_health_checks: bool = True,
    **kwargs: object
) -> ObservabilityToolExecutor:
    """Create a configured observability tool executor."""
    config = ToolExecutionConfig(
        default_timeout=default_timeout,
        max_retries=max_retries,
        enable_health_checks=enable_health_checks,
        **kwargs
    )
    return ObservabilityToolExecutor(config)


# Convenience function for direct usage
def tool_use_observability_execution(
    tool_id: str,
    command: str,
    parameters: dict[str, Any],
    execution_id: str | None = None,
    execution_type: str = "sync",
    timeout: float = 30.0
) -> dict[str, Any]:
    """Execute observability tool.

    Args:
        tool_id: Tool identifier
        command: Command to execute
        parameters: Command parameters
        execution_id: Optional unique execution identifier
        execution_type: Type of execution
        timeout: Execution timeout

    Returns:
        Dict: Execution result
    """
    executor = create_observability_tool_executor()

    request = ToolExecutionRequest(
        execution_id=execution_id or str(uuid.uuid4()),
        tool_id=tool_id,
        command=command,
        parameters=parameters,
        execution_type=ExecutionType(execution_type),
        timeout=timeout
    )

    result = executor.execute_tool(request)

    return {
        "execution_id": result.execution_id,
        "tool_id": result.tool_id,
        "command": result.command,
        "success": result.success,
        "output": result.output,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "metrics": result.metrics,
        "error": result.error,
        "warnings": result.warnings,
        "execution_time": result.execution_time
    }
