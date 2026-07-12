"""Micro-evals for Phase G repository-health materialization."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.materialized_views.phase_g_repo_health import (  # noqa: E402
    _score_higher_is_better,
    _score_lower_is_better,
    materialize_phase_g,
)
from tools.generate.sqlite_hardening import harden_sqlite_connection  # noqa: E402


def _create_canonical(tmp_path: Path) -> Path:
    path = tmp_path / "adg.sqlite"
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO meta VALUES ('commit_sha', 'test-snapshot');

            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                layer TEXT NOT NULL,
                resolved_path TEXT NOT NULL
            );

            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER NOT NULL,
                dst_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                source_file TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                symbol TEXT NOT NULL DEFAULT '',
                authority TEXT NOT NULL DEFAULT 'verified',
                bucket TEXT NOT NULL DEFAULT 'static',
                resolution_status TEXT NOT NULL DEFAULT 'VERIFIED_MODULE',
                authority_status TEXT NOT NULL DEFAULT 'AUTHORITATIVE',
                FOREIGN KEY(src_id) REFERENCES nodes(id),
                FOREIGN KEY(dst_id) REFERENCES nodes(id)
            );

            CREATE TABLE violations (
                id INTEGER PRIMARY KEY,
                edge_id INTEGER,
                file_path TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                disposition TEXT NOT NULL DEFAULT 'untriaged'
            );
            """)
    return path


