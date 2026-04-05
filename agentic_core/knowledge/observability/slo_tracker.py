"""SLO Tracker.

SLI/SLO tracking for service level objectives.
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class SLOResult:
    """SLO check result."""
    slo_name: str
    target: float
    actual: float
    is_met: bool
    window_seconds: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SLOTracker:
    """Tracks service level objectives.

    The SLOTracker monitors SLIs and evaluates them against
    defined SLO targets.
    """

    def __init__(
        self,
        latency_slo_ms: float = 500.0,
        availability_slo: float = 0.99,
        error_rate_slo: float = 0.01,
        window_seconds: float = 300.0,
    ):
        """Initialize the SLO tracker.

        Args:
            latency_slo_ms: Target latency in milliseconds
            availability_slo: Target availability (0-1)
            error_rate_slo: Target error rate (0-1)
            window_seconds: Evaluation window
        """
        self.latency_slo_ms = latency_slo_ms
        self.availability_slo = availability_slo
        self.error_rate_slo = error_rate_slo
        self.window_seconds = window_seconds

        # Sliding windows for SLIs
        self._latencies: deque = deque()
        self._outcomes: deque = deque()  # (timestamp, success)

        log.info(f"SLOTracker initialized (latency_slo={latency_slo_ms}ms)")

    def record_latency(self, latency_ms: float) -> None:
        """Record a latency measurement.

        Args:
            latency_ms: Latency in milliseconds
        """
        now = time.time()
        self._latencies.append((now, latency_ms))
        self._trim_old_data(now)

    def record_outcome(self, success: bool) -> None:
        """Record a request outcome.

        Args:
            success: Whether request succeeded
        """
        now = time.time()
        self._outcomes.append((now, success))
        self._trim_old_data(now)

    def check_slos(self) -> list[SLOResult]:
        """Check all SLOs.

        Returns:
            List of SLOResult for each SLO
        """
        trace_id = f"slo_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "SLOTracker.check_slos"
        )

        results = []

        # Check latency SLO
        latency_result = self._check_latency_slo()
        results.append(latency_result)

        # Check availability SLO
        availability_result = self._check_availability_slo()
        results.append(availability_result)

        # Check error rate SLO
        error_result = self._check_error_rate_slo()
        results.append(error_result)

        return results

    def _check_latency_slo(self) -> SLOResult:
        """Check latency SLO."""
        if not self._latencies:
            actual = 0.0
        else:
            actual = sum(l for _, l in self._latencies) / len(self._latencies)

        return SLOResult(
            slo_name="latency_p95",
            target=self.latency_slo_ms,
            actual=actual,
            is_met=actual <= self.latency_slo_ms,
            window_seconds=self.window_seconds,
        )

    def _check_availability_slo(self) -> SLOResult:
        """Check availability SLO."""
        if not self._outcomes:
            actual = 1.0
        else:
            successes = sum(1 for _, s in self._outcomes if s)
            actual = successes / len(self._outcomes)

        return SLOResult(
            slo_name="availability",
            target=self.availability_slo,
            actual=actual,
            is_met=actual >= self.availability_slo,
            window_seconds=self.window_seconds,
        )

    def _check_error_rate_slo(self) -> SLOResult:
        """Check error rate SLO."""
        if not self._outcomes:
            actual = 0.0
        else:
            errors = sum(1 for _, s in self._outcomes if not s)
            actual = errors / len(self._outcomes)

        return SLOResult(
            slo_name="error_rate",
            target=self.error_rate_slo,
            actual=actual,
            is_met=actual <= self.error_rate_slo,
            window_seconds=self.window_seconds,
        )

    def _trim_old_data(self, now: float) -> None:
        """Remove data older than window."""
        cutoff = now - self.window_seconds

        while self._latencies and self._latencies[0][0] < cutoff:
            self._latencies.popleft()

        while self._outcomes and self._outcomes[0][0] < cutoff:
            self._outcomes.popleft()


# Global instance
_global_tracker: SLOTracker | None = None


def get_slo_tracker() -> SLOTracker:
    """Get or create the global SLO tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = SLOTracker()
    return _global_tracker
