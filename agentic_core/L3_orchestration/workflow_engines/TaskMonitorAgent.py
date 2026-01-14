from __future__ import annotations
from dataclasses import dataclass
"""
DeadlockDetectorAgent - L3 System Health Specialist

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
from typing import Any, Dict, List, Optional, Protocol, Set

# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)

# Configuration
# NAMING FIXED: MAX_PHASE_TIME → max_phase_time
max_phase_time = 300  # 5 minutes in seconds
# NAMING FIXED: HEARTBEAT_INTERVAL → heartbeat_interval
heartbeat_interval = 30  # Check every 30 seconds
# NAMING FIXED: DEADLOCK_THRESHOLD → deadlock_threshold
deadlock_threshold = 2  # Alert after 2 consecutive timeouts


# NAMING FIXED: TaskMonitorAgent → TaskMonitorAgent
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

@dataclass
class TaskMonitorAgent(HealerMixin):
    """Monitors a single asyncio Task."""

    def __init__(self, Task: asyncio.Task, name: str = None) -> None:
        self.Task = Task
        self.name = name or f"Task-{id(Task)}"
        self.start_time = time.time()
        self.last_heartbeat = time.time()
        self.status = "RUNNING"
        self.timeout_count = 0
        self.stack_traces = []

    def update_heartbeat(self) -> Any:
        """Update the last heartbeat time."""
        self.last_heartbeat = time.time()
        self.timeout_count = 0  # Reset timeout count on heartbeat

    def check_timeout(self) -> bool:
        """Check if Task has timed out."""
        elapsed = time.time() - self.last_heartbeat
        if elapsed > MAX_PHASE_TIME:
            self.timeout_count += 1
            return True
        return False

    def get_stack_trace(self) -> str:
        """Get current stack trace of the Task."""
        if not self.Task.done():
            # Get the coroutine
            coro = self.Task._coro
            if coro:
                # Try to get frame information
                try:
                    frame = inspect.getcoroutinestate(coro)
                    return f"Coroutine state: {frame}"
                except:
                    return "Unable to get stack trace"
        return "Task completed"

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# NAMING FIXED: DeadlockDetectorAgent → DeadlockDetectorAgent
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin
from agentic_core.schemas.models.anomaly_report import AnomalyReport, AnomalySeverity


# Global instance
_deadlock_detector: Optional[DeadlockDetectorAgent] = None


def get_deadlock_detector() -> DeadlockDetectorAgent:
    """Get or create the global DeadlockDetectorAgent instance."""
    global _deadlock_detector
    if _deadlock_detector is None:
        _deadlock_detector = DeadlockDetectorAgent()
    return _deadlock_detector


async def initialize_deadlock_detector() -> Any:
    """Initialize the DeadlockDetectorAgent system."""
    detector = get_deadlock_detector()
    detector.start_monitoring()
    LOGGER.info("DeadlockDetectorAgent system initialized")


# Convenience functions
def register_task(Task: asyncio.Task, name: str = None) -> str:
    """Register a Task for deadlock monitoring."""
    detector = get_deadlock_detector()
    return detector.register_task(Task, name)


def send_heartbeat(task_id: str) -> Any:
    """Send heartbeat for a monitored Task."""
    detector = get_deadlock_detector()
    detector.heartbeat(task_id)


# Decorator for automatic monitoring
def monitor_task(name: str = None) -> Any:
    """Decorator to automatically monitor a coroutine."""
    def decorator(coro) -> Any:
        """Execute decorator operation."""
        async def wrapper(*args, **kwargs) -> Any:
            """Execute wrapper operation."""
            Task = asyncio.create_task(coro(*args, **kwargs))
            task_id = register_task(Task, name or coro.__name__)

            try:
                result = await Task
                return result
            finally:
                # Cleanup
                if task_id in get_deadlock_detector().monitored_tasks:
                    del get_deadlock_detector().monitored_tasks[task_id]

        return wrapper
    return decorator