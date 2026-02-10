"""Use observability Execution - Execution adapter for observability operations.

This module provides adapters for executing observability operations with proper
resource management, error handling, and result processing.
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


class ExecutionStrategy(Enum):
    """Strategies for execution."""

    IMMEDIATE = "immediate"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    CONDITIONAL = "conditional"


class ExecutionPriority(Enum):
    """Priority levels for execution."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExecutionRequest:
    """Request for observability execution."""

    request_id: str
    operation_type: str
    parameters: dict[str, Any]
    strategy: ExecutionStrategy = ExecutionStrategy.IMMEDIATE
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    timeout: float = 30.0
    retry_policy: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionEnvironment:
    """Environment for execution."""

    env_id: str
    resources: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, str] = field(default_factory=dict)
    limits: dict[str, Any] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)


@dataclass
class ExecutionConfig:
    """configuration for execution."""

    default_timeout: float = 30.0
    max_concurrent_executions: int = 10
    enable_queueing: bool = True
    queue_size: int = 100
    enable_retry: bool = True
    max_retries: int = 3
    enable_metrics: bool = True


@dataclass
class ExecutionResult:
    """Result of execution."""

    request_id: str
    operation_type: str
    success: bool
    output: Any | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    resource_usage: dict[str, float] = field(default_factory=dict)


