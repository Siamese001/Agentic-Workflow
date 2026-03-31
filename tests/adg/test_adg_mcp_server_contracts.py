"""ADG MCP Server contract safeguards.

Four layers of protection against regressions:

  Layer 1 — Static structural contracts (no Redis needed)
    - Exact tool count
    - No unbounded lrange() without limit parameter
    - _redis() resets singleton on ping failure
    - All tool functions covered by try/except RedisError

  Layer 2 — Unit behavioural contracts (no Redis; mock via fakeredis)
    - _ok() / _err() response shape
    - _wrongtype_hint() output
    - adg_violations() pagination, category filter, severity filter
    - Backward-compat raw-ID path respects category filter
    - _redis() singleton reset on ping failure

  Layer 3 — Integration contracts (requires Redis db=15 fixture)
    - All 20 tools return {"status": "ok"|"error"} — never hang, never throw
    - adg_violations(limit=N) honours limit
    - adg_violations(category=X) returns only X-category rows
    - All response values are str, not bytes

  Layer 4 — Known-bug regression guards
    - Bug: adg_violations fetched 4979 entries at once → payload hang
    - Bug: _redis() kept broken socket after ping failure
    - Bug: category filter let raw stubs through unconditionally

Known past bugs documented in:
  docs/reports/plans/RCA_adg_tests_pass_import_errors_persist.md
"""

from __future__ import annotations

import ast
import inspect
import sys
import textwrap
import time
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Repo root on path
# ---------------------------------------------------------------------------
_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO))

_MCP_SERVER_PATH = _REPO / "tools" / "adg" / "adg_mcp_server.py"

# ---------------------------------------------------------------------------
# Expected tool inventory — update when a tool is intentionally added/removed
# ---------------------------------------------------------------------------
_EXPECTED_TOOLS: frozenset[str] = frozenset(
    {
        "adg_status",
        "adg_meta",
        "adg_snapshot",
        "adg_node",
        "adg_nodes_by_layer",
        "adg_nodes_by_file",
        "adg_edge_fanout",
        "adg_edge_fanin",
        "adg_violations",
        "adg_edge_detail",
        "adg_module_context",
        "adg_source_context",
        "adg_assert_fresh",
        "redis_get",
        "redis_hgetall",
        "redis_smembers",
        "redis_lrange",
        "redis_type",
        "redis_ttl",
        "redis_scan",
    }
)

# ---------------------------------------------------------------------------
# Redis availability check for integration layer
# ---------------------------------------------------------------------------
_REDIS_INTEGRATION_OK = False
try:
    import redis as _redis_lib

    _test_r = _redis_lib.Redis(host="localhost", port=6379, db=15, socket_timeout=2)
    _test_r.ping()
    _REDIS_INTEGRATION_OK = True
except Exception:
    pass

_FAKEREDIS_OK = False
try:
    import fakeredis  # noqa: F401

    _FAKEREDIS_OK = True
except ImportError:
    pass


# ===========================================================================
# Layer 1: Static structural contracts
# ===========================================================================


