"""Unit tests for ``agentic_core.L1_cognition.reasoning.retrieval_mode_bandit``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` W6.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.retrieval_mode_bandit import (
    KNOWN_RETRIEVAL_MODES,
    RetrievalModeBandit,
    adaptive_k_cutoff,
    citation_coverage,
)


def test_bandit_rejects_unknown_mode() -> None:
    b = RetrievalModeBandit(seed=0)
    with pytest.raises(ValueError):
        b.update("legal", "telepathy", success=True)


def test_bandit_converges_on_winning_mode() -> None:
    b = RetrievalModeBandit(seed=42)
    for _ in range(80):
        b.update("legal", "graph", success=True)
    for _ in range(20):
        b.update("legal", "graph", success=False)
    for _ in range(20):
        b.update("legal", "dense", success=True)
    for _ in range(80):
        b.update("legal", "dense", success=False)

    picks = [b.choose("legal", ["dense", "graph"]) for _ in range(200)]
    assert picks.count("graph") / len(picks) > 0.8


def test_bandit_choose_default_uses_full_vocabulary() -> None:
    b = RetrievalModeBandit(seed=0)
    chosen = b.choose("ns")
    assert chosen in KNOWN_RETRIEVAL_MODES


def test_bandit_choose_empty_admissible_raises() -> None:
    b = RetrievalModeBandit(seed=0)
    with pytest.raises(ValueError):
        b.choose("ns", [])


def test_adaptive_k_stops_at_first_big_drop() -> None:
    # 0.95, 0.94, 0.93, 0.50 (drop of 0.43 at index 3 → cut at k=3)
    scores = [0.95, 0.94, 0.93, 0.50, 0.48]
    assert adaptive_k_cutoff(scores, marginal_drop_threshold=0.04) == 3


def test_adaptive_k_no_drop_returns_ceiling() -> None:
    scores = [0.95, 0.94, 0.93, 0.92, 0.91]
    assert adaptive_k_cutoff(scores, max_k=5) == 5


def test_adaptive_k_respects_min_k() -> None:
    """A drop at k=1 must still return at least min_k."""
    scores = [0.95, 0.10, 0.09]
    assert adaptive_k_cutoff(scores, min_k=2, max_k=3, marginal_drop_threshold=0.04) == 2


def test_adaptive_k_respects_max_k() -> None:
    scores = [0.95, 0.94, 0.93, 0.92, 0.91, 0.90]
    assert adaptive_k_cutoff(scores, max_k=3) == 3


def test_adaptive_k_empty_scores_returns_zero() -> None:
    assert adaptive_k_cutoff([]) == 0


def test_adaptive_k_rejects_unsorted_input() -> None:
    with pytest.raises(ValueError):
        adaptive_k_cutoff([0.5, 0.9, 0.4])


def test_adaptive_k_invalid_min_max_raises() -> None:
    with pytest.raises(ValueError):
        adaptive_k_cutoff([0.5], min_k=0)
    with pytest.raises(ValueError):
        adaptive_k_cutoff([0.5], min_k=5, max_k=2)


def test_citation_coverage_empty_claims_zero() -> None:
    assert citation_coverage([], {}, set()) == 0.0


def test_citation_coverage_full_match() -> None:
    claims = ["c1", "c2", "c3"]
    anchors = {"c1": "chunk_a", "c2": "chunk_b", "c3": "chunk_c"}
    returned = {"chunk_a", "chunk_b", "chunk_c"}
    assert citation_coverage(claims, anchors, returned) == 1.0


def test_citation_coverage_partial_match() -> None:
    claims = ["c1", "c2", "c3", "c4"]
    anchors = {"c1": "chunk_a", "c2": None, "c3": "chunk_x", "c4": "chunk_a"}
    returned = {"chunk_a"}
    # c1 covered, c2 None=uncovered, c3 missing chunk, c4 covered → 2/4
    assert citation_coverage(claims, anchors, returned) == 0.5
