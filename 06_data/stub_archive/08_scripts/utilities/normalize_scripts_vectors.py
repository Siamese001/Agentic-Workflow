"""
normalize_scripts_vectors.py - Adjustment Module

Domain: utilities
Generated: 2025-12-07T12:07:54.867990
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AdjustmentResult:
    """Result of adjustment."""
    original: Any
    adjusted: Any
    method: str


class NormalizeScriptsVectors:
    """Adjuster for utilities domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.method = self.config.get("method", "minmax")
        self.target_range = self.config.get("range", (0.0, 1.0))
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def adjust(self, values: Sequence[float], method: Optional[str] = None) -> List[AdjustmentResult]:
        """Adjust values."""
        adj_method = method or self.method
        adjusted = self._apply_adjustment(list(values), adj_method)
        return [AdjustmentResult(original=o, adjusted=a, method=adj_method) for o, a in zip(values, adjusted)]
    
    def _apply_adjustment(self, values: List[float], method: str) -> List[float]:
        """Apply adjustment method."""
        if not values:
            return []
        if method == "minmax":
            return self._minmax(values)
        elif method == "zscore":
            return self._zscore(values)
        return values
    
    def _minmax(self, values: List[float]) -> List[float]:
        """Min-max normalization."""
        min_v, max_v = min(values), max(values)
        if max_v == min_v:
            return [0.5] * len(values)
        t_min, t_max = self.target_range
        return [t_min + (v - min_v) / (max_v - min_v) * (t_max - t_min) for v in values]
    
    def _zscore(self, values: List[float]) -> List[float]:
        """Z-score normalization."""
        import math
        mean = sum(values) / len(values)
        std = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        return [(v - mean) / std if std > 0 else 0.0 for v in values]


def adjust(values: Sequence[float], method: str = "minmax", config: Optional[Dict] = None) -> List[AdjustmentResult]:
    """Convenience function for adjustment."""
    return NormalizeScriptsVectors(config).adjust(values, method)
