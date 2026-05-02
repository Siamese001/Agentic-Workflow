"""Tests for length-aware mirror_density + per-section buzzword caps (2026-05-01 calibration)."""

from __future__ import annotations

import pytest

from apps_rg.integrations.anti_overfitting import (
    AntiOverfittingConfig,
    _adaptive_min,
    gate_buzzword_soup,
    gate_mirror_density,
)


# ------------------------------------------------- length-aware mirror_min


def test_adaptive_min_short_text_uses_low_floor() -> None:
    cfg = AntiOverfittingConfig()
    short_text = "one two three four five six seven"  # 7 words
    assert _adaptive_min(short_text, cfg) == 0.04


def test_adaptive_min_medium_text_uses_mid_floor() -> None:
    cfg = AntiOverfittingConfig()
    medium_text = " ".join(["word"] * 50)  # 50 words
    assert _adaptive_min(medium_text, cfg) == 0.06


def test_adaptive_min_long_text_uses_full_floor() -> None:
    cfg = AntiOverfittingConfig()
    long_text = " ".join(["word"] * 100)  # 100 words
    assert _adaptive_min(long_text, cfg) == cfg.mirror_min


def test_adaptive_min_disabled_returns_config_min() -> None:
    cfg = AntiOverfittingConfig(adaptive_mirror=False)
    short_text = "one two three"
    assert _adaptive_min(short_text, cfg) == cfg.mirror_min


def test_adaptive_gate_short_bullet_passes_with_one_mirror_term() -> None:
    """A 20-word bullet with one mirror term ≈ 0.05 density — passes adaptive floor (0.04)."""
    cfg = AntiOverfittingConfig()
    text = "Delivered consulting work for Fortune 500 clients across nineteen distinct enterprise verticals in three years."
    # "consulting" matches -> 1/18 ≈ 0.056
    result = gate_mirror_density(text, ["consulting"], cfg)
    assert result.passed, result.detail


def test_gate_mirror_density_fails_when_zero_match_even_short() -> None:
    cfg = AntiOverfittingConfig()
    text = "The quick brown fox jumped over the lazy dog today and then slept peacefully."
    result = gate_mirror_density(text, ["consulting"], cfg)
    assert not result.passed


def test_gate_mirror_density_fails_when_over_max() -> None:
    cfg = AntiOverfittingConfig(mirror_max=0.15)
    text = "consulting consulting consulting consulting filler filler filler filler filler filler"
    # 4/10 = 0.4 -> over max=0.15
    result = gate_mirror_density(text, ["consulting"], cfg)
    assert not result.passed
    assert "max" in result.detail


# ---------------------------------------------- per-section buzzword caps


def test_buzzword_cap_headline_is_strict() -> None:
    cfg = AntiOverfittingConfig()
    text = "AI Transformation Enterprise Strategic Advisory"  # 4 buzzwords
    result = gate_buzzword_soup(text, cfg, section_id="hop_4a_headline")
    # Cap for headline is 2
    assert not result.passed
    assert "section=hop_4a_headline" in result.detail


def test_buzzword_cap_exec_summary_is_lenient() -> None:
    cfg = AntiOverfittingConfig()
    # 4 buzzwords — exec_summary cap is 5, so passes
    text = "AI Transformation Enterprise Strategic text in longer summary form."
    result = gate_buzzword_soup(text, cfg, section_id="hop_4b_exec_summary")
    assert result.passed


def test_buzzword_cap_competencies_is_mid() -> None:
    cfg = AntiOverfittingConfig()
    # 4 buzzwords, competencies cap is 4 — should pass (boundary)
    text = "AI Transformation Enterprise Strategic text"
    result = gate_buzzword_soup(text, cfg, section_id="hop_4c_competencies")
    assert result.passed


def test_buzzword_cap_default_falls_back_to_global() -> None:
    cfg = AntiOverfittingConfig()  # default max_buzzwords=3
    text = "AI Transformation Enterprise Strategic"  # 4 buzzwords
    # No section_id -> uses global max_buzzwords=3
    result = gate_buzzword_soup(text, cfg, section_id="")
    assert not result.passed


def test_buzzword_cap_unknown_section_uses_global() -> None:
    cfg = AntiOverfittingConfig()
    text = "AI Transformation Enterprise Strategic"  # 4 buzzwords
    result = gate_buzzword_soup(text, cfg, section_id="unknown_section")
    # Falls through to max_buzzwords=3 -> fails
    assert not result.passed


def test_buzzword_cap_config_override_by_section() -> None:
    cfg = AntiOverfittingConfig(
        max_buzzwords_by_section={"custom_section": 10}
    )
    text = "AI Transformation Enterprise Strategic Cloud Digital Innovation"  # 7 buzzwords
    result = gate_buzzword_soup(text, cfg, section_id="custom_section")
    assert result.passed


def test_mirror_max_raised_to_022() -> None:
    """Config default mirror_max raised from 0.18 -> 0.22 in 2026-05-01 calibration."""
    cfg = AntiOverfittingConfig()
    assert cfg.mirror_max == 0.22
