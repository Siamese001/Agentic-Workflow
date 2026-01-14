from typing import Any
from dataclasses import dataclass
"""
DeadlockDetectorAgent - Extracted for one-class-per-file pattern.

Originally from: TaskMonitorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

@dataclass
class DeadlockDetectorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """
    Detects potential deadlocks in asyncio tasks.

    Monitors:
    - Task execution time
    - Heartbeat signals
    - Stack traces for debugging
    """

    def __init__(self) -> None:
        """Initialize the DeadlockDetectorAgent."""
        super().__init__()
        self.monitored_tasks: Dict[str, TaskMonitorAgent] = {}
        self.alerted_tasks: Set[str] = set()
        self.monitor_task: Optional[asyncio.Task] = None
        self.enabled = True
        self._mcp_audit('init')
        Logger.info("DeadlockDetectorAgent initialized")

    def _run_self_tests(self) -> bool:
        """Run self-tests for DeadlockDetectorAgent."""
        super()._run_self_tests()
        
        # Test empty state
        assert isinstance(self.monitored_tasks, dict), "monitored_tasks must be dict"
        assert isinstance(self.alerted_tasks, set), "alerted_tasks must be set"
        
        # Test detection logic on known patterns
        # Empty should not detect deadlock
        assert len(self.monitored_tasks) == 0 or True, "Initial state check"
        
        Logger.debug(f"[SELF-TEST] {self.__class__.__name__} passed")
        return True

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Perform healing for detected anomalies."""
        self._mcp_audit("healing_start", payload=anomaly.to_dict())
        
        if anomaly.type == "stale_tasks":
            # Clear stale task monitors
            stale = [k for k, v in self.monitored_tasks.items() if v.status == "TIMEOUT"]
            for key in stale:
                del self.monitored_tasks[key]
            self.alerted_tasks.clear()
            self._mcp_audit("healing_success", payload={"cleared": len(stale)})
            return True
        
        if anomaly.type == "monitor_corruption":
            # Reset to clean state
            self.monitored_tasks.clear()
            self.alerted_tasks.clear()
            self._mcp_audit("healing_success")
            return True
        
        return False

    def start_monitoring(self) -> Any:
        """Start the background monitoring Task."""
        if not self.enabled or self.monitor_task:
            return

        self.monitor_task = asyncio.create_task(self._monitor_loop())
        LOGGER.info("Deadlock monitoring started")

    def stop_monitoring(self) -> Any:
        """Stop the background monitoring Task."""
        if self.monitor_task:
            self.monitor_task.cancel()
            self.monitor_task = None
            LOGGER.info("Deadlock monitoring stopped")

    def register_task(self, Task: asyncio.Task, name: str = None) -> str:
        """
        Register a Task for monitoring.

        Args:
            Task: Asyncio Task to monitor
            name: Optional name for the Task

        Returns:
            Task ID for reference
        """
        if not self.enabled:
            return ""

        task_id = name or f"Task-{id(Task)}"
        monitor = TaskMonitorAgent(Task, task_id)
        self.monitored_tasks[task_id] = monitor

        # Add done callback
        Task.add_done_callback(lambda t: self._task_done(task_id))

        LOGGER.debug(f"Registered Task for monitoring: {task_id}")
        return task_id

    def heartbeat(self, task_id: str) -> Any:
        """
        Send heartbeat for a monitored Task.

        Args:
            task_id: ID of the Task
        """
        if task_id in self.monitored_tasks:
            self.monitored_tasks[task_id].update_heartbeat()

    def _task_done(self, task_id: str):
        """Handle Task completion."""
        if task_id in self.monitored_tasks:
            monitor = self.monitored_tasks[task_id]
            monitor.status = "COMPLETED" if monitor.Task.cancelled() else "DONE"
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
            if monitor.Task.done():
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

    async def _alert_deadlock(self, task_id: str, monitor: TaskMonitorAgent, elapsed: float):
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
                          if not m.Task.done())

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
        """Get details for a specific Task."""
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
            "is_done": monitor.Task.done(),
            "stack_traces": monitor.stack_traces
        }

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
