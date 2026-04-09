"""C6 Shadow Evaluator - L6 analysis core and signal aggregation.

10C-REQ-163: L6 Analysis Core divergence classifier root cause tagger
10C-REQ-164: L6 Signal Aggregator anomaly burst promotion/demotion signal
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class DivergenceType(Enum):
    """Types of execution divergence."""
    OUTPUT_MISMATCH = auto()
    TIMING_DRIFT = auto()
    STATE_CORRUPTION = auto()
    DETERMINISM_FAILURE = auto()
    POLICY_VIOLATION = auto()


class AnomalySignal(Enum):
    """Anomaly aggregation signals."""
    PROMOTE = auto()
    DEMOTE = auto()
    INVESTIGATE = auto()
    IGNORE = auto()


@dataclass
class Divergence:
    """Detected divergence between expected and actual."""
    divergence_type: DivergenceType
    severity: float
    expected: Any
    actual: Any
    root_cause_tags: list[str]
    trace_id: str


@dataclass
class AggregatedSignal:
    """Aggregated anomaly signal."""
    signal: AnomalySignal
    burst_count: int
    confidence: float
    recommended_action: str


class ShadowEvaluator:
    """C6 Shadow Evaluator.
    
    10C-REQ-163/164: L6 analysis and signal aggregation.
    """
    
    def __init__(self) -> None:
        self._divergences: list[Divergence] = []
        self._anomaly_bursts: dict[str, list[float]] = {}
    
    def analyze(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
        trace_id: str,
    ) -> list[Divergence]:
        """Analyze for divergence between expected and actual."""
        divergences: list[Divergence] = []
        
        # Check output mismatch
        if expected.get("output") != actual.get("output"):
            divergences.append(Divergence(
                divergence_type=DivergenceType.OUTPUT_MISMATCH,
                severity=0.8,
                expected=expected.get("output"),
                actual=actual.get("output"),
                root_cause_tags=["output_diff", "logic_error"],
                trace_id=trace_id,
            ))
        
        # Check timing drift
        expected_time = expected.get("execution_time", 0)
        actual_time = actual.get("execution_time", 0)
        if expected_time > 0:
            drift = abs(actual_time - expected_time) / expected_time
            if drift > 0.2:  # 20% threshold
                divergences.append(Divergence(
                    divergence_type=DivergenceType.TIMING_DRIFT,
                    severity=min(1.0, drift),
                    expected=expected_time,
                    actual=actual_time,
                    root_cause_tags=["performance_drift", "resource_contention"],
                    trace_id=trace_id,
                ))
        
        # Check determinism
        if actual.get("determinism_digest") != expected.get("determinism_digest"):
            divergences.append(Divergence(
                divergence_type=DivergenceType.DETERMINISM_FAILURE,
                severity=1.0,
                expected=expected.get("determinism_digest"),
                actual=actual.get("determinism_digest"),
                root_cause_tags=["nondeterminism", "entropy_leak", "clock_drift"],
                trace_id=trace_id,
            ))
        
        self._divergences.extend(divergences)
        return divergences
    
    def aggregate_anomaly_burst(
        self,
        anomaly_type: str,
        occurrences: list[float],
    ) -> AggregatedSignal:
        """Aggregate anomaly burst into promotion/demotion signal."""
        self._anomaly_bursts[anomaly_type] = occurrences
        
        burst_count = len(occurrences)
        
        if burst_count >= 10:
            # High burst - investigate and potentially demote
            return AggregatedSignal(
                signal=AnomalySignal.INVESTIGATE,
                burst_count=burst_count,
                confidence=0.85,
                recommended_action="initiate_root_cause_analysis",
            )
        elif burst_count >= 5:
            # Medium burst - demote
            return AggregatedSignal(
                signal=AnomalySignal.DEMOTE,
                burst_count=burst_count,
                confidence=0.72,
                recommended_action="reduce_confidence_threshold",
            )
        elif burst_count == 0:
            # No anomalies - promote
            return AggregatedSignal(
                signal=AnomalySignal.PROMOTE,
                burst_count=0,
                confidence=0.90,
                recommended_action="increase_confidence_threshold",
            )
        else:
            return AggregatedSignal(
                signal=AnomalySignal.IGNORE,
                burst_count=burst_count,
                confidence=0.60,
                recommended_action="monitor",
            )
    
    def get_divergence_stats(self) -> dict[str, Any]:
        """Get divergence statistics."""
        by_type: dict[str, int] = {}
        for d in self._divergences:
            key = d.divergence_type.name
            by_type[key] = by_type.get(key, 0) + 1
        
        return {
            "total_divergences": len(self._divergences),
            "by_type": by_type,
        }