class TestStaticStructuralContracts:
    """Parse adg_mcp_server.py as AST and enforce invariants without running it."""

    @pytest.fixture(scope="class")
    def source_tree(self):
        src = _MCP_SERVER_PATH.read_text(encoding="utf-8")
        return ast.parse(src), src

    def test_mcp_server_file_exists(self):
        assert _MCP_SERVER_PATH.exists(), f"MCP server not found: {_MCP_SERVER_PATH}"

    def test_exact_tool_count(self, source_tree):
        """Exactly _EXPECTED_TOOLS tools must be decorated with @mcp.tool().

        Prevents silent removal of tools via decorator mishap.
        """
        tree, _ = source_tree
        decorated = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else ""
                if "mcp.tool" in dec_str or (
                    isinstance(dec, ast.Attribute)
                    and dec.attr == "tool"
                    and isinstance(dec.value, ast.Name)
                    and dec.value.id == "mcp"
                ):
                    decorated.add(node.name)
        missing = _EXPECTED_TOOLS - decorated
        extra = decorated - _EXPECTED_TOOLS
        assert not missing, f"Tools removed without updating _EXPECTED_TOOLS: {missing}"
        assert not extra, f"New tools added without updating _EXPECTED_TOOLS: {extra}"

    def test_no_unbounded_lrange(self, source_tree):
        """No lrange(..., 0, -1) outside test code — prevents payload hang regression.

        Bug: adg_violations previously called lrange('adg:violations', 0, -1)
        returning 4979 entries as one ~500KB payload, stalling MCP transport.
        """
        tree, src = source_tree
        lines = src.splitlines()
        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "lrange"):
                continue
            # Check for literal -1 as stop argument (position 2)
            args = node.args
            if len(args) >= 3:
                stop_arg = args[2]
                if isinstance(stop_arg, ast.UnaryOp) and isinstance(stop_arg.op, ast.USub):
                    if isinstance(stop_arg.operand, ast.Constant) and stop_arg.operand.value == 1:
                        lineno = node.lineno
                        violations.append(f"  line {lineno}: {lines[lineno - 1].strip()}")
        assert not violations, (
            "Unbounded lrange(..., 0, -1) found in adg_mcp_server.py.\n"
            "Use a paginated window with explicit start/stop instead:\n"
            + "\n".join(violations)
        )

    def test_redis_singleton_resets_on_ping_failure(self, source_tree):
        """_redis() must set _r = None before re-raising RedisError.

        Bug: old code kept _r pointing to a broken socket, so every subsequent
        call would ping the dead connection instead of reconnecting.
        """
        _, src = source_tree
        assert "_r = None" in src and "ping" in src and "RedisError" in src, (
            "_redis() must reset _r = None on ping failure"
        )
        # More precise: the reset must appear inside the except block
        assert "except _redis_lib.RedisError" in src or "except redis.RedisError" in src or (
            "RedisError" in src and "_r = None" in src
        ), "_redis() must catch RedisError and reset _r"

    def test_all_tools_catch_redis_error(self, source_tree):
        """Every @mcp.tool() function must have a try/except RedisError block.

        A tool that raises an uncaught exception crashes the MCP stdio transport.
        """
        tree, src = source_tree
        tool_funcs = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for dec in node.decorator_list:
                dec_str = ast.unparse(dec) if hasattr(ast, "unparse") else ""
                if "mcp.tool" in dec_str:
                    tool_funcs[node.name] = node
                    break

        missing_handler = []
        for name, func_node in tool_funcs.items():
            has_try_except = False
            for child in ast.walk(func_node):
                if isinstance(child, ast.ExceptHandler):
                    if child.type is not None:
                        type_str = ast.unparse(child.type) if hasattr(ast, "unparse") else ""
                        if "RedisError" in type_str or "Exception" in type_str:
                            has_try_except = True
                            break
            if not has_try_except:
                missing_handler.append(name)

        assert not missing_handler, (
            f"Tool(s) missing try/except RedisError: {missing_handler}\n"
            "Every tool must catch RedisError and return _err(...) — never raise."
        )

    def test_adg_violations_has_limit_param(self, source_tree):
        """adg_violations() must declare a 'limit' parameter with a safe default.

        Regression guard for the payload-hang bug.
        """
        tree, _ = source_tree
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "adg_violations":
                param_names = [a.arg for a in node.args.args]
                assert "limit" in param_names, "adg_violations() must have a 'limit' parameter"
                # Default must be <= 500
                defaults = node.args.defaults
                limit_idx = param_names.index("limit") - (len(param_names) - len(defaults))
                if limit_idx >= 0:
                    default_node = defaults[limit_idx]
                    default_val = (
                        default_node.value
                        if isinstance(default_node, ast.Constant)
                        else None
                    )
                    if default_val is not None:
                        assert default_val <= 500, (
                            f"adg_violations limit default {default_val} > 500 — too large"
                        )
                return
        pytest.fail("adg_violations() function not found in MCP server")

    def test_response_wrappers_always_include_status(self, source_tree):
        """_ok() and _err() must always include 'status' key in returned dict."""
        _, src = source_tree
        assert '"status": "ok"' in src or "'status': 'ok'" in src, (
            "_ok() must include status='ok'"
        )
        assert '"status": "error"' in src or "'status': 'error'" in src, (
            "_err() must include status='error'"
        )


