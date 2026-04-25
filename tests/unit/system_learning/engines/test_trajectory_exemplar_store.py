"""Unit tests for :mod:`system_learning.engines.trajectory_exemplar_store` and the consult adapter."""

from __future__ import annotations

import pytest

from system_learning.adapters.exemplar_consult_adapter import (
    consult,
    reset_default_store,
    seed_exemplars,
)
from system_learning.engines.trajectory_exemplar_store import (
    TrajectoryExemplar,
    TrajectoryExemplarStore,
)


@pytest.fixture(autouse=True)
def _reset_store():
    reset_default_store()
    yield
    reset_default_store()


def _ex(
    exemplar_id: str,
    query_text: str = "find stale dependencies in python package",
    score: float = 0.9,
    cost_tokens: int = 1000,
    tags: tuple[str, ...] = (),
) -> TrajectoryExemplar:
    return TrajectoryExemplar(
        exemplar_id=exemplar_id,
        query_text=query_text,
        trajectory={"steps": []},
        score=score,
        cost_tokens=cost_tokens,
        tags=frozenset(tags),
    )


def test_add_below_min_score_rejected() -> None:
    store = TrajectoryExemplarStore(min_score=0.8)
    assert store.add(_ex("low", score=0.5)) is False
    assert store.size == 0


def test_add_and_consult_exact_match() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    store.add(_ex("e1", query_text="refactor module X"))
    hits = store.consult("refactor module X", k=3)
    assert len(hits) == 1
    assert hits[0].exemplar.exemplar_id == "e1"
    assert hits[0].reason == "exact_shape_match"


def test_consult_ranks_by_score_then_cost() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    store.add(_ex("cheap_low", query_text="q", score=0.8, cost_tokens=500))
    store.add(_ex("expensive_high", query_text="q", score=0.95, cost_tokens=5000))
    store.add(_ex("cheap_high", query_text="q", score=0.95, cost_tokens=500))
    hits = store.consult("q", k=3)
    assert [h.exemplar.exemplar_id for h in hits] == [
        "cheap_high",  # highest score, lowest cost among top-score
        "expensive_high",  # same score, higher cost
        "cheap_low",  # lower score
    ]


def test_consult_fuzzy_token_subset() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    # stored query is a subset of the consult query's tokens.
    store.add(_ex("e1", query_text="list files"))
    hits = store.consult("please list files in the repository", k=3)
    assert len(hits) == 1
    assert hits[0].reason == "token_subset_match"


def test_consult_respects_required_tags() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    store.add(_ex("tagged", query_text="q", tags=("prod",)))
    store.add(_ex("untagged", query_text="q"))
    hits = store.consult("q", k=5, required_tags=["prod"])
    assert [h.exemplar.exemplar_id for h in hits] == ["tagged"]


def test_demote_below_min_score_evicts() -> None:
    store = TrajectoryExemplarStore(min_score=0.8)
    store.add(_ex("e1", score=0.95))
    assert store.size == 1
    store.demote("e1", 0.5)
    assert store.size == 0


def test_bulk_add_returns_count() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    added = store.bulk_add([_ex("e1"), _ex("e2", score=0.1), _ex("e3")])
    # e2 below min_score.
    assert added == 2
    assert store.size == 2


def test_max_entries_evicts_lowest() -> None:
    store = TrajectoryExemplarStore(min_score=0.5, max_entries=2)
    store.add(_ex("low", score=0.6))
    store.add(_ex("mid", score=0.7))
    store.add(_ex("high", score=0.9))  # should evict 'low'
    assert store.size == 2
    ids = {e.exemplar_id for e in store._by_id.values()}  # noqa: SLF001
    assert ids == {"mid", "high"}


def test_adapter_consult_empty_store_returns_empty() -> None:
    hits = consult("anything", k=3)
    assert hits == []


def test_adapter_seed_and_consult_roundtrip() -> None:
    n = seed_exemplars(
        [
            {
                "exemplar_id": "a1",
                "query_text": "plan a wave",
                "trajectory": {"foo": "bar"},
                "score": 0.91,
                "cost_tokens": 800,
                "tags": ["plan"],
            }
        ]
    )
    assert n == 1
    hits = consult("plan a wave")
    assert len(hits) == 1
    assert hits[0].exemplar.trajectory == {"foo": "bar"}
