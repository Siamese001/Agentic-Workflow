"""
Precision@K Metric

precision@k = relevant_docs_in_top_k / k
"""

from __future__ import annotations

from typing import Any

from .base import RetrievalMetric


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class PrecisionAtK(RetrievalMetric):
    """Measures what fraction of the top-k retrieved documents are relevant."""

    def __init__(self, k: int = 5):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    @property
    def name(self) -> str:
        return f"precision@{self.k}"

    def compute(
        self,
        prediction: list[str],
        ground_truth: list[str],
        context: Any = None,
    ) -> float:
        """Compute precision@k.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs
            context: Unused

        Returns:
            Fraction of top-k retrieved docs that are relevant, in [0, 1]
        """
        if not prediction:
            return 0.0
        if not ground_truth:
            return 0.0

        relevant_set = set(ground_truth)
        top_k = prediction[: self.k]
        relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_set)
        return relevant_in_top_k / self.k


__all__ = ["PrecisionAtK"]