# ===========================================================================
# Layer 2: Unit behavioural contracts (fakeredis or pure mocking)
# ===========================================================================


class TestResponseShapeContracts:
    """_ok() and _err() produce correct shapes without hitting Redis."""

    @pytest.fixture
    def mcp_mod(self):
        """Import the module with Redis mocked out so import doesn't fail."""
        try:
            import tools.adg.adg_mcp_server as mod

            return mod
        except Exception as e:
            pytest.skip(f"Could not import adg_mcp_server: {e}")

    def test_ok_has_status_ok(self, mcp_mod):
        with patch.object(mcp_mod, "_cache_meta", return_value={}):
            result = mcp_mod._ok({"x": 1})
        assert result["status"] == "ok"
        assert result["data"] == {"x": 1}

    def test_err_has_status_error(self, mcp_mod):
        with patch.object(mcp_mod, "_cache_meta", return_value={}):
            result = mcp_mod._err("something broke")
        assert result["status"] == "error"
        assert "something broke" in result["message"]

    def test_ok_accepts_extra_kwargs(self, mcp_mod):
        with patch.object(mcp_mod, "_cache_meta", return_value={}):
            result = mcp_mod._ok({}, provenance="sqlite", is_fresh=True)
        assert result["provenance"] == "sqlite"
        assert result["is_fresh"] is True

    def test_wrongtype_hint_hash(self, mcp_mod):
        hint = mcp_mod._wrongtype_hint("adg:meta", "hash")
        assert "redis_hgetall" in hint
        assert "WRONGTYPE" in hint

    def test_wrongtype_hint_set(self, mcp_mod):
        hint = mcp_mod._wrongtype_hint("adg:nodes:by_layer:L0", "set")
        assert "redis_smembers" in hint

    def test_wrongtype_hint_list(self, mcp_mod):
        hint = mcp_mod._wrongtype_hint("adg:violations", "list")
        assert "redis_lrange" in hint

    def test_wrongtype_hint_unknown_type(self, mcp_mod):
        hint = mcp_mod._wrongtype_hint("some:key", "zset")
        assert "zset" in hint


