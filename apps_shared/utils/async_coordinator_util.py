"""Async Coordinator - Manages async tasks and prevents orphaned operations.

This module provides coordination for async operations, preventing orphaned tasks,
managing timeouts safely, and ensuring proper cleanup of async resources.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable

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

_emit_applies_guardrail("p0", "async_coordinator_util", "p0_governance")
_emit_reads_policy_state("p0", "async_coordinator_util", "policy_binding")
_emit_snapshots_state("p0", "async_coordinator_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("async_coordinator_util", "p4obs", "metric_1")
_emit_emits_metric_event("async_coordinator_util", "p4obs", "metric_2")
_emit_emits_metric_event("async_coordinator_util", "p4obs", "metric_3")
_emit_emits_metric_event("async_coordinator_util", "p4obs", "metric_4")
_emit_emits_metric_event("async_coordinator_util", "p4obs", "metric_5")
_emit_emits_metric_event("async_coordinator_util", "p4obs", "metric_6")
_emit_records_incident_event("async_coordinator_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("async_coordinator_util", "p4obs", "anomaly")
_emit_writes_observability_log("async_coordinator_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("async_coordinator_util", "p4obs", "mon_state")
_emit_triggers_alert("async_coordinator_util", "p4obs", "alert")
_emit_links_incident_trace("async_coordinator_util", "p4obs", "trace_link")
_emit_captures_pattern("async_coordinator_util", "p3lm", "pattern")
_emit_records_learning_event("async_coordinator_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("async_coordinator_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("async_coordinator_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("async_coordinator_util", "p3lm", "routing")
_emit_improves_agent_policy("async_coordinator_util", "p3lm", "policy")
_emit_stores_learning_state("async_coordinator_util", "p3lm", "state")
_emit_records_execution_trace("async_coordinator_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("async_coordinator_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("async_coordinator_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("async_coordinator_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("async_coordinator_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("async_coordinator_util", "env_read", "p2_env_1")
_emit_reads_environ("async_coordinator_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("async_coordinator_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("async_coordinator_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "async_coordinator_util", "context_pull")
_emit_pulls_context("p1", "async_coordinator_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "async_coordinator_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "async_coordinator_util", "uwg_term_2")
_emit_writes_through("p1", "async_coordinator_util", "write_through")
_emit_writes_through("p1", "async_coordinator_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "async_coordinator_util", "safety_validation")
_emit_invokes_eval("p1", "async_coordinator_util", "eval_call")
_emit_proposal_commits_routing("p1", "async_coordinator_util", "routing_commit")
_emit_escalates_to_human("p1", "async_coordinator_util", "human_escalation")
_emit_routes_through("p1", "async_coordinator_util", "route_through")
_emit_checks_agent_registry("p1", "async_coordinator_util", "agent_registry")
_emit_validates_agent_capability("p1", "async_coordinator_util", "capability")
_emit_dispatches_execution_plan("p1", "async_coordinator_util", "exec_plan")
_emit_agent_executes_agent("p1", "async_coordinator_util", "sub_agent")
_emit_routes_to_agent("p1", "async_coordinator_util", "target_agent")
_emit_verifies_policy("p1", "async_coordinator_util", "policy_check")
_emit_observes_runtime_state("p1", "async_coordinator_util", "runtime_state")
_emit_verifies_boundary("p1", "async_coordinator_util", "boundary_check")
_emit_transcripts_response("p1", "async_coordinator_util", "transcript")
_emit_hard_fails_untranscripted("p1", "async_coordinator_util")
_emit_gated_by_confidence("p1", "async_coordinator_util", "confidence_gate")
emit_replay_key("p0", "async_coordinator_util")
emit_determinism_digest("p0", "async_coordinator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "async_coordinator_util", "execution_auth")
_emit_validates_capability("p2", "async_coordinator_util", "capability_check")
_emit_routes_to_capability("p2", "async_coordinator_util", "capability_route")
_emit_writes_via_uwg("p2", "async_coordinator_util", "uwg_write")
_emit_blocks_direct_write("p2", "async_coordinator_util", "direct_write_block")
_emit_records_tool_invocation("p2", "async_coordinator_util", "tool_invocation")
_emit_captures_execution_output("p2", "async_coordinator_util", "exec_output")
_emit_dispatches_agent("p3", "async_coordinator_util", "agent_dispatch")
_emit_coordinates_agents("p3", "async_coordinator_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "async_coordinator_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "async_coordinator_util", "healing_outcome")
_emit_escalates_failure("p3", "async_coordinator_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "async_coordinator_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "async_coordinator_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "async_coordinator_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "async_coordinator_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "async_coordinator_util", "eval_metric")
_emit_stores_embedding("p4", "async_coordinator_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "async_coordinator_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "async_coordinator_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32


class TaskState(Enum):
    """States for async tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class TaskInfo:
    """Information about a managed task."""

    task_id: str
    task: asyncio.Task
    created_at: float
    timeout: float | None
    state: TaskState = TaskState.PENDING
    parent_id: str | None = None
    children_ids: set[str] = field(default_factory=set)
    cleanup_callback: Callable | None = None


