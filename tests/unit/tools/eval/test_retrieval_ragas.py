"""Tests for retrieval RAGAS-shaped metrics — ADR-061 §3."""

from __future__ import annotations

import math

import pytest

from tools.eval.retrieval_ragas import (
    RetrievalCase,
    aggregate,
    context_precision,
    context_recall,
    mrr_at_k,
    ndcg_at_k,
    recall_at_k,
)


def _case(retrieved: list[str], expected: list[str] = None) -> RetrievalCase:  # type: ignore[assignment]
    return RetrievalCase(
        query_id="q",
        expected_chunks=tuple(expected or ["gold"]),
        retrieved_chunks=tuple(retrieved),
    )


# ---------------------------------------------------------------------------
# recall_at_k
# ---------------------------------------------------------------------------


def test_recall_hit_at_top() -> None:
    assert recall_at_k(_case(["gold", "x", "y"]), k=5) == 1.0


def test_recall_hit_at_k_minus_one() -> None:
    # Position 4 (1-indexed) inside K=5.
    assert recall_at_k(_case(["a", "b", "c", "d", "gold"]), k=5) == 1.0


def test_recall_miss_just_outside_k() -> None:
    assert recall_at_k(_case(["a", "b", "c", "d", "e", "gold"]), k=5) == 0.0


def test_recall_no_retrieved() -> None:
    assert recall_at_k(_case([]), k=5) == 0.0


def test_recall_invalid_k() -> None:
    with pytest.raises(ValueError, match="k must be"):
        recall_at_k(_case(["gold"]), k=0)


# ---------------------------------------------------------------------------
# mrr_at_k
# ---------------------------------------------------------------------------


def test_mrr_rank_1() -> None:
    assert mrr_at_k(_case(["gold", "x"]), k=10) == 1.0


def test_mrr_rank_3() -> None:
    assert mrr_at_k(_case(["a", "b", "gold", "c"]), k=10) == pytest.approx(1 / 3)


def test_mrr_no_hit_in_topk() -> None:
    assert mrr_at_k(_case(["a", "b"]), k=10) == 0.0


def test_mrr_first_of_multiple_hits_wins() -> None:
    case = _case(["a", "gold", "b", "gold"], expected=["gold"])
    assert mrr_at_k(case, k=10) == 0.5


# ---------------------------------------------------------------------------
# ndcg_at_k
# ---------------------------------------------------------------------------


def test_ndcg_perfect_at_rank_1() -> None:
    assert ndcg_at_k(_case(["gold", "x"]), k=10) == pytest.approx(1.0)


def test_ndcg_strictly_less_for_lower_rank() -> None:
    high = ndcg_at_k(_case(["gold", "x", "y"]), k=10)
    low = ndcg_at_k(_case(["x", "y", "gold"]), k=10)
    assert high > low > 0


def test_ndcg_no_relevant_returns_zero() -> None:
    assert ndcg_at_k(_case(["a", "b"]), k=5) == 0.0


def test_ndcg_two_relevant_at_top() -> None:
    case = _case(["a", "b"], expected=["a", "b"])
    out = ndcg_at_k(case, k=10)
    # Both ideal; expect 1.0.
    assert out == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# context_precision / context_recall
# ---------------------------------------------------------------------------


def test_context_precision_hits_over_topk() -> None:
    case = _case(["gold", "x", "gold", "y"], expected=["gold"])
    # 2 hits / 4 chunks = 0.5
    assert context_precision(case, k=4) == 0.5


def test_context_precision_zero_when_no_retrieved() -> None:
    assert context_precision(_case([]), k=10) == 0.0


def test_context_recall_full() -> None:
    case = _case(["a", "b", "c"], expected=["a", "b"])
    assert context_recall(case, k=3) == 1.0


def test_context_recall_partial() -> None:
    case = _case(["a", "x"], expected=["a", "b"])
    assert context_recall(case, k=2) == 0.5


def test_context_recall_zero() -> None:
    case = _case(["x", "y"], expected=["a", "b"])
    assert context_recall(case, k=2) == 0.0


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------


def test_aggregate_empty() -> None:
    out = aggregate([])
    assert out.n_cases == 0
    assert out.recall_at_5 == 0.0
    assert out.mrr_at_10 == 0.0


def test_aggregate_single_perfect() -> None:
    cases = [_case(["gold"], expected=["gold"])]
    out = aggregate(cases)
    assert out.n_cases == 1
    assert out.recall_at_5 == 1.0
    assert out.mrr_at_10 == 1.0
    assert out.ndcg_at_10 == pytest.approx(1.0)


def test_aggregate_mixed() -> None:
    cases = [
        _case(["gold", "x"], expected=["gold"]),
        _case(["x", "y", "z"], expected=["gold"]),  # miss
    ]
    out = aggregate(cases)
    assert out.recall_at_5 == 0.5
    assert math.isclose(out.mrr_at_10, 0.5)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_empty_expected_chunks_rejected() -> None:
    with pytest.raises(ValueError, match="expected_chunks must be non-empty"):
        RetrievalCase(query_id="q", expected_chunks=(), retrieved_chunks=())


def test_empty_query_id_rejected() -> None:
    with pytest.raises(ValueError, match="query_id must be non-empty"):
        RetrievalCase(query_id="", expected_chunks=("gold",), retrieved_chunks=())