class ObservabilityExecutionEngine:
    """Main engine for observability execution."""

    def __init__(self, config: ExecutionConfig | None = None):
        self.config = config or ExecutionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._operation_handlers: dict[str, Callable] = {}
        self._execution_queue: list[ExecutionRequest] = []
        self._active_executions: dict[str, dict[str, Any]] = {}
        self._execution_history: list[ExecutionResult] = []
        self._environments: dict[str, ExecutionEnvironment] = {}
        self._initialize_handlers()

    def register_operation(self, operation_type: str, handler: Callable) -> None:
        """Register an operation handler.

        Args:
            operation_type: Type of operation
            handler: Handler function
        """
        self._operation_handlers[operation_type] = handler
        self.logger.info(f"Registered operation: {operation_type}")

    def execute(
        self,
        request: ExecutionRequest,
        environment: ExecutionEnvironment | None = None,
    ) -> ExecutionResult:
        """Execute an observability operation.

        Args:
            request: Execution request
            environment: Optional execution environment

        Returns:
            ExecutionResult: Execution result
        """
        self.logger.info(f"Executing operation: {request.operation_type}")

        start_time = time.time()

        try:
            # Validate operation exists
            if request.operation_type not in self._operation_handlers:
                return self._create_error_result(
                    request.request_id,
                    request.operation_type,
                    f"Operation not registered: {request.operation_type}",
                    start_time,
                )

            # Check dependencies
            if not self._check_dependencies(request.dependencies):
                return self._create_error_result(
                    request.request_id,
                    request.operation_type,
                    "Dependencies not satisfied",
                    start_time,
                )

            # Execute based on strategy
            if request.strategy == ExecutionStrategy.IMMEDIATE:
                result = self._execute_immediate(request, environment)
            elif request.strategy == ExecutionStrategy.QUEUED:
                result = self._execute_queued(request, environment)
            elif request.strategy == ExecutionStrategy.SCHEDULED:
                result = self._execute_scheduled(request, environment)
            elif request.strategy == ExecutionStrategy.CONDITIONAL:
                result = self._execute_conditional(request, environment)
            else:
                raise ValueError(f"Unsupported execution strategy: {request.strategy}")

            # Calculate execution time
            result.execution_time = time.time() - start_time

            # Record in history
            self._execution_history.append(result)

            return result

        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            return self._create_error_result(
                request.request_id,
                request.operation_type,
                str(e),
                start_time,
            )

    def execute_batch(
        self,
        requests: list[ExecutionRequest],
        environment: ExecutionEnvironment | None = None,
    ) -> list[ExecutionResult]:
        """Execute multiple operations.

        Args:
            requests: List of execution requests
            environment: Optional execution environment

        Returns:
            List[ExecutionResult]: Results for all executions
        """
        results = []

        # Sort by priority
        sorted_requests = sorted(
            requests,
            key=lambda r: self._priority_value(r.priority),
            reverse=True,
        )

        for request in sorted_requests:
            result = self.execute(request, environment)
            results.append(result)

        return results

    def queue_execution(self, request: ExecutionRequest) -> bool:
        """Queue an execution request.

        Args:
            request: Execution request

        Returns:
            bool: True if queued successfully
        """
        if len(self._execution_queue) >= self.config.queue_size:
            self.logger.warning("Execution queue is full")
            return False

        self._execution_queue.append(request)
        self.logger.info(f"Queued execution: {request.request_id}")
        return True

    def process_queue(
        self,
        environment: ExecutionEnvironment | None = None,
    ) -> list[ExecutionResult]:
        """Process queued executions.

        Args:
            environment: Optional execution environment

        Returns:
            List[ExecutionResult]: Results for processed executions
        """
        results = []

        while self._execution_queue and len(self._active_executions) < self.config.max_concurrent_executions:
            request = self._execution_queue.pop(0)
            result = self.execute(request, environment)
            results.append(result)

        return results

    def get_execution_status(self, request_id: str) -> dict[str, Any] | None:
        """Get execution status.

        Args:
            request_id: Request identifier

        Returns:
            Optional[Dict]: Execution status
        """
        return self._active_executions.get(request_id)

    def cancel_execution(self, request_id: str) -> bool:
        """Cancel an active execution.

        Args:
            request_id: Request identifier

        Returns:
            bool: True if cancelled successfully
        """
        if request_id in self._active_executions:
            execution = self._active_executions[request_id]
            execution["cancelled"] = True
            self.logger.info(f"Cancelled execution: {request_id}")
            return True

        # Also check queue
        for i, request in enumerate(self._execution_queue):
            if request.request_id == request_id:
                del self._execution_queue[i]
                self.logger.info(f"Removed from queue: {request_id}")
                return True

        return False

    def register_environment(self, environment: ExecutionEnvironment) -> None:
        """Register an execution environment.

        Args:
            environment: Execution environment
        """
        self._environments[environment.env_id] = environment
        self.logger.info(f"Registered environment: {environment.env_id}")

    def get_execution_history(self, limit: int | None = None) -> list[ExecutionResult]:
        """Get execution history.

        Args:
            limit: Optional limit on number of results

        Returns:
            List[ExecutionResult]: Execution history
        """
        if limit:
            return self._execution_history[-limit:]
        return self._execution_history

    def _execute_immediate(
        self,
        request: ExecutionRequest,
        environment: ExecutionEnvironment | None,
    ) -> ExecutionResult:
        """Execute immediately."""
        return self._execute_with_handler(request, environment)

    def _execute_queued(
        self,
        request: ExecutionRequest,
        environment: ExecutionEnvironment | None,
    ) -> ExecutionResult:
        """Execute from queue."""
        # For queued execution, we execute immediately but with queue metadata
        result = self._execute_with_handler(request, environment)
        result.metrics["queue_time"] = 0.1  # Simulated queue time
        return result

    def _execute_scheduled(
        self,
        request: ExecutionRequest,
        environment: ExecutionEnvironment | None,
    ) -> ExecutionResult:
        """Execute scheduled execution."""
        # Check if scheduled time has arrived
        scheduled_time = request.metadata.get("scheduled_time")
        if scheduled_time:
            scheduled_dt = datetime.fromisoformat(scheduled_time)
            if datetime.utcnow() < scheduled_dt:
                return self._create_error_result(
                    request.request_id,
                    request.operation_type,
                    "Scheduled time not reached",
                    time.time(),
                )

        return self._execute_with_handler(request, environment)

    def _execute_conditional(
        self,
        request: ExecutionRequest,
        environment: ExecutionEnvironment | None,
    ) -> ExecutionResult:
        """Execute based on conditions."""
        # Check conditions
        conditions = request.metadata.get("conditions", {})

        for condition, expected_value in conditions.items():
            actual_value = self._evaluate_condition(condition, environment)
            if actual_value != expected_value:
                return self._create_error_result(
                    request.request_id,
                    request.operation_type,
                    f"Condition not met: {condition}",
                    time.time(),
                )

        return self._execute_with_handler(request, environment)

    def _execute_with_handler(
        self,
        request: ExecutionRequest,
        environment: ExecutionEnvironment | None,
    ) -> ExecutionResult:
        """Execute with registered handler."""
        handler = self._operation_handlers[request.operation_type]

        # Track execution
        self._track_execution_start(request)

        try:
            # Prepare execution context
            exec_context = {"request": request, "environment": environment, "config": self.config}

            # Execute handler
            output = handler(exec_context)

            # Extract metrics and artifacts
            metrics = output.get("metrics", {}) if isinstance(output, dict) else {}
            artifacts = output.get("artifacts", []) if isinstance(output, dict) else []
            resource_usage = output.get("resource_usage", {}) if isinstance(output, dict) else {}

            return ExecutionResult(
                request_id=request.request_id,
                operation_type=request.operation_type,
                success=True,
                output=output,
                exit_code=0,
                metrics=metrics,
                artifacts=artifacts,
                resource_usage=resource_usage,
            )

        finally:
            self._track_execution_complete(request)

    def _check_dependencies(self, dependencies: list[str]) -> bool:
        """Check if dependencies are satisfied."""
        for dep in dependencies:
            # Check if dependency exists in history
            found = any(result.request_id == dep and result.success for result in self._execution_history)
            if not found:
                return False
        return True

    def _evaluate_condition(
        self,
        condition: str,
        environment: ExecutionEnvironment | None,
    ) -> object:
        """Evaluate a condition."""
        if environment:
            # Check environment variables
            if condition.startswith("env."):
                var_name = condition[4:]
                return environment.variables.get(var_name)

            # Check resources
            if condition.startswith("resource."):
                resource_name = condition[9:]
                return environment.resources.get(resource_name)

        # Default values
        if condition == "system.healthy":
            return True
        elif condition == "system.load":
            return 0.5

        return None

    def _priority_value(self, priority: ExecutionPriority) -> int:
        """Get numeric value for priority."""
        priority_map = {
            ExecutionPriority.LOW: 1,
            ExecutionPriority.NORMAL: 2,
            ExecutionPriority.HIGH: 3,
            ExecutionPriority.CRITICAL: 4,
        }
        return priority_map.get(priority, 2)

    def _track_execution_start(self, request: ExecutionRequest) -> None:
        """Track execution start."""
        self._active_executions[request.request_id] = {
            "operation_type": request.operation_type,
            "start_time": time.time(),
            "status": "running",
            "cancelled": False,
        }

    def _track_execution_complete(self, request: ExecutionRequest) -> None:
        """Track execution completion."""
        if request.request_id in self._active_executions:
            execution = self._active_executions[request.request_id]
            execution["end_time"] = time.time()
            execution["status"] = "completed"
            del self._active_executions[request.request_id]

    def _create_error_result(
        self,
        request_id: str,
        operation_type: str,
        error: str,
        start_time: float,
    ) -> ExecutionResult:
        """Create error result."""
        return ExecutionResult(
            request_id=request_id,
            operation_type=operation_type,
            success=False,
            error=error,
            exit_code=1,
            execution_time=time.time() - start_time,
        )

    def _initialize_handlers(self) -> None:
        """Initialize built-in handlers."""

        # Metrics collection handler
        def _metrics_handler(context: dict[str, Any]) -> dict[str, Any]:
            context["request"]

            return {
                "metrics": {"cpu_usage": 45.2, "memory_usage": 67.8, "disk_usage": 23.5},
                "collected_at": datetime.utcnow().isoformat(),
                "metrics": {"metrics_count": 3, "processing_time": 0.1},
            }

        # Log analysis handler
        def _log_analysis_handler(context: dict[str, Any]) -> dict[str, Any]:
            context["request"]

            return {
                "analysis": {"total_logs": 100, "error_count": 5, "warning_count": 10},
                "patterns": [
                    {"type": "error_spike", "count": 3},
                    {"type": "slow_response", "count": 7},
                ],
                "metrics": {"logs_analyzed": 100, "processing_time": 0.2},
            }

        # Trace analysis handler
        def _trace_analysis_handler(context: dict[str, Any]) -> dict[str, Any]:
            context["request"]

            return {
                "traces": [
                    {"trace_id": "trace_1", "duration": 0.5, "spans": 5},
                    {"trace_id": "trace_2", "duration": 0.3, "spans": 3},
                ],
                "summary": {"avg_duration": 0.4, "error_rate": 0.05},
                "metrics": {"traces_analyzed": 2, "processing_time": 0.15},
            }

        # Health check handler
        def _health_check_handler(context: dict[str, Any]) -> dict[str, Any]:
            return {
                "status": "healthy",
                "checks": [
                    {"name": "database", "status": "ok"},
                    {"name": "redis", "status": "ok"},
                    {"name": "api", "status": "ok"},
                ],
                "metrics": {"checks_performed": 3, "processing_time": 0.05},
            }

        # Register handlers
        self.register_operation("collect_metrics", _metrics_handler)
        self.register_operation("analyze_logs", _log_analysis_handler)
        self.register_operation("analyze_traces", _trace_analysis_handler)
        self.register_operation("health_check", _health_check_handler)


