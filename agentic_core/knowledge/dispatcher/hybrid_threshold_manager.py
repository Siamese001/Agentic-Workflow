"""Hybrid Threshold Manager.

Dynamic threshold adjustment for hybrid retrieval with performance-based
optimization and policy-driven decision boundaries.
"""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class ThresholdConfig:
    """Threshold configuration for hybrid retrieval."""
    vector_weight: float = 0.5
    sparse_weight: float = 0.5
    vector_threshold: float = 0.7
    sparse_threshold: float = 0.3
    fusion_method: str = "rrf"  # reciprocal rank fusion


class HybridThresholdManager:
    """Manages dynamic thresholds for hybrid retrieval.

    The HybridThresholdManager adjusts thresholds based on performance
    metrics and enforces policy-driven decision boundaries.
    """

    def __init__(
        self,
        history_size: int = 100,
        adjustment_rate: float = 0.1,
    ):
        """Initialize the hybrid threshold manager.

        Args:
            history_size: Size of performance history window
            adjustment_rate: Rate of threshold adjustment (0-1)
        """
        self.history_size = history_size
        self.adjustment_rate = adjustment_rate

        # Performance history
        self._precision_history: deque = deque(maxlen=history_size)
        self._recall_history: deque = deque(maxlen=history_size)
        self._latency_history: deque = deque(maxlen=history_size)

        # Current thresholds
        self._config = ThresholdConfig()

        log.info("HybridThresholdManager initialized")

    def get_thresholds(
        self,
        query_context: dict[str, Any] | None = None,
    ) -> ThresholdConfig:
        """Get current thresholds, optionally adjusted for context.

        Args:
            query_context: Optional query context for adjustment

        Returns:
            ThresholdConfig with current thresholds
        """
        trace_id = f"thresholds_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "HybridThresholdManager.get_thresholds"
        )

        # Start with base config
        config = ThresholdConfig(
            vector_weight=self._config.vector_weight,
            sparse_weight=self._config.sparse_weight,
            vector_threshold=self._config.vector_threshold,
            sparse_threshold=self._config.sparse_threshold,
            fusion_method=self._config.fusion_method,
        )

        # Adjust based on query context
        if query_context:
            config = self._adjust_for_context(config, query_context)

        return config

    def update_performance(
        self,
        precision: float,
        recall: float,
        latency_ms: float,
    ) -> None:
        """Update performance metrics and adjust thresholds.

        Args:
            precision: Precision metric (0-1)
            recall: Recall metric (0-1)
            latency_ms: Latency in milliseconds
        """
        self._precision_history.append(precision)
        self._recall_history.append(recall)
        self._latency_history.append(latency_ms)

        # Adjust thresholds based on history
        self._auto_adjust()

    def set_thresholds(self, config: ThresholdConfig) -> None:
        """Manually set threshold configuration.

        Args:
            config: New threshold configuration
        """
        self._config = config
        log.info(f"Thresholds updated: vector={config.vector_weight}, sparse={config.sparse_weight}")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary statistics.

        Returns:
            Dictionary with performance metrics
        """
        if not self._precision_history:
            return {"status": "no_data"}

        return {
            "avg_precision": sum(self._precision_history) / len(self._precision_history),
            "avg_recall": sum(self._recall_history) / len(self._recall_history),
            "avg_latency_ms": sum(self._latency_history) / len(self._latency_history),
            "samples": len(self._precision_history),
        }

    def _adjust_for_context(
        self,
        config: ThresholdConfig,
        context: dict[str, Any],
    ) -> ThresholdConfig:
        """Adjust thresholds based on query context."""
        intent = context.get("intent")
        urgency = context.get("urgency", 0)

        # For urgent queries, lower thresholds to get more results
        if urgency > 0.7:
            config.vector_threshold *= 0.8
            config.sparse_threshold *= 0.8

        # For code queries, weight sparse more (exact matches matter)
        if intent == "code":
            config.vector_weight = 0.3
            config.sparse_weight = 0.7

        # For analytical queries, weight vector more (semantic similarity)
        if intent == "analytical":
            config.vector_weight = 0.7
            config.sparse_weight = 0.3

        return config

    def _auto_adjust(self) -> None:
        """Auto-adjust thresholds based on performance history."""
        if len(self._precision_history) < 10:
            return  # Not enough data

        avg_precision = sum(self._precision_history) / len(self._precision_history)
        avg_recall = sum(self._recall_history) / len(self._recall_history)

        # If precision is low, increase thresholds
        if avg_precision < 0.6:
            self._config.vector_threshold = min(
                0.9,
                self._config.vector_threshold * (1 + self.adjustment_rate)
            )

        # If recall is low, decrease thresholds
        if avg_recall < 0.6:
            self._config.vector_threshold = max(
                0.5,
                self._config.vector_threshold * (1 - self.adjustment_rate)
            )


# Global instance
_global_manager: HybridThresholdManager | None = None


def get_hybrid_threshold_manager() -> HybridThresholdManager:
    """Get or create the global hybrid threshold manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = HybridThresholdManager()
    return _global_manager


def get_hybrid_thresholds(context: dict[str, Any] | None = None) -> ThresholdConfig:
    """Convenience function to get thresholds."""
    return get_hybrid_threshold_manager().get_thresholds(context)
