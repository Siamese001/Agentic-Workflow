"""Invoke Observability Tool - Tool invocation adapter for observability operations.

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
    """Configuration for tool invocation."""
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

    def register_tool(self, tool_name: str, endpoint: ToolEndpoint,
                     handler: Callable | None = None) -> None:
        """Register a tool endpoint.

        Args:
            tool_name: Name of the tool
            endpoint: Tool endpoint definition
            handler: Optional handler function
        """
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
            # Check cache if enabled
            if self.config.enable_caching:
                cached_response = self._get_from_cache(request)
                if cached_response is not None:
                    self.logger.info(f"Returning cached response for: {request.invocation_id}")
                    cached_response.execution_time = time.time() - start_time
                    return cached_response

            # Validate tool exists
            if request.tool_name not in self._registered_tools:
                return self._create_error_response(
                    request.invocation_id,
                    request.tool_name,
                    f"Tool not registered: {request.tool_name}",
                    start_time
                )

            # Execute invocation based on type
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

            # Cache response if enabled and successful
            if self.config.enable_caching and response.success:
                self._store_in_cache(request, response)

            # Calculate execution time
            response.execution_time = time.time() - start_time

            return response

        except Exception as e:
            self.logger.error(f"Tool invocation failed: {str(e)}")
            return self._create_error_response(
                request.invocation_id,
                request.tool_name,
                str(e),
                start_time
            )

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

        # Get handler
        handler = self._tool_handlers.get(request.tool_name)
        if not handler:
            raise ValueError(f"No handler for tool: {request.tool_name}")

        # Execute and stream
        for chunk in handler(request.parameters, stream=True):
            yield chunk

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
            "last_check": datetime.utcnow().isoformat()
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

        # Clear matching entries
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
            # Use registered handler
            result = handler(request.method, request.parameters)
            return InvocationResponse(
                invocation_id=request.invocation_id,
                tool_name=request.tool_name,
                success=True,
                data=result,
                status_code=200
            )
        else:
            # Simulate direct invocation
            return self._simulate_invocation(request)

    def _invoke_proxy(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke tool through proxy."""
        # Simulate proxy invocation
        return self._simulate_invocation(request, proxy=True)

    def _invoke_async(self, request: InvocationRequest) -> InvocationResponse:
        """Invoke tool asynchronously."""
        # Simulate async invocation
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
                response_format=request.response_format
            )

            response = self._invoke_direct(item_request)
            results.append(response.data if response.success else {"error": response.error})

        return InvocationResponse(
            invocation_id=request.invocation_id,
            tool_name=request.tool_name,
            success=True,
            data=results,
            status_code=200
        )

    def _simulate_invocation(self, request: InvocationRequest,
                           proxy: bool = False,
                           async_mode: bool = False) -> InvocationResponse:
        """Simulate tool invocation."""
        # Simulate processing time
        time.sleep(0.1)

        # Generate mock response based on tool and method
        if request.tool_name == "trace_collector":
            data = {
                "trace_id": request.parameters.get("trace_id", "mock_trace_123"),
                "spans": [
                    {"operation": "span1", "duration": 0.1},
                    {"operation": "span2", "duration": 0.2}
                ]
            }
        elif request.tool_name == "metric_collector":
            data = {
                "metrics": [
                    {"name": "cpu", "value": 45.2},
                    {"name": "memory", "value": 67.8}
                ]
            }
        elif request.tool_name == "log_analyzer":
            data = {
                "logs": [
                    {"message": "Sample log", "level": "info"},
                    {"message": "Error log", "level": "error"}
                ]
            }
        else:
            data = {"message": f"Mock response from {request.tool_name}"}

        # Add metadata
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
            status_code=200
        )

    def _get_from_cache(self, request: InvocationRequest) -> InvocationResponse | None:
        """Get response from cache."""
        cache_key = self._generate_cache_key(request)

        if cache_key in self._invocation_cache:
            cached_response, timestamp = self._invocation_cache[cache_key]

            # Check if cache entry is still valid
            if time.time() - timestamp < self.config.cache_ttl:
                return cached_response
            else:
                del self._invocation_cache[cache_key]

        return None

    def _store_in_cache(self, request: InvocationRequest,
                       response: InvocationResponse) -> None:
        """Store response in cache."""
        cache_key = self._generate_cache_key(request)
        self._invocation_cache[cache_key] = (response, time.time())

    def _generate_cache_key(self, request: InvocationRequest) -> str:
        """Generate cache key for request."""
        key_data = {
            "tool_name": request.tool_name,
            "method": request.method,
            "parameters": request.parameters
        }
        return f"tool_invoke_{hash(json.dumps(key_data, sort_keys=True))}"

    def _create_error_response(self, invocation_id: str, tool_name: str,
                              error: str, start_time: float) -> InvocationResponse:
        """Create error response."""
        return InvocationResponse(
            invocation_id=invocation_id,
            tool_name=tool_name,
            success=False,
            error=error,
            execution_time=time.time() - start_time
        )

    def _initialize_handlers(self) -> None:
        """Initialize default tool handlers."""
        # Trace collector handler
        def _trace_handler(method: str, params: dict[str, Any]) -> dict[str, Any]:
            if method == "collect":
                return {
                    "traces": [
                        {"id": params.get("trace_id", "default"), "duration": 0.5}
                    ]
                }
            elif method == "analyze":
                return {"analysis": "trace_analysis_complete"}
            else:
                raise ValueError(f"Unknown method: {method}")

        # Metric collector handler
        def _metric_handler(method: str, params: dict[str, Any]) -> dict[str, Any]:
            if method == "collect":
                return {
                    "metrics": [
                        {"name": "cpu", "value": 45.2, "timestamp": datetime.utcnow().isoformat()}
                    ]
                }
            elif method == "query":
                return {"query_result": "metric_data"}
            else:
                raise ValueError(f"Unknown method: {method}")

        # Log analyzer handler
        def _log_handler(method: str, params: dict[str, Any]) -> dict[str, Any]:
            if method == "analyze":
                return {
                    "analysis": {
                        "total_logs": 100,
                        "error_count": 5,
                        "warnings": 10
                    }
                }
            elif method == "filter":
                return {"filtered_logs": []}
            else:
                raise ValueError(f"Unknown method: {method}")

        # Register handlers
        self._tool_handlers["trace_collector"] = _trace_handler
        self._tool_handlers["metric_collector"] = _metric_handler
        self._tool_handlers["log_analyzer"] = _log_handler


# Factory function for easy instantiation
def create_observability_tool_invoker(
    default_timeout: float = 30.0,
    retry_attempts: int = 3,
    enable_caching: bool = True,
    **kwargs: object
) -> ObservabilityToolInvoker:
    """Create a configured observability tool invoker."""
    config = InvocationConfig(
        default_timeout=default_timeout,
        retry_attempts=retry_attempts,
        enable_caching=enable_caching,
        **kwargs
    )
    return ObservabilityToolInvoker(config)


# Convenience function for direct usage
def invoke_observability_tool(
    invocation_id: str,
    tool_name: str,
    method: str,
    parameters: dict[str, Any],
    invocation_type: str = "direct",
    response_format: str = "json"
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
        response_format=ResponseFormat(response_format)
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
        "execution_time": response.execution_time
    }
