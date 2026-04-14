"""Reasoning Outcome Tracker — L6 Observability for ADG-Optimized Reasoning.

Captures per-call reasoning outcomes (latency, path selection, quality) and
aggregates for L0 calibration feedback. Operates non-authoritatively —
outcomes influence future calibration, not current execution.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ReasoningOutcome:
    """Single reasoning call outcome record."""

    trace_id: str
    timestamp: float
    profile_hash: str | None
    complexity_tier: str
    path_id: str
    latency_ms: float
    tokens_used: int
    quality_score: float | None = None  # 0.0-1.0, if available
    error_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        trace_id: str,
        profile_hash: str | None,
        complexity_tier: str,
        path_id: str,
        latency_ms: float,
        tokens_used: int,
        quality_score: float | None = None,
        error_type: str | None = None,
        **metadata,
    ) -> ReasoningOutcome:
        """Create a new outcome record."""
        return cls(
            trace_id=trace_id,
            timestamp=time.time(),
            profile_hash=profile_hash,
            complexity_tier=complexity_tier,
            path_id=path_id,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            quality_score=quality_score,
            error_type=error_type,
            metadata=metadata,
        )


@dataclass
class OutcomeAggregate:
    """Aggregated outcomes for a complexity tier."""

    complexity_tier: str
    path_id: str
    total_calls: int
    avg_latency_ms: float
    avg_tokens: float
    avg_quality_score: float | None
    error_rate: float
    p95_latency_ms: float
    timestamp: float


class ReasoningOutcomeTracker:
    """L6 outcome tracker for reasoning telemetry aggregation.

    Records individual outcomes and provides aggregated statistics
    for L0 ReasoningPolicyEngine calibration feedback.

    Usage:
        tracker = ReasoningOutcomeTracker()
        tracker.record_outcome(ReasoningOutcome.create(...))

        # Get aggregates for L0 calibration
        aggregates = tracker.get_aggregates(window_seconds=300)
    """

    _OUTCOMES_DIR = Path("artifacts/telemetry/reasoning_outcomes")
    _MAX_OUTCOMES = 10000

    def __init__(self, outcomes_dir: Path | None = None) -> None:
        """Initialize the outcome tracker."""
        self._outcomes_dir = outcomes_dir or self._OUTCOMES_DIR
        self._outcomes_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._outcomes: list[ReasoningOutcome] = []
        self._last_aggregate_time: float = 0.0

    def record_outcome(self, outcome: ReasoningOutcome) -> None:
        """Record a single reasoning outcome."""
        with self._lock:
            self._outcomes.append(outcome)

            # Prune if too many outcomes in memory
            if len(self._outcomes) > self._MAX_OUTCOMES:
                self._outcomes = self._outcomes[-self._MAX_OUTCOMES // 2 :]

        # Persist to disk for durability
        self._persist_outcome(outcome)

    def _persist_outcome(self, outcome: ReasoningOutcome) -> None:
        """Persist outcome to disk."""
        date_str = time.strftime("%Y%m%d")
        daily_file = self._outcomes_dir / f"outcomes_{date_str}.jsonl"

        line = json.dumps(asdict(outcome), default=str, sort_keys=True) + "\n"
        with self._lock:
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write(line)
                f.flush()

    def get_aggregates(
        self,
        window_seconds: float = 300.0,
        min_samples: int = 5,
    ) -> list[OutcomeAggregate]:
        """
        Get aggregated outcomes for L0 calibration feedback.

        Args:
            window_seconds: Time window for aggregation (default 5 min)
            min_samples: Minimum samples required for aggregation

        Returns:
            List of OutcomeAggregate by complexity_tier/path_id
        """
        window_seconds = max(0.0, window_seconds)
        min_samples = max(1, min_samples)
        cutoff_time = time.time() - window_seconds
        with self._lock:
            recent_outcomes = [o for o in self._outcomes if o.timestamp >= cutoff_time]

        # Group by (complexity_tier, path_id)
        groups: dict[tuple[str, str], list[ReasoningOutcome]] = {}
        for o in recent_outcomes:
            key = (o.complexity_tier, o.path_id)
            groups.setdefault(key, []).append(o)

        aggregates = []
        for (tier, path_id), outcomes in groups.items():
            if len(outcomes) < min_samples:
                continue

            latencies = [o.latency_ms for o in outcomes]
            tokens = [o.tokens_used for o in outcomes]
            qualities = [o.quality_score for o in outcomes if o.quality_score is not None]
            errors = [o for o in outcomes if o.error_type is not None]

            # Calculate p95 latency
            sorted_latencies = sorted(latencies)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p95_latency = sorted_latencies[min(p95_idx, len(sorted_latencies) - 1)]

            aggregates.append(
                OutcomeAggregate(
                    complexity_tier=tier,
                    path_id=path_id,
                    total_calls=len(outcomes),
                    avg_latency_ms=sum(latencies) / len(latencies),
                    avg_tokens=sum(tokens) / len(tokens),
                    avg_quality_score=sum(qualities) / len(qualities) if qualities else None,
                    error_rate=len(errors) / len(outcomes),
                    p95_latency_ms=p95_latency,
                    timestamp=time.time(),
                ),
            )

        with self._lock:
            self._last_aggregate_time = time.time()
        return aggregates

    def export_aggregates_json(self, aggregates: list[OutcomeAggregate] | None = None) -> str:
        """Export aggregates as JSON for L0 consumption."""
        if aggregates is None:
            aggregates = self.get_aggregates()

        return json.dumps(
            [asdict(a) for a in aggregates],
            indent=2,
            default=str,
        )

    def get_outcome_stats(self) -> dict[str, Any]:
        """Get basic stats about recorded outcomes."""
        with self._lock:
            total_outcomes = len(self._outcomes)
            last_aggregate_time = self._last_aggregate_time

        return {
            "total_outcomes_in_memory": total_outcomes,
            "last_aggregate_time": last_aggregate_time,
            "outcomes_dir": str(self._outcomes_dir),
        }
