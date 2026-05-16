"""Redis MV ranking + SQLite hydration for ``get_mv_hotspot_centrality``.

W2.1: read-through preference.  
W4: ``backend_used`` + payload-shape + cold/error/divergence (no redis-server).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.adg.core.sqlite_backend import SQLiteBackend


def _assert_hotspot_payload_shape(resp) -> None:
    assert resp.status == "ok"
    assert set(resp.data.keys()) == {"hotspots", "count"}
    assert len(resp.data["hotspots"]) == resp.data["count"]


@pytest.fixture
def hotspot_snapshot(tmp_path: Path, monkeypatch) -> Path:
    """Minimal ADG file with mv_hotspot_centrality (same layout as W3 MCP tests)."""
    import sqlite3

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
    """
    snap = tmp_path / "adg_indexed_01012099_0000.sqlite"
    con = sqlite3.connect(snap)
    con.executescript(SCHEMA)
    con.commit()
    con.close()
    monkeypatch.setenv("ADG_DIR", str(tmp_path))
    return snap


class _WarmMVStub:
    available = True

    def __init__(self, pairs: list[tuple[str, float]]) -> None:
        self._pairs = pairs

    def get_mv_top(self, mv_name: str, snapshot_id: str, k: int):  # noqa: ANN204
        assert mv_name == "mv_hotspot_centrality"
        return self._pairs[:k]


class _FailsMVStub:
    available = True

    def get_mv_top(self, mv_name: str, snapshot_id: str, k: int):  # noqa: ANN204
        raise ConnectionError("simulated Redis transport failure")


def _service_with_fake_reader(fake_reader, *, redis_down: bool = True):
    """Assemble ``ADGService`` without MCP runtime (no SQLite lock coupling)."""
    from tools.adg.core.service import ADGService

    svc = object.__new__(ADGService)
    svc._sqlite = SQLiteBackend(use_graph_store=False)
    st = svc._sqlite.get_status()
    svc._adg_snapshot_id = st["timestamp"]
    svc._redis_url = "redis://127.0.0.1:63999/13"
    mock_redis = MagicMock()
    mock_redis._available = not redis_down
    svc._redis = mock_redis
    svc._mv_reader = fake_reader
    return svc


def test_hotspot_redis_hit_preserves_mv_order_and_sets_backend_used_redis(
    hotspot_snapshot: Path,
) -> None:
    _ = hotspot_snapshot
    svc = _service_with_fake_reader(
        # Deliberately not canonical SQLite ORDER BY degree_centrality.
        _WarmMVStub([("3", 0.05), ("1", 0.95)]),
    )
    try:
        resp = svc.get_mv_hotspot_centrality(limit=10)
        _assert_hotspot_payload_shape(resp)
        assert resp.backend_used == "redis"
        assert resp.data["count"] == 2
        assert resp.data["hotspots"][0]["node_id"] == 3
        assert resp.data["hotspots"][0]["adg_name"] == "pkg.low_central"
        assert resp.data["hotspots"][1]["node_id"] == 1
        assert resp.data["hotspots"][1]["adg_name"] == "pkg.high_central"
    finally:
        svc._sqlite.close()


def test_hotspot_redis_miss_none_falls_through_sqlite_order(
    hotspot_snapshot: Path,
) -> None:
    _ = hotspot_snapshot

    class _NoneMVStub:
        available = True

        def get_mv_top(self, mv_name: str, snapshot_id: str, k: int):  # noqa: ANN204
            return None

    svc = _service_with_fake_reader(_NoneMVStub())
    try:
        resp = svc.get_mv_hotspot_centrality(limit=10)
        _assert_hotspot_payload_shape(resp)
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 3
        names = [r["adg_name"] for r in resp.data["hotspots"]]
        assert names == ["pkg.high_central", "pkg.mid_central", "pkg.low_central"]
    finally:
        svc._sqlite.close()


def test_hotspot_redis_empty_list_falls_through_sqlite(
    hotspot_snapshot: Path,
) -> None:
    _ = hotspot_snapshot

    class _EmptyMVStub:
        available = True

        def get_mv_top(self, mv_name: str, snapshot_id: str, k: int):  # noqa: ANN204
            return []

    svc = _service_with_fake_reader(_EmptyMVStub())
    try:
        resp = svc.get_mv_hotspot_centrality(limit=10)
        _assert_hotspot_payload_shape(resp)
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 3
    finally:
        svc._sqlite.close()


def test_hotspot_redis_raises_falls_through_sqlite(
    hotspot_snapshot: Path,
) -> None:
    _ = hotspot_snapshot
    svc = _service_with_fake_reader(_FailsMVStub())
    try:
        resp = svc.get_mv_hotspot_centrality(limit=2)
        _assert_hotspot_payload_shape(resp)
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 2
        assert resp.data["hotspots"][0]["adg_name"] == "pkg.high_central"
    finally:
        svc._sqlite.close()


def test_hotspot_mv_reader_down_falls_through_sqlite(
    hotspot_snapshot: Path,
) -> None:
    _ = hotspot_snapshot

    class _DownMVStub:
        available = False

        def get_mv_top(self, mv_name: str, snapshot_id: str, k: int):  # noqa: ANN204
            raise AssertionError("should not be called")

    svc = _service_with_fake_reader(_DownMVStub())
    try:
        resp = svc.get_mv_hotspot_centrality(limit=2)
        _assert_hotspot_payload_shape(resp)
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 2
        assert resp.data["hotspots"][0]["degree_centrality"] == pytest.approx(0.95)
    finally:
        svc._sqlite.close()


def test_hotspot_divergent_node_id_fallback_sqlite(hotspot_snapshot: Path) -> None:
    """Redis lists a member missing from SQLite — full canonical SQLite path."""
    _ = hotspot_snapshot
    svc = _service_with_fake_reader(_WarmMVStub([("999", 1.0), ("2", 0.5)]))
    try:
        resp = svc.get_mv_hotspot_centrality(limit=10)
        _assert_hotspot_payload_shape(resp)
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 3
        names = [r["adg_name"] for r in resp.data["hotspots"]]
        assert names == ["pkg.high_central", "pkg.mid_central", "pkg.low_central"]
    finally:
        svc._sqlite.close()


def test_sqlite_backend_hydrate_ordered_and_none_on_missing(
    hotspot_snapshot: Path,
) -> None:
    _ = hotspot_snapshot
    backend = SQLiteBackend(use_graph_store=False)
    try:
        rows = backend.hydrate_mv_hotspot_centrality_ordered(["3", "1"])
        assert rows is not None
        assert [r["node_id"] for r in rows] == [3, 1]
        assert rows[0]["adg_name"] == "pkg.low_central"

        missing = backend.hydrate_mv_hotspot_centrality_ordered(["404"])
        assert missing is None
    finally:
        backend.close()
