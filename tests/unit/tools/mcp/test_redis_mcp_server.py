"""Regression tests for the Redis MCP server hardening pass.

Strategy — no live Redis required:
- Pool/timeout tests patch redis_lib.ConnectionPool at construction time.
- All tool-behavior tests inject a fully-controlled MagicMock client by
  patching _safe_connect, bypassing real connection logic entirely.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[5])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_module():
    """Re-import server module with clean _pool so each test is isolated."""
    mod_name = "tools.mcp.redis_mcp_server"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    import tools.mcp.redis_mcp_server as mod  # noqa: PLC0415

    mod._reset_pool()
    return mod


def _mock_client(**overrides) -> MagicMock:
    c = MagicMock()
    c.ping.return_value = True
    for attr, val in overrides.items():
        setattr(c, attr, val)
    return c


def _inject(srv_mod, client: MagicMock):
    """Patch _safe_connect to return (client, None)."""
    return patch.object(srv_mod, "_safe_connect", return_value=(client, None))


def _inject_err(srv_mod, msg: str = "Redis connection refused"):
    """Patch _safe_connect to simulate a connection failure."""
    return patch.object(srv_mod, "_safe_connect", return_value=(None, msg))


# ---------------------------------------------------------------------------
# P3-A: Connection pool reuse
# ---------------------------------------------------------------------------


def test_pool_singleton_same_object():
    """Two _get_client() calls must share one ConnectionPool instance."""
    srv = _fresh_module()
    import redis as redis_lib

    fake_pool = MagicMock()
    with patch.object(redis_lib, "ConnectionPool", return_value=fake_pool) as mock_pool_cls:
        c1 = srv._get_client()
        c2 = srv._get_client()
        assert mock_pool_cls.call_count == 1
        assert c1.connection_pool is c2.connection_pool
    srv._reset_pool()


def test_reset_pool_allows_new_pool():
    """_reset_pool() must allow a fresh pool on the next call."""
    srv = _fresh_module()
    import redis as redis_lib

    with patch.object(redis_lib, "ConnectionPool", return_value=MagicMock()) as mock_pool_cls:
        srv._get_client()
        srv._reset_pool()
        srv._get_client()
        assert mock_pool_cls.call_count == 2
    srv._reset_pool()


# ---------------------------------------------------------------------------
# P0-A: REDIS_TIMEOUT parsed as float
# ---------------------------------------------------------------------------


def test_timeout_half_second(monkeypatch):
    """REDIS_TIMEOUT=0.5 must produce socket_timeout=0.5, not truncated to 0."""
    srv = _fresh_module()
    import redis as redis_lib

    monkeypatch.setenv("REDIS_TIMEOUT", "0.5")
    with patch.object(redis_lib, "ConnectionPool", return_value=MagicMock()) as mock_pool_cls:
        srv._get_client()
        _, kwargs = mock_pool_cls.call_args
        assert kwargs["socket_timeout"] == 0.5
        assert kwargs["socket_connect_timeout"] == 0.5
    srv._reset_pool()


def test_timeout_integer_string_is_float(monkeypatch):
    """REDIS_TIMEOUT=3 must arrive as float 3.0, not int 3."""
    srv = _fresh_module()
    import redis as redis_lib

    monkeypatch.setenv("REDIS_TIMEOUT", "3")
    with patch.object(redis_lib, "ConnectionPool", return_value=MagicMock()) as mock_pool_cls:
        srv._get_client()
        _, kwargs = mock_pool_cls.call_args
        assert kwargs["socket_timeout"] == 3.0
        assert isinstance(kwargs["socket_timeout"], float)
    srv._reset_pool()


# ---------------------------------------------------------------------------
# P0-B: redis_health keyspace reflects active REDIS_DB
# ---------------------------------------------------------------------------


def test_health_keyspace_active_db2(monkeypatch):
    """redis_health must read keyspace from db2, not db0, when REDIS_DB=2."""
    srv = _fresh_module()
    monkeypatch.setenv("REDIS_DB", "2")
    client = _mock_client()
    client.info.return_value = {
        "redis_version": "7.0.0",
        "uptime_in_seconds": 100,
        "connected_clients": 1,
        "used_memory_human": "1M",
        "used_memory_peak_human": "2M",
        "total_commands_processed": 500,
        "role": "master",
        "db0": {"keys": 0, "expires": 0},
        "db2": {"keys": 42, "expires": 1},
    }
    with _inject(srv, client):
        result = srv.redis_health()
    assert result["status"] == "ok"
    assert result["keyspace"] == {"keys": 42, "expires": 1}


def test_health_keyspace_db0_default(monkeypatch):
    """redis_health defaults to db0 keyspace when REDIS_DB is unset."""
    srv = _fresh_module()
    monkeypatch.delenv("REDIS_DB", raising=False)
    client = _mock_client()
    client.info.return_value = {
        "redis_version": "7.0.0",
        "uptime_in_seconds": 10,
        "connected_clients": 1,
        "used_memory_human": "1M",
        "used_memory_peak_human": "1M",
        "total_commands_processed": 1,
        "role": "master",
        "db0": {"keys": 7, "expires": 0},
    }
    with _inject(srv, client):
        result = srv.redis_health()
    assert result["keyspace"] == {"keys": 7, "expires": 0}


# ---------------------------------------------------------------------------
# P1-A: redis_get — type()=="none" replaces exists() round-trip
# ---------------------------------------------------------------------------


def test_get_missing_key_no_exists_call():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "none"
    with _inject(srv, client):
        result = srv.redis_get("nonexistent:key")
    assert result["status"] == "not_found"
    assert result["key"] == "nonexistent:key"
    client.exists.assert_not_called()


def test_get_string_non_truncated():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "string"
    client.strlen.return_value = 5
    client.get.return_value = "hello"
    client.ttl.return_value = -1
    with _inject(srv, client):
        result = srv.redis_get("mykey")
    assert result["status"] == "ok"
    assert result["value"] == "hello"
    assert result["truncated"] is False
    assert "value_bytes" not in result


# ---------------------------------------------------------------------------
# P2-B: redis_get large-string truncation (value_bytes fix included)
# ---------------------------------------------------------------------------


def test_get_large_string_truncated_with_value_bytes():
    """Strings > 64 KB must return value_bytes, truncated=True, no raw value."""
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "string"
    client.strlen.return_value = 65537
    client.ttl.return_value = 300
    with _inject(srv, client):
        result = srv.redis_get("bigkey")
    assert result["status"] == "ok"
    assert result["truncated"] is True
    assert result["value"] == "<truncated>"
    assert result["value_bytes"] == 65537
    client.get.assert_not_called()


def test_get_string_at_64kb_boundary_not_truncated():
    """Strings exactly 65536 bytes must NOT be truncated."""
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "string"
    client.strlen.return_value = 65536
    client.get.return_value = "x" * 65536
    client.ttl.return_value = -1
    with _inject(srv, client):
        result = srv.redis_get("borderkey")
    assert result["truncated"] is False
    assert "value_bytes" not in result


# ---------------------------------------------------------------------------
# P2-B: redis_get large-set truncation
# ---------------------------------------------------------------------------


def test_get_large_set_capped_at_500():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "set"
    client.scard.return_value = 600
    client.sscan.return_value = (0, [str(i) for i in range(500)])
    client.ttl.return_value = -1
    with _inject(srv, client):
        result = srv.redis_get("bigset")
    assert result["truncated"] is True
    assert len(result["value"]) <= 500
    client.smembers.assert_not_called()


def test_get_small_set_not_truncated():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "set"
    client.scard.return_value = 3
    client.smembers.return_value = {"a", "b", "c"}
    client.ttl.return_value = -1
    with _inject(srv, client):
        result = srv.redis_get("smallset")
    assert result["truncated"] is False
    assert set(result["value"]) == {"a", "b", "c"}


# ---------------------------------------------------------------------------
# P2-B: redis_hgetall large-hash truncation
# ---------------------------------------------------------------------------


def test_hgetall_large_hash_field_names_only():
    """Hashes > 500 fields must return field names (list) with truncated=True."""
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "hash"
    client.hlen.return_value = 600
    client.hkeys.return_value = [f"field_{i}" for i in range(600)]
    client.ttl.return_value = -1
    with _inject(srv, client):
        result = srv.redis_hgetall("bighash")
    assert result["status"] == "ok"
    assert result["truncated"] is True
    assert isinstance(result["fields"], list)
    client.hgetall.assert_not_called()


def test_hgetall_small_hash_full_dict():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "hash"
    client.hlen.return_value = 3
    client.hgetall.return_value = {"f1": "v1", "f2": "v2", "f3": "v3"}
    client.ttl.return_value = 60
    with _inject(srv, client):
        result = srv.redis_hgetall("smallhash")
    assert result["truncated"] is False
    assert isinstance(result["fields"], dict)
    assert result["fields"]["f1"] == "v1"


def test_hgetall_missing_key_no_exists_call():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "none"
    with _inject(srv, client):
        result = srv.redis_hgetall("gone")
    assert result["status"] == "not_found"
    client.exists.assert_not_called()


def test_hgetall_wrong_type():
    srv = _fresh_module()
    client = _mock_client()
    client.type.return_value = "string"
    with _inject(srv, client):
        result = srv.redis_hgetall("notahash")
    assert result["status"] == "error"
    assert "string" in result["error"]


# ---------------------------------------------------------------------------
# P1-A: redis_ttl — no exists field; -2 encodes missing key
# ---------------------------------------------------------------------------


def test_ttl_missing_key_no_exists_field():
    srv = _fresh_module()
    client = _mock_client()
    client.ttl.return_value = -2
    with _inject(srv, client):
        result = srv.redis_ttl("gone")
    assert result["status"] == "ok"
    assert result["ttl_seconds"] == -2
    assert result["interpretation"] == "not_found"
    assert "exists" not in result
    client.exists.assert_not_called()


def test_ttl_no_expiry_no_exists_field():
    srv = _fresh_module()
    client = _mock_client()
    client.ttl.return_value = -1
    with _inject(srv, client):
        result = srv.redis_ttl("permanent")
    assert result["interpretation"] == "no_expiry"
    assert "exists" not in result


def test_ttl_expiring_key():
    srv = _fresh_module()
    client = _mock_client()
    client.ttl.return_value = 42
    with _inject(srv, client):
        result = srv.redis_ttl("expiring")
    assert result["interpretation"] == "expires_in_42s"


# ---------------------------------------------------------------------------
# P1-A: redis_del_key — existed derived from delete() return value
# ---------------------------------------------------------------------------


def test_del_key_existed_from_delete_return():
    """delete() returning 1 → existed=True; no exists() pre-check."""
    srv = _fresh_module()
    client = _mock_client()
    client.delete.return_value = 1
    with _inject(srv, client):
        result = srv.redis_del_key("mykey")
    assert result["existed"] is True
    assert result["deleted"] is True
    client.exists.assert_not_called()


def test_del_key_absent():
    """delete() returning 0 → existed=False, deleted=False."""
    srv = _fresh_module()
    client = _mock_client()
    client.delete.return_value = 0
    with _inject(srv, client):
        result = srv.redis_del_key("gone")
    assert result["existed"] is False
    assert result["deleted"] is False
    client.exists.assert_not_called()


# ---------------------------------------------------------------------------
# P1-B + dry_run: redis_flush_namespace
# ---------------------------------------------------------------------------


def test_flush_dry_run_default_no_delete():
    """dry_run=True (default) must never call delete()."""
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, ["adg:node:1", "adg:node:2"])
    with _inject(srv, client):
        result = srv.redis_flush_namespace("adg:node:*")
    assert result["dry_run"] is True
    assert result["matching_count"] == 2
    assert "sample" in result
    client.delete.assert_not_called()


def _make_pipeline_mock(batch_results: list[int]) -> MagicMock:
    """Return a mock pipeline whose execute() returns batch_results."""
    pipe = MagicMock()
    pipe.execute.return_value = batch_results
    return pipe


def test_flush_live_delete_truncated_false_when_under_cap():
    """Live delete path must include truncated=False when < 5000 matches."""
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, ["adg:node:1", "adg:node:2"])
    client.pipeline.return_value = _make_pipeline_mock([2])
    with _inject(srv, client):
        result = srv.redis_flush_namespace("adg:node:*", dry_run=False)
    assert result["dry_run"] is False
    assert "truncated" in result
    assert result["truncated"] is False
    assert result["deleted_count"] == 2


def test_flush_live_delete_truncated_true_when_capped():
    """truncated=True must appear when SCAN collected > 5000 keys."""
    srv = _fresh_module()
    client = _mock_client()
    calls = [0]

    def _scan_side(cursor, match=None, count=None):
        calls[0] += 1
        if calls[0] == 1:
            return (1, [f"k:{i}" for i in range(5001)])
        return (0, [])

    client.scan.side_effect = _scan_side
    # 11 batches of 500 (5001 keys → 10 full + 1 partial)
    client.pipeline.return_value = _make_pipeline_mock([500] * 10 + [1])
    with _inject(srv, client):
        result = srv.redis_flush_namespace("k:*", dry_run=False)
    assert result["truncated"] is True


# ---------------------------------------------------------------------------
# Batched pipeline delete behavior (D3 hardening)
# ---------------------------------------------------------------------------


def test_flush_uses_pipeline_not_direct_delete():
    """Live delete must use pipeline(transaction=False), not client.delete()."""
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, ["adg:node:1", "adg:node:2", "adg:node:3"])
    pipe = _make_pipeline_mock([3])
    client.pipeline.return_value = pipe
    with _inject(srv, client):
        srv.redis_flush_namespace("adg:node:*", dry_run=False)
    client.pipeline.assert_called_once_with(transaction=False)
    client.delete.assert_not_called()
    pipe.execute.assert_called_once()


def test_flush_batches_500_keys_per_pipeline_command():
    """1200 matched keys must produce 3 pipeline.delete() calls (500+500+200)."""
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, [f"k:{i}" for i in range(1200)])
    pipe = _make_pipeline_mock([500, 500, 200])
    client.pipeline.return_value = pipe
    with _inject(srv, client):
        result = srv.redis_flush_namespace("k:*", dry_run=False)
    # 3 separate pipe.delete() calls issued
    assert pipe.delete.call_count == 3
    # first batch is exactly 500 keys
    first_batch_keys = pipe.delete.call_args_list[0][0]
    assert len(first_batch_keys) == 500
    # last batch is remaining 200
    last_batch_keys = pipe.delete.call_args_list[2][0]
    assert len(last_batch_keys) == 200
    # deleted_count sums all batch results
    assert result["deleted_count"] == 1200


def test_flush_empty_match_no_pipeline_call():
    """No matched keys must skip pipeline entirely and return deleted_count=0."""
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, [])
    with _inject(srv, client):
        result = srv.redis_flush_namespace("gone:*", dry_run=False)
    client.pipeline.assert_not_called()
    assert result["deleted_count"] == 0
    assert result["truncated"] is False


# ---------------------------------------------------------------------------
# P2-A: redis_namespace_stats top_n clamp
# ---------------------------------------------------------------------------


def test_namespace_stats_top_n_clamped_to_100():
    """top_n=99999 must be silently clamped; no error raised."""
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, [f"ns{i}:key" for i in range(150)])
    with _inject(srv, client):
        result = srv.redis_namespace_stats(top_n=99999)
    assert result["status"] == "ok"
    assert len(result["namespaces"]) <= 100


def test_namespace_stats_default_top_n_20():
    srv = _fresh_module()
    client = _mock_client()
    client.scan.return_value = (0, [f"ns{i}:key" for i in range(30)])
    with _inject(srv, client):
        result = srv.redis_namespace_stats()
    assert len(result["namespaces"]) <= 20


# ---------------------------------------------------------------------------
# Consistent unavailable error shape across all 10 tools
# ---------------------------------------------------------------------------


_KEY_TOOLS = ["redis_get", "redis_hgetall", "redis_ttl", "redis_del_key"]
_NO_ARG_TOOLS = ["redis_health", "redis_dbsize", "redis_stats"]


@pytest.mark.parametrize("tool_name", _KEY_TOOLS)
def test_unavailable_key_tools(tool_name):
    srv = _fresh_module()
    with _inject_err(srv, "Redis connection refused: [Errno 111]"):
        result = getattr(srv, tool_name)("somekey")
    assert result["status"] == "unavailable"
    assert "error" in result


@pytest.mark.parametrize("tool_name", _NO_ARG_TOOLS)
def test_unavailable_no_arg_tools(tool_name):
    srv = _fresh_module()
    with _inject_err(srv, "Redis connection refused: [Errno 111]"):
        result = getattr(srv, tool_name)()
    assert result["status"] == "unavailable"
    assert "error" in result


def test_unavailable_flush_namespace():
    srv = _fresh_module()
    with _inject_err(srv):
        result = srv.redis_flush_namespace("adg:*")
    assert result["status"] == "unavailable"
    assert "error" in result


def test_unavailable_namespace_stats():
    srv = _fresh_module()
    with _inject_err(srv):
        result = srv.redis_namespace_stats()
    assert result["status"] == "unavailable"
    assert "error" in result


def test_unavailable_keys():
    srv = _fresh_module()
    with _inject_err(srv):
        result = srv.redis_keys()
    assert result["status"] == "unavailable"
    assert "error" in result
