"""Deterministic retrieval metrics."""

from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

from apps_rg.evals.resume_graph.models import EvaluationDataError


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise EvaluationDataError("cannot calculate a mean from no observations")
    return sum(values) / len(values)


def recall_at_k(
    ranked_ids: Sequence[str],
    relevance: Mapping[str, float],
    k: int,
    *,
    positive_floor: float = 1.0,
) -> float:
    """Calculate Recall@K using all labelled relevant candidates as recall base."""

    if k <= 0:
        raise EvaluationDataError("k must be positive")
    relevant = {candidate_id for candidate_id, score in relevance.items() if score >= positive_floor}
    if not relevant:
        raise EvaluationDataError("Recall@K is undefined without a relevant candidate")
    return len(relevant.intersection(ranked_ids[:k])) / len(relevant)


def ndcg_at_k(
    ranked_ids: Sequence[str],
    relevance: Mapping[str, float],
    k: int,
    *,
    ranks: Sequence[int] | None = None,
) -> float:
    """Calculate nDCG@K with exponential gain and true explicit-rank discount."""

    if k <= 0:
        raise EvaluationDataError("k must be positive")

    explicit_ranks = tuple(ranks) if ranks is not None else tuple(range(1, len(ranked_ids) + 1))
    if len(explicit_ranks) != len(ranked_ids) or any(
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0 for rank in explicit_ranks
    ):
        raise EvaluationDataError("explicit ranks must be positive integers aligned to candidates")

    def discounted_gain(scores: Iterable[tuple[int, float]]) -> float:
        return sum((2.0 ** float(score) - 1.0) / math.log2(rank + 1.0) for rank, score in scores)

    actual = [
        (rank, float(relevance.get(candidate_id, 0.0)))
        for candidate_id, rank in zip(ranked_ids, explicit_ranks)
        if rank <= k
    ]
    ideal = enumerate(
        sorted((float(score) for score in relevance.values()), reverse=True)[:k],
        1,
    )
    ideal_gain = discounted_gain(ideal)
    if ideal_gain <= 0.0:
        raise EvaluationDataError("nDCG@K is undefined without positive relevance gain")
    return discounted_gain(actual) / ideal_gain


def reciprocal_rank(
    ranked_ids: Sequence[str],
    relevance: Mapping[str, float],
    *,
    positive_floor: float = 1.0,
    ranks: Sequence[int] | None = None,
) -> float:
    """Calculate reciprocal rank of the first labelled relevant candidate."""

    explicit_ranks = tuple(ranks) if ranks is not None else tuple(range(1, len(ranked_ids) + 1))
    if len(explicit_ranks) != len(ranked_ids) or any(
        not isinstance(rank, int) or isinstance(rank, bool) or rank <= 0 for rank in explicit_ranks
    ):
        raise EvaluationDataError("explicit ranks must be positive integers aligned to candidates")
    for rank, candidate_id in zip(explicit_ranks, ranked_ids):
        if float(relevance.get(candidate_id, 0.0)) >= positive_floor:
            return 1.0 / rank
    return 0.0
