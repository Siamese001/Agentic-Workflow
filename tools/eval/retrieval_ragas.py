"""Pure-stdlib RAGAS-shaped retrieval metrics.

Implements the three numeric metrics declared in ADR-061 §3 that do NOT need
an LLM judge:

    * recall_at_k       — fraction of queries whose ground-truth chunk is in
                          the top-K retrieved.
    * mrr_at_k          — mean reciprocal rank of the first ground-truth hit.
    * ndcg_at_k         — normalized discounted cumulative gain.
    * context_precision — signal-to-noise of the retrieved set (binary
                          relevance proxy).
    * context_recall    — fraction of ground-truth chunks present in the
                          retrieved set.

The two LLM-graded metrics from RAGAS proper (faithfulness, answer_relevancy)
require a generation step; they are gated behind ``RAGAS_FULL=1`` per ADR-061
§5 and live in ``retrieval_ragas_llm.py`` (not implemented here — landing
together with the cron in W5.2).

All inputs are plain Python; no numpy required. Outputs are deterministic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalCase:
    """One golden-set case — query, expected chunk ids, retrieved chunk ids."""

    query_id: str
    expected_chunks: tuple[str, ...]
    retrieved_chunks: tuple[str, ...]
    """Ranked top-K, position 0 is highest-ranked."""

    def __post_init__(self) -> None:
        if not self.query_id:
            raise ValueError("query_id must be non-empty")
        if not self.expected_chunks:
            raise ValueError(f"{self.query_id}: expected_chunks must be non-empty")


def recall_at_k(case: RetrievalCase, k: int) -> float:
    """Returns 1.0 iff any expected chunk appears in the top-K, else 0.0.

    Industry-standard "hit-rate@K". Strict: an expected chunk at rank K-1
    counts; rank K does not.
    """

    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    top_k = set(case.retrieved_chunks[:k])
    return 1.0 if any(c in top_k for c in case.expected_chunks) else 0.0


def mrr_at_k(case: RetrievalCase, k: int) -> float:
    """Mean reciprocal rank of the first expected hit within top-K.

    Returns ``1/r`` where ``r`` is the 1-indexed rank of the first hit,
    or 0.0 if no hit. Bounded to k.
    """

    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    expected = set(case.expected_chunks)
    for rank, cid in enumerate(case.retrieved_chunks[:k], start=1):
        if cid in expected:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(case: RetrievalCase, k: int) -> float:
    """Normalized DCG@K with binary relevance.

    ``dcg = sum(rel_i / log2(i+1))`` for i=1..K.
    ``idcg = sum(1 / log2(i+1))`` for i=1..min(K, |expected|).
    Returns dcg/idcg, or 0.0 when no relevant docs are retrieved.
    """

    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    expected = set(case.expected_chunks)
    dcg = 0.0
    for rank, cid in enumerate(case.retrieved_chunks[:k], start=1):
        if cid in expected:
            dcg += 1.0 / math.log2(rank + 1)
    ideal_hits = min(k, len(expected))
    if ideal_hits == 0:
        return 0.0
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0


def context_precision(case: RetrievalCase, k: int) -> float:
    """Fraction of top-K chunks that are relevant (binary).

    Equivalent to precision@K with the expected set as ground truth.
    """

    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    expected = set(case.expected_chunks)
    top_k = case.retrieved_chunks[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for cid in top_k if cid in expected)
    return hits / len(top_k)


def context_recall(case: RetrievalCase, k: int) -> float:
    """Fraction of expected chunks present in the top-K retrieved set.

    Differs from ``recall_at_k`` (which is binary hit/miss) by averaging
    over all expected chunks.
    """

    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    expected = set(case.expected_chunks)
    if not expected:
        return 0.0
    top_k = set(case.retrieved_chunks[:k])
    hits = sum(1 for c in expected if c in top_k)
    return hits / len(expected)


@dataclass(frozen=True)
class AggregateMetrics:
    """Mean metrics over a batch of retrieval cases."""

    n_cases: int
    recall_at_5: float
    recall_at_10: float
    recall_at_20: float
    mrr_at_10: float
    ndcg_at_10: float
    context_precision_at_20: float
    context_recall_at_20: float


def aggregate(cases: list[RetrievalCase]) -> AggregateMetrics:
    """Compute mean metrics across a batch of cases.

    Returns zero-valued metrics on an empty batch rather than raising — the
    nightly harness must be safely callable on an empty fixture.
    """

    n = len(cases)
    if n == 0:
        return AggregateMetrics(
            n_cases=0,
            recall_at_5=0.0,
            recall_at_10=0.0,
            recall_at_20=0.0,
            mrr_at_10=0.0,
            ndcg_at_10=0.0,
            context_precision_at_20=0.0,
            context_recall_at_20=0.0,
        )

    return AggregateMetrics(
        n_cases=n,
        recall_at_5=sum(recall_at_k(c, 5) for c in cases) / n,
        recall_at_10=sum(recall_at_k(c, 10) for c in cases) / n,
        recall_at_20=sum(recall_at_k(c, 20) for c in cases) / n,
        mrr_at_10=sum(mrr_at_k(c, 10) for c in cases) / n,
        ndcg_at_10=sum(ndcg_at_k(c, 10) for c in cases) / n,
        context_precision_at_20=sum(context_precision(c, 20) for c in cases) / n,
        context_recall_at_20=sum(context_recall(c, 20) for c in cases) / n,
    )


__all__ = [
    "AggregateMetrics",
    "RetrievalCase",
    "aggregate",
    "context_precision",
    "context_recall",
    "mrr_at_k",
    "ndcg_at_k",
    "recall_at_k",
]
