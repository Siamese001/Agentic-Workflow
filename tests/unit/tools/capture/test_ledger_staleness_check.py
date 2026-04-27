"""Unit tests for tools.capture.ledger_staleness_check.

This is THE gate that would have caught the 2026-04-23 → 2026-04-27 outage.
Exercises every regime: fresh, stale, missing, empty, advisory, bypass,
custom threshold, malformed timestamp, JSON output.
"""

# pylint: disable=redefined-outer-name,unused-argument

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

from tools.capture import ledger_staleness_check as lsc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ledger(tmp_path: Path, max_created_at: str | None) -> Path:
    """Build a minimal ledger DB with the needed schema and one row (or empty)."""
    p = tmp_path / "ledger.sqlite"
    con = sqlite3.connect(p)
    con.execute(
        "CREATE TABLE decisions (id INTEGER PRIMARY KEY, created_at TEXT)"
    )
    if max_created_at is not None:
        con.execute("INSERT INTO decisions (created_at) VALUES (?)", (max_created_at,))
    con.commit()
    con.close()
    return p


def _iso_hours_ago(h: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=h)).isoformat()


# ---------------------------------------------------------------------------
# parse_iso
# ---------------------------------------------------------------------------

class TestParseISO:
    def test_empty_returns_none(self):
        assert lsc.parse_iso("") is None
        assert lsc.parse_iso(None) is None  # type: ignore[arg-type]

    def test_valid_offset(self):
        dt = lsc.parse_iso("2026-04-27T10:40:09.209840+00:00")
        assert dt is not None
        assert dt.tzinfo is not None

    def test_z_suffix_accepted(self):
        dt = lsc.parse_iso("2026-04-27T10:40:09Z")
        assert dt is not None
        assert dt.tzinfo is not None

    def test_naive_ts_gets_utc_assigned(self):
        dt = lsc.parse_iso("2026-04-27T10:40:09")
        assert dt is not None
        assert dt.tzinfo is timezone.utc

    def test_malformed_returns_none(self):
        assert lsc.parse_iso("not a timestamp") is None
        assert lsc.parse_iso("2026-13-99") is None


# ---------------------------------------------------------------------------
# evaluate — the core policy function
# ---------------------------------------------------------------------------

class TestEvaluate:
    def test_fresh_ledger(self, tmp_path):
        p = _make_ledger(tmp_path, _iso_hours_ago(0.1))
        r = lsc.evaluate(p, max_age_hours=24)
        assert r["status"] == "fresh"
        assert r["age_hours"] is not None
        assert r["age_hours"] < 1

    def test_stale_ledger(self, tmp_path):
        p = _make_ledger(tmp_path, _iso_hours_ago(48))
        r = lsc.evaluate(p, max_age_hours=24)
        assert r["status"] == "stale"
        assert r["age_hours"] > 24

    def test_ledger_missing(self, tmp_path):
        r = lsc.evaluate(tmp_path / "nope.sqlite", max_age_hours=24)
        assert r["status"] == "ledger_missing"
        assert r["max_created_at"] is None

    def test_ledger_empty(self, tmp_path):
        p = _make_ledger(tmp_path, None)
        r = lsc.evaluate(p, max_age_hours=24)
        assert r["status"] == "ledger_empty"

    def test_unparseable_timestamp_is_stale(self, tmp_path):
        p = _make_ledger(tmp_path, "corrupted-timestamp-value")
        r = lsc.evaluate(p, max_age_hours=24)
        assert r["status"] == "stale"
        assert r["max_created_at"] == "corrupted-timestamp-value"

    def test_custom_threshold(self, tmp_path):
        p = _make_ledger(tmp_path, _iso_hours_ago(1))
        r_strict = lsc.evaluate(p, max_age_hours=0.5)
        r_loose = lsc.evaluate(p, max_age_hours=24)
        assert r_strict["status"] == "stale"
        assert r_loose["status"] == "fresh"


# ---------------------------------------------------------------------------
# main — exit codes and env var handling
# ---------------------------------------------------------------------------

class TestMainExitCodes:
    def test_fresh_exit_0(self, tmp_path, capsys):
        p = _make_ledger(tmp_path, _iso_hours_ago(0.1))
        rc = lsc.main(["--ledger", str(p), "--max-age-hours", "24"])
        assert rc == 0

    def test_stale_exit_2_block(self, tmp_path, capsys):
        p = _make_ledger(tmp_path, _iso_hours_ago(48))
        rc = lsc.main(["--ledger", str(p), "--max-age-hours", "24"])
        assert rc == 2
        assert "STALE" in capsys.readouterr().err

    def test_missing_exit_3_infra_defect(self, tmp_path, capsys):
        rc = lsc.main(["--ledger", str(tmp_path / "nope.sqlite")])
        assert rc == 3

    def test_empty_exit_2(self, tmp_path, capsys):
        p = _make_ledger(tmp_path, None)
        rc = lsc.main(["--ledger", str(p), "--max-age-hours", "24"])
        assert rc == 2

    def test_advisory_mode_never_blocks(self, tmp_path):
        p = _make_ledger(tmp_path, _iso_hours_ago(48))
        rc = lsc.main(["--ledger", str(p), "--max-age-hours", "24", "--advisory"])
        assert rc == 0  # stale but advisory

    def test_bypass_env_var(self, tmp_path, monkeypatch):
        p = _make_ledger(tmp_path, _iso_hours_ago(48))
        monkeypatch.setenv("AUTHOR_GATE_STALE_BYPASS", "1")
        rc = lsc.main(["--ledger", str(p), "--max-age-hours", "24"])
        assert rc == 0

    def test_env_threshold_override(self, tmp_path, monkeypatch):
        p = _make_ledger(tmp_path, _iso_hours_ago(10))
        monkeypatch.setenv("AUTHOR_GATE_STALE_THRESHOLD_H", "5")
        rc = lsc.main(["--ledger", str(p)])
        assert rc == 2  # 10h > 5h threshold

    def test_json_output_parses(self, tmp_path, capsys):
        p = _make_ledger(tmp_path, _iso_hours_ago(0.1))
        lsc.main(["--ledger", str(p), "--max-age-hours", "24", "--json"])
        out = capsys.readouterr().out.strip()
        report = json.loads(out)
        assert report["status"] == "fresh"
        assert "age_hours" in report
        assert "threshold_h" in report

    def test_quiet_suppresses_fresh_stdout(self, tmp_path, capsys):
        p = _make_ledger(tmp_path, _iso_hours_ago(0.1))
        lsc.main(["--ledger", str(p), "--max-age-hours", "24", "--quiet"])
        out = capsys.readouterr()
        assert out.out == ""  # nothing on stdout when fresh+quiet

    def test_stale_always_prints_remediation(self, tmp_path, capsys):
        p = _make_ledger(tmp_path, _iso_hours_ago(48))
        lsc.main(["--ledger", str(p), "--max-age-hours", "24"])
        err = capsys.readouterr().err
        assert "Remediation" in err
        assert "queue_to_ledger.py" in err
        assert "rca-author-gate-capture-outage" in err  # points to this RCA