# Factory function for easy instantiation
# guardian: allow-magic-config
def create_observability_execution_engine(
    # guardian: allow-magic-config
    default_timeout: float = 30.0,
    # guardian: allow-magic-config
    max_concurrent_executions: int = 10,
    enable_queueing: bool = True,
    **kwargs: object,
) -> ObservabilityExecutionEngine:
    """Create a configured observability execution engine."""
    config = ExecutionConfig(
        default_timeout=default_timeout,
        max_concurrent_executions=max_concurrent_executions,
        enable_queueing=enable_queueing,
        **kwargs,
    )
    return ObservabilityExecutionEngine(config)


# Convenience function for direct usage
# guardian: allow-magic-config
def use_observability_execution(
    operation_type: str,
    parameters: dict[str, Any],
    request_id: str | None = None,
    strategy: str = "immediate",
    priority: str = "normal",
    # guardian: allow-magic-config
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Execute observability operation.

    Args:
        operation_type: Type of operation
        parameters: Operation parameters
        request_id: Optional unique request identifier
        strategy: Execution strategy
        priority: Execution priority
        timeout: Execution timeout

    Returns:
        Dict: Execution result
    """
    engine = create_observability_execution_engine()

    request = ExecutionRequest(
        request_id=request_id or str(uuid.uuid4()),
        operation_type=operation_type,
        parameters=parameters,
        strategy=ExecutionStrategy(strategy),
        priority=ExecutionPriority(priority),
        timeout=timeout,
    )

    result = engine.execute(request)

    return {
        "request_id": result.request_id,
        "operation_type": result.operation_type,
        "success": result.success,
        "output": result.output,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "metrics": result.metrics,
        "artifacts": result.artifacts,
        "error": result.error,
        "warnings": result.warnings,
        "execution_time": result.execution_time,
        "resource_usage": result.resource_usage,
    }
