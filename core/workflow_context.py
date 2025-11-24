"""Workflow context for managing state and safety across L3, L4, and L5."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Optional, Type, TypeVar, Generic

from l4.manager import StateManager
from l4.types import StateSnapshot
from l5 import SafetySystem
from l5.types import PolicyDecision, SafetyContext, Verdict

from .errors import (
    ErrorSeverity,
    NodeExecutionError,
    SafetyViolationError,
    StateTransitionError,
    WorkflowError,
)
from .models.dag_models import DAGResult, NodeExecutionResult, NodeStatus


TState = TypeVar("TState")


@dataclass
class RetryConfig:
    """Configuration for retrying failed operations."""

    max_attempts: int = 3
    initial_delay: float = 0.1  # seconds
    max_delay: float = 5.0  # seconds
    backoff_factor: float = 2.0

    def get_delay(self, attempt: int) -> float:
        delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        return min(delay, self.max_delay)


@dataclass
class NodeExecutionConfig:
    """Configuration for executing a single node."""

    require_safety_check: bool = True
    retry: Optional[RetryConfig] = None
    timeout_seconds: Optional[float] = None


class WorkflowContext(Generic[TState]):
    """Execution-scoped context integrating L3, L4, and L5.

    Responsibilities:
    - Coordinate node execution with retries and timeouts.
    - Capture L4 snapshots before/after each node.
    - Invoke L5 safety for node outputs.
    - Produce a `DAGResult` view over the run.
    """

    def __init__(
        self,
        workflow_id: str,
        state_manager: StateManager[TState],
        safety_system: Optional[SafetySystem] = None,
        metadata: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
    ) -> None:
        self.workflow_id = workflow_id
        self.state_manager = state_manager
        self.safety_system = safety_system
        self.metadata: Dict[str, Any] = metadata or {}
        self.start_time = start_time or datetime.utcnow()

        self._error_handlers: Dict[Type[BaseException], Callable[[BaseException], Awaitable[None]]] = {}

    # ---------------------------------------------------------------------
    # Error handling
    # ---------------------------------------------------------------------
    def add_error_handler(
        self,
        exc_type: Type[BaseException],
        handler: Callable[[BaseException], Awaitable[None]],
    ) -> None:
        """Register an async handler for a given exception type."""

        self._error_handlers[exc_type] = handler

    async def _dispatch_error(self, exc: BaseException) -> None:
        for etype, handler in self._error_handlers.items():
            if isinstance(exc, etype):
                await handler(exc)
                return

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    async def _capture_snapshot(self, node_id: str, phase: str) -> Optional[StateSnapshot]:
        """Capture a snapshot with basic error wrapping."""

        try:
            return self.state_manager.create_snapshot(
                f"{phase}_{node_id}",
                metadata={
                    "workflow_id": self.workflow_id,
                    "node_id": node_id,
                    "phase": phase,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        except Exception as exc:  # noqa: BLE001
            raise StateTransitionError(
                message=f"Failed to capture {phase} snapshot for node {node_id}",
                transition={"workflow_id": self.workflow_id, "node_id": node_id, "phase": phase},
                cause=exc,
            ) from exc

    async def _with_retry_and_timeout(
        self,
        op: Callable[[], Awaitable[Any]],
        cfg: NodeExecutionConfig,
        node_id: str,
    ) -> Any:
        retry = cfg.retry or RetryConfig()
        last_exc: Optional[BaseException] = None

        for attempt in range(1, retry.max_attempts + 1):
            try:
                if cfg.timeout_seconds is not None:
                    return await asyncio.wait_for(op(), timeout=cfg.timeout_seconds)
                return await op()
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt == retry.max_attempts:
                    break
                await asyncio.sleep(retry.get_delay(attempt))

        assert last_exc is not None  # for type checkers
        if isinstance(last_exc, asyncio.TimeoutError):
            raise NodeExecutionError(
                message=f"Node {node_id} timed out",
                node_id=node_id,
                severity=ErrorSeverity.ERROR,
                metadata={"timeout_seconds": cfg.timeout_seconds},
            ) from last_exc

        raise NodeExecutionError(
            message=f"Node {node_id} failed after retries: {last_exc}",
            node_id=node_id,
            cause=last_exc,
        ) from last_exc

    async def _evaluate_safety(
        self,
        node_id: str,
        output: Any,
        pre_snapshot: Optional[StateSnapshot],
        post_snapshot: Optional[StateSnapshot],
    ) -> PolicyDecision:
        """Run L5 safety on a node output.

        On any internal error, returns a conservative BLOCK decision.
        """

        if self.safety_system is None:
            return PolicyDecision(verdict=Verdict.ALLOW)

        try:
            ctx = SafetyContext(
                content=output,
                content_type="application/json",
                metadata={
                    "workflow_id": self.workflow_id,
                    "node_id": node_id,
                    "pre_snapshot_id": pre_snapshot.snapshot_id if pre_snapshot else None,
                    "post_snapshot_id": post_snapshot.snapshot_id if post_snapshot else None,
                    **self.metadata,
                },
            )
            return self.safety_system.evaluate(ctx)
        except Exception as exc:  # noqa: BLE001
            return PolicyDecision(
                verdict=Verdict.BLOCK,
                reason="safety_engine_error",
                findings=[],
                metadata={"error": str(exc)},
            )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    async def execute_node(
        self,
        node_id: str,
        fn: Callable[..., Awaitable[Any]],
        cfg: Optional[NodeExecutionConfig] = None,
        **kwargs: Any,
    ) -> NodeExecutionResult[Any]:
        """Execute a single logical node with L4+L5 integration."""

        cfg = cfg or NodeExecutionConfig()
        result = NodeExecutionResult[Any](
            node_id=node_id,
            status=NodeStatus.RUNNING,
            start_time=datetime.utcnow(),
        )

        try:
            pre = await self._capture_snapshot(node_id, "pre")

            async def _op() -> Any:
                return await fn(**kwargs)

            output = await self._with_retry_and_timeout(_op, cfg, node_id)
            result.output = output

            post = await self._capture_snapshot(node_id, "post")
            result.state_snapshot_id = post.snapshot_id if post else None

            if cfg.require_safety_check and output is not None:
                decision = await self._evaluate_safety(node_id, output, pre, post)
                result.safety_decision = decision
                if decision.verdict == Verdict.BLOCK:
                    result.status = NodeStatus.BLOCKED
                    result.error = "Blocked by safety policy"
                    raise SafetyViolationError(
                        message=f"Safety violation in node {node_id}",
                        policy_decisions=decision.to_dict(),
                        node_id=node_id,
                        workflow_id=self.workflow_id,
                    )

            result.status = NodeStatus.COMPLETED
            return result

        except SafetyViolationError as exc:
            result.status = NodeStatus.BLOCKED
            result.error = str(exc)
            await self._dispatch_error(exc)
            raise
        except NodeExecutionError as exc:
            result.status = NodeStatus.FAILED
            result.error = str(exc)
            await self._dispatch_error(exc)
            raise
        except Exception as exc:  # noqa: BLE001
            wrapped = NodeExecutionError(
                message=f"Node {node_id} failed: {exc}",
                node_id=node_id,
                cause=exc,
            )
            result.status = NodeStatus.FAILED
            result.error = str(wrapped)
            await self._dispatch_error(wrapped)
            raise wrapped
        finally:
            result.end_time = datetime.utcnow()

    async def rollback_to_snapshot(self, snapshot_id: str) -> None:
        """Request a rollback to a prior snapshot via the state manager."""

        try:
            await self.state_manager.rollback(snapshot_id)  # type: ignore[func-returns-value]
        except Exception as exc:  # noqa: BLE001
            raise StateTransitionError(
                message=f"Failed to rollback to snapshot {snapshot_id}",
                transition={"workflow_id": self.workflow_id, "snapshot_id": snapshot_id},
                cause=exc,
            ) from exc

    def create_dag_result(
        self,
        status: str = "completed",
        error: Optional[WorkflowError] = None,
    ) -> DAGResult:
        """Materialize a `DAGResult` snapshot for this workflow."""

        dag = DAGResult(
            workflow_id=self.workflow_id,
            status=status,
            start_time=self.start_time,
            state_snapshots=self.state_manager.get_snapshots(),  # type: ignore[call-arg]
            state_transitions=self.state_manager.get_transitions(),  # type: ignore[call-arg]
        )

        if error is not None:
            dag.metrics.setdefault("workflow_error", error.to_dict())

        return dag
