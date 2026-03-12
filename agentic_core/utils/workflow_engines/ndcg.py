"""
Normalized Discounted Cumulative Gain (NDCG) Metric

NDCG measures ranking quality by giving higher weight to relevant
documents appearing at the top of the ranked list.
"""
from __future__ import annotations
import math
from .base import RetrievalMetric
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class NDCG(RetrievalMetric):
    """Normalized Discounted Cumulative Gain at cutoff k."""

    def __init__(self, k: int=10):
        if k <= 0:
            raise ValueError(f'k must be positive, got {k}')
        self.k = k

    @property
    def name(self) -> str:
        return f'NDCG@{self.k}'

    def _dcg(self, ranked_docs: list[str], relevance: dict[str, float]) -> float:
        """Compute Discounted Cumulative Gain."""
        dcg = 0.0
        for rank, doc_id in enumerate(ranked_docs[:self.k], start=1):
            rel = relevance.get(doc_id, 0.0)
            dcg += rel / math.log2(rank + 1)
        return dcg

    def _ideal_dcg(self, relevance: dict[str, float]) -> float:
        """Compute ideal DCG (best possible ranking)."""
        sorted_rels = sorted(relevance.values(), reverse=True)
        idcg = 0.0
        for rank, rel in enumerate(sorted_rels[:self.k], start=1):
            idcg += rel / math.log2(rank + 1)
        return idcg

    def compute(self, prediction: list[str], ground_truth: list[str], context: dict[str, float] | None=None) -> float:
        """Compute NDCG@k.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs (binary relevance = 1.0)
            context: Optional dict mapping doc_id -> graded relevance score.
                     If None, binary relevance (1.0 for any doc in ground_truth).

        Returns:
            NDCG score in [0, 1]
        """
        if not prediction:
            return 0.0
        if context is not None:
            relevance = context
        else:
            if not ground_truth:
                return 0.0
            relevance = dict.fromkeys(ground_truth, 1.0)
        idcg = self._ideal_dcg(relevance)
        if idcg == 0.0:
            return 0.0
        dcg = self._dcg(prediction, relevance)
        return dcg / idcg
__all__ = ['NDCG']
