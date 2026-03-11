"""
Mean Reciprocal Rank (MRR) Metric

MRR = 1 / rank_of_first_relevant_doc
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

class MeanReciprocalRank(RetrievalMetric):
    """MRR measures the rank position of the first relevant document."""

    @property
    def name(self) -> str:
        return "MRR"

    def compute(
        self,
        prediction: list[str],
        ground_truth: list[str],
        context: Any = None,
    ) -> float:
        """Compute MRR for a single query.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs
            context: Unused

        Returns:
            Reciprocal rank of first relevant doc, 0.0 if none found
        """
        if not prediction:
            return 0.0
        if not ground_truth:
            return 0.0

        relevant_set = set(ground_truth)
        for rank, doc_id in enumerate(prediction, start=1):
            if doc_id in relevant_set:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def mean(scores: list[float]) -> float:
        """Compute mean MRR across multiple queries.

        Args:
            scores: Per-query MRR scores

        Returns:
            Mean reciprocal rank
        """
        if not scores:
            return 0.0
        return sum(scores) / len(scores)


__all__ = ["MeanReciprocalRank"]
