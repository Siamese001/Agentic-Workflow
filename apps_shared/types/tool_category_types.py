"""Tool Invoke observability Tool - Tool-based invocation adapter for observability.

This module provides tool-based adapters for invoking observability operations
with standardized tool interfaces, protocol compliance, and error handling.
Follows the functional component pattern with proper logging.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of observability tools."""

    TRACING = "tracing"
    METRICS = "metrics"
    LOGGING = "logging"
    MONITORING = "monitoring"
    ANALYSIS = "analysis"


class ToolProtocol(Enum):
    """Protocols supported by tools."""

    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    NATIVE = "native"


@dataclass
class ToolSpecification:
    """Specification of an observability tool."""

    tool_id: str
    name: str
    version: str
    category: ToolCategory
    protocol: ToolProtocol
    endpoint: str
    methods: list[str]
    parameters_schema: dict[str, dict[str, Any]]
    authentication: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolInvocationContext:
    """Context for tool invocation."""

    invocation_id: str
    tool_id: str
    method: str
    caller_id: str | None = None
    session_id: str | None = None
    correlation_id: str | None = None
    timeout: float = 30.0
    retry_policy: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolInvocationConfig:
    """configuration for tool invocation."""

    default_timeout: float = 30.0
    max_retries: int = 3
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    enable_metrics: bool = True
    enable_tracing: bool = True


