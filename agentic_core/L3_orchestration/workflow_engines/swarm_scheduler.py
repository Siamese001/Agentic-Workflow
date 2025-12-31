"""
SwarmScheduler - L3 Task Scheduling System

Manages task scheduling and execution across the agentic swarm.
Optimizes resource utilization and ensures fair task distribution.
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Protocol, Set
logger: Any = logging.getLogger(__name__)

class task_priority(Enum):
    """Task priority levels."""
    LOW: Any = 1
    MEDIUM: Any = 2
    HIGH: Any = 3
    CRITICAL: Any = 4

class task_status(Enum):
    """Task status values."""
    PENDING: Any = 'PENDING'
    QUEUED: Any = 'QUEUED'
    RUNNING: Any = 'RUNNING'
    COMPLETED: Any = 'COMPLETED'
    FAILED: Any = 'FAILED'
    CANCELLED: Any = 'CANCELLED'

@dataclass
class task:
    """A task to be executed."""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: Set[str] = field(default_factory=set)
    timeout: float = 300.0
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {'id': self.id, 'name': self.name, 'priority': self.priority.value, 'status': self.status.value, 'dependencies': list(self.dependencies), 'retry_count': self.retry_count, 'created_at': self.created_at.isoformat(), 'started_at': self.started_at.isoformat() if self.started_at else None, 'completed_at': self.completed_at.isoformat() if self.completed_at else None, 'error': self.error}

class task_queue:
    """Priority queue for tasks."""

    def __init__(self):
        self._tasks: List[Task] = []
        self._task_map: Dict[str, Task] = {}

    def add(self, task: Task) -> Any:
        """Add a task to the queue."""
        self._tasks.append(task)
        self._task_map[task.id] = task
        self._sort()

    def _sort(self):
        """Sort tasks by priority and creation time."""
        self._tasks.sort(key=lambda t: (-t.priority.value, t.created_at))

    def get_next(self) -> Optional[Task]:
        """Get the next task to execute."""
        for task in self._tasks:
            if task.status == TaskStatus.PENDING:
                if self._dependencies_satisfied(task):
                    return task
        return None

    def _dependencies_satisfied(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id in self._task_map:
                dep_task = self._task_map[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._task_map.get(task_id)

    def remove(self, task_id: str) -> Any:
        """Remove a task from the queue."""
        if task_id in self._task_map:
            del self._task_map[task_id]
            self._tasks = [t for t in self._tasks if t.id != task_id]

    def get_pending_count(self) -> int:
        """Get count of pending tasks."""
        return sum((1 for t in self._tasks if t.status == TaskStatus.PENDING))

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return self._tasks.copy()

class swarm_scheduler:
    """
    Schedules and manages task execution across the swarm.

    Features:
    - Priority-based task scheduling
    - Dependency management
    - Parallel execution with worker pool
    - Task retry and timeout handling
    - Resource monitoring
    """

    def __init__(self, max_workers: int=4):
        """
        Initialize the SwarmScheduler.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.queue = TaskQueue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.stats = {'total_tasks': 0, 'completed': 0, 'failed': 0, 'cancelled': 0, 'avg_execution_time': 0.0}
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        LOGGER.info(f'SwarmScheduler initialized with {max_workers} workers')

    async def start(self) -> Any:
        """Start the scheduler."""
        if self.running:
            return
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        LOGGER.info('SwarmScheduler started')

    async def stop(self) -> Any:
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        for task_id, task in self.running_tasks.items():
            task.cancel()
            queued_task: Any = self.queue.get_task(task_id)
            if queued_task:
                queued_task.status = TaskStatus.CANCELLED
        LOGGER.info('SwarmScheduler stopped')

    def submit_task(self, task_id: str, name: str, func: Callable, args: tuple=(), kwargs: dict=None, priority: TaskPriority=TaskPriority.MEDIUM, dependencies: Set[str]=None, timeout: float=300.0) -> str:
        """
        Submit a task for execution.

        Args:
            task_id: Unique task identifier
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
        task: Any = Task(id=task_id, name=name, func=func, args=args, kwargs=kwargs or {}, priority=priority, dependencies=dependencies or set(), timeout=timeout)
        self.queue.add(task)
        self.stats['total_tasks'] += 1
        LOGGER.debug(f'Submitted task: {task_id} ({name})')
        return task_id

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                while len(self.running_tasks) < self.max_workers:
                    task = self.queue.get_next()
                    if not task:
                        break
                    await self._start_task(task)
                await self._cleanup_completed()
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                LOGGER.error(f'Error in scheduler loop: {e}')
                await asyncio.sleep(1)

    async def _start_task(self, task: Task):
        """Start executing a task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        worker_task = asyncio.create_task(self._execute_task(task), name=f'worker-{task.id}')
        self.running_tasks[task.id] = worker_task
        LOGGER.debug(f'Started task: {task.id}')

    async def _execute_task(self, task: Task):
        """Execute a single task."""
        try:
            result = await asyncio.wait_for(task.func(*task.args, **task.kwargs), timeout=task.timeout)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            self.stats['completed'] += 1
            LOGGER.debug(f'Task completed: {task.id}')
        except asyncio.TimeoutError:
            task.error = f'Task timed out after {task.timeout}s'
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            self.stats['failed'] += 1
            LOGGER.warning(f'Task timed out: {task.id}')
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            self.stats['failed'] += 1
            LOGGER.error(f'Task failed: {task.id} - {e}')
        finally:
            if task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                self._update_avg_execution_time(duration)

    async def _cleanup_completed(self):
        """Clean up completed tasks."""
        completed_ids = []
        for task_id, task in self.running_tasks.items():
            if task.done():
                completed_ids.append(task_id)
                queued_task = self.queue.get_task(task_id)
                if queued_task:
                    self.completed_tasks[task_id] = queued_task
                    self.queue.remove(task_id)
        for task_id in completed_ids:
            del self.running_tasks[task_id]

    def _update_avg_execution_time(self, duration: float):
        """Update average execution time."""
        completed = self.stats['completed']
        if completed == 1:
            self.stats['avg_execution_time'] = duration
        else:
            self.stats['avg_execution_time'] = (self.stats['avg_execution_time'] * (completed - 1) + duration) / completed

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task."""
        task: Any = self.queue.get_task(task_id)
        if not task:
            task: Any = self.completed_tasks.get(task_id)
        if task:
            return task.to_dict()
        return None

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled
        """
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            task: Any = self.queue.get_task(task_id)
            if task:
                task.status = TaskStatus.CANCELLED
                self.stats['cancelled'] += 1
            return True
        task: Any = self.queue.get_task(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self.queue.remove(task_id)
            self.stats['cancelled'] += 1
            return True
        return False

    def get_queue_status(self) -> Dict:
        """Get current queue status."""
        return {'running': self.running, 'workers_active': len(self.running_tasks), 'workers_available': self.max_workers - len(self.running_tasks), 'pending_tasks': self.queue.get_pending_count(), 'total_queued': len(self.queue.get_all_tasks()), 'statistics': self.stats.copy()}

    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks."""
        return [t.to_dict() for t in self.queue.get_all_tasks() if t.status == TaskStatus.PENDING]

    def get_running_tasks(self) -> List[Dict]:
        """Get all running tasks."""
        running: Any = []
        for task_id in self.running_tasks:
            task: Any = self.queue.get_task(task_id)
            if task:
                running.append(task.to_dict())
        return running
_swarm_scheduler: Optional[SwarmScheduler] = None

def get_swarm_scheduler() -> SwarmScheduler:
    """Get or create the global SwarmScheduler instance."""
    global _swarm_scheduler
    if _swarm_scheduler is None:
        _swarm_scheduler = SwarmScheduler()
    return _swarm_scheduler

async def initialize_swarm_scheduler(max_workers: int=4) -> Any:
    """
    Initialize the SwarmScheduler system.

    Args:
        max_workers: Maximum number of concurrent workers
    """
    scheduler: Any = get_swarm_scheduler()
    await scheduler.start()
    LOGGER.info('SwarmScheduler system initialized')

async def submit_task(task_id: str, name: str, func: Callable, args: tuple=(), kwargs: dict=None, priority: TaskPriority=TaskPriority.MEDIUM) -> str:
    """Submit a task for execution."""
    scheduler: Any = get_swarm_scheduler()
    return scheduler.submit_task(task_id, name, func, args, kwargs, priority)
