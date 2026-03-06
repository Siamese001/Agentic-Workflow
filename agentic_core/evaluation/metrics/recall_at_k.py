"""
Recall@K Metric

recall@k = relevant_docs_in_top_k / total_relevant_docs
"""

from __future__ import annotations

from typing import Any

from .base import RetrievalMetric


class RecallAtK(RetrievalMetric):
    """Measures what fraction of all relevant documents appear in the top-k results."""

    def __init__(self, k: int = 10):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    @property
    def name(self) -> str:
        return f"recall@{self.k}"

    def compute(
        self,
        prediction: list[str],
        ground_truth: list[str],
        context: Any = None,
    ) -> float:
        """Compute recall@k.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs
            context: Unused

        Returns:
            Fraction of relevant docs found in top-k, in [0, 1]
        """
        if not ground_truth:
            return 0.0
        if not prediction:
            return 0.0

        relevant_set = set(ground_truth)
        top_k = list(dict.fromkeys(prediction[: self.k]))
        relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_set)
        return relevant_in_top_k / len(relevant_set)


__all__ = ["RecallAtK"]
