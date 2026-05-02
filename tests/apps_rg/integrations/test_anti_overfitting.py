"""Tests for apps_rg.integrations.anti_overfitting hard-gate primitives."""

from __future__ import annotations

import pytest

from apps_rg.integrations.anti_overfitting import (
    AntiOverfittingConfig,
    count_buzzwords,
    filler_hits,
    gate_adjacent_repetition,
    gate_buzzword_soup,
    gate_filler_intensifiers,
    gate_mirror_density,
    mirror_density,
)


# ---------------------------------------------------------------- buzzwords


def test_count_buzzwords_zero_when_clean() -> None:
    assert count_buzzwords("Drove revenue lift across financial-services accounts.") == 0


def test_count_buzzwords_counts_each_match_once_per_occurrence() -> None:
    text = "AI strategy and AI delivery for enterprise clients in cloud era."
    # 'AI' x2, 'enterprise' x1, 'cloud' x1
    assert count_buzzwords(text) == 4


def test_count_buzzwords_word_boundary_excludes_substrings() -> None:
    # 'AI' must not match inside 'AIDA' or 'painting'
    text = "AIDA painting workshop."
    assert count_buzzwords(text) == 0


def test_gate_buzzword_soup_passes_at_max_count_boundary() -> None:
    cfg = AntiOverfittingConfig(max_buzzwords=3)
    text = "AI transformation enterprise initiative."
    result = gate_buzzword_soup(text, cfg)
    assert result.passed
    assert "buzzword_count=3" in result.detail


def test_gate_buzzword_soup_fails_when_over_limit() -> None:
    cfg = AntiOverfittingConfig(max_buzzwords=2)
    text = "AI transformation enterprise digital innovation."
    result = gate_buzzword_soup(text, cfg)
    assert not result.passed


# ----------------------------------------------------------------- filler


def test_filler_hits_detects_word_boundary() -> None:
    assert filler_hits("leading AWS solution") == ["leading"]


def test_filler_hits_detects_hyphenated_phrases() -> None:
    hits = set(filler_hits("world-class cutting-edge platform"))
    assert "world-class" in hits
    assert "cutting-edge" in hits


def test_gate_filler_passes_for_clean_text() -> None:
    result = gate_filler_intensifiers(
        "Drove 30% revenue lift across 12 enterprise accounts in two quarters.",
        AntiOverfittingConfig(),
    )
    assert result.passed


def test_gate_filler_fails_on_any_match() -> None:
    result = gate_filler_intensifiers("leveraged synergy", AntiOverfittingConfig())
    assert not result.passed


# ------------------------------------------------------------- mirror_density


def test_mirror_density_zero_when_no_terms() -> None:
    assert mirror_density("plain text", []) == 0.0


def test_mirror_density_zero_when_no_match() -> None:
    assert mirror_density("plain text", ["consulting", "agentic"]) == 0.0


def test_mirror_density_in_band() -> None:
    text = "Delivered consulting engagements with measurable outcomes for ten clients."
    # 1 token of "consulting" / 9 tokens ≈ 0.111
    d = mirror_density(text, ["consulting"])
    assert 0.08 <= d <= 0.18


def test_gate_mirror_density_under_min_fails() -> None:
    # Disable adaptive floor so the fixed mirror_min is enforced regardless
    # of text length. The adaptive path has its own test suite.
    cfg = AntiOverfittingConfig(mirror_min=0.10, mirror_max=0.20, adaptive_mirror=False)
    text = " ".join(["filler"] * 20 + ["consulting"])
    result = gate_mirror_density(text, ["consulting"], cfg)
    assert not result.passed
    assert "min=" in result.detail


def test_gate_mirror_density_over_max_fails() -> None:
    cfg = AntiOverfittingConfig(mirror_min=0.05, mirror_max=0.10)
    text = "consulting consulting consulting filler"
    result = gate_mirror_density(text, ["consulting"], cfg)
    assert not result.passed
    assert "max=" in result.detail


# -------------------------------------------------------- adjacent_repetition


def test_gate_adjacent_repetition_passes_when_distinct_leads() -> None:
    bullets = [
        "Consulting delivered measurable outcomes for clients.",
        "Agentic system shipped with full audit trail.",
        "Data platform reduced cost by 40%.",
    ]
    result = gate_adjacent_repetition(bullets, ["consulting", "agentic", "data"])
    assert result.passed


def test_gate_adjacent_repetition_fails_when_same_lead() -> None:
    bullets = [
        "Consulting team delivered the engagement.",
        "Consulting led the next quarter as well.",
    ]
    result = gate_adjacent_repetition(bullets, ["consulting"])
    assert not result.passed
    assert "consulting" in result.detail


def test_gate_adjacent_repetition_ignores_non_leading_match() -> None:
    bullets = [
        "Drove consulting engagement to closure.",
        "Agentic platform delivered consulting wins.",
    ]
    # "consulting" not in leading 3 words of bullet 0; no false positive.
    result = gate_adjacent_repetition(bullets, ["consulting", "agentic"])
    assert result.passed
