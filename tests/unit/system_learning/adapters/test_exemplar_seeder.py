"""Unit tests for :mod:`system_learning.adapters.exemplar_seeder`."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.exemplar_consult_adapter import reset_default_store
from agentic_core.L6_system_learning.exemplar_seeder import seed_from_cases
from agentic_core.L6_system_learning.trajectory_exemplar_store import TrajectoryExemplarStore


@pytest.fixture(autouse=True)
def _reset():
    reset_default_store()
    yield
    reset_default_store()


def _case(**overrides):
    base = {
        "exemplar_id": "e1",
        "query_text": "find stale deps",
        "trajectory": {"steps": []},
        "score": 0.9,
        "cost_tokens": 500,
        "tags": ["prod"],
    }
    base.update(overrides)
    return base


def test_seed_adds_valid_case() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    result = seed_from_cases([_case()], store=store)
    assert result.added == 1
    assert result.considered == 1
    assert store.size == 1


def test_seed_rejects_below_floor() -> None:
    store = TrajectoryExemplarStore(min_score=0.8)
    result = seed_from_cases([_case(score=0.5)], store=store)
    assert result.added == 0
    assert result.below_floor == 1


def test_seed_handles_duplicates() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    cases = [_case(), _case()]  # same id twice
    result = seed_from_cases(cases, store=store)
    assert result.added == 1
    assert result.duplicates == 1
    assert result.considered == 2


def test_seed_skips_malformed_records() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    bad = {"exemplar_id": "x"}  # missing required keys
    result = seed_from_cases([bad, _case()], store=store)
    assert result.malformed == 1
    assert result.added == 1


def test_seed_infers_cost_tokens_from_total_tokens() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    case = _case()
    del case["cost_tokens"]
    case["total_tokens"] = 1234
    seed_from_cases([case], store=store)
    # One entry; check via internal dict that cost_tokens was coerced.
    [exemplar] = list(store._by_id.values())  # noqa: SLF001
    assert exemplar.cost_tokens == 1234


def test_seed_accepts_string_tag() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    seed_from_cases([_case(tags="prod")], store=store)  # string, not iterable
    [exemplar] = list(store._by_id.values())  # noqa: SLF001
    assert exemplar.tags == frozenset({"prod"})


def test_seed_malformed_score_is_dropped() -> None:
    store = TrajectoryExemplarStore(min_score=0.5)
    result = seed_from_cases([_case(score="not-a-number")], store=store)
    assert result.malformed == 1


def test_seed_without_explicit_store_uses_default() -> None:
    # Default store path — empty by default via autouse fixture.
    result = seed_from_cases([_case()])
    assert result.added == 1
