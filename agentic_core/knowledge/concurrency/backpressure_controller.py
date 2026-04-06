"""Backpressure Controller.

Dynamic throttling based on load and resource usage.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class LoadLevel(Enum):
    """System load levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LoadMetrics:
    """Current load metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    queue_depth: int = 0
    active_requests: int = 0
    latency_p95_ms: float = 0.0


class BackpressureController:
    """Controls backpressure based on system load.

    The BackpressureController monitors system metrics and applies
    dynamic throttling to prevent overload.
    """

    def __init__(
        self,
        high_threshold: float = 0.8,
        critical_threshold: float = 0.9,
    ):
        """Initialize the backpressure controller.

        Args:
            high_threshold: Threshold for HIGH load level
            critical_threshold: Threshold for CRITICAL load level
        """
        self.high_threshold = high_threshold
        self.critical_threshold = critical_threshold

        self._current_level = LoadLevel.NORMAL
        self._throttle_factor = 1.0  # 1.0 = no throttling

        log.info(f"BackpressureController initialized (high={high_threshold}, critical={critical_threshold})")

    def update_load(self, metrics: LoadMetrics) -> LoadLevel:
        """Update load metrics and calculate backpressure.

        Args:
            metrics: Current load metrics

        Returns:
            Current load level
        """
        trace_id = f"backpressure_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "BackpressureController.update_load"
        )

        # Calculate composite load score
        load_score = self._calculate_load_score(metrics)

        # Determine load level
        new_level = self._determine_load_level(load_score)

        # Update throttle factor
        self._update_throttle(new_level)

        # Log level changes
        if new_level != self._current_level:
            log.warning(f"Load level changed: {self._current_level.value} -> {new_level.value}")

            _emit_records_telemetry_event(
                "backpressure",
                f"level_{new_level.value}"
            )

        self._current_level = new_level
        return new_level

    def should_accept_request(self) -> bool:
        """Check if new request should be accepted.

        Returns:
            True if request can be accepted
        """
        if self._current_level == LoadLevel.CRITICAL:
            return False

        if self._current_level == LoadLevel.HIGH:
            # Accept with probability based on throttle factor
            import random
            return random.random() < self._throttle_factor

        return True

    def get_throttle_delay(self) -> float:
        """Get recommended throttle delay.

        Returns:
            Delay in seconds before processing
        """
        if self._current_level == LoadLevel.LOW:
            return 0.0
        elif self._current_level == LoadLevel.NORMAL:
            return 0.0
        elif self._current_level == LoadLevel.HIGH:
            return 0.1
        else:  # CRITICAL
            return 0.5

    def get_stats(self) -> dict[str, Any]:
        """Get backpressure statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "current_level": self._current_level.value,
            "throttle_factor": self._throttle_factor,
            "high_threshold": self.high_threshold,
            "critical_threshold": self.critical_threshold,
        }

    def _calculate_load_score(self, metrics: LoadMetrics) -> float:
        """Calculate composite load score."""
        # Weighted combination of metrics
        cpu_weight = 0.3
        memory_weight = 0.2
        queue_weight = 0.2
        latency_weight = 0.3

        # Normalize queue depth (assume max 1000)
        queue_score = min(metrics.queue_depth / 1000, 1.0)

        # Normalize latency (assume max 5000ms)
        latency_score = min(metrics.latency_p95_ms / 5000, 1.0)

        return (
            metrics.cpu_percent * cpu_weight +
            metrics.memory_percent * memory_weight +
            queue_score * queue_weight +
            latency_score * latency_weight
        )

    def _determine_load_level(self, load_score: float) -> LoadLevel:
        """Determine load level from score."""
        if load_score >= self.critical_threshold:
            return LoadLevel.CRITICAL
        elif load_score >= self.high_threshold:
            return LoadLevel.HIGH
        elif load_score >= 0.5:
            return LoadLevel.NORMAL
        else:
            return LoadLevel.LOW

    def _update_throttle(self, level: LoadLevel) -> None:
        """Update throttle factor based on load level."""
        if level == LoadLevel.LOW:
            self._throttle_factor = 1.0
        elif level == LoadLevel.NORMAL:
            self._throttle_factor = 1.0
        elif level == LoadLevel.HIGH:
            self._throttle_factor = 0.5
        else:  # CRITICAL
            self._throttle_factor = 0.1


# Global instance
_global_controller: BackpressureController | None = None


def get_backpressure_controller() -> BackpressureController:
    """Get or create the global backpressure controller."""
    global _global_controller
    if _global_controller is None:
        _global_controller = BackpressureController()
    return _global_controller
