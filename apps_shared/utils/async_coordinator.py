"""Async Coordinator - Manages async tasks and prevents orphaned operations.

This module provides coordination for async operations, preventing orphaned tasks,
managing timeouts safely, and ensuring proper cleanup of async resources.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


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

        # Task tracking
        self._tasks: dict[str, TaskInfo] = {}
        self._task_counter = 0
        self._lock = asyncio.Lock()

        # Semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Background cleanup task
        self._cleanup_task: asyncio.Task | None = None
        self._running = False

        logger.debug(f"Initialized AsyncCoordinator: {name}")

    async def start(self) -> None:
        """Start the coordinator and cleanup task."""
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

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Cancel all managed tasks
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
        # Check concurrency limit
        await self._semaphore.acquire()

        # Generate task ID
        task_id = self.generate_task_id()

        # Create the task
        task = asyncio.create_task(self._run_with_timeout(coro, timeout, task_id))

        # Create task info
        task_info = TaskInfo(
            task_id=task_id,
            task=task,
            created_at=time.time(),
            timeout=timeout,
            parent_id=parent_id,
            cleanup_callback=cleanup_callback,
        )

        # Register task
        async with self._lock:
            self._tasks[task_id] = task_info

            # Add to parent's children if applicable
            if parent_id and parent_id in self._tasks:
                self._tasks[parent_id].children_ids.add(task_id)

        # Add done callback
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
            # Update state to running
            async with self._lock:
                if task_id in self._tasks:
                    self._tasks[task_id].state = TaskState.RUNNING

            # Run with timeout if specified
            if timeout:
                result = await asyncio.wait_for(coro, timeout)
            else:
                result = await coro

            # Update state to completed
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
        except Exception as e:
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
        # Release semaphore
        self._semaphore.release()

        # Get task info
        async with self._lock:
            task_info = self._tasks.get(task_id)
            if not task_info:
                return

        # Handle task result
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

        # Call cleanup callback
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

        # Cancel the task
        task_info.task.cancel()

        # Cancel children
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
                await asyncio.sleep(30)  # Cleanup every 30 seconds

                # Clean up completed tasks older than 5 minutes
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
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    @asynccontextmanager
    async def managed_task(
        self,
        coro: Awaitable,
        timeout: float | None = None,
        cleanup_callback: Callable | None = None,
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


# Global coordinator registry
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


# Decorator for managed async functions
def managed(
    coordinator_name: str = "default",
    timeout: float | None = None,
    cleanup_callback: Callable | None = None,
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
                func(*args, **kwargs),
                timeout=timeout,
                cleanup_callback=cleanup_callback,
            ) as task_id:
                return await coordinator.wait_for_task(task_id)

        return wrapper

    return decorator


# Safe timeout wrapper that prevents orphaned tasks
async def safe_wait_for(
    coro: Awaitable,
    timeout: float,
    coordinator_name: str = "timeout_coordinator",
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
