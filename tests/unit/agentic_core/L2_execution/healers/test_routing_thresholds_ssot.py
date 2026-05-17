"""Heal routing thresholds SSOT + ConfidenceScorer integration tests."""

from __future__ import annotations

from math import nextafter

import pytest

pytestmark = pytest.mark.unit


def test_default_pair_digest_and_sources(monkeypatch: pytest.MonkeyPatch):
    import agentic_core.L2_execution.healers.routing_thresholds_ssot as ssot

    monkeypatch.delenv("HEALING_CONFIDENCE_HIGH", raising=False)
    monkeypatch.delenv("HEALING_CONFIDENCE_MEDIUM", raising=False)
    ssot.invalidate_healing_confidence_threshold_cache()
    ssot.load_healing_confidence_thresholds.cache_clear()  # type: ignore[attr-defined]

    th = ssot.load_healing_confidence_thresholds()
    assert th.medium == 0.50
    assert th.high == 0.85
    assert th.threshold_source_map["high"] == "default"
    assert th.threshold_source_map["medium"] == "default"
    assert len(th.threshold_profile_digest) == 64


def test_whitespace_only_env_is_unset(monkeypatch: pytest.MonkeyPatch):
    import agentic_core.L2_execution.healers.routing_thresholds_ssot as ssot

    monkeypatch.setenv("HEALING_CONFIDENCE_HIGH", "  \t ")
    monkeypatch.setenv("HEALING_CONFIDENCE_MEDIUM", "")
    ssot.invalidate_healing_confidence_threshold_cache()
    ssot.load_healing_confidence_thresholds.cache_clear()  # type: ignore[attr-defined]
    th = ssot.load_healing_confidence_thresholds()
    assert th.high == ssot.DEFAULT_HEAL_CONFIDENCE_HIGH


@pytest.mark.parametrize(
    ("env_high", "env_medium", "error_fragment"),
    [
        ("nan", "0.2", "finite"),
        ("inf", "0.2", "finite"),
        ("0.5", "0.5", "MEDIUM"),
        ("-0.1", "0.2", "domain"),
        ("0.95", "oops", "non-numeric"),
    ],
)
def test_fail_closed_env_pairs(
    monkeypatch: pytest.MonkeyPatch,
    env_high: str,
    env_medium: str,
    error_fragment: str,
):
    import agentic_core.L2_execution.healers.routing_thresholds_ssot as ssot

    monkeypatch.setenv("HEALING_CONFIDENCE_HIGH", env_high)
    monkeypatch.setenv("HEALING_CONFIDENCE_MEDIUM", env_medium)
    ssot.invalidate_healing_confidence_threshold_cache()
    ssot.load_healing_confidence_thresholds.cache_clear()  # type: ignore[attr-defined]
    with pytest.raises(ValueError) as excinfo:
        ssot.load_healing_confidence_thresholds()
    assert error_fragment.lower() in str(excinfo.value).lower()


def test_env_pair_success(monkeypatch: pytest.MonkeyPatch):
    import agentic_core.L2_execution.healers.routing_thresholds_ssot as ssot

    monkeypatch.setenv("HEALING_CONFIDENCE_HIGH", "0.9")
    monkeypatch.setenv("HEALING_CONFIDENCE_MEDIUM", "0.4")
    ssot.invalidate_healing_confidence_threshold_cache()
    ssot.load_healing_confidence_thresholds.cache_clear()  # type: ignore[attr-defined]
    th = ssot.load_healing_confidence_thresholds()
    assert th.high == pytest.approx(0.9)
    assert th.medium == pytest.approx(0.4)
    assert th.threshold_source_map == {"high": "env", "medium": "env"}


@pytest.mark.parametrize(
    ("score", "tier_name"),
    [
        pytest.param(0.85, "HIGH", id="at-high-inclusive"),
        pytest.param(nextafter(0.85, float("-inf")), "MEDIUM", id="below-high-nextafter"),
        pytest.param(0.50, "MEDIUM", id="at-medium-inclusive"),
        pytest.param(nextafter(0.50, float("-inf")), "LOW", id="below-medium-nextafter"),
        pytest.param(0.0, "LOW", id="floor"),
        pytest.param(1.0, "HIGH", id="ceil"),
    ],
)
def test_scorer_maps_boundaries(monkeypatch: pytest.MonkeyPatch, score: float, tier_name: str):
    import agentic_core.L2_execution.healers.confidence_scorer as scorer

    monkeypatch.delenv("HEALING_CONFIDENCE_HIGH", raising=False)
    monkeypatch.delenv("HEALING_CONFIDENCE_MEDIUM", raising=False)

    from agentic_core.L2_execution.healers.routing_thresholds_ssot import (
        invalidate_healing_confidence_threshold_cache,
        load_healing_confidence_thresholds,
    )

    invalidate_healing_confidence_threshold_cache()
    load_healing_confidence_thresholds.cache_clear()  # type: ignore[attr-defined]

    scorer_obj = scorer.ConfidenceScorer(run_id="boundary-test")
    assert scorer_obj._tier_from_score(score).name == tier_name  # noqa: SLF001


def test_confidence_scorer_module_documents_ssot():
    from pathlib import Path

    cs = pytest.importorskip("agentic_core.L2_execution.healers.confidence_scorer")
    p = getattr(cs, "__file__")
    txt = Path(p).read_text(encoding="utf-8")
    assert "routing_thresholds_ssot" in txt


@pytest.mark.parametrize("legacy_name", ["SOVEREIGN_HIGH_CONFIDENCE", "SOVEREIGN_MEDIUM_CONFIDENCE"])
def test_forbidden_legacy_sovereign_names_not_in_examples_or_docs(legacy_name: str):
    from pathlib import Path

    root = Path(__file__).resolve().parents[5]
    assert legacy_name not in (root / ".env.example").read_text(encoding="utf-8")
    for md in (root / "docs").rglob("*.md"):
        assert legacy_name not in md.read_text(encoding="utf-8")
