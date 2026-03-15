from __future__ import annotations

"\nUnified Workflow Engine\n\nSingle entry point for all workflow orchestration, replacing 8 core engines:\n- NervousSystemAgent\n- MissionControllerEngine\n- SubatomicOrchestratorImpl\n- DAGManagerAgent\n- DagEngineAgent\n- SelfRecoveringOrchestratorAgent\n- WorkflowFissionManagerAgent\n- L3OrchestrationBase\n"
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.providers import get_clock

from .base_coordinator import WorkflowCoordinator, coordinator_registry
from .execution import (
    STRATEGY_REGISTRY,
    ExecutionStatus,
    ExecutionStrategy,
    WorkflowContext,
    WorkflowResult,
    WorkflowStep,
    get_strategy,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, emit_replay_key, emit_determinism_digest


@dataclass
class WorkflowMetrics:
    """Metrics for workflow execution."""

    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    total_time: float = 0.0
    avg_latency: float = 0.0


class ErrorHandler:
    """Unified error handling for workflows."""

    def __init__(self):
        """Initialize error handler."""
        self.recovery_strategies = {
            "retry": self._retry_strategy,
            "fallback": self._fallback_strategy,
            "skip": self._skip_strategy,
            "abort": self._abort_strategy,
        }
        # guardian: allow-magic-config
        self.max_retries = 3

    async def handle_error(
        self, error: Exception, context: WorkflowContext, recovery_type: str = "retry"
    ) -> WorkflowResult:
        """Handle workflow error with recovery strategy."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ErrorHandler.handle_error")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        strategy = self.recovery_strategies.get(recovery_type, self._abort_strategy)
        return await strategy(error, context)

    async def _retry_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Retry the workflow."""
        retries = context.state.get("retries", 0)
        if retries < self.max_retries:
            context.state["retries"] = retries + 1
            return WorkflowResult(
                workflow_id=context.workflow_id,
                status=ExecutionStatus.PENDING,
                error=f"Retry {retries + 1}/{self.max_retries}: {str(error)}",
            )
        return await self._abort_strategy(error, context)

    async def _fallback_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Use fallback logic."""
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output={"fallback": True, "original_error": str(error)},
            error=f"Fallback used: {str(error)}",
        )

    async def _skip_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Skip failed step."""
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output={"skipped": True},
            error=f"Skipped: {str(error)}",
        )

    async def _abort_strategy(self, error: Exception, context: WorkflowContext) -> WorkflowResult:
        """Abort workflow."""
        return WorkflowResult(
            workflow_id=context.workflow_id, status=ExecutionStatus.FAILED, error=str(error)
        )


class UnifiedWorkflowEngine:
    """
    Unified Workflow Engine - Single entry point for all orchestration.

    Replaces 8 core engines with:
    - Pluggable execution strategies (DAG, state machine, event-driven, reactive)
    - Unified error handling and recovery
    - Centralized logging and metrics
    - Coordinator registry for specialized domains
    """

    def __init__(self):
        """Initialize unified workflow engine."""
        self.strategies = STRATEGY_REGISTRY.copy()
        self.coordinator_registry = coordinator_registry
        self.error_handler = ErrorHandler()
        self.metrics = WorkflowMetrics()
        self.active_workflows: dict[str, WorkflowContext] = {}

    async def execute(
        self,
        workflow_type: str,
        input_data: dict[str, Any],
        steps: list[WorkflowStep] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """
        Execute workflow using appropriate strategy.

        Args:
            workflow_type: Type of workflow (dag, state_machine, event, reactive)
            input_data: Input data for workflow
            steps: Optional workflow steps
            metadata: Optional metadata

        Returns:
            Workflow result
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "UnifiedWorkflowEngine.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        workflow_id = str(uuid.uuid4())
        start_time = get_clock().now_epoch()
        self.metrics.total_workflows += 1
        context = WorkflowContext(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            input_data=input_data,
            metadata=metadata or {},
        )
        self.active_workflows[workflow_id] = context
        try:
            coordinator = self.coordinator_registry.get_for_workflow(workflow_type)
            if coordinator:
                result = await coordinator.safe_coordinate(context)
            else:
                strategy = get_strategy(workflow_type)
                if steps:
                    result = await strategy.execute(context, steps)
                else:
                    result = WorkflowResult(
                        workflow_id=workflow_id,
                        status=ExecutionStatus.COMPLETED,
                        output={"message": "No steps provided"},
                    )
            if result.status == ExecutionStatus.COMPLETED:
                self.metrics.completed_workflows += 1
            else:
                self.metrics.failed_workflows += 1
            elapsed = get_clock().now_epoch() - start_time
            self.metrics.total_time += elapsed
            self.metrics.avg_latency = self.metrics.total_time / self.metrics.total_workflows
            result.metrics["execution_time"] = elapsed
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.metrics.failed_workflows += 1
            return await self.error_handler.handle_error(e, context, "abort")
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

    async def execute_with_coordinator(
        self, coordinator_name: str, input_data: dict[str, Any], metadata: dict[str, Any] | None = None
    ) -> WorkflowResult:
        """
        Execute workflow using specific coordinator.

        Args:
            coordinator_name: Name of coordinator
            input_data: Input data
            metadata: Optional metadata

        Returns:
            Workflow result
        """
        coordinator = self.coordinator_registry.get(coordinator_name)
        if not coordinator:
            return WorkflowResult(
                workflow_id=str(uuid.uuid4()),
                status=ExecutionStatus.FAILED,
                error=f"Coordinator not found: {coordinator_name}",
            )
        context = WorkflowContext(
            workflow_id=str(uuid.uuid4()),
            workflow_type=coordinator_name,
            input_data=input_data,
            metadata=metadata or {},
        )
        return await coordinator.safe_coordinate(context)

    def register_coordinator(self, coordinator: WorkflowCoordinator) -> None:
        """Register coordinator with engine."""
        self.coordinator_registry.register(coordinator)

    def register_strategy(self, name: str, strategy: ExecutionStrategy) -> None:
        """Register execution strategy."""
        self.strategies[name] = strategy

    def get_statistics(self) -> dict[str, Any]:
        """Get engine statistics."""
        return {
            "metrics": {
                "total_workflows": self.metrics.total_workflows,
                "completed_workflows": self.metrics.completed_workflows,
                "failed_workflows": self.metrics.failed_workflows,
                "success_rate": self.metrics.completed_workflows / self.metrics.total_workflows * 100
                if self.metrics.total_workflows > 0
                else 0,
                "total_time": self.metrics.total_time,
                "avg_latency": self.metrics.avg_latency,
            },
            "active_workflows": len(self.active_workflows),
            "strategies": list(self.strategies.keys()),
            "coordinators": self.coordinator_registry.get_statistics(),
        }

    def get_active_workflows(self) -> list[str]:
        """Get list of active workflow IDs."""
        return list(self.active_workflows.keys())


unified_engine = UnifiedWorkflowEngine()
