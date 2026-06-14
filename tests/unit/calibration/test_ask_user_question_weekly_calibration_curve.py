"""Tests for the per-context calibration curve added to the weekly report (W3.1).

Plan: askq-confidence-meta-learning-loop-c4e7a1. Verifies the weekly report computes per-context
average stated confidence, a Wilson-95 acceptance CI, and a calibrated? flag.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.calibration import ask_user_question_weekly_report as wr


@pytest.fixture
def temp_ledger(tmp_path):
    import tools.ledgers.ask_user_question_ledger as ledger_mod

    original = ledger_mod.LEDGER_PATH
    ledger_mod.LEDGER_PATH = tmp_path / "weekly_calib_ledger.sqlite"
    ledger_mod.ensure_schema()
    yield ledger_mod
    ledger_mod.LEDGER_PATH = original


def _ts_days_ago(n: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=n)).isoformat()


def test_context_breakdown_has_calibration_fields(temp_ledger):
    # 10 decisions in 'design': stated 0.90 but only 50% accepted -> mis-calibrated (⚠️).
    for i in range(10):
        temp_ledger.write_decision(
            {
                "context": "design",
                "recommended_index": 0,
                "option_count": 2,
                "confidence_score": 0.90,
                "timestamp": _ts_days_ago(2),
            },
            selected_index=(0 if i % 2 == 0 else 1),
        )
    report = wr.generate_report(db_path=temp_ledger.LEDGER_PATH, reference_date=datetime.now(timezone.utc))
    ctx = {c.context: c for c in report.context_breakdown}
    assert "design" in ctx
    cb = ctx["design"]
    assert cb.total == 10
    assert cb.avg_confidence == pytest.approx(0.90, abs=1e-6)
    assert abs(cb.acceptance_rate - 0.5) < 1e-6
    point, low, high = cb.acceptance_ci
    assert 0.0 <= low <= point <= high <= 1.0
    # avg confidence 0.90 is far above the acceptance CI for 5/10 -> not calibrated
    assert cb.calibrated is False


def test_calibrated_true_when_confidence_matches_acceptance(temp_ledger):
    # stated ~0.70, ~70% accepted -> CI should overlap avg confidence.
    pattern = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1]  # 7/10 accepted
    for i in range(10):
        temp_ledger.write_decision(
            {
                "context": "aligned",
                "recommended_index": 0,
                "option_count": 2,
                "confidence_score": 0.70,
                "timestamp": _ts_days_ago(2),
            },
            selected_index=pattern[i],
        )
    report = wr.generate_report(db_path=temp_ledger.LEDGER_PATH, reference_date=datetime.now(timezone.utc))
    cb = {c.context: c for c in report.context_breakdown}["aligned"]
    assert cb.calibrated is True


def test_markdown_renders_calibration_table(temp_ledger):
    for i in range(6):
        temp_ledger.write_decision(
            {"context": "render", "recommended_index": 0, "option_count": 2, "confidence_score": 0.8, "timestamp": _ts_days_ago(1)},
            selected_index=0,
        )
    report = wr.generate_report(db_path=temp_ledger.LEDGER_PATH, reference_date=datetime.now(timezone.utc))
    md = wr.render_markdown(report)
    assert "Per-Context Calibration Curve" in md
    assert "Acceptance (Wilson 95% CI)" in md
    assert "calibrated?" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
