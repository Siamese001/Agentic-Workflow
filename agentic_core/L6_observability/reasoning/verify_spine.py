"""C2 Verify Spine S1-S4 - Verification stages.

10C-REQ-129: S1 Time Audit - stamp verification monotonic drift frozen clock check
10C-REQ-130: S2 Isolation Check - seed entropy verify no external random
10C-REQ-131: S3 Drift Detection - budget thrash detect
10C-REQ-132: S4 Packet Seal - metrics normalize
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class SpineStage(Enum):
    """Verify spine stages."""
    S1_TIME_AUDIT = auto()
    S2_ISOLATION_CHECK = auto()
    S3_DRIFT_DETECTION = auto()
    S4_PACKET_SEAL = auto()


@dataclass
class SpineResult:
    """Result of spine verification."""
    stage: SpineStage
    passed: bool
    anomalies: list[str]
    metrics: dict[str, float]
    sealed: bool = False


class VerifySpine:
    """C2 Verify Spine S1-S4.
    
    10C-REQ-129 to REQ-132: Four-stage verification pipeline.
    """
    
    def __init__(self) -> None:
        self._drift_threshold = 0.05  # 5% drift threshold
        self._thrash_threshold = 100  # 100 threshold violations
    
    def verify(self, trace: dict[str, Any]) -> list[SpineResult]:
        """Run full spine verification S1-S4."""
        results: list[SpineResult] = []
        
        results.append(self._s1_time_audit(trace))
        results.append(self._s2_isolation_check(trace))
        results.append(self._s3_drift_detection(trace))
        results.append(self._s4_packet_seal(results))
        
        return results
    
    def _s1_time_audit(self, trace: dict[str, Any]) -> SpineResult:
        """S1: Time audit - verify stamps, monotonicity, frozen clock."""
        anomalies: list[str] = []
        metrics: dict[str, float] = {}
        
        stamps = trace.get("timestamps", [])
        if len(stamps) >= 2:
            for i in range(1, len(stamps)):
                if stamps[i] < stamps[i-1]:
                    anomalies.append(f"non_monotonic_at_index_{i}")
            
            frozen_at = trace.get("frozen_clock")
            if frozen_at:
                for stamp in stamps:
                    if stamp > frozen_at + 0.1:
                        anomalies.append("clock_after_freeze_boundary")
                        break
            
            metrics["time_span_ms"] = (stamps[-1] - stamps[0]) * 1000
        
        return SpineResult(
            stage=SpineStage.S1_TIME_AUDIT,
            passed=len(anomalies) == 0,
            anomalies=anomalies,
            metrics=metrics,
        )
    
    def _s2_isolation_check(self, trace: dict[str, Any]) -> SpineResult:
        """S2: Isolation check - verify seed entropy, no external random."""
        anomalies: list[str] = []
        metrics: dict[str, float] = {}
        
        entropy_source = trace.get("entropy_source", "")
        
        if entropy_source == "random":
            anomalies.append("non_deterministic_entropy")
        elif entropy_source == "seeded":
            seed_value = trace.get("seed_value")
            if seed_value is None:
                anomalies.append("seed_value_missing")
            else:
                metrics["seed"] = float(seed_value)
        
        if trace.get("uuid4_calls", 0) > 0:
            anomalies.append("uuid4_detected")
        if trace.get("random_calls", 0) > 0:
            anomalies.append("random_module_detected")
        
        return SpineResult(
            stage=SpineStage.S2_ISOLATION_CHECK,
            passed=len(anomalies) == 0,
            anomalies=anomalies,
            metrics=metrics,
        )
    
    def _s3_drift_detection(self, trace: dict[str, Any]) -> SpineResult:
        """S3: Drift detection - budget thrash detection."""
        anomalies: list[str] = []
        metrics: dict[str, float] = {}
        
        budget_used = trace.get("budget_used", 0.0)
        budget_planned = trace.get("budget_planned", 1.0)
        
        if budget_planned > 0:
            drift = abs(budget_used - budget_planned) / budget_planned
            metrics["budget_drift_pct"] = drift * 100
            
            if drift > self._drift_threshold:
                anomalies.append(f"budget_drift_{drift:.2%}")
        
        state_changes = trace.get("state_changes", [])
        if len(state_changes) > self._thrash_threshold:
            anomalies.append(f"state_thrash_{len(state_changes)}_changes")
            metrics["state_change_rate"] = len(state_changes)
        
        return SpineResult(
            stage=SpineStage.S3_DRIFT_DETECTION,
            passed=len(anomalies) == 0,
            anomalies=anomalies,
            metrics=metrics,
        )
    
    def _s4_packet_seal(self, previous_results: list[SpineResult]) -> SpineResult:
        """S4: Packet seal - normalize metrics, compute final state."""
        all_passed = all(r.passed for r in previous_results)
        all_anomalies = [a for r in previous_results for a in r.anomalies]
        
        metrics: dict[str, float] = {}
        for r in previous_results:
            metrics.update(r.metrics)
        
        return SpineResult(
            stage=SpineStage.S4_PACKET_SEAL,
            passed=all_passed,
            anomalies=all_anomalies,
            metrics=metrics,
            sealed=True,
        )