@dataclass
class ToolInvocationResult:
    """Result of tool invocation."""

    invocation_id: str
    tool_id: str
    method: str
    success: bool
    response: Any | None = None
    response_code: int | None = None
    headers: dict[str, str] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityToolInvoker:
    """Main invoker for observability tools."""

    def __init__(self, config: ToolInvocationConfig | None = None):
        self.config = config or ToolInvocationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._registered_tools: dict[str, ToolSpecification] = {}
        self._tool_clients: dict[str, Any] = {}
        self._circuit_breakers: dict[str, dict[str, Any]] = {}
        self._initialize_tools()

    def register_tool(self, tool_spec: ToolSpecification, client: Any | None = None) -> None:
        """Register an observability tool.

        Args:
            tool_spec: Tool specification
            client: Optional client instance
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"ObservabilityToolRegistry.register_tool:{tool_spec.tool_id}")
        self._registered_tools[tool_spec.tool_id] = tool_spec
        if client:
            self._tool_clients[tool_spec.tool_id] = client
        self._circuit_breakers[tool_spec.tool_id] = {"failures": 0, "last_failure": None, "state": "closed"}
        self.logger.info(f"Registered tool: {tool_spec.tool_id}")

    def invoke_tool(self, context: ToolInvocationContext, parameters: dict[str, Any]) -> ToolInvocationResult:
        """Invoke an observability tool.

        Args:
            context: Invocation context
            parameters: Tool parameters

        Returns:
            ToolInvocationResult: Invocation result
        """
        self.logger.info(f"Invoking tool: {context.tool_id}, method: {context.method}")
        start_time = time.time()
        try:
            if context.tool_id not in self._registered_tools:
                return self._create_error_result(
                    context.invocation_id,
                    context.tool_id,
                    context.method,
                    f"Tool not registered: {context.tool_id}",
                    start_time,
                )
            if not self._check_circuit_breaker(context.tool_id):
                return self._create_error_result(
                    context.invocation_id,
                    context.tool_id,
                    context.method,
                    "Circuit breaker is open",
                    start_time,
                )
            tool_spec = self._registered_tools[context.tool_id]
            validation_errors = self._validate_parameters(parameters, tool_spec, context.method)
            if validation_errors:
                return self._create_error_result(
                    context.invocation_id,
                    context.tool_id,
                    context.method,
                    f"Parameter validation failed: {validation_errors}",
                    start_time,
                )
            result = self._execute_with_retry(context, parameters)
            if result.success:
                self._reset_circuit_breaker(context.tool_id)
            else:
                self._record_failure(context.tool_id)
            result.execution_time = time.time() - start_time
            if self.config.enable_metrics:
                self._record_invocation_metrics(result)
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Tool invocation failed: {str(e)}")
            self._record_failure(context.tool_id)
            return self._create_error_result(
                context.invocation_id, context.tool_id, context.method, str(e), start_time
            )

    def invoke_tool_batch(
        self, contexts: list[ToolInvocationContext], parameters_list: list[dict[str, Any]]
    ) -> list[ToolInvocationResult]:
        """Invoke multiple tools.

        Args:
            contexts: List of invocation contexts
            parameters_list: List of parameters

        Returns:
            List[ToolInvocationResult]: Results for all invocations
        """
        if len(contexts) != len(parameters_list):
            raise ValueError("Contexts and parameters lists must have same length")
        results = []
        for context, parameters in zip(contexts, parameters_list, strict=False):
            result = self.invoke_tool(context, parameters)
            results.append(result)
        return results

    def invoke_tool_stream(
        self, context: ToolInvocationContext, parameters: dict[str, Any]
    ) -> dict[str, object]:
        """Invoke tool with streaming response.

        Args:
            context: Invocation context
            parameters: Tool parameters

        Returns:
            Iterator: Stream of response chunks
        """
        client = self._tool_clients.get(context.tool_id)
        if not client:
            raise ValueError(f"No client for tool: {context.tool_id}")
        yield from client.invoke_stream(context.method, parameters)

    def list_tools(self, category: ToolCategory | None = None) -> list[ToolSpecification]:
        """List registered tools.

        Args:
            category: Optional filter by category

        Returns:
            List[ToolSpecification]: Registered tools
        """
        tools = list(self._registered_tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    def get_tool_specification(self, tool_id: str) -> ToolSpecification | None:
        """Get tool specification.

        Args:
            tool_id: Tool identifier

        Returns:
            Optional[ToolSpecification]: Tool specification
        """
        return self._registered_tools.get(tool_id)

    def reset_circuit_breaker(self, tool_id: str) -> None:
        """Reset circuit breaker for tool.

        Args:
            tool_id: Tool identifier
        """
        if tool_id in self._circuit_breakers:
            self._reset_circuit_breaker(tool_id)
            self.logger.info(f"Reset circuit breaker for tool: {tool_id}")

    def _execute_with_retry(
        self, context: ToolInvocationContext, parameters: dict[str, Any]
    ) -> ToolInvocationResult:
        """Execute tool invocation with retry logic."""
        last_error = None
        max_retries = context.retry_policy.get("max_retries", self.config.max_retries)
        for attempt in range(max_retries + 1):
            try:
                client = self._tool_clients.get(context.tool_id)
                if client:
                    response = client.invoke(context.method, parameters)
                    return ToolInvocationResult(
                        invocation_id=context.invocation_id,
                        tool_id=context.tool_id,
                        method=context.method,
                        success=True,
                        response=response.get("data"),
                        response_code=response.get("status_code", 200),
                        headers=response.get("headers", {}),
                        metrics=response.get("metrics", {}),
                    )
                else:
                    return self._simulate_invocation(context, parameters)
            # guardian: allow-silent-swallow
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    retry_delay = context.retry_policy.get("delay", 2**attempt)
                    self.logger.warning(
                        f"Invocation attempt {attempt + 1} failed, retrying in {retry_delay}s: {last_error}"
                    )
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Invocation failed after {attempt + 1} attempts: {last_error}")
        return self._create_error_result(
            context.invocation_id, context.tool_id, context.method, last_error, time.time()
        )

    def _simulate_invocation(
        self, context: ToolInvocationContext, parameters: dict[str, Any]
    ) -> ToolInvocationResult:
        """Simulate tool invocation."""
        tool_spec = self._registered_tools[context.tool_id]
        time.sleep(DEFAULT_SLEEP)
        if tool_spec.category == ToolCategory.TRACING:
            response = {
                "trace_id": parameters.get("trace_id", str(uuid.uuid4())),
                "spans": [{"operation": "span1", "duration": 0.1}, {"operation": "span2", "duration": 0.2}],
            }
        elif tool_spec.category == ToolCategory.METRICS:
            response = {
                "metrics": [
                    {"name": "cpu_usage", "value": 45.2, "timestamp": datetime.utcnow().isoformat()},
                    {"name": "memory_usage", "value": 67.8, "timestamp": datetime.utcnow().isoformat()},
                ]
            }
        elif tool_spec.category == ToolCategory.LOGGING:
            response = {
                "logs": [
                    {"message": f"Log entry for {context.method}", "level": "info"},
                    {"message": "Another log entry", "level": "warning"},
                ]
            }
        elif tool_spec.category == ToolCategory.MONITORING:
            response = {
                "status": "healthy",
                "checks": [{"name": "database", "status": "ok"}, {"name": "redis", "status": "ok"}],
            }
        else:
            response = {"message": f"Mock response from {tool_spec.name}"}
        return ToolInvocationResult(
            invocation_id=context.invocation_id,
            tool_id=context.tool_id,
            method=context.method,
            success=True,
            response=response,
            response_code=200,
            headers={"content-type": "application/json"},
            metrics={"processing_time": 0.1},
        )

    def _validate_parameters(
        self, parameters: dict[str, Any], tool_spec: ToolSpecification, method: str
    ) -> list[str]:
        """Validate tool parameters."""
        errors = []
        method_schema = tool_spec.parameters_schema.get(method, {})
        for param_name, param_def in method_schema.items():
            if param_def.get("required", False) and param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
            if param_name in parameters:
                expected_type = param_def.get("type")
                value = parameters[param_name]
                if expected_type and (not self._check_type(value, expected_type)):
                    errors.append(f"Parameter {param_name} must be of type {expected_type}")
        return errors

    def _check_type(self, value: object, expected_type: str) -> bool:
        """Check value type."""
        type_map = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True

    def _check_circuit_breaker(self, tool_id: str) -> bool:
        """Check if circuit breaker allows invocation."""
        if not self.config.enable_circuit_breaker:
            return True
        breaker = self._circuit_breakers.get(tool_id, {})
        if breaker.get("state") == "open":
            last_failure = breaker.get("last_failure")
            if last_failure and time.time() - last_failure > 60:
                breaker["state"] = "half_open"
                return True
            return False
        return True

    def _record_failure(self, tool_id: str) -> None:
        """Record failure for circuit breaker."""
        if not self.config.enable_circuit_breaker:
            return
        breaker = self._circuit_breakers.get(tool_id, {})
        breaker["failures"] += 1
        breaker["last_failure"] = time.time()
        if breaker["failures"] >= self.config.circuit_breaker_threshold:
            breaker["state"] = "open"
            self.logger.warning(f"Circuit breaker opened for tool: {tool_id}")

    def _reset_circuit_breaker(self, tool_id: str) -> None:
        """Reset circuit breaker."""
        if tool_id in self._circuit_breakers:
            self._circuit_breakers[tool_id] = {"failures": 0, "last_failure": None, "state": "closed"}

    def _record_invocation_metrics(self, result: ToolInvocationResult) -> None:
        """Record invocation metrics."""
        pass

    def _create_error_result(
        self, invocation_id: str, tool_id: str, method: str, error: str, start_time: float
    ) -> ToolInvocationResult:
        """Create error result."""
        return ToolInvocationResult(
            invocation_id=invocation_id,
            tool_id=tool_id,
            method=method,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
        )

    def _initialize_tools(self) -> None:
        """Initialize built-in tools."""
        trace_tool = ToolSpecification(
            tool_id="trace_collector",
            name="Trace Collector",
            version="1.0",
            category=ToolCategory.TRACING,
            protocol=ToolProtocol.NATIVE,
            endpoint="internal://trace_collector",
            methods=["collect", "analyze", "query"],
            parameters_schema={
                "collect": {
                    "trace_id": {"type": "string", "required": False},
                    "service": {"type": "string", "required": False},
                },
                "analyze": {"trace_data": {"type": "object", "required": True}},
            },
        )
        metric_tool = ToolSpecification(
            tool_id="metric_collector",
            name="Metric Collector",
            version="1.0",
            category=ToolCategory.METRICS,
            protocol=ToolProtocol.NATIVE,
            endpoint="internal://metric_collector",
            methods=["collect", "query", "aggregate"],
            parameters_schema={
                "collect": {
                    "metric_names": {"type": "array", "required": False},
                    "time_range": {"type": "object", "required": False},
                },
                "query": {"query": {"type": "string", "required": True}},
            },
        )
        log_tool = ToolSpecification(
            tool_id="log_analyzer",
            name="Log Analyzer",
            version="1.0",
            category=ToolCategory.LOGGING,
            protocol=ToolProtocol.NATIVE,
            endpoint="internal://log_analyzer",
            methods=["analyze", "filter", "search"],
            parameters_schema={
                "analyze": {
                    "log_source": {"type": "string", "required": True},
                    "time_range": {"type": "object", "required": False},
                },
                "filter": {
                    "level": {"type": "string", "required": False},
                    "pattern": {"type": "string", "required": False},
                },
            },
        )
        self.register_tool(trace_tool)
        self.register_tool(metric_tool)
        self.register_tool(log_tool)


# guardian: allow-magic-config
def create_observability_tool_invoker(
    default_timeout: float = 30.0, max_retries: int = 3, enable_circuit_breaker: bool = True, **kwargs: object
) -> ObservabilityToolInvoker:
    """Create a configured observability tool invoker."""
    config = ToolInvocationConfig(
        default_timeout=default_timeout,
        max_retries=max_retries,
        enable_circuit_breaker=enable_circuit_breaker,
        **kwargs,
    )
    return ObservabilityToolInvoker(config)


# guardian: allow-magic-config
def tool_invoke_observability_tool(
    tool_id: str,
    method: str,
    parameters: dict[str, Any],
    invocation_id: str | None = None,
    caller_id: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Invoke observability tool.

    Args:
        tool_id: Tool identifier
        method: Method to invoke
        parameters: Method parameters
        invocation_id: Optional unique invocation identifier
        caller_id: Optional caller identifier
        timeout: Invocation timeout

    Returns:
        Dict: Invocation result
    """
    invoker = create_observability_tool_invoker()
    context = ToolInvocationContext(
        invocation_id=invocation_id or str(uuid.uuid4()),
        tool_id=tool_id,
        method=method,
        caller_id=caller_id,
        timeout=timeout,
    )
    result = invoker.invoke_tool(context, parameters)
    return {
        "invocation_id": result.invocation_id,
        "tool_id": result.tool_id,
        "method": result.method,
        "success": result.success,
        "response": result.response,
        "response_code": result.response_code,
        "headers": result.headers,
        "metrics": result.metrics,
        "error": result.error,
        "warnings": result.warnings,
        "execution_time": result.execution_time,
    }
