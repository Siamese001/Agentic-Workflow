"""Tests for `ops_scripts/calibration/_router_calibration_base.py`.

Constitutional §28 / closed-loop-router-enforcement.md.
Covers Wilson lower-bound, ledger snapshot read paths, report rendering for
the three states (unavailable / empty / populated), and the generate() round-trip.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ops_scripts.calibration import _router_calibration_base as base


@pytest.fixture
def spec(tmp_path, monkeypatch) -> base.RouterCalibrationSpec:
    """Return a spec wired to a tmp ledgers/reports root."""
    monkeypatch.setattr(base, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(base, "LEDGERS_DIR", tmp_path / "artifacts" / "ledgers")
    monkeypatch.setattr(
        base, "REPORT_BASE_DIR", tmp_path / "docs" / "reports" / "calibration" / "routers"
    )
    return base.RouterCalibrationSpec(
        layer="L0",
        router="bandit",
        purpose="test purpose",
        nominal_thresholds={"floor": 0.5},
    )


# ---------------------------------------------------------------------------
# Wilson lower bound
# ---------------------------------------------------------------------------


class TestWilsonLower:
    def test_zero_total_returns_zero(self) -> None:
        assert base._wilson_lower(0, 0) == 0.0

    def test_zero_successes_is_zero_or_low(self) -> None:
        # 0/100 → Wilson lower bound is 0.0 (clamped)
        assert base._wilson_lower(0, 100) == pytest.approx(0.0, abs=0.01)

    def test_perfect_score_returns_high_bound(self) -> None:
        # 100/100 → Wilson lower bound > 0.95
        assert base._wilson_lower(100, 100) > 0.95

    def test_half_score_below_half(self) -> None:
        # 50/100 → Wilson lower bound < 0.5 (because of margin)
        assert base._wilson_lower(50, 100) < 0.5

    def test_promote_floor_boundary(self) -> None:
        # 25/30 = 83% → Wilson lower bound ≈ 0.66 (above the §28 floor of 0.60)
        assert base._wilson_lower(25, 30) > 0.60

    def test_too_few_samples_below_floor(self) -> None:
        # 5/6 = 83% but n=6 too small → Wilson < 0.60
        assert base._wilson_lower(5, 6) < 0.60


# ---------------------------------------------------------------------------
# ISO week
# ---------------------------------------------------------------------------


class TestIsoWeek:
    def test_format_padded(self) -> None:
        dt = datetime(2026, 1, 5, tzinfo=timezone.utc)  # ISO week 2
        assert base.iso_week(dt) == "2026-W02"

    def test_late_year(self) -> None:
        dt = datetime(2026, 12, 28, tzinfo=timezone.utc)  # ISO week 53
        result = base.iso_week(dt)
        assert result.startswith("2026-W")
        # Format YYYY-Www → 8 chars (e.g. "2026-W53")
        assert len(result) == 8

    def test_default_uses_now(self) -> None:
        result = base.iso_week()
        assert result.startswith("20")
        assert "-W" in result


# ---------------------------------------------------------------------------
# Ledger snapshot — three states
# ---------------------------------------------------------------------------


class TestLedgerSnapshot:
    def test_missing_ledger_unavailable(self, spec) -> None:
        snap = base._read_ledger(spec)
        assert not snap.available
        assert "not yet" in (snap.error or "")
        assert snap.total_rows == 0

    def test_present_but_no_events_table(self, spec) -> None:
        spec.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(spec.ledger_path))
        conn.execute("CREATE TABLE wrong_table (id INTEGER)")
        conn.commit()
        conn.close()
        snap = base._read_ledger(spec)
        assert not snap.available
        assert "events" in (snap.error or "")

    def test_empty_events_table(self, spec) -> None:
        _create_events_table(spec.ledger_path)
        snap = base._read_ledger(spec)
        assert snap.available
        assert snap.total_rows == 0
        assert snap.bound_rows == 0

    def test_populated_events_with_outcomes(self, spec) -> None:
        _create_events_table(spec.ledger_path)
        _insert_events(spec.ledger_path, [
            ("predicted", "high", 50, None),
            ("bound", "high", 100, json.dumps({"success": True})),
            ("bound", "high", 200, json.dumps({"success": True})),
            ("bound", "low", 150, json.dumps({"success": False})),
        ])
        snap = base._read_ledger(spec)
        assert snap.available
        assert snap.total_rows == 4
        assert snap.predicted_rows == 1
        assert snap.bound_rows == 3
        assert snap.success_rows == 2
        assert snap.band_distribution == {"high": 3, "low": 1}
        assert sorted(snap.latencies_ms) == [50, 100, 150, 200]


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


class TestRenderReport:
    def test_unavailable_renders_awaiting_section(self, spec) -> None:
        report = base.render_report(spec)
        assert spec.key in report
        assert "Awaiting telemetry" in report
        assert "Nominal Thresholds" in report
        assert "Sunset Tracking" in report

    def test_empty_renders_empty_message(self, spec) -> None:
        _create_events_table(spec.ledger_path)
        report = base.render_report(spec)
        assert "awaiting first router decisions" in report

    def test_populated_renders_metrics(self, spec) -> None:
        _create_events_table(spec.ledger_path)
        _insert_events(spec.ledger_path, [
            ("bound", "high", 100, json.dumps({"success": True})),
            ("bound", "high", 100, json.dumps({"success": True})),
            ("bound", "high", 100, json.dumps({"success": True})),
            ("bound", "low", 100, json.dumps({"success": False})),
        ])
        report = base.render_report(spec)
        assert "Wilson lower bound" in report
        assert "Total rows" in report
        # Success rate = 0.75 → look for the literal
        assert "0.750" in report

    def test_thresholds_render_as_table(self, spec) -> None:
        report = base.render_report(spec)
        assert "| `floor` | 0.5 |" in report

    def test_no_thresholds_renders_placeholder(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setattr(base, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(base, "LEDGERS_DIR", tmp_path / "art")
        monkeypatch.setattr(base, "REPORT_BASE_DIR", tmp_path / "rep")
        s = base.RouterCalibrationSpec(layer="L0", router="bandit", purpose="x")
        report = base.render_report(s)
        assert "no nominal thresholds declared" in report


# ---------------------------------------------------------------------------
# Drift comparison
# ---------------------------------------------------------------------------


class TestDrift:
    def test_no_prior_report_baseline(self, spec) -> None:
        result = base.generate(spec)
        report = result.output_path.read_text(encoding="utf-8")
        assert "drift baseline established this week" in report

    def test_prior_report_referenced(self, spec) -> None:
        # Write a prior-week file
        spec.report_dir.mkdir(parents=True, exist_ok=True)
        prior = spec.report_dir / "2025-W50.md"
        prior.write_text("# prior", encoding="utf-8")
        report = base.render_report(spec, now=datetime(2026, 1, 5, tzinfo=timezone.utc))
        assert "Prior report" in report
        assert "2025-W50.md" in report


# ---------------------------------------------------------------------------
# generate() round-trip
# ---------------------------------------------------------------------------


class TestGenerate:
    def test_writes_file_with_iso_week_name(self, spec) -> None:
        now = datetime(2026, 4, 26, 14, 0, tzinfo=timezone.utc)
        result = base.generate(spec, now=now)
        assert result.output_path.exists()
        assert result.output_path.name == "2026-W17.md"
        assert result.output_path.parent == spec.report_dir
        assert result.bytes_written > 0
        assert result.spec_key == "L0_bandit"

    def test_idempotent_within_week(self, spec) -> None:
        now = datetime(2026, 4, 26, 14, 0, tzinfo=timezone.utc)
        r1 = base.generate(spec, now=now)
        r2 = base.generate(spec, now=now)
        assert r1.output_path == r2.output_path
        assert r1.bytes_written == r2.bytes_written

    def test_available_flag_reflects_ledger_state(self, spec) -> None:
        # No ledger
        result_unavail = base.generate(spec)
        assert not result_unavail.available
        # With ledger
        _create_events_table(spec.ledger_path)
        result_avail = base.generate(spec)
        assert result_avail.available


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class TestCli:
    def test_cli_returns_zero_on_success(self, spec, capsys) -> None:
        rc = base.cli(spec, [])
        out = capsys.readouterr().out
        assert rc == 0
        assert spec.key in out
        assert "wrote" in out

    def test_cli_returns_two_on_oserror(self, spec, monkeypatch, capsys) -> None:
        def boom(*a, **kw) -> base.GenerationResult:
            raise OSError("disk full")

        monkeypatch.setattr(base, "generate", boom)
        rc = base.cli(spec, [])
        err = capsys.readouterr().err
        assert rc == 2
        assert "FAILED" in err
        assert "disk full" in err


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_events_table(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE events (
            event_id TEXT PRIMARY KEY,
            event_kind TEXT,
            ts_utc TEXT,
            status TEXT,
            score_band TEXT,
            score_numeric REAL,
            latency_ms INTEGER,
            prediction_json TEXT,
            outcome_json TEXT,
            metadata_json TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _insert_events(db_path: Path, rows: list[tuple]) -> None:
    """Insert rows of (status, score_band, latency_ms, outcome_json)."""
    conn = sqlite3.connect(str(db_path))
    for i, (status, band, latency, outcome) in enumerate(rows):
        conn.execute(
            "INSERT INTO events (event_id, status, score_band, latency_ms, outcome_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (f"e{i}", status, band, latency, outcome),
        )
    conn.commit()
    conn.close()