def _seed_full_evidence(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            INSERT INTO nodes VALUES
                (1, 'ADG::Module::agentic_core/a.py', 'module', 'L2', 'agentic_core/a.py'),
                (2, 'ADG::Module::agentic_core/b.py', 'module', 'L4', 'agentic_core/b.py'),
                (3, 'ADG::Module::tests/test_a.py', 'module', 'L_TEST', 'tests/test_a.py');

            INSERT INTO edges(
                id, src_id, dst_id, relation_type, source_file, line_no,
                authority, bucket, resolution_status, authority_status
            ) VALUES
                (1, 1, 2, 'imports', 'agentic_core/a.py', 10,
                 'verified', 'static', 'VERIFIED_MODULE', 'AUTHORITATIVE'),
                (2, 1, 2, 'in_cycle', 'agentic_core/a.py', 11,
                 'unresolved', 'static', 'UNRESOLVED_MODULE', 'RISK_SIGNAL_ONLY'),
                (3, 1, 2, 'dynamic_exec', 'agentic_core/a.py', 12,
                 'dynamic', 'static', 'UNRESOLVED_DYNAMIC', 'UNKNOWN_NOT_PROOF'),
                (4, 2, 1, 'imports', 'agentic_core/b.py', 20,
                 'unresolved', 'static', 'UNRESOLVED_MODULE', 'PARTIAL'),
                (5, 3, 1, 'imports', 'tests/test_a.py', 5,
                 'test_only', 'static', 'VERIFIED_MODULE', 'EXCLUDED_TEST_ONLY');

            INSERT INTO violations(
                id, edge_id, file_path, line_no, category, severity, message, disposition
            ) VALUES
                (1, 2, 'agentic_core/a.py', 11, 'structural', 'HIGH', 'cycle', 'untriaged'),
                (2, 4, 'agentic_core/b.py', 20, 'antipattern', 'MEDIUM', 'risk', 'untriaged'),
                (3, 5, 'tests/test_a.py', 5, 'test', 'HIGH', 'ignored by hotspot path', 'resolved');

            CREATE TABLE mv_write_sovereignty_paths (
                file TEXT NOT NULL,
                is_uwg_routed INTEGER NOT NULL
            );
            INSERT INTO mv_write_sovereignty_paths VALUES
                ('agentic_core/a.py', 0),
                ('agentic_core/b.py', 1);

            CREATE TABLE mv_gateway_bypass_paths (file TEXT NOT NULL);
            INSERT INTO mv_gateway_bypass_paths VALUES ('agentic_core/a.py');

            CREATE TABLE mv_unknown_taxonomy_and_orphans (file TEXT NOT NULL);
            INSERT INTO mv_unknown_taxonomy_and_orphans VALUES ('agentic_core/b.py');

            CREATE TABLE mv_hotspot_coverage_risk (
                node_id INTEGER,
                file TEXT,
                layer TEXT,
                criticality_score REAL,
                combined_risk_score REAL,
                total_debt_score REAL,
                coverage_pct REAL,
                priority_band TEXT,
                risk_band TEXT
            );
            INSERT INTO mv_hotspot_coverage_risk VALUES
                (1, 'agentic_core/a.py', 'L2', 100.0, 50.0, 18.0, -1.0, 'P1_URGENT', 'CRITICAL'),
                (2, 'agentic_core/b.py', 'L4', 20.0, 5.0, 2.0, 95.0, 'P3_OK', 'LOW');

            CREATE TABLE mv_snapshot_baseline (debt_score REAL NOT NULL);
            INSERT INTO mv_snapshot_baseline VALUES (20.0);

            CREATE TABLE mv_snapshot_regression_summary (
                violation_delta INTEGER,
                cross_layer_delta INTEGER,
                bypass_delta INTEGER,
                debt_delta REAL,
                is_first_run INTEGER
            );
            INSERT INTO mv_snapshot_regression_summary VALUES (2, 3, 1, 4.0, 0);

            CREATE TABLE mv_high_fan_in_out_with_defects (
                node_id INTEGER,
                combined_risk_score REAL
            );
            INSERT INTO mv_high_fan_in_out_with_defects VALUES (1, 50.0);
            """)
        harden_sqlite_connection(conn)


def _row(path: Path, sql: str) -> sqlite3.Row:
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(sql).fetchone()
        assert row is not None
        return row


class TestScoringContract:
    def test_lower_is_better_is_monotonic(self) -> None:
        scores = [_score_lower_is_better(value, 1, 10) for value in (0, 1, 5, 10, 20)]
        assert scores == sorted(scores, reverse=True)
        assert scores[0] == 100.0
        assert scores[-1] == 0.0

    def test_higher_is_better_is_monotonic(self) -> None:
        scores = [_score_higher_is_better(value, 70, 90) for value in (0, 50, 70, 80, 90)]
        assert scores == sorted(scores)
        assert scores[0] == 0.0
        assert scores[-1] == 100.0


class TestMaterialization:
    def test_full_evidence_emits_auditable_summary_and_hotspots(self, tmp_path: Path) -> None:
        path = _create_canonical(tmp_path)
        _seed_full_evidence(path)

        counts = materialize_phase_g(path)

        assert counts == {
            "mv_repo_health_signals": 21,
            "mv_repo_health_dimensions": 6,
            "mv_repo_health_summary": 1,
            "mv_repo_health_hotspots": 2,
        }

        summary = _row(path, "SELECT * FROM mv_repo_health_summary")
        assert summary["status"] in {"AT_RISK", "CRITICAL"}
        assert summary["confidence"] >= 0.70
        assert summary["active_high_violation_count"] == 1
        assert summary["p1_urgent_hotspot_count"] == 1
        assert summary["top_hotspot_file"] == "agentic_core/a.py"
        assert summary["metric_contract_version"] == "1.0"
        assert summary["source_node_count"] == 3
        assert summary["source_edge_count"] == 5
        assert summary["source_violation_count"] == 3

        hotspot = _row(
            path,
            "SELECT * FROM mv_repo_health_hotspots " "ORDER BY health_risk_score DESC LIMIT 1",
        )
        assert hotspot["file"] == "agentic_core/a.py"
        assert hotspot["health_risk_band"] in {"P0_CRITICAL", "P1_HIGH"}
        assert hotspot["primary_driver"] in {
            "governance",
            "coverage",
            "topology",
            "criticality",
            "debt",
        }
        assert hotspot["evidence_count"] > 0

        signal = _row(
            path,
            "SELECT * FROM mv_repo_health_signals " "WHERE signal_key='authoritative_edge_pct'",
        )
        assert signal["available"] == 1
        assert signal["source_table"] == "edges.authority_status"
        assert signal["value"] < 100.0

    def test_missing_optional_evidence_emits_unknown_not_false_green(self, tmp_path: Path) -> None:
        path = _create_canonical(tmp_path)
        with sqlite3.connect(path) as conn:
            conn.execute(
                "INSERT INTO nodes VALUES "
                "(1, 'ADG::Module::agentic_core/a.py', 'module', 'L2', 'agentic_core/a.py')"
            )
            conn.commit()

        materialize_phase_g(path)
        summary = _row(path, "SELECT * FROM mv_repo_health_summary")
        assert summary["status"] == "UNKNOWN"
        assert summary["confidence"] < 0.70

        unavailable = _row(
            path,
            "SELECT COUNT(*) AS n FROM mv_repo_health_signals WHERE available=0",
        )
        assert unavailable["n"] > 0

    def test_idempotent_refresh_replaces_rows(self, tmp_path: Path) -> None:
        path = _create_canonical(tmp_path)
        _seed_full_evidence(path)

        first = materialize_phase_g(path)
        second = materialize_phase_g(path)

        assert first == second
        assert _row(path, "SELECT COUNT(*) AS n FROM mv_repo_health_summary")["n"] == 1
        assert _row(path, "SELECT COUNT(*) AS n FROM mv_repo_health_hotspots")["n"] == 2

    def test_test_modules_are_not_ranked_as_repo_hotspots(self, tmp_path: Path) -> None:
        path = _create_canonical(tmp_path)
        _seed_full_evidence(path)
        materialize_phase_g(path)

        paths = {row[0] for row in sqlite3.connect(path).execute("SELECT file FROM mv_repo_health_hotspots")}
        assert "tests/test_a.py" not in paths

    def test_summary_meta_is_published_for_lightweight_consumers(self, tmp_path: Path) -> None:
        path = _create_canonical(tmp_path)
        _seed_full_evidence(path)
        materialize_phase_g(path)

        with sqlite3.connect(path) as conn:
            meta = dict(conn.execute("SELECT key, value FROM meta WHERE key LIKE 'repo_health_%'"))
        assert meta["repo_health_contract_version"] == "1.0"
        assert meta["repo_health_status"] in {"AT_RISK", "CRITICAL"}
        assert 0.0 <= float(meta["repo_health_score"]) <= 100.0
        assert 0.0 <= float(meta["repo_health_confidence"]) <= 1.0


def test_zero_risk_module_has_no_fabricated_primary_driver(tmp_path: Path) -> None:
    path = _create_canonical(tmp_path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT INTO nodes VALUES "
            "(1, 'ADG::Module::agentic_core/clean.py', 'module', 'L2', 'agentic_core/clean.py')"
        )
        conn.commit()

    materialize_phase_g(path)
    hotspot = _row(path, "SELECT * FROM mv_repo_health_hotspots")

    assert hotspot["health_risk_score"] == 0.0
    assert hotspot["primary_driver"] == "none"
    assert hotspot["recommended_action"] == "No material graph-health risk is currently evidenced for this module."
