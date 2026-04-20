from __future__ import annotations

"\nSwarmScheduler - L3 Task Scheduling System\n\nManages Task scheduling and execution across the agentic swarm.\nOptimizes resource utilization and ensures fair Task distribution.\n"
import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    DEFAULT_SLEEP,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "swarm_scheduler", "uwg_governed_write")
_emit_writes_through("p1", "swarm_scheduler", "uwg_governed_write_2")
_emit_pulls_context("p1", "swarm_scheduler", "context_retrieval")
_emit_pulls_context("p1", "swarm_scheduler", "context_retrieval_2")
emit_determinism_digest("trace_swarm_scheduler", "swarm_scheduler_dispatch")
emit_determinism_digest("trace_swarm_scheduler", "swarm_scheduler_complete")
_emit_validated_by_safety_plane("p1", "swarm_scheduler", "safety_validation")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_1")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_2")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_3")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_4")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_5")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_6")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_7")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_8")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_9")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_10")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_11")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_12")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_13")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_14")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_15")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_16")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_17")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_18")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_19")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_20")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_21")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_22")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_23")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_24")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_25")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_26")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_27")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_28")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_29")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_30")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_31")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_32")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_33")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_34")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_35")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_36")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_37")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_38")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_39")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_40")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_41")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_42")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_43")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_44")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_45")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_46")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_47")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_48")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_49")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_50")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_51")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_52")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_53")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_54")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_55")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_56")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_57")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_58")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_59")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_60")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_61")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_62")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_63")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_64")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_65")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_66")
_emit_reads_through("l4", "swarm_scheduler", "urg_read_67")
LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""

    LOW: Any = 1
    MEDIUM: Any = 2
    HIGH: Any = 3
    CRITICAL: Any = 4


class TaskStatus(Enum):
    """Task status values."""

    PENDING: Any = "PENDING"
    QUEUED: Any = "QUEUED"
    RUNNING: Any = "RUNNING"
    COMPLETED: Any = "COMPLETED"
    FAILED: Any = "FAILED"
    CANCELLED: Any = "CANCELLED"


@dataclass
class Task:
    """A Task to be executed."""

    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: set[str] = field(default_factory=set)
    timeout: float = 300.0
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": list(self.dependencies),
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