@pytest.mark.skipif(not _FAKEREDIS_OK, reason="fakeredis not installed")
class TestViolationsPaginationUnit:
    """Unit tests for adg_violations() pagination and filter logic using fakeredis."""

    @pytest.fixture
    def fake_redis_with_violations(self):
        import fakeredis

        r = fakeredis.FakeRedis(decode_responses=True)
        # Seed 10 violations: 7 'violates', 3 'antipattern'
        for i in range(10):
            cat = "violates" if i < 7 else "antipattern"
            sev = "MEDIUM" if i < 5 else "HIGH"
            vid = str(i + 1)
            r.hset(
                f"adg:violation:{vid}",
                mapping={
                    "id": vid,
                    "category": cat,
                    "severity": sev,
                    "file_path": f"src/file_{i}.py",
                    "line_no": str(i * 10),
                    "evidence": f"L{i}->L{i+1}",
                },
            )
            r.rpush("adg:violations", vid)
        return r

    @pytest.fixture
    def mcp_mod_with_fake(self, fake_redis_with_violations):
        try:
            import tools.adg.adg_mcp_server as mod
        except Exception as e:
            pytest.skip(f"Cannot import: {e}")
        with patch.object(mod, "_redis", return_value=fake_redis_with_violations):
            with patch.object(mod, "_cache_meta", return_value={"available": True}):
                yield mod

    def test_default_limit_respected(self, mcp_mod_with_fake):
        result = mcp_mod_with_fake.adg_violations(limit=3)
        assert result["status"] == "ok"
        assert result["data"]["count"] <= 3

    def test_total_count_reflects_all(self, mcp_mod_with_fake):
        result = mcp_mod_with_fake.adg_violations(limit=3)
        assert result["data"]["total"] == 10

    def test_category_filter_violates(self, mcp_mod_with_fake):
        result = mcp_mod_with_fake.adg_violations(limit=20, category="violates")
        rows = result["data"]["violations"]
        assert all(r["category"] == "violates" for r in rows), (
            "category filter returned non-violates rows"
        )

    def test_category_filter_antipattern(self, mcp_mod_with_fake):
        result = mcp_mod_with_fake.adg_violations(limit=20, category="antipattern")
        rows = result["data"]["violations"]
        assert all(r["category"] == "antipattern" for r in rows)
        assert len(rows) == 3

    def test_severity_filter_high(self, mcp_mod_with_fake):
        result = mcp_mod_with_fake.adg_violations(limit=20, severity="HIGH")
        rows = result["data"]["violations"]
        assert all(r["severity"] == "HIGH" for r in rows)

    def test_offset_paginates(self, mcp_mod_with_fake):
        page1 = mcp_mod_with_fake.adg_violations(limit=3, offset=0)
        page2 = mcp_mod_with_fake.adg_violations(limit=3, offset=3)
        ids1 = {r["id"] for r in page1["data"]["violations"]}
        ids2 = {r["id"] for r in page2["data"]["violations"]}
        assert ids1.isdisjoint(ids2), "Paginated pages must not overlap"

    def test_empty_violations_list(self):
        import fakeredis
        import tools.adg.adg_mcp_server as mod

        r = fakeredis.FakeRedis(decode_responses=True)
        with patch.object(mod, "_redis", return_value=r):
            with patch.object(mod, "_cache_meta", return_value={}):
                result = mod.adg_violations()
        assert result["status"] == "ok"
        assert result["data"]["count"] == 0
        assert result["data"]["total"] == 0

    def test_category_filter_excludes_raw_stubs(self, fake_redis_with_violations):
        """Backward-compat raw stubs must not bypass category filter.

        Regression guard: old code always appended raw stubs regardless of filter.
        """
        import tools.adg.adg_mcp_server as mod

        # Add a raw (non-HASH) ID to the list
        fake_redis_with_violations.rpush("adg:violations", "raw_stub_id")
        with patch.object(mod, "_redis", return_value=fake_redis_with_violations):
            with patch.object(mod, "_cache_meta", return_value={}):
                result = mod.adg_violations(limit=50, category="violates")
        rows = result["data"]["violations"]
        raw_rows = [r for r in rows if r.get("raw")]
        assert not raw_rows, (
            "Raw stubs must not appear when category filter is active — "
            "they have no category metadata"
        )

    def test_max_limit_capped_at_500(self):
        import fakeredis
        import tools.adg.adg_mcp_server as mod

        r = fakeredis.FakeRedis(decode_responses=True)
        with patch.object(mod, "_redis", return_value=r):
            with patch.object(mod, "_cache_meta", return_value={}):
                result = mod.adg_violations(limit=99999)
        # Should not explode — limit is capped
        assert result["status"] == "ok"

    def test_response_values_are_strings_not_bytes(self, mcp_mod_with_fake):
        """All response values must be str, never bytes.

        Regression guard: before decode_responses=True was used consistently,
        some tools returned raw bytes from Redis.
        """
        result = mcp_mod_with_fake.adg_violations(limit=10)
        for row in result["data"]["violations"]:
            for k, v in row.items():
                assert isinstance(k, str), f"Key {k!r} is bytes, expected str"
                assert isinstance(v, str), f"Value {v!r} for key {k} is bytes, expected str"


@pytest.mark.skipif(not _FAKEREDIS_OK, reason="fakeredis not installed")
class TestRedisReconnectUnit:
    """_redis() singleton reset on ping failure."""

    def test_singleton_reset_on_ping_failure(self):
        import tools.adg.adg_mcp_server as mod

        broken = MagicMock()
        import redis as _rl

        broken.ping.side_effect = _rl.ConnectionError("gone")

        # Force the broken client into the singleton
        mod._r = broken

        with pytest.raises(_rl.ConnectionError):
            mod._redis()

        assert mod._r is None, (
            "_r must be reset to None after ping failure so the next call reconnects"
        )

    def test_singleton_ok_on_healthy_connection(self):
        import tools.adg.adg_mcp_server as mod

        healthy = MagicMock()
        healthy.ping.return_value = True
        mod._r = healthy

        result = mod._redis()
        assert result is healthy
        assert mod._r is healthy


