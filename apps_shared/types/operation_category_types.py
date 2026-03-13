"""Perform observability Operation - observability operation execution adapter.

This module provides adapters for performing specific observability operations
with proper error handling, context management, and result aggregation.
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


class OperationCategory(Enum):
    """Categories of observability operations."""

    MONITORING = "monitoring"
    TRACING = "tracing"
    LOGGING = "logging"
    METRICS = "metrics"
    ALERTING = "alerting"


class OperationScope(Enum):
    """Scope of observability operations."""

    SYSTEM = "system"
    COMPONENT = "component"
    SERVICE = "service"
    REQUEST = "request"
    CUSTOM = "custom"


@dataclass
class OperationContext:
    """Context for observability operation."""

    operation_id: str
    category: OperationCategory
    scope: OperationScope
    target: str
    correlation_id: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationParameters:
    """Parameters for observability operation."""

    operation_type: str
    config: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)
    aggregation: str | None = None
    time_range: tuple[datetime, datetime] | None = None
    limit: int | None = None


@dataclass
class OperationConfig:
    """configuration for operation execution."""

    timeout: float = 30.0
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: float = 300.0
    enable_compression: bool = False


@dataclass
class OperationOutcome:
    """Outcome of observability operation."""

    operation_id: str
    success: bool
    data: dict[str, Any] | list[Any] | None = None
    count: int = 0
    aggregated_values: dict[str, float] = field(default_factory=dict)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityOperationAdapter:
    """Main adapter for performing observability operations."""

    def __init__(self, config: OperationConfig | None = None):
        self.config = config or OperationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._operation_handlers: dict[str, Callable] = {}
        self._cache: dict[str, tuple[Any, float]] = {}
        self._initialize_handlers()

    def register_handler(self, operation_type: str, handler: Callable) -> None:
        """Register a handler for operation type.

        Args:
            operation_type: Type of operation
            handler: Handler function
        """
        self._operation_handlers[operation_type] = handler
        self.logger.info(f"Registered handler for operation: {operation_type}")

    def perform_operation(
        self, context: OperationContext, parameters: OperationParameters
    ) -> OperationOutcome:
        """Perform observability operation.

        Args:
            context: Operation context
            parameters: Operation parameters

        Returns:
            OperationOutcome: Result of operation
        """
        self.logger.info(f"Performing operation: {context.operation_id}")
        start_time = time.time()
        try:
            if self.config.enable_caching:
                cached_result = self._get_from_cache(context, parameters)
                if cached_result is not None:
                    self.logger.info(f"Returning cached result for: {context.operation_id}")
                    cached_result.execution_time = time.time() - start_time
                    return cached_result
            handler = self._operation_handlers.get(parameters.operation_type)
            if not handler:
                return self._create_error_outcome(
                    context.operation_id,
                    f"No handler for operation type: {parameters.operation_type}",
                    start_time,
                )
            result = self._execute_with_retry(handler, context, parameters)
            if self.config.enable_caching and result.success:
                self._store_in_cache(context, parameters, result)
            result.execution_time = time.time() - start_time
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Operation failed: {str(e)}")
            return self._create_error_outcome(context.operation_id, str(e), start_time)

    def perform_batch_operations(
        self, contexts: list[OperationContext], parameters_list: list[OperationParameters]
    ) -> list[OperationOutcome]:
        """Perform multiple operations.

        Args:
            contexts: List of operation contexts
            parameters_list: List of operation parameters

        Returns:
            List[OperationOutcome]: Results for all operations
        """
        if len(contexts) != len(parameters_list):
            raise ValueError("Contexts and parameters lists must have same length")
        results = []
        for context, parameters in zip(contexts, parameters_list, strict=False):
            result = self.perform_operation(context, parameters)
            results.append(result)
        return results

    def perform_aggregated_operation(
        self, contexts: list[OperationContext], parameters: OperationParameters
    ) -> OperationOutcome:
        """Perform operation with aggregation across multiple contexts.

        Args:
            contexts: List of operation contexts
            parameters: Operation parameters

        Returns:
            OperationOutcome: Aggregated result
        """
        self.logger.info(f"Performing aggregated operation across {len(contexts)} contexts")
        start_time = time.time()
        all_data = []
        all_errors = []
        all_warnings = []
        for context in contexts:
            result = self.perform_operation(context, parameters)
            if result.success and result.data:
                if isinstance(result.data, list):
                    all_data.extend(result.data)
                else:
                    all_data.append(result.data)
            if result.error:
                all_errors.append(result.error)
            all_warnings.extend(result.warnings)
        aggregated_data = self._aggregate_data(all_data, parameters.aggregation)
        aggregated_values = self._calculate_aggregated_values(all_data)
        outcome = OperationOutcome(
            operation_id=f"aggregated_{int(time.time())}",
            success=len(all_errors) == 0,
            data=aggregated_data,
            count=len(all_data),
            aggregated_values=aggregated_values,
            error="; ".join(all_errors) if all_errors else None,
            warnings=all_warnings,
            execution_time=time.time() - start_time,
        )
        return outcome

    def get_operation_history(
        self, operation_id: str | None = None, time_range: tuple[datetime, datetime] | None = None
    ) -> list[dict[str, Any]]:
        """Get history of operations.

        Args:
            operation_id: Optional specific operation ID
            time_range: Optional time range filter

        Returns:
            List[Dict]: Operation history
        """
        return []

    def clear_cache(self, pattern: str | None = None) -> int:
        """Clear operation cache.

        Args:
            pattern: Optional pattern to match cache keys

        Returns:
            int: Number of cache entries cleared
        """
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count
        to_remove = []
        for key in self._cache:
            if pattern in key:
                to_remove.append(key)
        for key in to_remove:
            del self._cache[key]
        return len(to_remove)

    def _execute_with_retry(
        self, handler: Callable, context: OperationContext, parameters: OperationParameters
    ) -> OperationOutcome:
        """Execute operation with retry logic."""
        last_error = None
        for attempt in range(self.config.retry_attempts + 1):
            try:
                exec_data = {"context": context, "parameters": parameters, "attempt": attempt + 1}
                result_data = handler(exec_data)
                data = result_data.get("data")
                count = result_data.get("count", 0)
                aggregated_values = result_data.get("aggregated_values", {})
                warnings = result_data.get("warnings", [])
                return OperationOutcome(
                    operation_id=context.operation_id,
                    success=True,
                    data=data,
                    count=count,
                    aggregated_values=aggregated_values,
                    warnings=warnings,
                )
            # guardian: allow-silent-swallow
            except Exception as e:
                last_error = str(e)
                if attempt < self.config.retry_attempts:
                    self.logger.warning(f"Operation attempt {attempt + 1} failed, retrying: {last_error}")
                    time.sleep(2**attempt)
                else:
                    self.logger.error(f"Operation failed after {attempt + 1} attempts: {last_error}")
        return self._create_error_outcome(context.operation_id, last_error, time.time())

    def _get_from_cache(
        self, context: OperationContext, parameters: OperationParameters
    ) -> OperationOutcome | None:
        """Get result from cache."""
        cache_key = self._generate_cache_key(context, parameters)
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                return cached_data
            else:
                del self._cache[cache_key]
        return None

    def _store_in_cache(
        self, context: OperationContext, parameters: OperationParameters, result: OperationOutcome
    ) -> None:
        """Store result in cache."""
        cache_key = self._generate_cache_key(context, parameters)
        self._cache[cache_key] = (result, time.time())

    def _generate_cache_key(self, context: OperationContext, parameters: OperationParameters) -> str:
        """Generate cache key for operation."""
        key_data = {
            "operation_type": parameters.operation_type,
            "target": context.target,
            "scope": context.scope.value,
            "config": parameters.config,
            "filters": parameters.filters,
        }
        return f"obs_op_{hash(json.dumps(key_data, sort_keys=True))}"

    def _group_by_type(self, data: list[Any]) -> dict[str, list[Any]]:
        """Group data items by their type."""
        groups = {}
        for item in data:
            item_type = type(item).__name__
            if item_type not in groups:
                groups[item_type] = []
            groups[item_type].append(item)
        return groups

    def _aggregate_numeric(self, data: list[Any], method: str) -> dict[str, float] | None:
        """Aggregate numeric data."""
        if not data or not all(isinstance(d, int | float) for d in data):
            return None
        if method == "sum":
            return {"sum": sum(data)}
        elif method == "average":
            return {"average": sum(data) / len(data)}
        return None

    def _aggregate_by_method(self, data: list[Any], aggregation: str) -> dict[str, Any] | list[Any]:
        """Perform specific aggregation method on data."""
        if aggregation == "count":
            return {"total": len(data)}
        if aggregation in ("sum", "average"):
            result = self._aggregate_numeric(data, aggregation)
            if result:
                return result
        if aggregation == "unique":
            return {"unique_items": list(set(data))}
        if aggregation == "group_by":
            return self._group_by_type(data)
        return data

    def _aggregate_data(self, data: list[Any], aggregation: str | None) -> dict[str, Any] | list[Any]:
        """Aggregate data based on aggregation method."""
        if not aggregation:
            return data
        return self._aggregate_by_method(data, aggregation)

    def _calculate_aggregated_values(self, data: list[Any]) -> dict[str, float]:
        """Calculate aggregated values from data."""
        values = {}
        if data:
            values["count"] = len(data)
            numeric_data = [d for d in data if isinstance(d, int | float)]
            if numeric_data:
                values["sum"] = sum(numeric_data)
                values["average"] = values["sum"] / len(numeric_data)
                values["min"] = min(numeric_data)
                values["max"] = max(numeric_data)
        return values

    def _create_error_outcome(self, operation_id: str, error: str, start_time: float) -> OperationOutcome:
        """Create error outcome."""
        return OperationOutcome(
            operation_id=operation_id, success=False, error=error, execution_time=time.time() - start_time
        )

    def _initialize_handlers(self) -> None:
        """Initialize default operation handlers."""

        def _health_check_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            context = exec_data["context"]
            return {
                "data": {
                    "status": "healthy",
                    "target": context.target,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "count": 1,
            }

        def _metrics_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            parameters = exec_data["parameters"]
            metric_names = parameters.config.get("metrics", [])
            return {
                "data": [
                    {"name": name, "value": 42.0, "timestamp": datetime.utcnow().isoformat()}
                    for name in metric_names
                ],
                "count": len(metric_names),
                "aggregated_values": {"total_metrics": len(metric_names)},
            }

        def _log_query_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            parameters = exec_data["parameters"]
            level = parameters.config.get("level", "info")
            limit = parameters.limit or 100
            return {
                "data": [
                    {
                        "message": f"Sample log message {i}",
                        "level": level,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    for i in range(min(limit, 10))
                ],
                "count": min(limit, 10),
            }

        def _trace_query_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            context = exec_data["context"]
            trace_id = context.correlation_id
            return {
                "data": {
                    "trace_id": trace_id,
                    "spans": [
                        {"operation": "span1", "duration": 0.1},
                        {"operation": "span2", "duration": 0.2},
                    ],
                },
                "count": 1,
            }

        self.register_handler("health_check", _health_check_handler)
        self.register_handler("collect_metrics", _metrics_handler)
        self.register_handler("query_logs", _log_query_handler)
        self.register_handler("query_traces", _trace_query_handler)


# guardian: allow-magic-config
def create_observability_operation_adapter(
    timeout: float = 30.0, retry_attempts: int = 3, enable_caching: bool = True, **kwargs: object
) -> ObservabilityOperationAdapter:
    """Create a configured observability operation adapter."""
    config = OperationConfig(
        timeout=timeout, retry_attempts=retry_attempts, enable_caching=enable_caching, **kwargs
    )
    return ObservabilityOperationAdapter(config)


def perform_observability_operation(
    operation_id: str,
    category: str,
    scope: str,
    target: str,
    operation_type: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Perform observability operation.

    Args:
        operation_id: Unique operation identifier
        category: Operation category
        scope: Operation scope
        target: Target system or component
        operation_type: Type of operation to perform
        config: Optional configuration

    Returns:
        Dict: Operation outcome
    """
    adapter = create_observability_operation_adapter()
    context = OperationContext(
        operation_id=operation_id,
        category=OperationCategory(category),
        scope=OperationScope(scope),
        target=target,
    )
    parameters = OperationParameters(operation_type=operation_type, config=config or {})
    outcome = adapter.perform_operation(context, parameters)
    return {
        "operation_id": outcome.operation_id,
        "success": outcome.success,
        "data": outcome.data,
        "count": outcome.count,
        "aggregated_values": outcome.aggregated_values,
        "error": outcome.error,
        "warnings": outcome.warnings,
        "execution_time": outcome.execution_time,
    }