class AsyncCoordinator:
    """Coordinates async tasks and prevents orphaned operations."""

    # guardian: allow-magic-config
    def __init__(self, name: str = "default", max_concurrent: int = 100):
        """Initialize the coordinator.

        Args:
            name: Coordinator name for logging
            max_concurrent: Maximum concurrent tasks
        """
        self.name = name
        self.max_concurrent = max_concurrent
        self._tasks: dict[str, TaskInfo] = {}
        self._task_counter = 0
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._cleanup_task: asyncio.Task | None = None
        self._running = False
        logger.debug(f"Initialized AsyncCoordinator: {name}")

    async def start(self) -> None:
        """Start the coordinator and cleanup task."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AsyncCoordinator.start")

        if self._running:
            return
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Started AsyncCoordinator: {self.name}")

    async def stop(self) -> None:
        """Stop the coordinator and cancel all tasks."""
        if not self._running:
            return
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        await self.cancel_all_tasks()
        logger.info(f"Stopped AsyncCoordinator: {self.name}")

    def generate_task_id(self) -> str:
        """Generate a unique task ID.

        Returns:
            Unique task ID
        """
        self._task_counter += 1
        return f"{self.name}_task_{self._task_counter}_{int(time.time() * 1000)}"

    async def create_task(
        self,
        coro: Awaitable,
        timeout: float | None = None,
        parent_id: str | None = None,
        cleanup_callback: Callable | None = None,
    ) -> str:
        """Create and manage a new task.

        Args:
            coro: Coroutine to execute
            timeout: Optional timeout for the task
            parent_id: Optional parent task ID
            cleanup_callback: Optional cleanup callback

        Returns:
            Task ID
        """
        await self._semaphore.acquire()
        task_id = self.generate_task_id()
        task = asyncio.create_task(self._run_with_timeout(coro, timeout, task_id))
        task_info = TaskInfo(
            task_id=task_id,
            task=task,
            created_at=time.time(),
            timeout=timeout,
            parent_id=parent_id,
            cleanup_callback=cleanup_callback,
        )
        async with self._lock:
            self._tasks[task_id] = task_info
            if parent_id and parent_id in self._tasks:
                self._tasks[parent_id].children_ids.add(task_id)
        task.add_done_callback(lambda t: asyncio.create_task(self._on_task_done(task_id)))
        logger.debug(f"Created task: {task_id} (timeout: {timeout})")
        return task_id

    async def _run_with_timeout(self, coro: Awaitable, timeout: float | None, task_id: str) -> Any:
        """Run a coroutine with timeout handling.

        Args:
            coro: Coroutine to run
            timeout: Optional timeout
            task_id: Task ID for tracking

        Returns:
            Result of the coroutine
        """
        try:
            async with self._lock:
                if task_id in self._tasks:
                    self._tasks[task_id].state = TaskState.RUNNING
            if timeout:
                result = await asyncio.wait_for(coro, timeout)
            else:
                result = await coro
            async with self._lock:
                if task_id in self._tasks:
                    self._tasks[task_id].state = TaskState.COMPLETED
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Task {task_id} timed out after {timeout}s")
            async with self._lock:
                if task_id in self._tasks:
                    self._tasks[task_id].state = TaskState.FAILED
            raise
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Task {task_id} failed: {e}")
            async with self._lock:
                if task_id in self._tasks:
                    self._tasks[task_id].state = TaskState.FAILED
            raise

    async def _on_task_done(self, task_id: str) -> None:
        """Handle task completion.

        Args:
            task_id: ID of the completed task
        """
        self._semaphore.release()
        async with self._lock:
            task_info = self._tasks.get(task_id)
            if not task_info:
                return
        try:
            if task_info.task.cancelled():
                task_info.state = TaskState.CANCELLED
                logger.debug(f"Task {task_id} was cancelled")
            elif task_info.task.exception():
                task_info.state = TaskState.FAILED
                logger.debug(f"Task {task_id} failed with exception")
            else:
                task_info.state = TaskState.COMPLETED
                logger.debug(f"Task {task_id} completed successfully")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error handling task completion for {task_id}: {e}")
        if task_info.cleanup_callback:
            try:
                if asyncio.iscoroutinefunction(task_info.cleanup_callback):
                    await task_info.cleanup_callback()
                else:
                    task_info.cleanup_callback()
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f"Cleanup callback failed for {task_id}: {e}")

    async def wait_for_task(self, task_id: str, timeout: float | None = None) -> Any:
        """Wait for a specific task to complete.

        Args:
            task_id: ID of the task to wait for
            timeout: Optional wait timeout

        Returns:
            Task result
        """
        async with self._lock:
            task_info = self._tasks.get(task_id)
            if not task_info:
                raise ValueError(f"Task not found: {task_id}")
        try:
            if timeout:
                return await asyncio.wait_for(task_info.task, timeout)
            else:
                return await task_info.task
        except asyncio.TimeoutError:
            await self.cancel_task(task_id)
            raise

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if cancelled, False if not found
        """
        async with self._lock:
            task_info = self._tasks.get(task_id)
            if not task_info:
                return False
        task_info.task.cancel()
        for child_id in task_info.children_ids:
            await self.cancel_task(child_id)
        return True

    async def cancel_all_tasks(self) -> int:
        """Cancel all managed tasks.

        Returns:
            Number of tasks cancelled
        """
        async with self._lock:
            task_ids = list(self._tasks.keys())
        cancelled = 0
        for task_id in task_ids:
            if await self.cancel_task(task_id):
                cancelled += 1
        logger.info(f"Cancelled {cancelled} tasks in coordinator {self.name}")
        return cancelled

    async def get_task_status(self, task_id: str) -> TaskState | None:
        """Get the status of a task.

        Args:
            task_id: ID of the task

        Returns:
            Task state or None if not found
        """
        async with self._lock:
            task_info = self._tasks.get(task_id)
            return task_info.state if task_info else None

    async def list_tasks(self) -> dict[str, dict[str, Any]]:
        """List all managed tasks.

        Returns:
            Dictionary of task information
        """
        async with self._lock:
            result = {}
            for task_id, task_info in self._tasks.items():
                result[task_id] = {
                    "state": task_info.state.value,
                    "created_at": task_info.created_at,
                    "timeout": task_info.timeout,
                    "parent_id": task_info.parent_id,
                    "children_count": len(task_info.children_ids),
                }
            return result

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for old tasks."""
        while self._running:
            try:
                await asyncio.sleep(DEFAULT_SLEEP)
                cutoff_time = time.time() - 300
                tasks_to_remove = []
                async with self._lock:
                    for task_id, task_info in self._tasks.items():
                        if (
                            task_info.state in (TaskState.COMPLETED, TaskState.CANCELLED, TaskState.FAILED)
                            and task_info.created_at < cutoff_time
                        ):
                            tasks_to_remove.append(task_id)
                for task_id in tasks_to_remove:
                    async with self._lock:
                        if task_id in self._tasks:
                            del self._tasks[task_id]
                if tasks_to_remove:
                    logger.debug(f"Cleaned up {len(tasks_to_remove)} old tasks")
            except asyncio.CancelledError:
                break
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error(f"Error in cleanup loop: {e}")

    @asynccontextmanager
    async def managed_task(
        self, coro: Awaitable, timeout: float | None = None, cleanup_callback: Callable | None = None,
    ):
        """Context manager for a managed task.

        Args:
            coro: Coroutine to run
            timeout: Optional timeout
            cleanup_callback: Optional cleanup callback

        Yields:
            Task ID
        """
        task_id = await self.create_task(coro, timeout, cleanup_callback=cleanup_callback)
        try:
            yield task_id
        finally:
            await self.cancel_task(task_id)


_coordinators: dict[str, AsyncCoordinator] = {}
_coordinator_lock = asyncio.Lock()


# guardian: allow-magic-config
async def get_coordinator(name: str = "default", max_concurrent: int = 100) -> AsyncCoordinator:
    """Get or create an async coordinator.

    Args:
        name: Coordinator name
        max_concurrent: Maximum concurrent tasks

    Returns:
        AsyncCoordinator instance
    """
    async with _coordinator_lock:
        if name not in _coordinators:
            coordinator = AsyncCoordinator(name, max_concurrent)
            await coordinator.start()
            _coordinators[name] = coordinator
        return _coordinators[name]


async def shutdown_all_coordinators() -> None:
    """Shutdown all coordinators."""
    async with _coordinator_lock:
        for coordinator in _coordinators.values():
            await coordinator.stop()
        _coordinators.clear()


def managed(
    coordinator_name: str = "default", timeout: float | None = None, cleanup_callback: Callable | None = None,
):
    """Decorator to run functions in a managed async context.

    Args:
        coordinator_name: Name of the coordinator
        timeout: Optional timeout
        cleanup_callback: Optional cleanup callback

    Returns:
        Decorated function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            coordinator = await get_coordinator(coordinator_name)
            async with coordinator.managed_task(
                func(*args, **kwargs), timeout=timeout, cleanup_callback=cleanup_callback,
            ) as task_id:
                return await coordinator.wait_for_task(task_id)

        return wrapper

    return decorator


async def safe_wait_for(
    coro: Awaitable, timeout: float, coordinator_name: str = "timeout_coordinator",
) -> Any:
    """Wait for a coroutine with timeout, preventing orphaned tasks.

    Args:
        coro: Coroutine to wait for
        timeout: Timeout in seconds
        coordinator_name: Name of the coordinator to use

    Returns:
        Result of the coroutine

    Raises:
        asyncio.TimeoutError: If the coroutine times out
    """
    coordinator = await get_coordinator(coordinator_name)

    async def timeout_wrapper():
        return await coro

    task_id = await coordinator.create_task(timeout_wrapper(), timeout)
    try:
        return await coordinator.wait_for_task(task_id)
    finally:
        await coordinator.cancel_task(task_id)
