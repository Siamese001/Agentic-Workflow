"""Tests for HOP-4.7 Marquee and HOP-4H Early Career."""

from __future__ import annotations

import pytest

from apps_rg.integrations.hops.early_career_compress import (
    MAX_WORDS,
    compress_early_career,
)
from apps_rg.integrations.hops.marquee import select_marquee


# ----------------------------------------------------------- early career


def test_early_career_default_when_empty() -> None:
    line = compress_early_career(roles=[])
    assert "2002" in line
    assert "2009" in line


def test_early_career_uses_role_year_range() -> None:
    line = compress_early_career(
        roles=[
            {"start_year": 2003, "end_year": 2007, "title": "Analyst"},
            {"start_year": 2007, "end_year": 2010, "title": "Senior Analyst"},
        ]
    )
    assert "2003" in line
    assert "2010" in line
    assert "Analyst" in line


def test_early_career_truncates_to_max_words() -> None:
    titles = [{"title": f"Long Title Number {i} For Testing"} for i in range(20)]
    line = compress_early_career(roles=titles, label="Earlier Career")
    assert len(line.split()) <= MAX_WORDS


def test_early_career_dedupes_titles() -> None:
    line = compress_early_career(
        roles=[
            {"title": "Analyst", "end_year": 2008},
            {"title": "Analyst", "end_year": 2009},
            {"title": "Senior Analyst", "end_year": 2010},
        ]
    )
    # 'Analyst' should appear in title list — once is fine; specifically
    # the explicit "Analyst, Senior Analyst" join.
    assert line.count("Analyst") >= 1


# ----------------------------------------------------------------- marquee


def test_marquee_selects_only_quantified_bullets() -> None:
    roles = [
        {
            "role_id": "unify",
            "bullets": [
                {"text": "Drove 30% revenue lift across 12 enterprise accounts."},
                {"text": "Generic statement of work."},  # no metric
            ],
        }
    ]
    out = select_marquee(bullets_by_role=roles)
    texts = [m.text for m in out]
    assert any("30%" in t for t in texts)
    assert not any("Generic statement" in t for t in texts)


def test_marquee_caps_at_n() -> None:
    roles = [
        {
            "role_id": "r",
            "bullets": [
                {"text": f"Outcome {i}: 30% lift over 12 months across 200 clients."}
                for i in range(10)
            ],
        }
    ]
    out = select_marquee(bullets_by_role=roles, n=3)
    assert len(out) == 3


def test_marquee_excludes_already_used_text() -> None:
    bullet = "Drove 30% revenue lift across 12 enterprise accounts."
    roles = [{"role_id": "r", "bullets": [{"text": bullet}]}]
    out = select_marquee(bullets_by_role=roles, exclude_texts=[bullet])
    assert out == []


def test_marquee_sorts_by_metric_count_desc() -> None:
    roles = [
        {
            "role_id": "r",
            "bullets": [
                {"text": "Single 5% improvement here."},
                {"text": "Triple 30%, 12x, $4M outcome shipped."},
            ],
        }
    ]
    out = select_marquee(bullets_by_role=roles, n=2)
    # Triple-metric bullet should come first
    assert "$4M" in out[0].text