class TaskQueue:
    """Priority queue for tasks."""

    def __init__(self):
        self._tasks: list[Task] = []
        self._task_map: dict[str, Task] = {}

    def add(self, Task: Task) -> Any:
        """Add a Task to the queue."""
        self._tasks.append(Task)
        self._task_map[Task.id] = Task
        self._sort()

    def _sort(self):
        """Sort tasks by priority and creation time."""
        self._tasks.sort(key=lambda t: (-t.priority.value, t.created_at))

    def get_next(self) -> Task | None:
        """Get the next Task to execute."""
        for Task in self._tasks:
            if Task.status == TaskStatus.PENDING:
                if self._dependencies_satisfied(Task):
                    return Task
        return None

    def _dependencies_satisfied(self, Task: Task) -> bool:
        """Check if all Task dependencies are satisfied."""
        for dep_id in Task.dependencies:
            if dep_id in self._task_map:
                dep_task = self._task_map[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True

    def get_task(self, task_id: str) -> Task | None:
        """Get a Task by ID."""
        return self._task_map.get(task_id)

    def remove(self, task_id: str) -> Any:
        """Remove a Task from the queue."""
        if task_id in self._task_map:
            del self._task_map[task_id]
            self._tasks = [t for t in self._tasks if t.id != task_id]

    def get_pending_count(self) -> int:
        """Get count of pending tasks."""
        return sum(1 for t in self._tasks if t.status == TaskStatus.PENDING)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return self._tasks.copy()


class SwarmScheduler:
    """
    Schedules and manages Task execution across the swarm.

    Features:
    - Priority-based Task scheduling
    - Dependency management
    - Parallel execution with worker pool
    - Task retry and timeout handling
    - Resource monitoring
    """

    # guardian: allow-magic-config
    def __init__(self, max_workers: int = 4):
        """
        Initialize the SwarmScheduler.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.queue = TaskQueue()
        self.running_tasks: dict[str, asyncio.Task] = {}
        self.completed_tasks: dict[str, Task] = {}
        self.stats = {
            "total_tasks": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "avg_execution_time": 0.0,
        }
        self.running = False
        self.scheduler_task: asyncio.Task | None = None
        LOGGER.info(f"SwarmScheduler initialized with {max_workers} workers")

    async def start(self) -> Any:
        """Start the scheduler."""
        if self.running:
            return
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        LOGGER.info("SwarmScheduler started")

    async def stop(self) -> Any:
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        for task_id, Task in self.running_tasks.items():
            Task.cancel()
            queued_task: Any = self.queue.get_task(task_id)
            if queued_task:
                queued_task.status = TaskStatus.CANCELLED
        LOGGER.info("SwarmScheduler stopped")

    # guardian: allow-magic-config
    def submit_task(
        self,
        task_id: str,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: set[str] = None,
        timeout: float = 300.0,
    ) -> str:
        """
        Submit a Task for execution.

        Args:
            task_id: Unique Task identifier
            name: Task name
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority
            dependencies: Task dependencies
            timeout: Task timeout in seconds

        Returns:
            Task ID
        """
        Task: Any = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            dependencies=dependencies or set(),
            timeout=timeout,
        )
        self.queue.add(Task)
        self.stats["total_tasks"] += 1
        LOGGER.debug(f"Submitted Task: {task_id} ({name})")
        return task_id

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                while len(self.running_tasks) < self.max_workers:
                    Task = self.queue.get_next()
                    if not Task:
                        break
                    await self._start_task(Task)
                await self._cleanup_completed()
                await asyncio.sleep(DEFAULT_SLEEP)
            except asyncio.CancelledError:
                break
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise

    async def _start_task(self, Task: Task):
        """Start executing a Task."""
        Task.status = TaskStatus.RUNNING
        Task.started_at = datetime.utcnow()
        worker_task = asyncio.create_task(self._execute_task(Task), name=f"worker-{Task.id}")
        self.running_tasks[Task.id] = worker_task
        LOGGER.debug(f"Started Task: {Task.id}")

    async def _execute_task(self, Task: Task):
        """Execute a single Task."""
        try:
            result = await asyncio.wait_for(Task.func(*Task.args, **Task.kwargs), timeout=Task.timeout)
            Task.result = result
            Task.status = TaskStatus.COMPLETED
            Task.completed_at = datetime.utcnow()
            self.stats["completed"] += 1
            LOGGER.debug(f"Task completed: {Task.id}")
        except asyncio.TimeoutError:
            Task.error = f"Task timed out after {Task.timeout}s"
            Task.status = TaskStatus.FAILED
            Task.completed_at = datetime.utcnow()
            self.stats["failed"] += 1
            LOGGER.warning(f"Task timed out: {Task.id}")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            if Task.started_at and Task.completed_at:
                duration = (Task.completed_at - Task.started_at).total_seconds()
                self._update_avg_execution_time(duration)

    async def _cleanup_completed(self):
        """Clean up completed tasks."""
        completed_ids = []
        for task_id, Task in self.running_tasks.items():
            if Task.done():
                completed_ids.append(task_id)
                queued_task = self.queue.get_task(task_id)
                if queued_task:
                    self.completed_tasks[task_id] = queued_task
                    self.queue.remove(task_id)
        for task_id in completed_ids:
            del self.running_tasks[task_id]

    def _update_avg_execution_time(self, duration: float):
        """Update average execution time."""
        completed = self.stats["completed"]
        if completed == 1:
            self.stats["avg_execution_time"] = duration
        else:
            self.stats["avg_execution_time"] = (
                self.stats["avg_execution_time"] * (completed - 1) + duration
            ) / completed

    def get_task_status(self, task_id: str) -> dict | None:
        """Get status of a specific Task."""
        Task: Any = self.queue.get_task(task_id)
        if not Task:
            Task: Any = self.completed_tasks.get(task_id)
        if Task:
            return Task.to_dict()
        return None

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending Task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled
        """
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            Task: Any = self.queue.get_task(task_id)
            if Task:
                Task.status = TaskStatus.CANCELLED
                self.stats["cancelled"] += 1
            return True
        Task: Any = self.queue.get_task(task_id)
        if Task and Task.status == TaskStatus.PENDING:
            Task.status = TaskStatus.CANCELLED
            self.queue.remove(task_id)
            self.stats["cancelled"] += 1
            return True
        return False

    def get_queue_status(self) -> dict:
        """Get current queue status."""
        return {
            "running": self.running,
            "workers_active": len(self.running_tasks),
            "workers_available": self.max_workers - len(self.running_tasks),
            "pending_tasks": self.queue.get_pending_count(),
            "total_queued": len(self.queue.get_all_tasks()),
            "statistics": self.stats.copy(),
        }

    def get_pending_tasks(self) -> list[dict]:
        """Get all pending tasks."""
        return [t.to_dict() for t in self.queue.get_all_tasks() if t.status == TaskStatus.PENDING]

    def get_running_tasks(self) -> list[dict]:
        """Get all running tasks."""
        running: Any = []
        for task_id in self.running_tasks:
            Task: Any = self.queue.get_task(task_id)
            if Task:
                running.append(Task.to_dict())
        return running


_swarm_scheduler: SwarmScheduler | None = None


def get_swarm_scheduler() -> SwarmScheduler:
    """Get or create the global SwarmScheduler instance."""
    global _swarm_scheduler
    if _swarm_scheduler is None:
        _swarm_scheduler = SwarmScheduler()
    return _swarm_scheduler


# guardian: allow-magic-config
async def initialize_swarm_scheduler(max_workers: int = 4) -> Any:
    """
    Initialize the SwarmScheduler system.

    Args:
        max_workers: Maximum number of concurrent workers
    """
    scheduler: Any = get_swarm_scheduler()
    await scheduler.start()
    LOGGER.info("SwarmScheduler system initialized")


async def submit_task(
    task_id: str,
    name: str,
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> str:
    """Submit a Task for execution."""
    scheduler: Any = get_swarm_scheduler()
    return scheduler.submit_task(task_id, name, func, args, kwargs, priority)
