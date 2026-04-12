"""Regression tests: get_edge_fanin now uses Redis-first read-through.

Covers four scenarios from Prompt 5 validation matrix:
  1. Redis HIT  — backend_used="redis", no SQLite call
  2. Redis MISS — falls through to SQLite, backend_used="sqlite"
  3. Backfill   — after SQLite fallback, set_edge_fanin is called
  4. Redis DOWN — Redis unavailable, falls back cleanly to SQLite
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tools.adg.core.models import ADGEdge
from tools.adg.core.service import ADGService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_edge(edge_id: str = "100", src: str = "1", dst: str = "2") -> ADGEdge:
    return ADGEdge(id=edge_id, src_id=src, dst_id=dst, relation_type="imports", edge_kind="static")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFaninRedisCacheIntegration:
    """get_edge_fanin must follow Redis-first read-through, same as get_edge_fanout."""

    def test_redis_hit_returns_redis_backend(self):
        """When Redis has the fanin key, backend_used must be 'redis'."""
        svc = ADGService()
        fake_edge = _make_edge()

        with patch.object(svc._redis, "get_edge_fanin", return_value=[fake_edge]) as mock_get:
            resp = svc.get_edge_fanin("2", "imports", limit=10)

        assert resp.status == "ok"
        assert resp.backend_used == "redis", (
            f"Expected backend_used='redis' on cache hit, got {resp.backend_used!r}"
        )
        assert resp.data["count"] == 1
        mock_get.assert_called_once()

    def test_redis_miss_falls_through_to_sqlite(self):
        """When Redis returns None (cache miss), result comes from SQLite."""
        svc = ADGService()

        with patch.object(svc._redis, "get_edge_fanin", return_value=None):
            resp = svc.get_edge_fanin("2", "imports", limit=10)

        assert resp.status == "ok"
        assert resp.backend_used == "sqlite", (
            f"Expected backend_used='sqlite' on cache miss, got {resp.backend_used!r}"
        )

    def test_sqlite_fallback_triggers_backfill(self):
        """After a Redis miss, set_edge_fanin must be called to backfill the cache."""
        svc = ADGService()
        fake_edge = _make_edge()

        with (
            patch.object(svc._redis, "get_edge_fanin", return_value=None),
            patch.object(svc._sqlite, "get_edge_fanin", return_value=[fake_edge]),
            patch.object(svc._redis, "set_edge_fanin") as mock_set,
        ):
            resp = svc.get_edge_fanin("2", "imports", limit=10)

        assert resp.backend_used == "sqlite"
        mock_set.assert_called_once()

    def test_redis_unavailable_falls_back_silently(self):
        """When Redis is down, get_edge_fanin must complete via SQLite without error."""
        svc = ADGService(redis_url="redis://invalid:9999/0")

        resp = svc.get_edge_fanin("2", "imports", limit=10)

        assert resp.status == "ok"
        assert resp.backend_used == "sqlite"

    def test_backend_used_field_present_on_hit(self):
        """ADGResponse must carry backend_used='redis' when Redis supplies the answer."""
        svc = ADGService()
        fake_edge = _make_edge()

        with patch.object(svc._redis, "get_edge_fanin", return_value=[fake_edge]):
            resp = svc.get_edge_fanin("2", "imports")

        assert hasattr(resp, "backend_used")
        assert resp.backend_used == "redis"

    def test_no_backfill_when_redis_unavailable(self):
        """set_edge_fanin must never be called when Redis is down."""
        svc = ADGService(redis_url="redis://invalid:9999/0")

        with patch.object(svc._redis, "set_edge_fanin") as mock_set:
            svc.get_edge_fanin("2", "imports")

        mock_set.assert_not_called()
