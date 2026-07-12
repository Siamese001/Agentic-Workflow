"""Micro-evals for read-only ADG repository-health diagnostics."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.core.repo_health import read_repo_health  # noqa: E402
from tools.adg.mcp.health import HealthDiagnostics  # noqa: E402


def _make_phase_g_db(tmp_path: Path) -> Path:
    path = tmp_path / "adg.sqlite"
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO meta VALUES
                ('commit_sha', 'snapshot'),
                ('sqlite_quick_check', 'ok'),
                ('repo_health_status', 'WATCH');

            CREATE TABLE nodes (id INTEGER PRIMARY KEY);
            CREATE TABLE edges (id INTEGER PRIMARY KEY);
            CREATE TABLE violations (id INTEGER PRIMARY KEY);

            CREATE TABLE mv_repo_health_summary (
                snapshot_id TEXT PRIMARY KEY,
                overall_score REAL,
                status TEXT,
                confidence REAL,
                source_node_count INTEGER,
                source_edge_count INTEGER,
                source_violation_count INTEGER
            );
            INSERT INTO mv_repo_health_summary VALUES
                ('snapshot', 82.5, 'WATCH', 0.95, 0, 0, 0);

            CREATE TABLE mv_repo_health_dimensions (
                dimension TEXT,
                score REAL
            );
            INSERT INTO mv_repo_health_dimensions VALUES
                ('architecture', 70.0),
                ('graph_truth', 95.0);

            CREATE TABLE mv_repo_health_hotspots (
                file TEXT,
                health_risk_score REAL
            );
            INSERT INTO mv_repo_health_hotspots VALUES
                ('agentic_core/a.py', 80.0),
                ('agentic_core/b.py', 50.0);
            """)
    return path


def test_reader_is_fail_soft_for_legacy_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")

    result = read_repo_health(path)

    assert result["available"] is False
    assert result["reason"] == "phase_g_not_materialized"


def test_reader_returns_summary_dimensions_hotspots_and_hardening(tmp_path: Path) -> None:
    path = _make_phase_g_db(tmp_path)

    result = read_repo_health(path, hotspot_limit=1)

    assert result["available"] is True
    assert result["summary"]["status"] == "WATCH"
    assert result["summary"]["effective_status"] == "WATCH"
    assert result["stale"] is False
    assert [row["dimension"] for row in result["dimensions"]] == [
        "architecture",
        "graph_truth",
    ]
    assert [row["file"] for row in result["top_hotspots"]] == ["agentic_core/a.py"]
    assert result["sqlite_hardening"]["sqlite_quick_check"] == "ok"
    assert result["sqlite_hardening"]["repo_health_status"] == "WATCH"


class _DummySQLite:
    def __init__(self, path: Path) -> None:
        self._path = path

    def health(self):
        return "healthy", {"path": str(self._path)}


class _DummyService:
    def __init__(self, path: Path) -> None:
        self._sqlite = _DummySQLite(path)

    def health(self):
        return SimpleNamespace(
            mode="sqlite_only",
            sqlite="healthy",
            redis="unavailable",
            cache_hit_capable=False,
            schema_version="1.0",
            adg_snapshot_id="snapshot",
            views_materialized_at=None,
        )

    def get_status(self):
        return SimpleNamespace(status="ok", data={"timestamp": "snapshot"})

    def get_projection_status(self):
        return SimpleNamespace(data={"available": False, "stale": False, "projection_path": None})


def test_adg_health_report_includes_phase_g_without_changing_primary_status(
    tmp_path: Path,
) -> None:
    path = _make_phase_g_db(tmp_path)
    diagnostics = HealthDiagnostics(_DummyService(path))

    report = diagnostics.full_report()

    assert report["sqlite"] == "healthy"
    assert report["mode"] == "sqlite_only"
    assert report["repo_health"]["available"] is True
    assert report["repo_health"]["summary"]["overall_score"] == 82.5


def test_reader_forces_unknown_when_phase_g_source_counts_are_stale(tmp_path: Path) -> None:
    path = _make_phase_g_db(tmp_path)
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO nodes VALUES (1)")

    result = read_repo_health(path)

    assert result["available"] is True
    assert result["stale"] is True
    assert result["summary"]["status"] == "WATCH"
    assert result["summary"]["effective_status"] == "UNKNOWN"
    assert result["stale_reasons"] == ["nodes:materialized=0,current=1"]
    assert result["source_counts_current"]["nodes"] == 1
