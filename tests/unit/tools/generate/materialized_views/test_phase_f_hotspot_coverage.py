"""Unit tests for tools/generate/materialized_views/phase_f_hotspot_coverage.py.

Plan: .windsurf/plans/hotspot-coverage-pipeline-c4e8d2.md (W2)

Edge cases (W5 hardening):
    - W5.5: missing upstream MV (no mv_path_criticality_rollup) → graceful
            fallback to all-LOW risk band
    - missing coverage_by_path → table auto-created empty, all coverage_band='ABSENT'
    - missing test_stubs → mock_count = 0
    - empty nodes table → 0 rows
    - priority_band derivation correctness for each (risk, coverage) combo
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest  # noqa: F401  (used for fixtures / parametrize in future tests)

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.materialized_views.phase_f_hotspot_coverage import (  # noqa: E402
    materialize_phase_f,
)


# ---------------------------------------------------------------------------
# Skeleton ADG factory — only the tables phase_f reads
# ---------------------------------------------------------------------------


def _make_adg(tmp_path: Path) -> Path:
    """Build a minimal ADG snapshot containing the tables phase_f reads."""
    adg = tmp_path / "adg.sqlite"
    con = sqlite3.connect(adg)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
        INSERT INTO meta(key, value) VALUES ('commit_sha', 'test_commit');

        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            entity_type TEXT,
            layer TEXT,
            resolved_path TEXT
        );

        CREATE TABLE mv_path_criticality_rollup (
            snapshot_id TEXT,
            node_id INTEGER,
            adg_name TEXT,
            layer TEXT,
            resolved_path TEXT,
            fan_in INTEGER,
            fan_out INTEGER,
            violation_count INTEGER,
            cross_layer_edges INTEGER,
            criticality_score REAL
        );

        CREATE TABLE mv_high_fan_in_out_with_defects (
            snapshot_id TEXT,
            node_id INTEGER,
            adg_name TEXT,
            layer TEXT,
            resolved_path TEXT,
            fan_in INTEGER,
            fan_out INTEGER,
            degree INTEGER,
            violation_count INTEGER,
            combined_risk_score REAL
        );

        CREATE TABLE mv_debt_concentration_hotspots (
            snapshot_id TEXT,
            file TEXT,
            layer TEXT,
            p0_count INTEGER,
            p1_count INTEGER,
            p2_count INTEGER,
            p3_count INTEGER,
            total_violations INTEGER,
            total_debt_score REAL,
            hotspot_rank INTEGER
        );
        """
    )
    con.commit()
    con.close()
    return adg


def _seed_modules(
    adg: Path,
    modules: list[tuple[int, str, str, float]],
) -> None:
    """Insert (node_id, resolved_path, layer, criticality_score) tuples."""
    con = sqlite3.connect(adg)
    cur = con.cursor()
    for node_id, rel, layer, crit in modules:
        cur.execute(
            "INSERT INTO nodes(id, adg_name, entity_type, layer, resolved_path) "
            "VALUES (?, ?, 'module', ?, ?)",
            (node_id, f"ADG::Module::{rel}", layer, rel),
        )
        cur.execute(
            "INSERT INTO mv_path_criticality_rollup(snapshot_id, node_id, "
            "adg_name, layer, resolved_path, fan_in, fan_out, violation_count, "
            "cross_layer_edges, criticality_score) "
            "VALUES ('s', ?, ?, ?, ?, 0, 0, 0, 0, ?)",
            (node_id, f"ADG::Module::{rel}", layer, rel, crit),
        )
    con.commit()
    con.close()


