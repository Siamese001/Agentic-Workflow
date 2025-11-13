"""Metrics tracking for QA performance."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from ..qa.qa_validator import QAResult


@dataclass
class MetricsTracker:
    """Collect run-level QA metrics for later analysis."""

    total_runs: int = 0
    passes: int = 0
    latency_samples_ms: List[int] = field(default_factory=list)
    token_samples: List[int] = field(default_factory=list)
    token_drift_samples: List[float] = field(default_factory=list)
    failure_reasons: Counter = field(default_factory=Counter)
    retry_attempts: int = 0
    retry_successes: int = 0

    def record(
        self,
        result: QAResult,
        latency_ms: int | None = None,
        token_count: int | None = None,
        *,
        retry_attempted: bool = False,
        retry_succeeded: bool = False,
        token_drift: float | None = None,
    ) -> None:
        self.total_runs += 1
        if result.ok:
            self.passes += 1
        else:
            for reason in result.reasons:
                self.failure_reasons[reason] += 1
        if latency_ms is not None:
            self.latency_samples_ms.append(int(latency_ms))
        if token_count is not None:
            self.token_samples.append(int(token_count))
        if token_drift is not None:
            self.token_drift_samples.append(float(token_drift))
        if retry_attempted:
            self.retry_attempts += 1
            if retry_succeeded:
                self.retry_successes += 1

    def pass_rate(self) -> float:
        if not self.total_runs:
            return 0.0
        return self.passes / self.total_runs

    def latency_p95(self) -> int:
        if not self.latency_samples_ms:
            return 0
        ordered = sorted(self.latency_samples_ms)
        index = max(0, math.ceil(0.95 * len(ordered)) - 1)
        return ordered[index]

    def average_tokens(self) -> float:
        if not self.token_samples:
            return 0.0
        return sum(self.token_samples) / len(self.token_samples)

    def failure_breakdown(self) -> Dict[str, int]:
        return dict(self.failure_reasons)

    def retry_success_rate(self) -> float:
        if not self.retry_attempts:
            return 0.0
        return self.retry_successes / self.retry_attempts

    def token_drift(self) -> float:
        if not self.token_drift_samples:
            return 0.0
        return max(self.token_drift_samples)

    def reset(self) -> None:
        self.total_runs = 0
        self.passes = 0
        self.latency_samples_ms.clear()
        self.token_samples.clear()
        self.token_drift_samples.clear()
        self.failure_reasons.clear()
        self.retry_attempts = 0
        self.retry_successes = 0
