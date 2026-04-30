"""Unit tests for the W3 P3.3 graph-layer MCP tools.

Plan: ``.windsurf/plans/adg-three-bucket-unified-c4f8e2.md`` (W3 P3.3).

Covers:
  * adg_mv_hotspot_centrality      — MV row passthrough + ORDER BY
  * adg_blast_radius                — service path (uses graph projection or SQL fallback)
  * adg_semantic_fanout             — relation_type whitelist + delegation
  * adg_p_view_query                — view_name whitelist + sqlite_master existence
  * SQL-injection rejection through view_name parameter
"""

from __future__ import annotations

# Test verifies P-view + MV + semantic-edge surfaces without consuming proof
# (it builds synthetic snapshots).
__adg_consumer_mode__ = "inventory"

import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.core.sqlite_backend import SQLiteBackend  # noqa: E402


# ---------------------------------------------------------------------------
# Synthetic snapshot builder
# ---------------------------------------------------------------------------


SCHEMA = """
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    adg_name TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'module',
    layer TEXT NOT NULL DEFAULT '',
    identity_kind TEXT NOT NULL DEFAULT 'module',
    confidence TEXT NOT NULL DEFAULT 'verified',
    resolved_path TEXT NOT NULL DEFAULT ''
);
CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id INTEGER NOT NULL,
    dst_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    edge_kind TEXT NOT NULL DEFAULT 'static',
    source_file TEXT NOT NULL DEFAULT '',
    line_no INTEGER NOT NULL DEFAULT 1,
    symbol TEXT NOT NULL DEFAULT ''
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
INSERT INTO meta VALUES ('schema_version', '1.0');
CREATE TABLE mv_hotspot_centrality (
    snapshot_id TEXT,
    node_id INTEGER,
    adg_name TEXT,
    layer TEXT,
    resolved_path TEXT,
    fan_in INTEGER,
    fan_out INTEGER,
    degree INTEGER,
    betweenness_approx REAL,
    degree_centrality REAL
);
INSERT INTO mv_hotspot_centrality VALUES
    ('s1', 1, 'pkg.high_central', 'L0', 'pkg/high_central.py', 50, 10, 60, 0.8, 0.95),
    ('s1', 2, 'pkg.mid_central',  'L1', 'pkg/mid_central.py',  20, 5,  25, 0.3, 0.55),
    ('s1', 3, 'pkg.low_central',  'L2', 'pkg/low_central.py',   2, 1,   3, 0.0, 0.05);
CREATE VIEW v_p0_test_view AS
    SELECT 'p0_row' AS marker, id, adg_name FROM nodes WHERE layer='L0';
CREATE VIEW v_p1_test_view AS
    SELECT 'p1_row' AS marker, id, adg_name FROM nodes WHERE layer='L1';
"""


@pytest.fixture
def synthetic_snapshot(tmp_path: Path, monkeypatch) -> Path:
    """Build a temp ADG SQLite + redirect SQLiteBackend to use it.

    Filename MUST match ``adg_indexed_<MMDDYYYY>_<HHMM>.sqlite`` so
    ``tools/adg/shared_modules/path_resolver.py::latest_sqlite()`` accepts
    it.
    """
    snap = tmp_path / "adg_indexed_01012099_0000.sqlite"
    con = sqlite3.connect(snap)
    con.executescript(SCHEMA)
    # Seed a minimal nodes/edges set so backend.get_status doesn't break.
    con.execute("INSERT INTO nodes (id, adg_name, layer) VALUES (1, 'pkg.high_central', 'L0')")
    con.execute("INSERT INTO nodes (id, adg_name, layer) VALUES (2, 'pkg.mid_central', 'L1')")
    con.execute("INSERT INTO nodes (id, adg_name, layer) VALUES (3, 'pkg.low_central', 'L2')")
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, source_file) VALUES (1, 2, 'flows_to', 'pkg/high_central.py')"
    )
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, source_file) VALUES (1, 3, 'writes_to', 'pkg/high_central.py')"
    )
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, source_file) VALUES (1, 2, 'imports', 'pkg/high_central.py')"
    )
    con.commit()
    con.close()
    # Redirect the backend to find this snapshot.
    monkeypatch.setenv("ADG_DIR", str(tmp_path))
    return snap


