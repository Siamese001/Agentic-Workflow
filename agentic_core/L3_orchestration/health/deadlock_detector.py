"""
DeadlockDetector - L3 System Health Specialist

Monitors asyncio tasks for potential deadlocks and long-running operations.
Alerts when tasks exceed MAX_PHASE_TIME without progress.
"""
import asyncio
import inspect
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Protocol, Dict, List, Set

LOGGER = logging.getLogger(__name__)

# Configuration
MAX_PHASE_TIME = 300  # 5 minutes in seconds
HEARTBEAT_INTERVAL = 30  # Check every 30 seconds
DEADLOCK_THRESHOLD = 2  # Alert after 2 consecutive timeouts


class TaskMonitor:
    """Monitors a single asyncio task."""

    def __init__(self, task: asyncio.Task, name: str = None):
        self.task = task
        self.name = name or f"Task-{id(task)}"
        self.start_time = time.time()
        self.last_heartbeat = time.time()
        self.status = "RUNNING"
        self.timeout_count = 0
        self.stack_traces = []

    def update_heartbeat(self):
        """Update the last heartbeat time."""
        self.last_heartbeat = time.time()
        self.timeout_count = 0  # Reset timeout count on heartbeat

    def check_timeout(self) -> bool:
        """Check if task has timed out."""
        elapsed = time.time() - self.last_heartbeat
        if elapsed > MAX_PHASE_TIME:
            self.timeout_count += 1
            return True
        return False

    def get_stack_trace(self) -> str:
        """Get current stack trace of the task."""
        if not self.task.done():
            # Get the coroutine
            coro = self.task._coro
            if coro:
                # Try to get frame information
                try:
                    frame = inspect.getcoroutinestate(coro)
                    return f"Coroutine state: {frame}"
                except:
                    return "Unable to get stack trace"
        return "Task completed"


