"""P24 — Snapshot rotation safety: prove old snapshot keys are never served for a new snapshot.

Key isolation is guaranteed by design: every Redis key embeds the snapshot_id:
    adg:v1:{snapshot_id}:{base}

When the snapshot rotates, the service loads a new snapshot_id.  All old keys have
a different prefix and produce cache misses.  SQLite serves the new data; backfill
then writes fresh keys under the new snapshot prefix.

Live evidence (captured 2026-04-12, snapshot 04122026_1126):
  - adg_nodes_by_file  -> backend_used=redis  (lazy-warmed in session)
  - adg_edge_fanin     -> backend_used=redis  (pre-warmed by ingest)
  - adg_nodes_by_layer -> backend_used=sqlite (MCP not yet restarted with P21 code)
  - adg:v1:99991231_9999:* -> 0 Redis keys   (hypothetical new snapshot: zero hits)
"""

from __future__ import annotations

from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Helpers (duplicated locally to keep this file self-contained)
# ---------------------------------------------------------------------------

def _make_service_with_snap(snap: str, redis_available: bool = True):
    from tools.adg.core.service import ADGService

    svc = object.__new__(ADGService)
    svc._adg_snapshot_id = snap
    svc._sqlite = MagicMock()
    svc._redis = MagicMock()
    svc._redis._available = redis_available
    return svc


def _make_redis_cache_with_snap(snap: str):
    from tools.adg.cache.redis_cache import RedisCache

    mock_client = MagicMock()
    cache = object.__new__(RedisCache)
    cache._client = mock_client
    cache._available = True
    cache._cache_version = "v1"
    cache._redis_url = "redis://localhost:6379/0"
    return cache, mock_client, snap


# ===========================================================================
# Key-namespace isolation unit tests
# ===========================================================================

class TestSnapshotKeyNamespaceIsolation:

    def test_different_snapshots_produce_different_key_prefixes(self):
        """_key() embeds snapshot_id: two snapshots share zero key namespace."""
        from tools.adg.cache.redis_cache import RedisCache

        cache = object.__new__(RedisCache)
        cache._cache_version = "v1"

        old_key = cache._key("layer_nodes:L4", "04122026_1126")
        new_key = cache._key("layer_nodes:L4", "04122026_9999")

        assert old_key != new_key
        assert "04122026_1126" in old_key
        assert "04122026_9999" in new_key
        assert not old_key.startswith(new_key[:20]) or old_key == new_key  # prefixes differ

    def test_old_snapshot_key_not_found_under_new_snapshot(self):
        """After rotation, Redis returns None for old-snap key looked up under new snap."""
        cache, mock_client, _ = _make_redis_cache_with_snap("04122026_9999")

        # Simulate: old key exists in Redis under 04122026_1126, new snap queries 04122026_9999
        mock_client.get.return_value = None  # new-snap key absent

        result = cache.get_nodes_by_file("foo.py", "04122026_9999")

        assert result is None  # cache miss -> SQLite will serve
        called_key = mock_client.get.call_args[0][0]
        assert "04122026_9999" in called_key
        assert "04122026_1126" not in called_key


class TestSnapshotRotationFallback:
    """After rotation, each accelerated method must fall back to SQLite and report it."""

    def _edge(self):
        from tools.adg.core.models import ADGEdge
        return ADGEdge(id="1", src_id="a", dst_id="b", relation_type="imports", edge_kind="from_import")

    def _node(self):
        from tests.unit.tools.adg.test_adg_cache_service import _make_node
        return _make_node(id="1")

    def test_adg_edge_fanin_misses_after_rotation(self):
        """adg_edge_fanin: old-snap keys absent under new snap -> backend_used=sqlite."""
        svc = _make_service_with_snap("04122026_9999")
        edge = self._edge()
        svc._redis.get_edge_fanin.return_value = None  # new-snap miss
        svc._sqlite.get_edge_fanin.return_value = [edge]

        resp = svc.get_edge_fanin("tgt_1", "imports")

        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1

    def test_adg_nodes_by_file_misses_after_rotation(self):
        """adg_nodes_by_file: old-snap lazy-warm key absent under new snap -> backend_used=sqlite."""
        svc = _make_service_with_snap("04122026_9999")
        node = self._node()
        svc._redis.get_nodes_by_file.return_value = None  # new-snap miss
        svc._sqlite.get_nodes_by_file.return_value = [node]

        resp = svc.get_nodes_by_file("foo.py")

        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1

    def test_adg_nodes_by_layer_misses_after_rotation(self):
        """adg_nodes_by_layer: old-snap lazy-warm key absent under new snap -> backend_used=sqlite."""
        svc = _make_service_with_snap("04122026_9999")
        node = self._node()
        svc._redis.get_nodes_by_layer.return_value = None  # new-snap miss
        svc._sqlite.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L4")

        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1

    def test_backfill_writes_to_new_snapshot_prefix(self):
        """After rotation miss, backfill must use new snapshot_id (not old) in key."""
        svc = _make_service_with_snap("04122026_9999")
        node = self._node()
        svc._redis.get_nodes_by_file.return_value = None
        svc._sqlite.get_nodes_by_file.return_value = [node]

        svc.get_nodes_by_file("bar.py")

        # Backfill must be called with the correct file_path AND the new snapshot_id
        call_args = svc._redis.set_nodes_by_file.call_args
        assert call_args is not None
        written_path = call_args[0][0]   # positional: (file_path, nodes, snapshot_id)
        written_snap = call_args[0][2]
        assert written_path == "bar.py"
        assert written_snap == "04122026_9999"

    def test_repopulation_on_second_call_hits_redis(self):
        """After first miss+backfill, second call returns redis backend."""
        svc = _make_service_with_snap("04122026_9999")
        node = self._node()

        # First call: miss -> SQLite -> backfill
        svc._redis.get_nodes_by_layer.return_value = None
        svc._sqlite.get_nodes_by_layer.return_value = [node]
        resp1 = svc.get_nodes_by_layer("L1")
        assert resp1.backend_used == "sqlite"

        # Second call: backfill now live -> redis hit
        svc._redis.get_nodes_by_layer.return_value = [node]
        resp2 = svc.get_nodes_by_layer("L1")
        assert resp2.backend_used == "redis"
        assert resp2.data["count"] == 1
