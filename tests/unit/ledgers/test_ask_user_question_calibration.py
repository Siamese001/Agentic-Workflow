"""Tests for ask_user_question_calibration — the CONSULT half of the meta-learning loop.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W2.1).

Verifies that prior captured decisions (recommended vs selected) calibrate the confidence the
model should state next: high historical acceptance pulls the number up, heavy overrides pull it
down, and too little precedent is a no-op.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.ledgers import ask_user_question_calibration as calib


@pytest.fixture
def temp_ledger(tmp_path):
    """Temp ask_user_question ledger; returns (module, db_path)."""
    import tools.ledgers.ask_user_question_ledger as ledger_mod

    original = ledger_mod.LEDGER_PATH
    db = tmp_path / "test_calib_ledger.sqlite"
    ledger_mod.LEDGER_PATH = db
    ledger_mod.ensure_schema()
    yield ledger_mod, db
    ledger_mod.LEDGER_PATH = original


def _add(ledger_mod, context, recommended, selected, n=1):
    for _ in range(n):
        ledger_mod.write_decision(
            {"context": context, "recommended_index": recommended, "option_count": 2},
            selected_index=selected,
        )


class TestInsufficientSample:
    def test_no_change_below_min(self, temp_ledger):
        ledger_mod, db = temp_ledger
        _add(ledger_mod, "sparse", recommended=0, selected=0, n=3)
        r = calib.lookup_calibrated_confidence("sparse", 0.80, db_path=db)
        assert r.signal == "none"
        assert r.calibrated_confidence == 0.80
        assert r.n == 3
        assert not r.diverged

    def test_empty_ledger_fail_open(self, temp_ledger):
        _, db = temp_ledger
        r = calib.lookup_calibrated_confidence("missing", 0.72, db_path=db)
        assert r.signal == "none"
        assert r.calibrated_confidence == 0.72


class TestHighAcceptance:
    def test_high_acceptance_pulls_up_and_strong(self, temp_ledger):
        ledger_mod, db = temp_ledger
        _add(ledger_mod, "accept", recommended=0, selected=0, n=12)  # all accepted
        r = calib.lookup_calibrated_confidence("accept", 0.60, db_path=db)
        assert r.n == 12
        assert r.signal == "strong"
        assert r.empirical_acceptance == 1.0
        assert r.wilson_lower <= r.empirical_acceptance <= r.wilson_upper
        # under-stated relative to 100% acceptance -> calibrated rises toward the lower bound
        assert r.calibrated_confidence > 0.60
        assert r.diverged  # |0.60 - 1.0| > 0.15


class TestLowAcceptance:
    def test_overrides_pull_confidence_down(self, temp_ledger):
        ledger_mod, db = temp_ledger
        _add(ledger_mod, "override", recommended=0, selected=1, n=12)  # all overridden
        r = calib.lookup_calibrated_confidence("override", 0.85, db_path=db)
        assert r.n == 12
        assert r.empirical_acceptance == 0.0
        assert r.calibrated_confidence < 0.85  # pulled down hard
        assert r.diverged
        assert r.signal == "strong"


class TestSuggestiveBand:
    def test_mid_sample_is_suggestive(self, temp_ledger):
        ledger_mod, db = temp_ledger
        _add(ledger_mod, "mid", recommended=0, selected=0, n=4)
        _add(ledger_mod, "mid", recommended=0, selected=1, n=2)  # n=6 total, 4 accepted
        r = calib.lookup_calibrated_confidence("mid", 0.75, db_path=db)
        assert r.n == 6
        assert r.signal == "suggestive"
        assert 0.0 < r.empirical_acceptance < 1.0


class TestBoundsAndClamp:
    def test_calibrated_stays_in_range(self, temp_ledger):
        ledger_mod, db = temp_ledger
        _add(ledger_mod, "c", recommended=0, selected=1, n=20)
        r = calib.lookup_calibrated_confidence("c", 1.5, db_path=db)  # out-of-range stated
        assert 0.0 <= r.calibrated_confidence <= 1.0
        assert r.stated_confidence == 1.0  # clamped

    def test_rows_missing_selected_index_excluded(self, temp_ledger):
        ledger_mod, db = temp_ledger
        _add(ledger_mod, "partial", recommended=0, selected=0, n=6)
        # rows with no selection (free-text 'Other') must not count toward n
        ledger_mod.write_decision({"context": "partial", "recommended_index": 0, "option_count": 2}, selected_index=None)
        r = calib.lookup_calibrated_confidence("partial", 0.7, db_path=db)
        assert r.n == 6  # the None-selection row excluded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
