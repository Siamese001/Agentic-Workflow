"""Tests for ops_scripts/calibration/calibration_drift_detector.py (G13)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.calibration.calibration_drift_detector import (
    EXIT_ALERT,
    EXIT_OK,
    EXIT_WARN,
    compute_breach_rates,
    evaluate_drift,
    main,
)


def _records(*verdicts: tuple[str, str]) -> list[dict]:
    """Build [(judge_id, verdict), ...] records."""
    out = []
    for i, (judge, verdict) in enumerate(verdicts):
        out.append(
            {
                "dimension_id": f"dim_{i}",
                "judge_id": judge,
                "verdict": verdict,
                "score": None if verdict == "UNKNOWN" else 0.9,
                "trace_id": f"run_{i}",
            }
        )
    return out


def test_compute_rates_simple() -> None:
    recs = _records(
        ("gemini", "PASS"),
        ("gemini", "PASS"),
        ("gemini", "UNKNOWN"),
        ("claude", "PASS"),
    )
    rates, totals, runs = compute_breach_rates(recs)
    assert rates["gemini"] == pytest.approx(1 / 3, abs=1e-6)
    assert rates["claude"] == 0.0
    assert totals["gemini"] == 3
    assert runs == 4


def test_evaluate_drift_alert_threshold() -> None:
    rates = {"gemini": 0.25, "claude": 0.05}
    totals = {"gemini": 100, "claude": 100}
    policy = {
        "rolling_window_days": 7,
        "breach_rate_warn_threshold": 0.10,
        "breach_rate_alert_threshold": 0.20,
        "min_runs_for_signal": 5,
    }
    code, lines = evaluate_drift(rates, totals, total_runs=20, policy=policy)
    assert code == EXIT_ALERT
    assert any("ALERT" in line and "gemini" in line for line in lines)


def test_evaluate_drift_warn_threshold() -> None:
    rates = {"gemini": 0.12}
    totals = {"gemini": 50}
    policy = {
        "breach_rate_warn_threshold": 0.10,
        "breach_rate_alert_threshold": 0.20,
        "min_runs_for_signal": 5,
    }
    code, lines = evaluate_drift(rates, totals, total_runs=10, policy=policy)
    assert code == EXIT_WARN


def test_evaluate_drift_insufficient_runs_returns_ok() -> None:
    rates = {"gemini": 0.99}  # would alert if runs >= min
    totals = {"gemini": 3}
    policy = {
        "breach_rate_warn_threshold": 0.10,
        "breach_rate_alert_threshold": 0.20,
        "min_runs_for_signal": 5,
    }
    code, lines = evaluate_drift(rates, totals, total_runs=2, policy=policy)
    assert code == EXIT_OK
    assert any("INSUFFICIENT_DATA" in line for line in lines)


def test_evaluate_drift_all_ok() -> None:
    rates = {"gemini": 0.05, "claude": 0.02}
    totals = {"gemini": 100, "claude": 100}
    policy = {
        "breach_rate_warn_threshold": 0.10,
        "breach_rate_alert_threshold": 0.20,
        "min_runs_for_signal": 5,
    }
    code, _ = evaluate_drift(rates, totals, total_runs=10, policy=policy)
    assert code == EXIT_OK


def test_main_smoke_with_empty_dir(tmp_path: Path) -> None:
    """Empty scorecard dir -> insufficient data -> exit 0."""
    empty = tmp_path / "scorecards"
    empty.mkdir()
    code = main(
        [
            "--scorecard-dir",
            str(empty),
            "--window",
            "7",
            "--quiet",
        ]
    )
    assert code == EXIT_OK


def test_main_with_jsonl_alert(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Synthesize a scorecard JSONL with high Unknown rate -> exit 2."""
    scorecard_dir = tmp_path / "scorecards"
    scorecard_dir.mkdir()
    rows = []
    # 6 distinct runs (>= min_runs_for_signal=5) with 50% Unknown
    for i in range(6):
        rows.append(
            {
                "dimension_id": "d",
                "judge_id": "gemini",
                "verdict": "UNKNOWN",
                "score": None,
                "trace_id": f"r{i}",
            }
        )
        rows.append(
            {"dimension_id": "d", "judge_id": "gemini", "verdict": "PASS", "score": 0.9, "trace_id": f"r{i}"}
        )
    sc_file = scorecard_dir / "today.jsonl"
    sc_file.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    code = main(
        [
            "--scorecard-dir",
            str(scorecard_dir),
            "--window",
            "7",
            "--quiet",
        ]
    )
    captured = capsys.readouterr().out
    assert "ALERT" in captured
    assert code == EXIT_ALERT
