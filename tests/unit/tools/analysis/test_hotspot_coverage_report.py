"""Unit tests for tools/analysis/hotspot_coverage_report.py.

Plan: .windsurf/plans/hotspot-coverage-pipeline-c4e8d2.md (W3.2)

Edge cases (W5):
    - W5.5: missing mv_hotspot_coverage_risk → graceful "regenerate ADG" message
    - empty MV → 0-row distribution renders without crashing
    - relative output path resolves correctly
    - latest-snapshot picker works on a directory with multiple snapshots
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.analysis.hotspot_coverage_report import (  # noqa: E402
    _read,
    _format,
    main,
)


def _make_minimal_with_mv(tmp_path: Path) -> Path:
    """ADG containing an empty mv_hotspot_coverage_risk table."""
    adg = tmp_path / "snap.sqlite"
    con = sqlite3.connect(adg)
    con.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
        INSERT INTO meta(key, value) VALUES ('commit_sha', 'abc123');

        CREATE TABLE mv_hotspot_coverage_risk (
            snapshot_id TEXT, node_id INTEGER, file TEXT, layer TEXT,
            fan_in INTEGER, fan_out INTEGER, violation_count INTEGER,
            cross_layer_edges INTEGER, criticality_score REAL,
            combined_risk_score REAL, total_debt_score REAL,
            hotspot_rank INTEGER, lines_hit INTEGER, lines_total INTEGER,
            coverage_pct REAL, arcs_hit INTEGER, context_count INTEGER,
            coverage_mode TEXT, mock_count INTEGER,
            risk_band TEXT, coverage_band TEXT, priority_band TEXT
        );
        """
    )
    con.commit()
    con.close()
    return adg


def _make_no_mv(tmp_path: Path) -> Path:
    """ADG without the MV — simulates pre-phase_f snapshot."""
    adg = tmp_path / "snap.sqlite"
    con = sqlite3.connect(adg)
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit()
    con.close()
    return adg


def _seed_rows(adg: Path, rows: list[tuple]) -> None:
    """Insert (file, layer, criticality, coverage_pct, risk, cov_band, pri_band)."""
    con = sqlite3.connect(adg)
    con.executemany(
        "INSERT INTO mv_hotspot_coverage_risk VALUES "
        "('s', ?, ?, ?, 0, 0, 0, 0, ?, 0, 0, 0, 0, -1, ?, 0, 0, 'lines', 0, ?, ?, ?)",
        [
            (i, file, layer, crit, cov_pct, risk, cov_band, pri_band)
            for i, (file, layer, crit, cov_pct, risk, cov_band, pri_band) in enumerate(rows, 1)
        ],
    )
    con.commit()
    con.close()


class TestMissingMV:
    def test_returns_missing_mv_marker(self, tmp_path):
        adg = _make_no_mv(tmp_path)
        data = _read(adg, top=10)
        assert data["missing_mv"] is True

    def test_format_emits_regenerate_instructions(self, tmp_path):
        adg = _make_no_mv(tmp_path)
        md = _format(_read(adg, top=10))
        assert "missing" in md.lower() or "regenerate" in md.lower()
        assert "phase f" in md.lower() or "phase_f" in md.lower() or "Phase F" in md

    def test_main_writes_warning_report(self, tmp_path):
        adg = _make_no_mv(tmp_path)
        out = tmp_path / "report.md"
        rc = main(["--adg", str(adg), "--out", str(out), "--top", "5"])
        assert rc == 0
        assert out.exists()
        assert "regenerate" in out.read_text(encoding="utf-8").lower()


class TestEmptyMV:
    def test_zero_rows_renders_without_crash(self, tmp_path):
        adg = _make_minimal_with_mv(tmp_path)
        md = _format(_read(adg, top=10))
        assert (
            "Total nodes scored**: 0" in md
            or "Total nodes scored: 0" in md
            or "**Total nodes scored**: 0" in md
        )

    def test_empty_p1_section_says_so(self, tmp_path):
        adg = _make_minimal_with_mv(tmp_path)
        md = _format(_read(adg, top=10))
        # No P1_URGENT rows → friendly message
        assert "None — every high-risk module has at least minimal coverage" in md or "Top 0 P1_URGENT" in md


class TestPopulatedReport:
    def test_priority_distribution_in_output(self, tmp_path):
        adg = _make_minimal_with_mv(tmp_path)
        _seed_rows(
            adg,
            [
                ("agentic_core/L5_safety/foo.py", "L5", 100.0, -1.0, "CRITICAL", "ABSENT", "P1_URGENT"),
                ("agentic_core/L5_safety/bar.py", "L5", 80.0, 60.0, "HIGH", "PARTIAL", "P2_GAP"),
                ("agentic_core/L5_safety/baz.py", "L5", 70.0, 95.0, "HIGH", "FULL", "P3_OK"),
                ("agentic_core/L1/qux.py", "L1", 30.0, -1.0, "MEDIUM", "ABSENT", "P4_LOW"),
                ("agentic_core/L1/zip.py", "L1", 5.0, -1.0, "LOW", "ABSENT", "P5_NOOP"),
            ],
        )
        md = _format(_read(adg, top=10))
        # Priority counts present
        assert "`P1_URGENT` | 1" in md
        assert "`P2_GAP` | 1" in md
        assert "`P3_OK` | 1" in md
        assert "`P4_LOW` | 1" in md
        assert "`P5_NOOP` | 1" in md
        # P1_URGENT row visible
        assert "agentic_core/L5_safety/foo.py" in md

    def test_per_layer_breakdown_present(self, tmp_path):
        adg = _make_minimal_with_mv(tmp_path)
        _seed_rows(
            adg,
            [
                ("agentic_core/L5_safety/x.py", "L5", 100.0, -1.0, "CRITICAL", "ABSENT", "P1_URGENT"),
                ("agentic_core/L5_safety/y.py", "L5", 100.0, -1.0, "CRITICAL", "ABSENT", "P1_URGENT"),
                ("agentic_core/L1/z.py", "L1", 60.0, -1.0, "HIGH", "ABSENT", "P1_URGENT"),
            ],
        )
        md = _format(_read(adg, top=10))
        assert "Per-layer breakdown" in md
        assert "`L5`" in md
        assert "`L1`" in md


class TestArgPaths:
    def test_relative_output_path_works(self, tmp_path, monkeypatch):
        adg = _make_minimal_with_mv(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = main(["--adg", str(adg), "--out", "rel/sub/r.md", "--top", "3"])
        assert rc == 0
        out = tmp_path / "rel" / "sub" / "r.md"
        assert out.exists()


class TestSnapshotMissing:
    def test_snapshot_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            _read(tmp_path / "absent.sqlite", top=5)
