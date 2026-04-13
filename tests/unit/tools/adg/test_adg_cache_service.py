"""ADG cache service tests — P21 get_nodes_by_layer + P22 negative-path hardening."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from tools.adg.core.models import ADGNode, ADGEdge


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_node(**kwargs) -> ADGNode:
    defaults = dict(
        id="1",
        adg_name="ADG::Module::foo.py",
        entity_type="module",
        layer="L4",
        resolved_path="foo.py",
        identity_kind="repo_module",
        confidence="HIGH",
        precision_type="symbol",
        span_start=0,
        span_end=0,
        span_line=0,
        span_column=0,
        span_end_line=0,
        span_end_column=0,
        logical_sequence_id=0,
        control_path_id="",
        temporal_order=0,
        type_surface="",
        enclosing_symbol="",
    )
    defaults.update(kwargs)
    return ADGNode(**defaults)


def _make_edge(**kwargs) -> ADGEdge:
    defaults = dict(id="9", src_id="1", dst_id="2", relation_type="imports", edge_kind="from_import")
    defaults.update(kwargs)
    return ADGEdge(**defaults)


def _make_service(redis_available: bool = True):
    """Build an ADGService with fully mocked backends."""
    from tools.adg.core.service import ADGService

    svc = object.__new__(ADGService)
    svc._adg_snapshot_id = "test0001_snap"

    mock_sqlite = MagicMock()
    mock_redis = MagicMock()
    mock_redis._available = redis_available

    svc._sqlite = mock_sqlite
    svc._redis = mock_redis
    return svc, mock_sqlite, mock_redis


# ===========================================================================
# P21 — get_nodes_by_layer Redis-first tests
# ===========================================================================


class TestGetNodesByLayerRedisFirst:
    def test_redis_hit_returns_redis_backend(self):
        """Cache hit: backend_used should be 'redis'."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        node = _make_node(id="42", layer="L4")
        mock_redis.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L4", limit=100)

        assert resp.backend_used == "redis"
        assert resp.data["count"] == 1
        assert resp.data["layer"] == "L4"
        mock_sqlite.get_nodes_by_layer.assert_not_called()

    def test_redis_miss_falls_through_to_sqlite_and_backfills(self):
        """Cache miss: SQLite serves, then backfill is written to Redis."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        node = _make_node(id="7", layer="L0")
        mock_redis.get_nodes_by_layer.return_value = None  # cache miss
        mock_sqlite.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L0", limit=100)

        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1
        mock_redis.set_nodes_by_layer.assert_called_once_with("L0", [node], "test0001_snap")

    def test_redis_empty_list_treated_as_miss(self):
        """Empty list from Redis falls through to SQLite (intentional: indistinguishable from miss)."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        node = _make_node(id="3", layer="L1")
        mock_redis.get_nodes_by_layer.return_value = []  # cached empty — treated as miss
        mock_sqlite.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L1", limit=100)

        assert resp.backend_used == "sqlite"
        mock_sqlite.get_nodes_by_layer.assert_called_once()

    def test_redis_unavailable_uses_sqlite_directly(self):
        """Redis unavailable: SQLite serves without attempting Redis."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=False)
        node = _make_node(id="5", layer="L2")
        mock_sqlite.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L2", limit=100)

        assert resp.backend_used == "sqlite"
        mock_redis.get_nodes_by_layer.assert_not_called()
        mock_redis.set_nodes_by_layer.assert_not_called()

    def test_response_shape_is_consistent_regardless_of_backend(self):
        """backend_used changes but data shape is identical for both backends."""
        svc_redis, mock_sqlite_r, mock_redis_r = _make_service(redis_available=True)
        svc_sqlite, mock_sqlite_s, mock_redis_s = _make_service(redis_available=False)

        node = _make_node(id="11", layer="L3")
        mock_redis_r.get_nodes_by_layer.return_value = [node]
        mock_sqlite_s.get_nodes_by_layer.return_value = [node]

        resp_redis = svc_redis.get_nodes_by_layer("L3")
        resp_sqlite = svc_sqlite.get_nodes_by_layer("L3")

        assert set(resp_redis.data.keys()) == set(resp_sqlite.data.keys())
        assert resp_redis.data["count"] == resp_sqlite.data["count"] == 1


# ===========================================================================
# P22 — Negative-path hardening
# ===========================================================================


class TestNegativePaths:
    def test_redis_exception_falls_through_to_sqlite(self):
        """Redis raises exception during query → falls through to SQLite, backend_used='sqlite'."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        mock_redis.get_nodes_by_layer.side_effect = ConnectionError("Redis connection reset")
        node = _make_node(id="99")
        mock_sqlite.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L4")

        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1

    def test_redis_unavailable_backend_truthful_fanout(self):
        """_available=False: get_edge_fanout backend_used='sqlite'."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=False)
        mock_sqlite.get_edge_fanout.return_value = []

        resp = svc.get_edge_fanout("src_1", "imports", limit=10)

        assert resp.backend_used == "sqlite"
        mock_redis.get_edge_fanout.assert_not_called()

    def test_redis_unavailable_backend_truthful_fanin(self):
        """_available=False: get_edge_fanin backend_used='sqlite'."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=False)
        edge = _make_edge()
        mock_sqlite.get_edge_fanin.return_value = [edge]

        resp = svc.get_edge_fanin("tgt_99", "imports", limit=10)

        assert resp.backend_used == "sqlite"
        mock_redis.get_edge_fanin.assert_not_called()

    def test_redis_unavailable_backend_truthful_nodes_by_file(self):
        """_available=False: get_nodes_by_file backend_used='sqlite'."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=False)
        node = _make_node()
        mock_sqlite.get_nodes_by_file.return_value = [node]

        resp = svc.get_nodes_by_file("foo.py")

        assert resp.backend_used == "sqlite"
        mock_redis.get_nodes_by_file.assert_not_called()

    def test_partial_fanin_cache_dangling_edge_returns_none(self):
        """Fanin set has edge_id but edge_detail hash is missing.

        Expected behaviour after P23 completeness hardening:
        - get_edge_fanin returns None when len(assembled) != len(edge_ids)
        - _query_with_fallback sees None and goes to SQLite fallback
        - SQLite fallback serves the correct result
        - backend_used='sqlite'
        """
        from tools.adg.cache.redis_cache import RedisCache

        mock_client = MagicMock()
        cache = object.__new__(RedisCache)
        cache._client = mock_client
        cache._available = True
        cache._cache_version = "v1"
        cache._redis_url = "redis://localhost:6379/0"

        snap = "test0001_snap"

        # fanin set exists with one edge_id
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = {"59999"}
        # but edge_detail hash is missing (hgetall returns {})
        mock_client.hgetall.return_value = {}

        result = cache.get_edge_fanin("tgt_77", "imports", snap)
        # completeness check fires: len(assembled=0) != len(edge_ids=1) -> None
        assert result is None

        # Now verify _query_with_fallback treats None as a miss and goes to SQLite
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        edge = _make_edge(id="59999", src_id="1", dst_id="tgt_77")
        mock_redis.get_edge_fanin.return_value = []  # simulate the partial cache
        mock_sqlite.get_edge_fanin.return_value = [edge]

        resp = svc.get_edge_fanin("tgt_77", "imports")
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1

    def test_backfill_exception_does_not_propagate(self):
        """Cache backfill failure must not crash the request."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        node = _make_node()
        mock_redis.get_nodes_by_layer.return_value = None  # cache miss
        mock_sqlite.get_nodes_by_layer.return_value = [node]
        mock_redis.set_nodes_by_layer.side_effect = RuntimeError("write failed")

        resp = svc.get_nodes_by_layer("L5")

        assert resp.status == "ok"
        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1

    def test_sqlite_still_authoritative_when_redis_stale(self):
        """Even if Redis has data, caller should be able to trust SQLite via a forced miss
        if Redis returns None (e.g. after snapshot rotation clears keys)."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        node = _make_node(id="new_snap_node")
        mock_redis.get_nodes_by_layer.return_value = None  # stale keys cleared
        mock_sqlite.get_nodes_by_layer.return_value = [node]

        resp = svc.get_nodes_by_layer("L6")

        assert resp.backend_used == "sqlite"
        assert resp.data["nodes"][0]["id"] == "new_snap_node"

    def test_empty_sqlite_result_not_backfilled_to_redis(self):
        """When SQLite returns [], backfill must NOT be called.

        The hit-check in _query_with_fallback treats [] as a miss (result != []).
        Caching [] would write a Redis entry that is immediately ignored on
        re-read, creating a perpetual wasted write on every empty-result call.
        """
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        mock_redis.get_nodes_by_layer.return_value = None  # cache miss
        mock_sqlite.get_nodes_by_layer.return_value = []  # empty layer

        resp = svc.get_nodes_by_layer("EMPTY_LAYER")

        assert resp.status == "ok"
        assert resp.data["count"] == 0
        mock_redis.set_nodes_by_layer.assert_not_called()


# ===========================================================================
# P23 — Completeness-check regression tests
# ===========================================================================


def _make_redis_cache():
    """Build a bare RedisCache with a MagicMock client."""
    from tools.adg.cache.redis_cache import RedisCache

    mock_client = MagicMock()
    cache = object.__new__(RedisCache)
    cache._client = mock_client
    cache._available = True
    cache._cache_version = "v1"
    cache._redis_url = "redis://localhost:6379/0"
    cache._consecutive_errors = 0
    cache._last_reconnect_attempt = 0.0
    return cache, mock_client


def _edge_detail(edge_id: str, src: str = "1", dst: str = "2") -> dict:
    return {
        "id": edge_id,
        "src_id": src,
        "dst_id": dst,
        "relation_type": "imports",
        "edge_kind": "from_import",
    }


class TestFaninCompletenessCheck:
    def test_fanin_all_details_present_returns_full_list(self):
        """All edge_detail hashes present: full edge list returned (no completeness failure)."""
        cache, mock_client = _make_redis_cache()
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = {"10", "11"}
        mock_client.hgetall.side_effect = [
            _edge_detail("10"),
            _edge_detail("11"),
        ]

        result = cache.get_edge_fanin("tgt_1", "imports", "snap1")

        assert result is not None
        assert len(result) == 2
        assert all(e.relation_type == "imports" for e in result)
        assert all(e.edge_kind == "from_import" for e in result)

    def test_fanin_partial_detail_missing_returns_none(self):
        """Some edge_detail hashes missing: completeness check fires, returns None."""
        cache, mock_client = _make_redis_cache()
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = {"10", "11", "12"}
        mock_client.hgetall.side_effect = [
            _edge_detail("10"),
            _edge_detail("11"),
            {},  # missing: edge 12 detail hash absent
        ]

        result = cache.get_edge_fanin("tgt_1", "imports", "snap1")

        assert result is None

    def test_fanin_all_details_missing_returns_none(self):
        """All edge_detail hashes missing: completeness check returns None (not [])."""
        cache, mock_client = _make_redis_cache()
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = {"10"}
        mock_client.hgetall.return_value = {}

        result = cache.get_edge_fanin("tgt_1", "imports", "snap1")

        assert result is None

    def test_fanin_empty_set_still_returns_empty_list(self):
        """Fanin key exists but set is empty (valid: node has no importers): returns []."""
        cache, mock_client = _make_redis_cache()
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = set()

        result = cache.get_edge_fanin("tgt_isolated", "imports", "snap1")

        assert result == []

    def test_fanout_all_details_present_returns_full_list(self):
        """Fanout: all edge_detail hashes present, full list returned."""
        cache, mock_client = _make_redis_cache()
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = {"20", "21"}
        mock_client.hgetall.side_effect = [
            _edge_detail("20"),
            _edge_detail("21"),
        ]

        result = cache.get_edge_fanout("src_1", "imports", "snap1")

        assert result is not None
        assert len(result) == 2
        assert all(e.relation_type == "imports" for e in result)
        assert all(e.edge_kind == "from_import" for e in result)

    def test_fanout_partial_detail_missing_returns_none(self):
        """Fanout: partial edge_detail state triggers completeness check -> None."""
        cache, mock_client = _make_redis_cache()
        mock_client.exists.return_value = True
        mock_client.smembers.return_value = {"20", "21"}
        mock_client.hgetall.side_effect = [
            _edge_detail("20"),
            {},  # edge 21 detail missing
        ]

        result = cache.get_edge_fanout("src_1", "imports", "snap1")

        assert result is None

    def test_get_nodes_by_layer_malformed_json_returns_none(self):
        """get_nodes_by_layer: corrupted JSON in Redis cache raises JSONDecodeError -> returns None (not raise)."""
        cache, mock_client = _make_redis_cache()
        mock_client.get.return_value = "not-valid-json{{{corrupted"

        result = cache.get_nodes_by_layer("L4", "snap1")

        assert result is None

    def test_service_partial_fanin_falls_through_to_sqlite(self):
        """Service-level: None from Redis cache triggers SQLite fallback, backend_used=sqlite."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        edge = _make_edge(id="10", src_id="1", dst_id="tgt_1")
        mock_redis.get_edge_fanin.return_value = None  # partial state detected
        mock_sqlite.get_edge_fanin.return_value = [edge]

        resp = svc.get_edge_fanin("tgt_1", "imports")

        assert resp.backend_used == "sqlite"
        assert resp.data["count"] == 1
        mock_sqlite.get_edge_fanin.assert_called_once()


