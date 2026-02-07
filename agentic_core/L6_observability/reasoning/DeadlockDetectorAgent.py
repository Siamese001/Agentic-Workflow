"""
[PHASE 16] TaskMonitorAgent & DeadlockDetectorAgent - L6 System Health Specialist.

Monitors asyncio tasks for potential deadlocks and long-running operations.
Integrates with SovereignBaseAgent for autonomous health reporting.
"""

import asyncio
import inspect
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin

# NAMING FIXED: Consistent Logger usage
Logger = logging.getLogger(__name__)

# configuration (NAMING FIXED: Consistent lowercase to match usage)
max_phase_time = 300  # 5 minutes
heartbeat_interval = 30  # 30 seconds
deadlock_threshold = 2  # Alerts after 2 timeouts


@dataclass
class TaskMonitor:
    """
    Data container for monitoring a single asyncio Task.
    Note: Not an agent itself, but a resource managed by the DeadlockDetectorAgent.
    """

    task: asyncio.Task
    name: str
    start_time: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    status: str = "RUNNING"
    timeout_count: int = 0

    def update_heartbeat(self):
        """Update the last heartbeat time."""
        self.last_heartbeat = time.time()
        self.timeout_count = 0

    def check_timeout(self) -> bool:
        """Check if Task has timed out (FIXED: Uses max_phase_time)."""
        elapsed = time.time() - self.last_heartbeat
        if elapsed > max_phase_time:
            self.timeout_count += 1
            return True
        return False

    def get_stack_trace(self) -> str:
        """Get current stack trace of the Task."""
        if not self.task.done():
            coro = self.task.get_coro()
            if coro:
                try:
                    return f"Coroutine: {coro} | State: {inspect.getcoroutinestate(coro)}"
                except Exception as e:
                    return f"Error getting stack: {e}"
        return "Task completed"


class DeadlockDetectorAgent(AtomicExecutionMixin, SovereignBaseAgent):
    """
    L6 Agent responsible for monitoring system-wide asyncio health.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.monitored_tasks: dict[str, TaskMonitor] = {}
        self._monitor_loop_task: asyncio.Task | None = None

    def register_task(self, task: asyncio.Task, name: str = None) -> str:
        """Register a new task for monitoring."""
        task_id = str(id(task))
        name = name or f"Task-{task_id}"
        self.monitored_tasks[task_id] = TaskMonitor(task=task, name=name)
        Logger.info(f"[HEALTH] Monitoring task: {name} ({task_id})")
        return task_id

    def heartbeat(self, task_id: str):
        """Register a heartbeat for a specific task."""
        if task_id in self.monitored_tasks:
            self.monitored_tasks[task_id].update_heartbeat()

    def start_monitoring(self):
        """Start the background monitoring loop."""
        if self._monitor_loop_task is None:
            self._monitor_loop_task = asyncio.create_task(self._monitor_loop())
            Logger.info("[HEALTH] Deadlock detection loop started")

    async def _monitor_loop(self):
        """Internal loop to check all monitored tasks."""
        while True:
            await asyncio.sleep(heartbeat_interval)
            for tid, monitor in list(self.monitored_tasks.items()):
                if monitor.task.done():
                    del self.monitored_tasks[tid]
                    continue

                if monitor.check_timeout():
                    Logger.warning(f"[HEALTH] Task Timeout Detected: {monitor.name} (TID: {tid})")
                    if monitor.timeout_count >= deadlock_threshold:
                        Logger.error(
                            f"[DEADLOCK] Potential deadlock in {monitor.name}! Stack: {monitor.get_stack_trace()}",
                        )

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal a specific violation (IHealerProtocol compliance).

        Args:
            violation: Dict containing violation details

        Returns:
            Dict with status, details, artifacts, errors
        """
        return {
            "status": "success",
            "details": "DeadlockDetectorAgent observability heal - no action required",
            "artifacts": [],
            "errors": [],
        }

    def heal_repository(self, **kwargs) -> dict[str, Any]:
        """Standard autonomous healing interface."""
        return {"status": "healthy", "tasks_monitored": len(self.monitored_tasks)}


# Global Singleton Management
_deadlock_detector: DeadlockDetectorAgent | None = None


def get_deadlock_detector() -> DeadlockDetectorAgent:
    """Get or create the global DeadlockDetectorAgent instance."""
    global _deadlock_detector
    if _deadlock_detector is None:
        _deadlock_detector = DeadlockDetectorAgent()
    return _deadlock_detector


async def initialize_deadlock_detector():
    """Initialize the global health monitor system."""
    detector = get_deadlock_detector()
    detector.start_monitoring()
    Logger.info("[HEALTH] System health specialist initialized.")


# Convenience functions for global use
def register_task_for_monitoring(task: asyncio.Task, name: str = None) -> str:
    """Global hook to register a task."""
    return get_deadlock_detector().register_task(task, name)


def send_task_heartbeat(task_id: str):
    """Global hook to send a heartbeat."""
    get_deadlock_detector().heartbeat(task_id)


def monitor_task(name: str = None):
    """Decorator to automatically monitor a coroutine."""

    def decorator(coro):
        async def wrapper(*args, **kwargs):
            task = asyncio.current_task()
            if not task:
                return await coro(*args, **kwargs)

            task_id = register_task_for_monitoring(task, name or coro.__name__)
            try:
                return await coro(*args, **kwargs)
            finally:
                # Heartbeat before finishing to prove liveness
                send_task_heartbeat(task_id)

        return wrapper

    return decorator