def _seed_coverage(adg: Path, coverage_rows: list[tuple[str, float]]) -> None:
    """Insert (resolved_path, coverage_pct) into coverage_by_path."""
    con = sqlite3.connect(adg)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS coverage_by_path (
            resolved_path TEXT PRIMARY KEY,
            lines_hit INTEGER NOT NULL DEFAULT 0,
            arcs_hit INTEGER NOT NULL DEFAULT 0,
            context_count INTEGER NOT NULL DEFAULT 0,
            lines_total INTEGER NOT NULL DEFAULT -1,
            coverage_pct REAL NOT NULL DEFAULT -1.0,
            mode TEXT NOT NULL DEFAULT 'empty',
            ingested_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    for rel, pct in coverage_rows:
        cur.execute(
            "INSERT OR REPLACE INTO coverage_by_path("
            "resolved_path, lines_hit, arcs_hit, context_count, "
            "lines_total, coverage_pct, mode, ingested_at) "
            "VALUES (?, 50, 0, 1, 100, ?, 'lines', '2026-04-28')",
            (rel, pct),
        )
    con.commit()
    con.close()


def _row(adg: Path, where: str = "1=1") -> list[sqlite3.Row]:
    con = sqlite3.connect(adg)
    con.row_factory = sqlite3.Row
    rows = list(con.execute(f"SELECT * FROM mv_hotspot_coverage_risk WHERE {where}"))
    con.close()
    return rows


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestEmptyADG:
    def test_no_modules_yields_zero_rows(self, tmp_path):
        adg = _make_adg(tmp_path)
        counts = materialize_phase_f(adg)
        assert counts["mv_hotspot_coverage_risk"] == 0


class TestMissingCoverageTable:
    def test_table_auto_created_when_absent(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(adg, [(1, "agentic_core/L5_safety/foo.py", "L5", 100.0)])
        # Do NOT seed coverage_by_path — phase_f should auto-create it
        counts = materialize_phase_f(adg)
        assert counts["mv_hotspot_coverage_risk"] == 1
        rows = _row(adg)
        assert rows[0]["coverage_band"] == "ABSENT"
        assert rows[0]["coverage_pct"] == -1.0


class TestPriorityBandDerivation:
    def test_high_risk_no_coverage_is_p1_urgent(self, tmp_path):
        adg = _make_adg(tmp_path)
        # 5 modules, criticality 10..50 → P75 = 40, P95 = 50
        _seed_modules(
            adg,
            [(i, f"agentic_core/L5_safety/m{i}.py", "L5", float(i * 10)) for i in range(1, 6)],
        )
        # No coverage seeded
        materialize_phase_f(adg)
        rows = _row(adg, "criticality_score = 50.0")
        assert len(rows) == 1
        assert rows[0]["risk_band"] == "CRITICAL"
        assert rows[0]["coverage_band"] == "ABSENT"
        assert rows[0]["priority_band"] == "P1_URGENT"

    def test_high_risk_full_coverage_is_p3_ok(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(
            adg,
            [(i, f"agentic_core/L5_safety/m{i}.py", "L5", float(i * 10)) for i in range(1, 6)],
        )
        _seed_coverage(adg, [("agentic_core/L5_safety/m5.py", 95.0)])
        materialize_phase_f(adg)
        rows = _row(adg, "criticality_score = 50.0")
        assert rows[0]["risk_band"] == "CRITICAL"
        assert rows[0]["coverage_band"] == "FULL"
        assert rows[0]["priority_band"] == "P3_OK"

    def test_high_risk_partial_coverage_is_p2_gap(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(
            adg,
            [(i, f"agentic_core/L5_safety/m{i}.py", "L5", float(i * 10)) for i in range(1, 6)],
        )
        _seed_coverage(adg, [("agentic_core/L5_safety/m5.py", 55.0)])
        materialize_phase_f(adg)
        rows = _row(adg, "criticality_score = 50.0")
        assert rows[0]["coverage_band"] == "PARTIAL"
        assert rows[0]["priority_band"] == "P2_GAP"

    def test_low_risk_is_p5_noop(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(
            adg,
            [(i, f"agentic_core/L5_safety/m{i}.py", "L5", float(i * 10)) for i in range(1, 6)],
        )
        materialize_phase_f(adg)
        rows = _row(adg, "criticality_score = 10.0")
        assert rows[0]["risk_band"] == "LOW"
        assert rows[0]["priority_band"] == "P5_NOOP"


class TestPathFiltering:
    def test_tests_directory_excluded(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(
            adg,
            [
                (1, "tests/unit/foo_test.py", "L_TEST", 100.0),
                (2, "agentic_core/L5_safety/real.py", "L5", 100.0),
            ],
        )
        materialize_phase_f(adg)
        rows = _row(adg)
        files = {r["file"] for r in rows}
        assert "agentic_core/L5_safety/real.py" in files
        assert "tests/unit/foo_test.py" not in files

    def test_tools_directory_excluded(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(adg, [(1, "tools/whatever.py", "L_TOOLS", 100.0)])
        materialize_phase_f(adg)
        assert _row(adg) == []


class TestIdempotency:
    def test_double_materialize_no_duplication(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(adg, [(1, "agentic_core/L5_safety/foo.py", "L5", 100.0)])
        materialize_phase_f(adg)
        materialize_phase_f(adg)
        rows = _row(adg)
        assert len(rows) == 1


class TestPercentileFallback:
    def test_empty_criticality_table_yields_all_low_risk(self, tmp_path):
        adg = _make_adg(tmp_path)
        # Modules with NO matching mv_path_criticality_rollup row
        con = sqlite3.connect(adg)
        cur = con.cursor()
        for i in range(1, 4):
            cur.execute(
                "INSERT INTO nodes(id, adg_name, entity_type, layer, resolved_path) "
                "VALUES (?, ?, 'module', 'L5', ?)",
                (i, f"ADG::Module::m{i}", f"agentic_core/L5_safety/m{i}.py"),
            )
        con.commit()
        con.close()
        materialize_phase_f(adg)
        rows = _row(adg)
        assert len(rows) == 3
        # All should be LOW risk because criticality_score is COALESCEd to 0.0
        # and percentiles are (0,0,0)
        for r in rows:
            assert r["risk_band"] == "LOW"
            assert r["priority_band"] == "P5_NOOP"


class TestSchemaDefinition:
    def test_expected_columns_present(self, tmp_path):
        adg = _make_adg(tmp_path)
        _seed_modules(adg, [(1, "agentic_core/L5_safety/foo.py", "L5", 100.0)])
        materialize_phase_f(adg)
        con = sqlite3.connect(adg)
        cols = {r[1] for r in con.execute("PRAGMA table_info(mv_hotspot_coverage_risk)")}
        con.close()
        required = {
            "snapshot_id",
            "node_id",
            "file",
            "layer",
            "fan_in",
            "fan_out",
            "violation_count",
            "cross_layer_edges",
            "criticality_score",
            "combined_risk_score",
            "total_debt_score",
            "hotspot_rank",
            "lines_hit",
            "lines_total",
            "coverage_pct",
            "arcs_hit",
            "context_count",
            "coverage_mode",
            "mock_count",
            "risk_band",
            "coverage_band",
            "priority_band",
        }
        assert required.issubset(cols), f"missing: {required - cols}"
