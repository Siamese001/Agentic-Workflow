"""Tests for apps_rg.engines.hallucination_detector.HallucinationDetector.

Covers the gaps G3 (generic-superlative blocklist) and G4 (implausible-growth
+ short-horizon proximity) restored in plan
apps-rg-prior-art-gap-closure-3e3d5b (Phase P3) plus regression guards on
existing literal patterns.
"""

from __future__ import annotations

import pytest

from apps_rg.engines.hallucination_detector import HallucinationDetector


@pytest.fixture
def detector() -> HallucinationDetector:
    """Bypass BaseRGEngine ctx requirement — we only need check_batch()."""
    return HallucinationDetector.__new__(HallucinationDetector)


def _issue_kinds(result: dict) -> list[str]:
    """Return list of issue-prefix labels (everything before the first ':')."""
    return [issue.split(":", 1)[0] for issue in result["issues"]]


class TestG3GenericSuperlatives:
    """G3 — >=2 generic superlatives flag the bullet."""

    def test_three_superlatives_flagged(self, detector: HallucinationDetector) -> None:
        result = detector.check_batch(
            ["Delivered world-class cutting-edge revolutionary platform at scale"]
        )
        assert "excessive_superlatives" in _issue_kinds(result)

    def test_one_superlative_not_flagged(self, detector: HallucinationDetector) -> None:
        result = detector.check_batch(
            ["Delivered best-in-class data platform handling 5TB daily"]
        )
        # exactly one superlative — must not trip G3 (threshold = 2).
        assert "excessive_superlatives" not in _issue_kinds(result)

    def test_two_superlatives_at_threshold(self, detector: HallucinationDetector) -> None:
        result = detector.check_batch(
            ["Delivered best-in-class cutting-edge data platform"]
        )
        assert "excessive_superlatives" in _issue_kinds(result)

    def test_score_penalty_is_minus_zero_two(self, detector: HallucinationDetector) -> None:
        # Plain text → score 1.0; with two superlatives → 0.8.
        plain = detector.check_batch(["Built and shipped a data ingestion service"])
        sup = detector.check_batch(
            ["Built best-in-class cutting-edge data ingestion service"]
        )
        assert plain["score"] == pytest.approx(1.0, abs=1e-9)
        assert sup["score"] == pytest.approx(0.8, abs=1e-9)


class TestG4ImplausibleGrowthHorizon:
    """G4 — \\d{3,}% within month/quarter/90-day horizon flags the bullet."""

    def test_100_percent_in_6_months_flagged(
        self, detector: HallucinationDetector
    ) -> None:
        """The canonical example E1 caught and current literal patterns missed."""
        result = detector.check_batch(["Achieved 100% revenue growth in 6 months"])
        assert "implausible_growth_with_horizon" in _issue_kinds(result)

    def test_quarter_horizon_flagged(self, detector: HallucinationDetector) -> None:
        result = detector.check_batch(["Drove 250% pipeline growth in one quarter"])
        assert "implausible_growth_with_horizon" in _issue_kinds(result)

    def test_90_day_horizon_flagged(self, detector: HallucinationDetector) -> None:
        result = detector.check_batch(["Boosted retention 500% in 90 days"])
        assert "implausible_growth_with_horizon" in _issue_kinds(result)

    def test_no_horizon_not_flagged_by_g4(
        self, detector: HallucinationDetector
    ) -> None:
        """Without month/quarter/90-day proximity, G4 should not fire."""
        result = detector.check_batch(["Achieved 500% YoY revenue growth"])
        assert "implausible_growth_with_horizon" not in _issue_kinds(result)

    def test_two_digit_percent_not_flagged_by_g4(
        self, detector: HallucinationDetector
    ) -> None:
        """\\d{3,} requires 3+ digits — '50% in 6 months' should NOT trigger G4."""
        result = detector.check_batch(["Improved latency 50% in 6 months"])
        assert "implausible_growth_with_horizon" not in _issue_kinds(result)


class TestExistingPatternsRegressionGuards:
    """Existing _SUSPICIOUS_PATTERNS / _OVERCLAIM_PATTERNS still fire."""

    def test_1000_percent_still_flagged_by_existing_pattern(
        self, detector: HallucinationDetector
    ) -> None:
        result = detector.check_batch(["Achieved 1000% sales growth"])
        # The existing _SUSPICIOUS_PATTERNS labels the magnitude regardless of
        # horizon — must not be regressed by the G3/G4 additions.
        assert "implausible_growth" in _issue_kinds(result)

    def test_100_percent_accuracy_overclaim_still_flagged(
        self, detector: HallucinationDetector
    ) -> None:
        result = detector.check_batch(["Delivered 100% accuracy on all queries"])
        assert "overclaim_phrase" in _issue_kinds(result)


class TestSuperlativeBlocklistContent:
    """The 8 superlatives match the 2025-12-08 snapshot list verbatim."""

    def test_blocklist_contains_8_words(self) -> None:
        assert len(HallucinationDetector._GENERIC_SUPERLATIVES) == 8

    def test_blocklist_matches_snapshot(self) -> None:
        expected = {
            "revolutionary",
            "groundbreaking",
            "unprecedented",
            "unparalleled",
            "game-changing",
            "world-class",
            "best-in-class",
            "cutting-edge",
        }
        assert set(HallucinationDetector._GENERIC_SUPERLATIVES) == expected
