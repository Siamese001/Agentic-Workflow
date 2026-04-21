"""Wave 6 P6.1: Unit tests for tools.routing.calibrate_thresholds."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.routing.calibrate_thresholds import (
    CalibrationReport,
    brier_score,
    compute_report,
    load_feed,
    main,
    platt_recommend_threshold,
    render_markdown,
)

pytestmark = pytest.mark.unit


# ==========================================================================
# brier_score
# ==========================================================================


def test_brier_perfect_calibration_all_success():
    # All predicted conf=1.0 and all successful → Brier = 0.0
    pairs = [(1.0, True)] * 10
    assert brier_score(pairs) == 0.0


def test_brier_perfect_calibration_all_fail():
    # All predicted conf=0.0 and all failed → Brier = 0.0
    pairs = [(0.0, False)] * 10
    assert brier_score(pairs) == 0.0


def test_brier_worst_case():
    # Predicted 1.0 but all failed → Brier = 1.0
    pairs = [(1.0, False)] * 10
    assert brier_score(pairs) == 1.0


def test_brier_mixed():
    # Half correct (1.0→success) half wrong (1.0→fail) → Brier = 0.5
    pairs = [(1.0, True), (1.0, False)]
    assert brier_score(pairs) == 0.5


def test_brier_empty_returns_zero():
    assert brier_score([]) == 0.0


# ==========================================================================
# platt_recommend_threshold
# ==========================================================================


def test_platt_insufficient_data_returns_none():
    # Less than 10 events → None
    assert platt_recommend_threshold([(0.9, True)] * 5) is None


def test_platt_all_success_recommends_minimum_observed():
    # All successful at confidence >= 0.7 → threshold at the minimum
    pairs = [(0.7 + 0.02 * i, True) for i in range(15)]
    result = platt_recommend_threshold(pairs, target_success_rate=0.85)
    assert result is not None
    assert result == pytest.approx(0.7, abs=0.05)


def test_platt_low_success_recommends_high_cutoff():
    # Mix: top half succeeds, bottom half fails → cutoff near midpoint
    high_conf_success = [(0.95 - 0.01 * i, True) for i in range(10)]
    low_conf_fail = [(0.50 - 0.02 * i, False) for i in range(10)]
    pairs = high_conf_success + low_conf_fail
    result = platt_recommend_threshold(pairs, target_success_rate=0.85)
    assert result is not None
    # The cutoff should be somewhere between the success and failure bands
    # (success band starts at 0.86 ascending, failure band ends at 0.50)
    assert 0.40 <= result <= 0.90


# ==========================================================================
# load_feed + compute_report
# ==========================================================================


def test_load_feed_missing_file_returns_empty(tmp_path):
    path = tmp_path / "missing.jsonl"
    assert load_feed(path) == []


def test_load_feed_skips_malformed_lines(tmp_path, capsys):
    path = tmp_path / "feed.jsonl"
    path.write_text(
        '{"recommended_tier":"HIGH","heal_confidence":0.9,"outcome_success":true}\n'
        "NOT_JSON\n"
        '{"recommended_tier":"LOW","heal_confidence":0.2,"outcome_success":false}\n',
        encoding="utf-8",
    )
    events = load_feed(path)
    assert len(events) == 2
    captured = capsys.readouterr()
    assert "malformed JSON" in captured.err


def test_compute_report_empty_returns_insufficient():
    report = compute_report([])
    assert report.total_events == 0
    assert report.insufficient_data is True
    assert report.recommended_high_threshold is None
    assert report.recommended_medium_threshold is None


def test_compute_report_per_tier_brier():
    events = [
        {"recommended_tier": "HIGH", "heal_confidence": 0.9, "outcome_success": True},
        {"recommended_tier": "HIGH", "heal_confidence": 0.9, "outcome_success": True},
        {"recommended_tier": "LOW", "heal_confidence": 0.2, "outcome_success": False},
        {"recommended_tier": "LOW", "heal_confidence": 0.2, "outcome_success": False},
    ]
    report = compute_report(events)
    assert report.total_events == 4
    assert report.per_tier_counts["HIGH"] == 2
    assert report.per_tier_counts["LOW"] == 2
    # HIGH: (0.9, True) × 2 → Brier = (0.1)² = 0.01
    assert report.per_tier_brier["HIGH"] == pytest.approx(0.01, abs=0.001)
    # LOW: (0.2, False) × 2 → Brier = (0.2)² = 0.04
    assert report.per_tier_brier["LOW"] == pytest.approx(0.04, abs=0.001)


def test_compute_report_ignores_malformed_events():
    events = [
        {"recommended_tier": "HIGH", "heal_confidence": 0.9, "outcome_success": True},
        {"recommended_tier": "HIGH"},  # missing confidence + outcome
        {"heal_confidence": 0.5, "outcome_success": True},  # missing tier
        {"recommended_tier": "HIGH", "heal_confidence": "bad", "outcome_success": True},
    ]
    report = compute_report(events)
    # Only the first event is valid
    assert report.per_tier_counts["HIGH"] == 1


# ==========================================================================
# render_markdown
# ==========================================================================


def test_render_markdown_empty_report():
    report = CalibrationReport(total_events=0, insufficient_data=True)
    md = render_markdown(report)
    assert "Insufficient data" in md
    assert "Routing Threshold Calibration Report" in md


def test_render_markdown_with_alert():
    report = CalibrationReport(
        total_events=50,
        per_tier_counts={"HIGH": 25, "LOW": 25},
        per_tier_brier={"HIGH": 0.05, "LOW": 0.30},  # LOW exceeds 0.25 threshold
        per_tier_success_rate={"HIGH": 0.95, "LOW": 0.50},
        recommended_high_threshold=0.85,
        recommended_medium_threshold=0.40,
    )
    md = render_markdown(report)
    assert "⚠️" in md
    assert "LOW" in md
    assert "0.30" in md
    assert "HEALING_CONFIDENCE_X" in md
    assert "0.85" in md


# ==========================================================================
# CLI integration
# ==========================================================================


def test_main_empty_feed_exits_with_insufficient_data(tmp_path, capsys):
    feed = tmp_path / "empty.jsonl"
    feed.write_text("", encoding="utf-8")
    out = tmp_path / "report.md"

    exit_code = main(["--feed", str(feed), "--out", str(out)])
    assert exit_code == 2  # insufficient_data signal
    assert out.exists()
    captured = capsys.readouterr()
    assert "insufficient_data=True" in captured.out


def test_main_sufficient_data_exits_zero(tmp_path):
    feed = tmp_path / "feed.jsonl"
    events = []
    # 15 HIGH events with high confidence + success
    for i in range(15):
        events.append({"recommended_tier": "HIGH", "heal_confidence": 0.9, "outcome_success": True})
    # 15 LOW events with low confidence + failure
    for i in range(15):
        events.append({"recommended_tier": "LOW", "heal_confidence": 0.2, "outcome_success": False})
    feed.write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")

    out = tmp_path / "report.md"
    exit_code = main(["--feed", str(feed), "--out", str(out)])

    assert exit_code == 0
    content = out.read_text(encoding="utf-8")
    assert "**Events:** 30" in content
    assert "HEALING_CONFIDENCE_X" in content
