"""Recovery Manager.

State recovery and graceful degradation.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)
from tqdm import tqdm

log = logging.getLogger(__name__)


@dataclass
class RecoveryAction:
    """A recovery action."""

    name: str
    action: Callable
    priority: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


class RecoveryManager:
    """Manages recovery and graceful degradation.

    The RecoveryManager coordinates recovery actions and handles
    graceful degradation when services are unavailable.
    """

    def __init__(self):
        """Initialize the recovery manager."""
        self._recovery_actions: list[RecoveryAction] = []
        self._degradation_levels: dict[str, int] = {}
        self._recovery_history: list[dict[str, Any]] = []

        log.info("RecoveryManager initialized")

    def register_recovery_action(
        self,
        name: str,
        action: Callable,
        priority: int = 1,
    ) -> None:
        """Register a recovery action.

        Args:
            name: Action name
            action: Callable recovery function
            priority: Priority (lower = higher priority)
        """
        recovery_action = RecoveryAction(
            name=name,
            action=action,
            priority=priority,
        )

        self._recovery_actions.append(recovery_action)
        # Sort by priority
        self._recovery_actions.sort(key=lambda x: x.priority)

        log.info(f"Registered recovery action: {name} (priority={priority})")

    def attempt_recovery(
        self,
        failure_context: dict[str, Any] | None = None,
    ) -> bool:
        """Attempt recovery using registered actions.

        Args:
            failure_context: Optional context about the failure

        Returns:
            True if recovery succeeded
        """
        trace_id = f"recovery_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "RecoveryManager.attempt_recovery",
        )

        for action in tqdm(self._recovery_actions, desc="Processing", unit="item"):
            try:
                log.info(f"Attempting recovery action: {action.name}")

                result = action.action()

                if result:
                    self._record_recovery(action.name, True, failure_context)

                    _emit_records_telemetry_event(
                        "recovery",
                        f"success_{action.name}",
                    )

                    log.info(f"Recovery action succeeded: {action.name}")
                    return True

            except Exception as e:  # guardian: allow-broad-exception allow-log-and-swallow -- recovery action isolation: non-fatal, next action attempted
                log.warning(f"Recovery action failed: {action.name} - {e}")
                self._record_recovery(action.name, False, failure_context, str(e))

        _emit_records_telemetry_event(
            "recovery",
            "all_actions_failed",
        )

        log.error("All recovery actions failed")
        return False

    def get_degradation_level(self, service_name: str) -> int:
        """Get current degradation level for a service.

        Args:
            service_name: Service identifier

        Returns:
            Degradation level (0 = normal, higher = more degraded)
        """
        return self._degradation_levels.get(service_name, 0)

    def set_degradation_level(self, service_name: str, level: int) -> None:
        """Set degradation level for a service.

        Args:
            service_name: Service identifier
            level: Degradation level
        """
        old_level = self._degradation_levels.get(service_name, 0)
        self._degradation_levels[service_name] = level

        if level != old_level:
            log.info(f"Service '{service_name}' degradation: {old_level} -> {level}")

    def degrade_gracefully(
        self,
        service_name: str,
        normal_fn: Callable,
        degraded_fn: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with graceful degradation.

        Args:
            service_name: Service identifier
            normal_fn: Normal function to execute
            degraded_fn: Degraded function fallback
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        degradation_level = self.get_degradation_level(service_name)

        if degradation_level == 0:
            try:
                return normal_fn(*args, **kwargs)
            except Exception as e:  # guardian: allow-broad-exception allow-log-and-swallow -- normal execution failure: degraded fallback invoked
                log.warning(f"Normal execution failed, attempting degraded: {e}")
                return degraded_fn(*args, **kwargs)
        else:
            log.info(f"Executing in degraded mode (level={degradation_level})")
            return degraded_fn(*args, **kwargs)

    def _record_recovery(
        self,
        action_name: str,
        success: bool,
        context: dict[str, Any] | None,
        error: str | None = None,
    ) -> None:
        """Record a recovery attempt."""
        entry = {
            "timestamp": time.time(),
            "action": action_name,
            "success": success,
            "context": context,
            "error": error,
        }
        self._recovery_history.append(entry)

    def get_recovery_stats(self) -> dict[str, Any]:
        """Get recovery statistics.

        Returns:
            Dictionary with stats
        """
        if not self._recovery_history:
            return {"total_attempts": 0}

        successful = sum(1 for r in self._recovery_history if r["success"])

        return {
            "total_attempts": len(self._recovery_history),
            "successful": successful,
            "failed": len(self._recovery_history) - successful,
            "success_rate": successful / len(self._recovery_history),
        }


# Global instance
_global_recovery: RecoveryManager | None = None


def get_recovery_manager() -> RecoveryManager:
    """Get or create the global recovery manager."""
    global _global_recovery
    if _global_recovery is None:
        _global_recovery = RecoveryManager()
    return _global_recovery
