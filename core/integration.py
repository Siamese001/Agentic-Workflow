"""Integration helpers for L3, L4, and L5 layers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar

from l4.manager import StateManager
from l5 import SafetySystem

from .errors import (
    ErrorContext,
    ErrorSeverity,
    NodeExecutionError,
    WorkflowError,
    WorkflowErrorCode,
)
from .models.dag_models import DAGResult, NodeExecutionResult, NodeStatus
from .workflow_context import NodeExecutionConfig, RetryConfig, WorkflowContext


TState = TypeVar("TState")


@dataclass
class WorkflowExecutionConfig:
    """High-level workflow execution configuration."""

    max_retries: int = 3
    retry_delay: float = 0.5
    fail_fast: bool = True
    default_node_timeout: Optional[float] = 30.0


def create_workflow_context(
    workflow_id: str,
    initial_state: TState,
    safety_system: Optional[SafetySystem] = None,
    **metadata: Any,
) -> WorkflowContext[TState]:
    """Factory for a `WorkflowContext` wired with L4 and optional L5."""

    state_manager: StateManager[TState] = StateManager(initial_state)
    return WorkflowContext(
        workflow_id=workflow_id,
        state_manager=state_manager,
        safety_system=safety_system,
        metadata=metadata,
    )


async def execute_workflow(
    workflow_id: str,
    initial_state: TState,
    node_executors: Dict[str, Callable[..., Awaitable[Any]]],
    node_dependencies: Dict[str, List[str]],
    safety_system: Optional[SafetySystem] = None,
    config: Optional[WorkflowExecutionConfig] = None,
    **metadata: Any,
) -> DAGResult:
    """Execute a simple DAG with L4+L5 integration and error handling."""

    cfg = config or WorkflowExecutionConfig()
    ctx = create_workflow_context(
        workflow_id=workflow_id,
        initial_state=initial_state,
        safety_system=safety_system,
        **metadata,
    )

    # Register basic error handlers for observability / hooks.
    async def _on_node_error(exc: BaseException) -> None:  # noqa: D401, ANN001
        # Hook point for logging/metrics in later phases.
        _ = exc

    ctx.add_error_handler(NodeExecutionError, _on_node_error)

    executed: set[str] = set()
    pending: set[str] = set(node_executors.keys())
    node_results: Dict[str, NodeExecutionResult[Any]] = {}

    try:
        while pending:
            progress = False

            for node_id in list(pending):
                deps = node_dependencies.get(node_id, [])
                if not all(d in executed for d in deps):
                    continue

                fn = node_executors[node_id]
                node_cfg = NodeExecutionConfig(
                    retry=RetryConfig(max_attempts=cfg.max_retries, initial_delay=cfg.retry_delay),
                    timeout_seconds=cfg.default_node_timeout,
                )

                try:
                    result = await ctx.execute_node(node_id, fn, node_cfg)
                    node_results[node_id] = result
                    executed.add(node_id)
                    pending.remove(node_id)
                    progress = True

                    if result.status is not NodeStatus.COMPLETED and cfg.fail_fast:
                        err = NodeExecutionError(
                            message=f"Node {node_id} failed with status {result.status}",
                            node_id=node_id,
                            severity=ErrorSeverity.ERROR,
                            metadata={"status": result.status.value, "error": result.error},
                        )
                        return ctx.create_dag_result(status="failed", error=err)

                except NodeExecutionError as exc:
                    if cfg.fail_fast:
                        return ctx.create_dag_result(status="failed", error=exc)
                except Exception as exc:  # noqa: BLE001
                    if cfg.fail_fast:
                        wrapped = WorkflowError(
                            code=WorkflowErrorCode.UNKNOWN_ERROR,
                            message=str(exc),
                            severity=ErrorSeverity.ERROR,
                            context=ErrorContext(
                                workflow_id=workflow_id,
                                node_id=node_id,
                                component="workflow_engine",
                                operation="node_execution",
                                metadata={},
                            ),
                            cause=exc,
                        )
                        return ctx.create_dag_result(status="failed", error=wrapped)

            if not progress:
                # Dependency deadlock or cycle.
                for node_id in pending:
                    missing = [d for d in node_dependencies.get(node_id, []) if d not in executed]
                    if missing:
                        err = WorkflowError(
                            code=WorkflowErrorCode.NODE_DEPENDENCY_FAILED,
                            message=f"Node {node_id} has unsatisfied dependencies: {missing}",
                            severity=ErrorSeverity.ERROR,
                            context=ErrorContext(
                                workflow_id=workflow_id,
                                node_id=node_id,
                                component="workflow_engine",
                                operation="dependency_check",
                                metadata={"missing_dependencies": missing},
                            ),
                        )
                        return ctx.create_dag_result(status="failed", error=err)

                err = WorkflowError(
                    code=WorkflowErrorCode.NODE_DEPENDENCY_FAILED,
                    message=f"Workflow execution blocked; possible cycle. Pending: {sorted(pending)}",
                    severity=ErrorSeverity.ERROR,
                    context=ErrorContext(
                        workflow_id=workflow_id,
                        node_id=None,
                        component="workflow_engine",
                        operation="cycle_detection",
                        metadata={"pending_nodes": sorted(pending)},
                    ),
                )
                return ctx.create_dag_result(status="failed", error=err)

        if all(r.status is NodeStatus.COMPLETED for r in node_results.values()):
            return ctx.create_dag_result(status="completed")

        failed_nodes = [nid for nid, r in node_results.items() if r.status is not NodeStatus.COMPLETED]
        err = WorkflowError(
            code=WorkflowErrorCode.NODE_EXECUTION_FAILED,
            message=f"Workflow completed with failed nodes: {failed_nodes}",
            severity=ErrorSeverity.WARNING,
            context=ErrorContext(
                workflow_id=workflow_id,
                node_id=None,
                component="workflow_engine",
                operation="workflow_completion",
                metadata={"failed_nodes": failed_nodes},
            ),
        )
        return ctx.create_dag_result(status="partially_completed", error=err)

    except Exception as exc:  # noqa: BLE001
        wrapped = WorkflowError(
            code=WorkflowErrorCode.UNKNOWN_ERROR,
            message=str(exc),
            severity=ErrorSeverity.ERROR,
            context=ErrorContext(
                workflow_id=workflow_id,
                node_id=None,
                component="workflow_engine",
                operation="workflow_execution",
                metadata={},
            ),
            cause=exc,
        )
        return ctx.create_dag_result(status="failed", error=wrapped)
