"""Tests for apps_rg.integrations.length_budget."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.integrations.length_budget import (
    DEFAULT_TOLERANCE,
    LengthBudget,
    best_fit,
    budget_for_section,
    budget_from_text,
    count_sentences,
    count_words,
    extract_master_resume_budgets,
)


def test_count_words_basic() -> None:
    assert count_words("one two three") == 3


def test_count_words_empty_handles_none_safely() -> None:
    assert count_words("") == 0
    assert count_words(None) == 0  # type: ignore[arg-type]


def test_count_sentences_terminators() -> None:
    assert count_sentences("Hello world. This is a test! Are you ok?") == 3


def test_budget_from_text_default_tolerance_is_15pct() -> None:
    budget = budget_from_text("test", "one two three four five six seven eight nine ten")
    assert budget.target_words == 10
    # 15% of 10 is 1.5 -> rounded delta = 2 (max with 1)
    assert budget.min_words >= 8
    assert budget.max_words <= 12


def test_budget_fits_in_band() -> None:
    budget = budget_from_text("b", "a b c d e f g h i j")  # 10
    assert budget.fits("one two three four five six seven eight nine")  # 9 within
    assert not budget.fits("a b c")  # 3 way out


def test_budget_for_section_with_sentence_target() -> None:
    budget = budget_for_section("hl", target_words=12, target_sentences=1, tolerance=0.20)
    assert budget.fits("ten word headline here for the candidate today now seems great")
    # Wrong sentence count
    assert not budget.fits("Headline. Subline. Tagline.")


def test_extract_master_resume_budgets_smoke(tmp_path: Path) -> None:
    payload = {
        "experience": [
            {
                "company": "TestCo",
                "bullet_pool": [
                    {"text": "Delivered five word bullet here."},
                    {"text": "Another bullet of seven words for sure."},
                ],
            }
        ]
    }
    path = tmp_path / "master.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    budgets = extract_master_resume_budgets(path)
    assert len(budgets) == 2
    keys = list(budgets.keys())
    assert all(k.startswith("TestCo::") for k in keys)


def test_extract_master_resume_budgets_missing_file(tmp_path: Path) -> None:
    assert extract_master_resume_budgets(tmp_path / "missing.json") == {}


def test_best_fit_returns_closest_target() -> None:
    budgets = [
        LengthBudget(label="a", target_words=5, min_words=4, max_words=6),
        LengthBudget(label="b", target_words=10, min_words=9, max_words=11),
    ]
    fit = best_fit(budgets, "one two three four five")  # 5 words
    assert fit is not None
    assert fit.label == "a"


def test_best_fit_returns_none_when_no_candidate() -> None:
    budgets = [LengthBudget(label="a", target_words=5, min_words=4, max_words=6)]
    assert best_fit(budgets, "one") is None