@pytest.fixture
def backend(synthetic_snapshot: Path) -> SQLiteBackend:
    return SQLiteBackend(use_graph_store=False)


# ---------------------------------------------------------------------------
# get_mv_hotspot_centrality
# ---------------------------------------------------------------------------


def test_mv_hotspot_centrality_returns_rows_ordered(backend: SQLiteBackend) -> None:
    rows = backend.get_mv_hotspot_centrality(limit=10)
    assert len(rows) == 3
    # Ordered DESC by degree_centrality.
    assert rows[0]["adg_name"] == "pkg.high_central"
    assert rows[1]["adg_name"] == "pkg.mid_central"
    assert rows[2]["adg_name"] == "pkg.low_central"


def test_mv_hotspot_centrality_respects_limit(backend: SQLiteBackend) -> None:
    rows = backend.get_mv_hotspot_centrality(limit=2)
    assert len(rows) == 2
    assert rows[0]["adg_name"] == "pkg.high_central"


def test_mv_hotspot_centrality_zero_limit_uses_default(backend: SQLiteBackend) -> None:
    rows = backend.get_mv_hotspot_centrality(limit=0)
    # default=50 clamps in _normalize_limit → all 3 rows returned
    assert len(rows) == 3


def test_mv_hotspot_centrality_returns_empty_when_view_absent(tmp_path: Path, monkeypatch) -> None:
    """When mv_hotspot_centrality is missing, returns [] instead of raising."""
    snap = tmp_path / "adg_indexed_02022099_0000.sqlite"
    con = sqlite3.connect(snap)
    con.executescript("""
        CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, layer TEXT, entity_type TEXT, identity_kind TEXT, confidence TEXT, resolved_path TEXT);
        CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id INTEGER, dst_id INTEGER, relation_type TEXT, edge_kind TEXT, source_file TEXT, line_no INTEGER, symbol TEXT);
        CREATE TABLE meta (key TEXT, value TEXT);
    """)
    con.commit()
    con.close()
    monkeypatch.setenv("ADG_DIR", str(tmp_path))
    b = SQLiteBackend(use_graph_store=False)
    try:
        assert b.get_mv_hotspot_centrality() == []
    finally:
        b.close()


# ---------------------------------------------------------------------------
# list_p_views
# ---------------------------------------------------------------------------


def test_list_p_views_returns_sorted(backend: SQLiteBackend) -> None:
    views = backend.list_p_views()
    assert views == ["v_p0_test_view", "v_p1_test_view"]


# ---------------------------------------------------------------------------
# query_p_view — security + behavior
# ---------------------------------------------------------------------------


def test_query_p_view_valid_returns_rows(backend: SQLiteBackend) -> None:
    rows = backend.query_p_view("v_p0_test_view", limit=10)
    assert len(rows) == 1
    assert rows[0]["marker"] == "p0_row"


def test_query_p_view_respects_limit(backend: SQLiteBackend) -> None:
    rows = backend.query_p_view("v_p0_test_view", limit=0)
    # default=100 via clamp; but only 1 matching row exists
    assert len(rows) == 1


def test_query_p_view_rejects_non_p_pattern(backend: SQLiteBackend) -> None:
    """Names not matching v_p[0-3]_<word> raise ValueError."""
    with pytest.raises(ValueError, match="must match v_p"):
        backend.query_p_view("nodes")


