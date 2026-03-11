"""
ShadowReplayValidator — Pre-activation regression guard for meta-learning.

Before any meta-learning config change is activated, this validator
replays a sample of previous execution traces under the proposed config
and rejects activation if:

  1. The determinism digest changes AND performance does not improve, OR
  2. Safety metrics degrade (any regression).
  3. The regression_threshold exceeds EPSILON.

EPSILON is a hard constant — it is NOT configurable at runtime.

Phase 2.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Hard constant — must NOT be made configurable at runtime.
EPSILON: float = 0.01


class RegressionError(RuntimeError):
    """Raised when shadow replay detects an unacceptable regression."""


@dataclass(frozen=True)
class ReplayResult:
    """Outcome of a single shadow replay run."""

    trace_id: str
    original_digest: str
    replayed_digest: str
    original_performance: float
    replayed_performance: float
    original_safety_score: float
    replayed_safety_score: float

    @property
    def digest_changed(self) -> bool:
        return self.original_digest != self.replayed_digest

    @property
    def performance_delta(self) -> float:
        return self.replayed_performance - self.original_performance

    @property
    def safety_degraded(self) -> bool:
        return self.replayed_safety_score < self.original_safety_score

    @property
    def regression_threshold(self) -> float:
        """Worst-case regression as a positive fraction (0 = no regression)."""
        return max(0.0, -self.performance_delta)


@dataclass(frozen=True)
class ShadowReplaySummary:
    """Aggregated result across all replayed traces."""

    total_traces: int
    regression_count: int
    max_regression_threshold: float
    any_safety_degraded: bool
    all_digests_stable: bool

    @property
    def activation_safe(self) -> bool:
        return (
            self.regression_count == 0
            and not self.any_safety_degraded
            and self.max_regression_threshold <= EPSILON
        )


class ShadowReplayValidator:
    """Validates meta-learning proposals via shadow replay."""

    def validate(
        self,
        replay_results: Sequence[ReplayResult],
    ) -> ShadowReplaySummary:
        """Run validation over *replay_results* and raise on failure.

        Args:
            replay_results: One ReplayResult per replayed trace.

        Returns:
            ShadowReplaySummary if activation is safe.

        Raises:
            RegressionError: If any regression exceeds EPSILON or safety degrades.
            ValueError: If *replay_results* is empty.
        """
        if not replay_results:
            raise ValueError("ShadowReplayValidator.validate: replay_results must not be empty")

        regression_count = 0
        max_threshold = 0.0
        any_safety_degraded = False
        digests_stable = True

        for result in replay_results:
            if result.digest_changed:
                digests_stable = False
                # Digest change is only acceptable if performance improves AND
                # safety does not degrade.
                if result.performance_delta <= 0.0:
                    regression_count += 1
                if result.safety_degraded:
                    any_safety_degraded = True

            if result.regression_threshold > max_threshold:
                max_threshold = result.regression_threshold

            if result.safety_degraded:
                any_safety_degraded = True

        summary = ShadowReplaySummary(
            total_traces=len(replay_results),
            regression_count=regression_count,
            max_regression_threshold=max_threshold,
            any_safety_degraded=any_safety_degraded,
            all_digests_stable=digests_stable,
        )

        if not summary.activation_safe:
            raise RegressionError(
                f"Shadow replay rejected activation: "
                f"regressions={regression_count}, "
                f"max_regression_threshold={max_threshold:.4f} (epsilon={EPSILON}), "
                f"safety_degraded={any_safety_degraded}"
            )

        return summary


__all__ = [
    "EPSILON",
    "RegressionError",
    "ReplayResult",
    "ShadowReplaySummary",
    "ShadowReplayValidator",
]
