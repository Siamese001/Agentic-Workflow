"""Tests for the reflective-retrieval loop — ADR-060 §1."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.retrieval_grader import (
    Chunk,
    RetrievalGrader,
)
from agentic_core.L1_cognition.reasoning.retrieval_reflexion import (
    ReflectiveLoopConfig,
    run_reflective_retrieval,
)
from agentic_core.L6_observability.semconv import rag as semconv
from agentic_core.runtime.types.reflection_types import ReflectionNextAction


def _grader() -> RetrievalGrader:
    return RetrievalGrader(gateway=None)


# ---------------------------------------------------------------------------
# Convergence
# ---------------------------------------------------------------------------


def test_converges_when_first_pass_relevant() -> None:
    target_text = "reranker factory selects backend per env var"

    def retriever(q: str) -> list[Chunk]:
        return [
            Chunk("c1", target_text),
            Chunk("c2", target_text),
            Chunk("c3", target_text),
        ]

    result = run_reflective_retrieval(
        query="reranker factory backend",
        retriever=retriever,
        grader=_grader(),
        config=ReflectiveLoopConfig(max_iters=3, relevant_k_min=2),
    )
    assert result.outcome == semconv.OUTCOME_CONVERGED
    assert result.iterations == 1
    assert result.evidence_quality == semconv.EVIDENCE_STRONG


def test_abstains_when_consecutive_irrelevant() -> None:
    def retriever(_q: str) -> list[Chunk]:
        return [Chunk("c1", "completely unrelated bread recipe")]

    result = run_reflective_retrieval(
        query="reranker factory backend",
        retriever=retriever,
        grader=_grader(),
        config=ReflectiveLoopConfig(max_iters=4, consecutive_irrelevant_to_abort=2),
    )
    assert result.outcome == semconv.OUTCOME_ABSTAINED
    assert result.evidence_quality == semconv.EVIDENCE_NONE
    assert result.iterations >= 2


def test_caps_at_max_iters() -> None:
    # Always-ambiguous: never converges, never two-in-a-row irrelevant,
    # so the loop must hit the iter cap.
    def retriever(_q: str) -> list[Chunk]:
        return [Chunk("c1", "factory pattern software design")]

    result = run_reflective_retrieval(
        query="reranker factory backend selection",
        retriever=retriever,
        grader=_grader(),
        config=ReflectiveLoopConfig(max_iters=2, consecutive_irrelevant_to_abort=99),
    )
    assert result.iterations == 2
    assert result.outcome in {semconv.OUTCOME_CAP, semconv.OUTCOME_BUDGET_EXCEEDED}


# ---------------------------------------------------------------------------
# Errors and budgets
# ---------------------------------------------------------------------------


def test_retriever_error_aborts_with_outcome_error() -> None:
    def retriever(_q: str) -> list[Chunk]:
        raise RuntimeError("chroma down")

    result = run_reflective_retrieval(
        query="anything",
        retriever=retriever,
        grader=_grader(),
    )
    assert result.outcome == semconv.OUTCOME_ERROR
    assert result.iterations == 1


def test_total_budget_exceeded_stops_loop() -> None:
    import time

    def retriever(_q: str) -> list[Chunk]:
        time.sleep(0.05)
        return [Chunk("c1", "unrelated")]

    result = run_reflective_retrieval(
        query="x",
        retriever=retriever,
        grader=_grader(),
        config=ReflectiveLoopConfig(
            max_iters=10,
            iter_budget_ms=10_000,
            total_budget_ms=20,
            consecutive_irrelevant_to_abort=99,
        ),
    )
    assert result.outcome == semconv.OUTCOME_BUDGET_EXCEEDED


def test_empty_query_rejected() -> None:
    with pytest.raises(ValueError, match="query must be non-empty"):
        run_reflective_retrieval(
            query="",
            retriever=lambda _q: [],
            grader=_grader(),
        )


# ---------------------------------------------------------------------------
# Layer-gravity guard
# ---------------------------------------------------------------------------


def test_expander_returning_l3_action_raises() -> None:
    def bad_expander(q: str, _v: list) -> tuple[str, ReflectionNextAction]:
        return q, ReflectionNextAction.REPLAN  # L3-only

    def retriever(_q: str) -> list[Chunk]:
        return [Chunk("c1", "factory pattern")]

    with pytest.raises(RuntimeError, match="non-L1 action"):
        run_reflective_retrieval(
            query="reranker factory backend selection",
            retriever=retriever,
            grader=_grader(),
            expander=bad_expander,
            config=ReflectiveLoopConfig(consecutive_irrelevant_to_abort=99),
        )


# ---------------------------------------------------------------------------
# Trace shape
# ---------------------------------------------------------------------------


def test_traces_record_iteration_and_dist() -> None:
    def retriever(_q: str) -> list[Chunk]:
        return [Chunk("c1", "reranker factory backend")]

    result = run_reflective_retrieval(
        query="reranker factory backend",
        retriever=retriever,
        grader=_grader(),
        config=ReflectiveLoopConfig(relevant_k_min=1),
    )
    assert len(result.traces) == result.iterations
    assert result.traces[0].iteration == 0
    assert "verdict_dist" in result.traces[0].extras
