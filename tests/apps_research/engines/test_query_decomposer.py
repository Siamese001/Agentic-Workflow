"""Tests for apps_research.engines.query_decomposer (plan P1.1)."""

from __future__ import annotations

import pytest

from apps_research.engines.query_decomposer import SubQuery, decompose


def test_depth_shallow_returns_three():
    subs = decompose("Blend360", depth="shallow")
    assert len(subs) == 3
    assert all(isinstance(s, SubQuery) for s in subs)


def test_depth_standard_returns_four():
    assert len(decompose("Blend360", depth="standard")) == 4


def test_depth_deep_returns_five():
    subs = decompose("Blend360", depth="deep")
    assert len(subs) == 5


def test_facets_are_unique_across_depth():
    subs = decompose("Blend360", depth="deep")
    facets = [s.facet for s in subs]
    assert len(set(facets)) == len(facets)


def test_subqueries_contain_topic():
    for s in decompose("Blend360", depth="deep"):
        assert "Blend360" in s.text


def _jaccard(a: str, b: str) -> float:
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    return len(wa & wb) / max(1, len(wa | wb))


def test_subqueries_jaccard_below_70pct():
    """Acceptance: no two sub-queries share >70% of words (plan P1.1)."""
    subs = decompose("Blend360", depth="deep")
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            similarity = _jaccard(a.text, b.text)
            assert similarity <= 0.70, (
                f"Jaccard similarity {similarity:.2f} between facets "
                f"{a.facet!r} and {b.facet!r}"
            )


def test_empty_topic_raises():
    with pytest.raises(ValueError):
        decompose("", depth="standard")


def test_whitespace_topic_raises():
    with pytest.raises(ValueError):
        decompose("   ", depth="standard")