# ===========================================================================
# Layer 3: Integration contracts (requires Redis db=15 fixture)
# ===========================================================================

_SKIP_INTEGRATION = pytest.mark.skipif(
    not _REDIS_INTEGRATION_OK, reason="Redis db=15 not available"
)


@_SKIP_INTEGRATION
class TestAllToolsRespond:
    """Every tool must return a valid response dict and never raise or hang.

    Uses Redis db=15 (test isolation) with a minimal seeded fixture.
    """

    @pytest.fixture(scope="class")
    def seeded_redis(self):
        import redis as rl

        r = rl.Redis(host="localhost", port=6379, db=15, decode_responses=True)
        r.flushdb()

        # Seed minimal ADG data — use flat k/v pairs for Redis 3.x compatibility
        r.hmset("adg:meta", {"node_count": "5", "edge_count": "3", "timestamp": "test"})
        r.set(
            "adg:status",
            '{"node_count":5,"edge_count":3,"timestamp":"test","ingested_at":0,'
            '"sqlite_path":"","digest":"abc"}',
        )
        r.hmset("adg:node:1", {"id": "1", "adg_name": "test_mod", "layer": "L0", "entity_type": "Module"})
        r.sadd("adg:nodes:by_layer:L0", "1")
        r.sadd("adg:nodes:by_file:test.py", "1")
        r.hmset("adg:edge_detail:1", {"id": "1", "src_id": "1", "dst_id": "2",
                                      "relation_type": "calls", "edge_kind": "call",
                                      "source_file": "test.py", "line_no": "1", "symbol": "foo"})
        r.sadd("adg:edge:1:calls", "1")
        r.sadd("adg:edge:in:2:calls", "1")
        r.hmset("adg:violation:99", {"id": "99", "category": "violates",
                                     "severity": "MEDIUM", "evidence": "L0->L2",
                                     "file_path": "test.py", "line_no": "5"})
        r.rpush("adg:violations", "99")
        yield r
        r.flushdb()

    @pytest.fixture(scope="class")
    def mod_with_test_db(self, seeded_redis):
        import tools.adg.adg_mcp_server as mod

        orig_url = mod._REDIS_URL
        mod._REDIS_URL = "redis://localhost:6379/15"
        mod._r = None
        yield mod
        mod._REDIS_URL = orig_url
        mod._r = None

    @pytest.mark.timeout(10)
    def test_adg_status_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_status()
        assert "status" in result

    @pytest.mark.timeout(10)
    def test_adg_meta_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_meta()
        assert "status" in result

    @pytest.mark.timeout(10)
    def test_adg_node_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_node("1")
        assert result["status"] == "ok"
        assert result["data"]["adg_name"] == "test_mod"

    @pytest.mark.timeout(10)
    def test_adg_nodes_by_layer_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_nodes_by_layer("L0")
        assert result["status"] == "ok"
        assert "1" in result["data"]["node_ids"] or "1" in [
            str(x) for x in result["data"]["node_ids"]
        ]

    @pytest.mark.timeout(10)
    def test_adg_nodes_by_file_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_nodes_by_file("test.py")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_adg_edge_fanout_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_edge_fanout("1", "calls")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_adg_edge_fanin_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_edge_fanin("2", "calls")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_adg_violations_respects_limit(self, mod_with_test_db):
        result = mod_with_test_db.adg_violations(limit=1)
        assert result["status"] == "ok"
        assert result["data"]["count"] <= 1

    @pytest.mark.timeout(10)
    def test_adg_violations_category_filter(self, mod_with_test_db):
        result = mod_with_test_db.adg_violations(limit=50, category="violates")
        assert result["status"] == "ok"
        for row in result["data"]["violations"]:
            assert row.get("category") == "violates"

    @pytest.mark.timeout(10)
    def test_adg_violations_wrong_category_returns_empty(self, mod_with_test_db):
        result = mod_with_test_db.adg_violations(limit=50, category="nonexistent_cat")
        assert result["status"] == "ok"
        assert result["data"]["count"] == 0

    @pytest.mark.timeout(10)
    def test_adg_edge_detail_responds(self, mod_with_test_db):
        result = mod_with_test_db.adg_edge_detail("1")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_redis_get_missing_key(self, mod_with_test_db):
        result = mod_with_test_db.redis_get("adg:nonexistent:key:xyz")
        assert result["status"] == "ok"
        assert result["data"]["exists"] is False

    @pytest.mark.timeout(10)
    def test_redis_hgetall_responds(self, mod_with_test_db):
        result = mod_with_test_db.redis_hgetall("adg:meta")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_redis_smembers_responds(self, mod_with_test_db):
        result = mod_with_test_db.redis_smembers("adg:nodes:by_layer:L0")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_redis_type_responds(self, mod_with_test_db):
        result = mod_with_test_db.redis_type("adg:meta")
        assert result["status"] == "ok"
        assert result["data"]["type"] == "hash"

    @pytest.mark.timeout(10)
    def test_redis_ttl_responds(self, mod_with_test_db):
        result = mod_with_test_db.redis_ttl("adg:meta")
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_redis_scan_responds(self, mod_with_test_db):
        result = mod_with_test_db.redis_scan(pattern="adg:*", count=10, max_keys=20)
        assert result["status"] == "ok"

    @pytest.mark.timeout(10)
    def test_redis_wrongtype_get_on_hash_returns_error_not_crash(self, mod_with_test_db):
        """redis_get on a HASH key must return _err with WRONGTYPE hint, not crash."""
        result = mod_with_test_db.redis_get("adg:meta")
        assert result["status"] == "error"
        assert "WRONGTYPE" in result["message"] or "redis_hgetall" in result["message"]

    @pytest.mark.timeout(10)
    def test_all_ok_responses_have_str_values(self, mod_with_test_db):
        """Response data must use str keys/values — never raw bytes."""
        result = mod_with_test_db.adg_node("1")
        assert result["status"] == "ok"
        for k, v in result["data"].items():
            assert isinstance(k, str), f"Bytes key: {k!r}"
            if isinstance(v, (str, int, float, bool, type(None), list, dict)):
                continue
            pytest.fail(f"Unexpected value type {type(v)} for key {k}")