# ===========================================================================
# P25 — get_node failure-path coverage
# ===========================================================================


class TestGetNodeFailurePath:
    def test_node_not_found_returns_error_status(self):
        """get_node: both Redis and SQLite return None -> ADGResponse(status='error')."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        mock_redis.get_node.return_value = None
        mock_sqlite.get_node.return_value = None

        resp = svc.get_node("nonexistent_node_99")

        assert resp.status == "error"
        assert "nonexistent_node_99" in resp.data["message"]
        assert resp.backend_used == "sqlite"

    def test_node_not_found_redis_unavailable_still_returns_error(self):
        """get_node with Redis down and missing node -> status='error', Redis not queried."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=False)
        mock_sqlite.get_node.return_value = None

        resp = svc.get_node("missing_node_in_sqlite")

        assert resp.status == "error"
        assert "missing_node_in_sqlite" in resp.data["message"]
        mock_redis.get_node.assert_not_called()

    def test_node_found_returns_ok_status(self):
        """get_node happy path: Redis hit returns ADGResponse(status='ok')."""
        svc, mock_sqlite, mock_redis = _make_service(redis_available=True)
        node = _make_node(id="42", adg_name="ADG::Module::bar.py")
        mock_redis.get_node.return_value = node

        resp = svc.get_node("42")

        assert resp.status == "ok"
        assert resp.backend_used == "redis"
        assert resp.data["id"] == "42"
        mock_sqlite.get_node.assert_not_called()


