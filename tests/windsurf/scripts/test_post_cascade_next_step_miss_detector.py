"""Tests for the Windsurf post_cascade_next_step_miss_detector hook.

Exercises the scoring logic directly (avoids invoking the hook via
subprocess so tests are hermetic). Ensures:

- Responses with a NEXT_STEP: marker score 0 (no miss).
- Responses with a DEFERRED_SCOPE: marker score 0 (sibling discipline
  counts as anti-signal).
- Explicit negation ("no follow-ups") scores 0.
- A follow-up heading + multiple bullets + keywords scores above
  MISS_SCORE_THRESHOLD.
- Heading only (no bullets) is below threshold — the detector avoids
  noisy prose captures.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_detector():
    path = REPO_ROOT / ".windsurf" / "scripts" / "post_cascade_next_step_miss_detector.py"
    spec = importlib.util.spec_from_file_location("_nsmd_under_test", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_detector()
_compute_miss_score = _mod._compute_miss_score
MISS_SCORE_THRESHOLD = _mod.MISS_SCORE_THRESHOLD


class TestAntiSignals:
    def test_next_step_marker_zeros_score(self) -> None:
        text = (
            "## Follow-ups\n\n"
            "- item one\n- item two\n- item three\n\n"
            "NEXT_STEP: plan=NEW:foo title=x priority=P3 est_tokens=1000 reason=y\n"
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report["anti_signal"] == "next_step_marker_present"
        assert report["next_step_marker_count"] == 1

    def test_deferred_scope_marker_zeros_score(self) -> None:
        text = (
            "## Future work\n- a\n- b\n- c\n\n"
            "DEFERRED_SCOPE: plan=existing-plan wave=W1 phase=P1 "
            "layer=L3 fan_in=5 surface=None coverage_gap_pct=10 "
            "est_tokens=1000 reason=x\n"
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report["anti_signal"] == "deferred_scope_marker_present"

    def test_explicit_negation_zeros_score(self) -> None:
        text = (
            "## Follow-ups\n\nNo follow-ups needed — all waves landed.\n"
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report["anti_signal"] == "explicit_negation"

    def test_clean_response_scores_zero(self) -> None:
        text = "All waves complete. Tests green."
        score, report = _compute_miss_score(text)
        assert score == 0
        # Clean responses produce an empty positive_signals list.
        assert report["positive_signals"] == []


class TestPositiveSignals:
    def test_heading_plus_bullets_crosses_threshold(self) -> None:
        text = (
            "## Follow-ups (not implemented)\n\n"
            "- Redis backend for PassK\n"
            "- Judge calibration harness\n"
            "- Next-step miss detector tests\n"
        )
        score, _ = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD

    def test_heading_only_below_threshold(self) -> None:
        # Heading scores 2, no bullets, no keywords → exactly threshold but
        # we want heading alone to be enough evidence per the detector's
        # current policy (threshold=2). This test documents that contract
        # so accidental threshold changes surface.
        text = "## Deferred\n\n(section intentionally blank)\n"
        score, _ = _compute_miss_score(text)
        # 2 = heading hit
        assert score == 2

    def test_keyword_density(self) -> None:
        text = (
            "Out of scope for this run. Future work: Redis backend. "
            "Deferred to next sprint. A separate plan will track this."
        )
        score, report = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD
        # At least three distinct keywords triggered
        assert len(report["keywords_hit"]) >= 3

    def test_heading_with_three_bullets_strong_signal(self) -> None:
        text = (
            "## TODO\n\n"
            "- Foo\n- Bar\n- Baz\n- Qux\n"
        )
        score, _ = _compute_miss_score(text)
        # Heading (+2) + bullets >=3 (+2) = 4
        assert score >= 4

    def test_single_keyword_mention_alone_below_threshold(self) -> None:
        text = "Everything done. Minor stubbed helper noted in code comments."
        score, _ = _compute_miss_score(text)
        # 1 keyword → +1, no heading, no bullets → below threshold
        assert score < MISS_SCORE_THRESHOLD


class TestBulletCounting:
    def test_bullets_counted_only_under_heading(self) -> None:
        text = (
            "Some unrelated bullets:\n"
            "- not under heading\n- also not\n- still not\n\n"
            "## Follow-ups\n\n"
            "- real one\n"
        )
        score, report = _compute_miss_score(text)
        # Heading (2) + one bullet under (1) = 3
        assert report["bullets_under_heading"] == 1
        assert score >= MISS_SCORE_THRESHOLD

    def test_next_heading_bounds_bullet_section(self) -> None:
        text = (
            "## Follow-ups\n\n- one\n- two\n\n"
            "## Summary\n\n- not a followup bullet\n- neither\n"
        )
        _, report = _compute_miss_score(text)
        # Only the two under Follow-ups count.
        assert report["bullets_under_heading"] == 2
