"""Tests for `agentic_core.cache.redis_cache_client`.

Covers the 3 ADG Surfaces intersected by this module (Execution + Write +
Observability per hardened concentration analysis 2026-04-28):
    - input validation (keys, TTL, port parsing)
    - canonical JSON / hash determinism
    - fail-closed behavior when Redis is unreachable (no connection errors
      bubble to callers; cache methods return None/False)
    - get/set/delete roundtrip via mocked redis.Redis
    - DB isolation (hot / coordination / workspace factories)

Does NOT require a live Redis — uses unittest.mock to stub redis.Redis.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.cache.redis_cache_client import (  # noqa: E402
    DB_COORDINATION,
    DB_HOT,
    DB_WORKSPACE,
    DeterministicRedisCache,
    _parse_redis_port,
    _require_cache_key,
    _require_positive_ttl,
    canonical_json_bytes,
    check_redis_health,
    content_hash,
    get_coordination_cache,
    get_hot_cache,
    get_workspace_cache,
    reset_cache_singletons,
)


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Ensure no cross-test pollution of singleton hot-cache instance."""
    reset_cache_singletons()
    yield
    reset_cache_singletons()


class TestPortParsing:
    def test_none_defaults_to_6379(self):
        assert _parse_redis_port(None) == 6379

    def test_empty_string_defaults_to_6379(self):
        assert _parse_redis_port("") == 6379

    def test_valid_port(self):
        assert _parse_redis_port("6380") == 6380

    def test_non_numeric_falls_back(self):
        assert _parse_redis_port("not-a-port") == 6379

    def test_out_of_range_high_falls_back(self):
        assert _parse_redis_port("99999") == 6379

    def test_zero_or_negative_falls_back(self):
        assert _parse_redis_port("0") == 6379
        assert _parse_redis_port("-1") == 6379


class TestInputValidation:
    def test_require_positive_ttl_rejects_zero(self):
        with pytest.raises(ValueError, match="ttl_seconds"):
            _require_positive_ttl(0)

    def test_require_positive_ttl_rejects_negative(self):
        with pytest.raises(ValueError, match="ttl_seconds"):
            _require_positive_ttl(-5)

    def test_require_positive_ttl_allows_positive(self):
        assert _require_positive_ttl(60) == 60

    def test_require_cache_key_rejects_empty(self):
        with pytest.raises(ValueError, match="key must not be empty"):
            _require_cache_key("")

    def test_require_cache_key_allows_non_empty(self):
        assert _require_cache_key("my-key") == "my-key"


class TestCanonicalSerialization:
    def test_canonical_json_sorts_keys(self):
        payload = {"b": 2, "a": 1}
        out = canonical_json_bytes(payload)
        assert out == b'{"a":1,"b":2}'

    def test_canonical_json_deterministic(self):
        p1 = {"z": [1, 2], "a": "x"}
        p2 = {"a": "x", "z": [1, 2]}
        assert canonical_json_bytes(p1) == canonical_json_bytes(p2)

    def test_content_hash_stable(self):
        h1 = content_hash(b"hello")
        h2 = content_hash(b"hello")
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex


class TestFailClosed:
    """Redis unavailable → cache methods return None/False, never raise."""

    def test_get_returns_none_when_client_is_none(self):
        cache = DeterministicRedisCache(host="no-such-host", port=1)
        with mock.patch.object(cache, "_get_client", return_value=None):
            assert cache.get("k") is None

    def test_set_returns_false_when_client_is_none(self):
        cache = DeterministicRedisCache()
        with mock.patch.object(cache, "_get_client", return_value=None):
            assert cache.set("k", "v") is False

    def test_set_nx_returns_false_when_client_is_none(self):
        cache = DeterministicRedisCache()
        with mock.patch.object(cache, "_get_client", return_value=None):
            assert cache.set_nx("k", "v") is False

    def test_delete_returns_false_when_client_is_none(self):
        cache = DeterministicRedisCache()
        with mock.patch.object(cache, "_get_client", return_value=None):
            assert cache.delete("k") is False

    def test_set_json_returns_false_on_unserializable(self):
        cache = DeterministicRedisCache()
        mock_client = mock.MagicMock()
        with mock.patch.object(cache, "_get_client", return_value=mock_client):
            # object() is not JSON-serializable
            result = cache.set_json("k", object())
            assert result is False


class TestRoundtrip:
    def test_set_then_get_via_mock(self):
        cache = DeterministicRedisCache()
        mock_client = mock.MagicMock()
        mock_client.setex.return_value = b"OK"
        mock_client.get.return_value = "hello"
        with mock.patch.object(cache, "_get_client", return_value=mock_client):
            assert cache.set("k", "hello", ttl_seconds=60) is True
            assert cache.get("k") == "hello"
            mock_client.setex.assert_called_once_with("k", 60, "hello")

    def test_set_json_roundtrip(self):
        cache = DeterministicRedisCache()
        mock_client = mock.MagicMock()
        mock_client.setex.return_value = b"OK"
        serialized = json.dumps({"a": 1, "b": 2}, sort_keys=True, separators=(",", ":"))
        mock_client.get.return_value = serialized
        with mock.patch.object(cache, "_get_client", return_value=mock_client):
            assert cache.set_json("k", {"a": 1, "b": 2}) is True
            assert cache.get_json("k") == {"a": 1, "b": 2}

    def test_get_json_returns_none_when_key_absent(self):
        cache = DeterministicRedisCache()
        mock_client = mock.MagicMock()
        mock_client.get.return_value = None
        with mock.patch.object(cache, "_get_client", return_value=mock_client):
            assert cache.get_json("absent") is None

    def test_get_json_raises_on_invalid_json(self):
        cache = DeterministicRedisCache()
        mock_client = mock.MagicMock()
        mock_client.get.return_value = "{not json"
        with mock.patch.object(cache, "_get_client", return_value=mock_client):
            with pytest.raises(ValueError, match="Invalid JSON"):
                cache.get_json("k")


class TestDBIsolation:
    def test_hot_cache_uses_db_0(self):
        reset_cache_singletons()
        c = get_hot_cache()
        assert c.db == DB_HOT == 0

    def test_coordination_cache_uses_db_1(self):
        c = get_coordination_cache()
        assert c.db == DB_COORDINATION == 1

    def test_workspace_cache_uses_db_2(self):
        c = get_workspace_cache()
        assert c.db == DB_WORKSPACE == 2

    def test_hot_cache_is_singleton(self):
        c1 = get_hot_cache()
        c2 = get_hot_cache()
        assert c1 is c2

    def test_reset_releases_singleton(self):
        c1 = get_hot_cache()
        reset_cache_singletons()
        c2 = get_hot_cache()
        assert c1 is not c2


class TestHealth:
    def test_health_unhealthy_when_client_is_none(self):
        reset_cache_singletons()
        with mock.patch(
            "agentic_core.cache.redis_cache_client.DeterministicRedisCache._get_client",
            return_value=None,
        ):
            h = check_redis_health()
            assert h["status"] == "unhealthy"
            assert h["connected"] is False
