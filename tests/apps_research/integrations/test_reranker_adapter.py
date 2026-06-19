"""Tests for apps_research.integrations.reranker_adapter (plan P1.3)."""

from __future__ import annotations

from apps_research.integrations.reranker_adapter import rerank
from apps_research.integrations.search_retrieval import RetrievedDoc


def _mkdocs(scores: list[float]) -> list[RetrievedDoc]:
    return [
        RetrievedDoc(url=f"https://x/{i}", title=f"t{i}", snippet="s", score=s)
        for i, s in enumerate(scores)
    ]


def test_returns_exactly_cutoff_docs():
    docs = _mkdocs([0.1, 0.9, 0.5, 0.7, 0.3, 0.8, 0.2, 0.4, 0.6, 0.05])
    out = rerank("q", docs, cutoff=5)
    assert len(out) == 5


def test_monotonic_score_ordering():
    docs = _mkdocs([0.3, 0.9, 0.1, 0.7, 0.5])
    out = rerank("q", docs, cutoff=5)
    scores = [d.score for d in out]
    assert scores == sorted(scores, reverse=True)


def test_stable_ordering_for_tied_scores():
    docs = [
        RetrievedDoc(url="https://a", title="a", snippet="", score=0.5),
        RetrievedDoc(url="https://b", title="b", snippet="", score=0.5),
        RetrievedDoc(url="https://c", title="c", snippet="", score=0.5),
    ]
    out = rerank("q", docs, cutoff=3)
    assert [d.url for d in out] == ["https://a", "https://b", "https://c"]


def test_fewer_docs_than_cutoff_returns_all():
    docs = _mkdocs([0.1, 0.2])
    out = rerank("q", docs, cutoff=5)
    assert len(out) == 2


def test_zero_cutoff_returns_empty():
    assert rerank("q", _mkdocs([0.9, 0.5]), cutoff=0) == []


def test_empty_docs_returns_empty():
    assert rerank("q", [], cutoff=5) == []