class DeadlockDetector:
    """
    Detects potential deadlocks in asyncio tasks.

    Monitors:
    - Task execution time
    - Heartbeat signals
    - Stack traces for debugging
    """

    def __init__(self):
        """Initialize the DeadlockDetector."""
        self.monitored_tasks: Dict[str, TaskMonitor] = {}
        self.alerted_tasks: Set[str] = set()
        self.monitor_task: Optional[asyncio.Task] = None
        self.enabled = True

        LOGGER.info("DeadlockDetector initialized")

    def start_monitoring(self):
        """Start the background monitoring task."""
        if not self.enabled or self.monitor_task:
            return

        self.monitor_task = asyncio.create_task(self._monitor_loop())
        LOGGER.info("Deadlock monitoring started")

    def stop_monitoring(self):
        """Stop the background monitoring task."""
        if self.monitor_task:
            self.monitor_task.cancel()
            self.monitor_task = None
            LOGGER.info("Deadlock monitoring stopped")

    def register_task(self, task: asyncio.Task, name: str = None) -> str:
        """
        Register a task for monitoring.

        Args:
            task: Asyncio task to monitor
            name: Optional name for the task

        Returns:
            Task ID for reference
        """
        if not self.enabled:
            return ""

        task_id = name or f"task-{id(task)}"
        monitor = TaskMonitor(task, task_id)
        self.monitored_tasks[task_id] = monitor

        # Add done callback
        task.add_done_callback(lambda t: self._task_done(task_id))

        LOGGER.debug(f"Registered task for monitoring: {task_id}")
        return task_id

    def heartbeat(self, task_id: str):
        """
        Send heartbeat for a monitored task.

        Args:
            task_id: ID of the task
        """
        if task_id in self.monitored_tasks:
            self.monitored_tasks[task_id].update_heartbeat()

    def _task_done(self, task_id: str):
        """Handle task completion."""
        if task_id in self.monitored_tasks:
            monitor = self.monitored_tasks[task_id]
            monitor.status = "COMPLETED" if monitor.task.cancelled() else "DONE"
            LOGGER.debug(f"Task completed: {task_id}")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                await self._check_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                LOGGER.error(f"Error in monitor loop: {e}")

    async def _check_tasks(self):
        """Check all monitored tasks for timeouts."""
        current_time = time.time()

        for task_id, monitor in list(self.monitored_tasks.items()):
            # Skip completed tasks
            if monitor.task.done():
                continue

            # Check for timeout
            if monitor.check_timeout():
                elapsed = current_time - monitor.last_heartbeat

                # Get stack trace
                stack_trace = monitor.get_stack_trace()
                monitor.stack_traces.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "elapsed": elapsed,
                    "trace": stack_trace
                })

                # Alert if threshold exceeded
                if monitor.timeout_count >= DEADLOCK_THRESHOLD:
                    await self._alert_deadlock(task_id, monitor, elapsed)
                else:
                    LOGGER.warning(
                        f"Task {task_id} timeout #{monitor.timeout_count}: "
                        f"{elapsed:.1f}s without heartbeat"
                    )

    async def _alert_deadlock(self, task_id: str, monitor: TaskMonitor, elapsed: float):
        """Alert about a potential deadlock."""
        if task_id in self.alerted_tasks:
            return  # Already alerted

        self.alerted_tasks.add(task_id)

        # Create alert message
        alert = {
            "type": "DEADLOCK_DETECTED",
            "task_id": task_id,
            "elapsed_seconds": elapsed,
            "start_time": datetime.fromtimestamp(monitor.start_time).isoformat(),
            "last_heartbeat": datetime.fromtimestamp(monitor.last_heartbeat).isoformat(),
            "timeout_count": monitor.timeout_count,
            "stack_traces": monitor.stack_traces[-3:],  # Last 3 traces
            "timestamp": datetime.utcnow().isoformat()
        }

        # Log alert
        LOGGER.error(f"[ALERT] DEADLOCK DETECTED: {task_id}")
        LOGGER.error(f"  Elapsed: {elapsed:.1f}s (threshold: {MAX_PHASE_TIME}s)")
        LOGGER.error(f"  Stack traces: {len(monitor.stack_traces)} captured")

        # Store alert for reporting
        alert_file = Path("observability/alerts/deadlocks.json")
        alert_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if alert_file.exists():
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            else:
                alerts = []

            alerts.append(alert)

            # Keep only last 100 alerts
            if len(alerts) > 100:
                alerts = alerts[-100:]

            with open(alert_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        except Exception as e:
            LOGGER.error(f"Failed to save deadlock alert: {e}")

    def get_status(self) -> Dict:
        """Get current monitoring status."""
        active_tasks = sum(1 for m in self.monitored_tasks.values()
                          if not m.task.done())

        return {
            "enabled": self.enabled,
            "monitoring": self.monitor_task is not None,
            "active_tasks": active_tasks,
            "total_registered": len(self.monitored_tasks),
            "alerted_tasks": len(self.alerted_tasks),
            "max_phase_time": MAX_PHASE_TIME,
            "heartbeat_interval": HEARTBEAT_INTERVAL
        }

    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get details for a specific task."""
        if task_id not in self.monitored_tasks:
            return None

        monitor = self.monitored_tasks[task_id]
        return {
            "name": monitor.name,
            "status": monitor.status,
            "start_time": datetime.fromtimestamp(monitor.start_time).isoformat(),
            "last_heartbeat": datetime.fromtimestamp(monitor.last_heartbeat).isoformat(),
            "elapsed": time.time() - monitor.start_time,
            "timeout_count": monitor.timeout_count,
            "is_done": monitor.task.done(),
            "stack_traces": monitor.stack_traces
        }


# Global instance
_deadlock_detector: Optional[DeadlockDetector] = None


def get_deadlock_detector() -> DeadlockDetector:
    """Get or create the global DeadlockDetector instance."""
    global _deadlock_detector
    if _deadlock_detector is None:
        _deadlock_detector = DeadlockDetector()
    return _deadlock_detector


async def initialize_deadlock_detector():
    """Initialize the DeadlockDetector system."""
    detector = get_deadlock_detector()
    detector.start_monitoring()
    LOGGER.info("DeadlockDetector system initialized")


# Convenience functions
def register_task(task: asyncio.Task, name: str = None) -> str:
    """Register a task for deadlock monitoring."""
    detector = get_deadlock_detector()
    return detector.register_task(task, name)


def send_heartbeat(task_id: str):
    """Send heartbeat for a monitored task."""
    detector = get_deadlock_detector()
    detector.heartbeat(task_id)


# Decorator for automatic monitoring
def monitor_task(name: str = None):
    """Decorator to automatically monitor a coroutine."""
    def decorator(coro):
        async def wrapper(*args, **kwargs):
            task = asyncio.create_task(coro(*args, **kwargs))
            task_id = register_task(task, name or coro.__name__)

            try:
                result = await task
                return result
            finally:
                # Cleanup
                if task_id in get_deadlock_detector().monitored_tasks:
                    del get_deadlock_detector().monitored_tasks[task_id]

        return wrapper
    return decorator