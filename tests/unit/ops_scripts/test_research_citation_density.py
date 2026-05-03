"""Tests for ops_scripts/ci/check_research_citation_density.py (plan §P4.4)."""

from __future__ import annotations

from ops_scripts.ci.check_research_citation_density import check_density


def _make_brief(tokens: int, url_count: int) -> dict:
    """Build a synthetic brief with ``tokens`` rendered words and ``url_count`` URLs."""
    body = " ".join(f"word{i}" for i in range(tokens))
    return {
        "summary": [body],
        "source_register": [
            {"url": f"https://example.com/src{i}"} for i in range(url_count)
        ],
    }


def test_density_passes_when_enough_citations():
    # Use large URL count to be robust to tiktoken vs whitespace token counting.
    brief = _make_brief(tokens=400, url_count=50)
    passed, report = check_density(brief, min_per_200=1.0)
    assert passed
    assert report["required_urls"] <= report["urls"]


def test_density_fails_when_sparse_citations():
    # 400 whitespace-tokens but 0 URLs → must fail regardless of tokenizer.
    brief = _make_brief(tokens=400, url_count=0)
    passed, report = check_density(brief, min_per_200=1.0)
    assert not passed
    assert report["required_urls"] > report["urls"]


def test_density_low_threshold_regression_guard():
    """Plan §P4.4 acceptance: gate fails when density is 1 URL per 400 tokens.

    Uses 2000 tokens with 1 URL — regardless of tokenizer, 2000 tokens
    demands ≥ ~5-10 URLs to meet the 1/200 floor.
    """
    brief = _make_brief(tokens=2000, url_count=1)
    passed, _ = check_density(brief, min_per_200=1.0)
    assert not passed


def test_density_short_brief_below_200_tokens_requires_one_url():
    brief = _make_brief(tokens=50, url_count=1)
    passed, _ = check_density(brief, min_per_200=1.0)
    assert passed


def test_density_report_includes_computed_fields():
    brief = _make_brief(tokens=200, url_count=1)
    _, report = check_density(brief, min_per_200=1.0)
    for key in ("tokens", "urls", "required_urls", "density_per_200_tokens", "passed"):
        assert key in report