# ===========================================================================
# P26 — clear_snapshot direct coverage
# ===========================================================================


class TestClearSnapshot:
    """Direct tests for clear_snapshot — server-level tests mock the whole method;
    these prove the guard and scan loop actually execute."""

    def test_clear_snapshot_noop_when_unavailable(self):
        """G1: _available=False → early return, no SCAN or DELETE calls."""
        cache, mock_client = _make_redis_cache()
        cache._available = False

        cache.clear_snapshot("snap_old_123")

        mock_client.scan.assert_not_called()
        mock_client.delete.assert_not_called()

    def test_clear_snapshot_scans_and_deletes_single_page(self):
        """G2a: Single-page SCAN (cursor=0 on first return) deletes all matched keys."""
        cache, mock_client = _make_redis_cache()
        mock_client.scan.return_value = (0, ["adg:v1:snap_old:node:1", "adg:v1:snap_old:node:2"])

        cache.clear_snapshot("snap_old")

        mock_client.scan.assert_called_once_with(cursor=0, match="adg:v1:snap_old:*", count=100)
        mock_client.delete.assert_called_once_with("adg:v1:snap_old:node:1", "adg:v1:snap_old:node:2")

    def test_clear_snapshot_iterates_multi_page_scan(self):
        """G2b: Multi-page SCAN loop continues until cursor returns 0."""
        cache, mock_client = _make_redis_cache()
        mock_client.scan.side_effect = [
            (42, ["key_page1"]),
            (0, ["key_page2"]),
        ]

        cache.clear_snapshot("snap_multi")

        assert mock_client.scan.call_count == 2
        assert mock_client.delete.call_count == 2
        mock_client.delete.assert_any_call("key_page1")
        mock_client.delete.assert_any_call("key_page2")

    def test_clear_snapshot_no_delete_when_scan_returns_empty_keys(self):
        """G2c: SCAN returning empty key list must not call delete."""
        cache, mock_client = _make_redis_cache()
        mock_client.scan.return_value = (0, [])

        cache.clear_snapshot("snap_empty")

        mock_client.scan.assert_called_once()
        mock_client.delete.assert_not_called()
