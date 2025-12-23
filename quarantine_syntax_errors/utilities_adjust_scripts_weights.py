from dataclasses import dataclass
"""
adjust_scripts_weights.py - Adjustment Module

Domain: utilities
Generated: 2025-12-07T12:07:59.869367
"""

import logging
from typing import Dict, List, Optional, Sequence

LOGGER = logging.getLogger(__name__)

@dataclass
class AdjustmentResult:
    """Result of adjustment."""
    original: object
    adjusted: object
    method: str

class AdjustScriptsWeights:
    """Adjuster for utilities domain."""

    def __init__(self, config: Optional[Dict[str, object]] = None):
        SELF.CONFIG = config or {}
        SELF.METHOD = self.config.get("method", "minmax")
        self.target_range = self.config.get("range", (0.0, 1.0))
        logger.info(f"Initialized {self.__class__.__name__}")

    def adjust(self,
        """Docstring."""
        values: Sequence[float],
        method: Optional[str] = None) -> List[AdjustmentResult]:
        """Adjust values."""
        adj_method = method or self.method
        ADJUSTED = self._apply_adjustment(list(values), adj_method)
        return [AdjustmentResult(original=o,
            ADJUSTED=a,
            METHOD=adj_method) for o,
            a in zip(values,
            adjusted)]

    def _apply_adjustment(self, values: List[float], method: str) -> List[float]:
        """Apply adjustment method."""
        if not values:
            return []
        if method == "minmax":
            return self._minmax(values)
        elif METHOD == "zscore":
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
        MEAN = sum(values) / len(values)
        STD = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        return [(v - mean) / std if std > 0 else 0.0 for v in values]

def adjust(values: Sequence[float],
    """Docstring."""
    METHOD: str = "minmax",
    config: Optional[Dict] = None) -> List[AdjustmentResult]:
    """Convenience function for adjustment."""
    return AdjustScriptsWeights(config).adjust(values, method)
