"""C2 Drift Detector - Budget and behavior drift detection.

10C-REQ-131: S3 Drift Detection budget thrash detect
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from collections import deque


@dataclass
class DriftSignal:
    """Drift detection signal."""
    drift_type: str
    severity: float  # 0.0 to 1.0
    metric: str
    baseline_value: float
    current_value: float
    window_size: int


class DriftDetector:
    """C2 Drift Detector.
    
    10C-REQ-131: Budget thrash detection and behavioral drift.
    """
    
    def __init__(self, window_size: int = 100) -> None:
        self._window_size = window_size
        self._metric_history: dict[str, deque[float]] = {}
        self._thresholds: dict[str, tuple[float, float]] = {}  # (lower, upper)
        self._drift_count: int = 0
    
    def set_threshold(self, metric: str, lower: float, upper: float) -> None:
        """Set drift thresholds for metric."""
        self._thresholds[metric] = (lower, upper)
    
    def observe(self, metric: str, value: float) -> DriftSignal | None:
        """Observe metric value and detect drift."""
        if metric not in self._metric_history:
            self._metric_history[metric] = deque(maxlen=self._window_size)
        
        history = self._metric_history[metric]
        
        # Calculate baseline from history
        baseline = sum(history) / len(history) if history else value
        
        # Add to history
        history.append(value)
        
        # Check thresholds
        if metric in self._thresholds:
            lower, upper = self._thresholds[metric]
            
            if value < lower or value > upper:
                self._drift_count += 1
                
                # Calculate severity (0.0 to 1.0)
                if value < lower and lower > 0:
                    severity = min(1.0, (lower - value) / lower)
                elif upper > 0:
                    severity = min(1.0, (value - upper) / upper)
                else:
                    severity = 0.5
                
                return DriftSignal(
                    drift_type="threshold_violation",
                    severity=severity,
                    metric=metric,
                    baseline_value=baseline,
                    current_value=value,
                    window_size=len(history),
                )
        
        # Check for statistical drift (3-sigma rule)
        if len(history) >= 10:
            mean = sum(history) / len(history)
            variance = sum((x - mean) ** 2 for x in history) / len(history)
            std = variance ** 0.5
            
            if std > 0 and abs(value - mean) > 3 * std:
                self._drift_count += 1
                severity = min(1.0, abs(value - mean) / (3 * std) - 1)
                
                return DriftSignal(
                    drift_type="statistical_outlier",
                    severity=severity,
                    metric=metric,
                    baseline_value=mean,
                    current_value=value,
                    window_size=len(history),
                )
        
        return None
    
    def get_baseline(self, metric: str) -> float | None:
        """Get current baseline for metric."""
        history = self._metric_history.get(metric)
        if not history:
            return None
        return sum(history) / len(history)
    
    def get_stats(self) -> dict[str, Any]:
        """Get drift detector statistics."""
        return {
            "drift_count": self._drift_count,
            "metrics_tracked": len(self._metric_history),
            "window_size": self._window_size,
        }