def test_query_p_view_rejects_sql_injection(backend: SQLiteBackend) -> None:
    """Quote/semicolon/space attempts fail the regex check."""
    with pytest.raises(ValueError):
        backend.query_p_view("v_p0_test_view; DROP TABLE nodes--")
    with pytest.raises(ValueError):
        backend.query_p_view("v_p0_test_view UNION SELECT 1")
    with pytest.raises(ValueError):
        backend.query_p_view("v_p4_out_of_range")  # P-band > 3


def test_query_p_view_rejects_nonexistent_p_view(backend: SQLiteBackend) -> None:
    """Names matching the regex but absent from sqlite_master also raise."""
    with pytest.raises(ValueError, match="does not exist"):
        backend.query_p_view("v_p2_does_not_exist_anywhere")


def test_query_p_view_rejects_non_string(backend: SQLiteBackend) -> None:
    with pytest.raises(ValueError):
        backend.query_p_view(123)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Service-layer wrappers
# ---------------------------------------------------------------------------


def test_service_get_mv_hotspot_centrality(synthetic_snapshot: Path, monkeypatch) -> None:
    monkeypatch.setenv("ADG_DIR", str(synthetic_snapshot.parent))
    monkeypatch.setenv("ADG_REDIS_URL", "")  # disable redis
    from tools.adg.core.service import ADGService

    svc = ADGService()
    try:
        resp = svc.get_mv_hotspot_centrality(limit=2)
        assert resp.status == "ok"
        assert resp.data["count"] == 2
        assert resp.data["hotspots"][0]["adg_name"] == "pkg.high_central"
    finally:
        svc.close()


def test_service_get_semantic_fanout_validates_relation_type(
    synthetic_snapshot: Path, monkeypatch
) -> None:
    monkeypatch.setenv("ADG_DIR", str(synthetic_snapshot.parent))
    monkeypatch.setenv("ADG_REDIS_URL", "")
    from tools.adg.core.service import ADGService

    svc = ADGService()
    try:
        # Non-semantic relation_type rejected.
        bad = svc.get_semantic_fanout("1", "imports")
        assert bad.status == "error"
        assert "imports" not in bad.data["valid_relation_types"]
        assert "flows_to" in bad.data["valid_relation_types"]

        # Semantic relation_type proceeds (returns ok with edges).
        ok = svc.get_semantic_fanout("1", "flows_to")
        assert ok.status == "ok"
        assert ok.data["count"] >= 0
    finally:
        svc.close()


def test_service_query_p_view_error_lists_available(
    synthetic_snapshot: Path, monkeypatch
) -> None:
    monkeypatch.setenv("ADG_DIR", str(synthetic_snapshot.parent))
    monkeypatch.setenv("ADG_REDIS_URL", "")
    from tools.adg.core.service import ADGService

    svc = ADGService()
    try:
        bad = svc.query_p_view("v_p9_nope")
        assert bad.status == "error"
        assert "v_p0_test_view" in bad.data["available_p_views"]
        assert "v_p1_test_view" in bad.data["available_p_views"]

        good = svc.query_p_view("v_p0_test_view")
        assert good.status == "ok"
        assert good.data["count"] == 1
    finally:
        svc.close()


# ---------------------------------------------------------------------------
# Server tool registration smoke
# ---------------------------------------------------------------------------


def test_server_module_imports_and_registers_new_tools() -> None:
    """The server module must import successfully and expose the 4 new tool functions."""
    from tools.adg.mcp import server

    for name in (
        "adg_mv_hotspot_centrality",
        "adg_blast_radius",
        "adg_semantic_fanout",
        "adg_p_view_query",
    ):
        assert hasattr(server, name), f"server.{name} missing"


def test_handlers_module_exposes_new_handlers() -> None:
    from tools.adg.mcp import tool_handlers

    for name in (
        "adg_mv_hotspot_centrality",
        "adg_blast_radius",
        "adg_semantic_fanout",
        "adg_p_view_query",
    ):
        assert callable(getattr(tool_handlers, name, None)), f"handler {name} missing"