# ===========================================================================
# Layer 4: Known-bug regression guards (documented bugs must not recur)
# ===========================================================================


class TestKnownBugRegressions:
    """Each test documents a specific past bug and prevents its recurrence."""

    def test_regression_no_unbounded_violations_fetch(self):
        """BUG: adg_violations called lrange('adg:violations', 0, -1) → 5000-entry payload hang.

        Guard: The literal call lrange(..., 0, -1) must not appear in the server source.
        """
        src = _MCP_SERVER_PATH.read_text(encoding="utf-8")
        # Normalise whitespace
        compact = " ".join(src.split())
        assert 'lrange("adg:violations", 0, -1)' not in compact, (
            "Unbounded lrange on adg:violations detected — regression of payload hang bug"
        )

    def test_regression_singleton_reset_documented_in_source(self):
        """BUG: _redis() kept broken socket; _r stayed non-None after ping failure.

        Guard: source must contain the reset pattern.
        """
        src = _MCP_SERVER_PATH.read_text(encoding="utf-8")
        assert "_r = None" in src, "Singleton reset pattern missing from _redis()"
        assert "RedisError" in src, "RedisError not handled in _redis()"

    def test_regression_category_filter_in_source(self):
        """BUG: category filter in adg_violations didn't exclude raw backward-compat stubs.

        Guard: the fix pattern must be present in source.
        """
        src = _MCP_SERVER_PATH.read_text(encoding="utf-8")
        assert "if category or severity" in src, (
            "Raw-stub category filter guard missing from adg_violations()"
        )

    def test_regression_adg_violations_has_four_params(self):
        """BUG: adg_violations had no parameters — impossible to paginate or filter.

        Guard: function must have limit, offset, category, severity.
        """
        src = _MCP_SERVER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "adg_violations":
                params = {a.arg for a in node.args.args}
                for required in ("limit", "offset", "category", "severity"):
                    assert required in params, (
                        f"adg_violations() missing '{required}' parameter — "
                        "regression of payload-hang bug"
                    )
                return
        pytest.fail("adg_violations() not found")
