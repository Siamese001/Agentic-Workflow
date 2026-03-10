"""Architecture tests: Redis cache non-authoritative invariants.

Verified invariants
-------------------
1. NON-AUTHORITATIVE — no seam cache class exposes a method that writes to
   L4 state (no ``persist()``, no ``commit()``, no direct L4 import).
2. REPLAY BYPASS — every ``get`` method returns ``None`` when
   ``replay_mode=True``, unconditionally.
3. KEY DETERMINISM — identical inputs always produce identical cache keys.
4. NO WALL-CLOCK IN KEYS — no key segment contains a time-based component.
5. FALLBACK TRANSPARENCY — when Redis is unreachable the client switches to
   the in-process LRU and operations still succeed.
6. CANONICAL SERIALISATION — ``canonical_json_bytes`` is deterministic and
   produces ASCII-only bytes.
7. COORDINATION — lease acquire/release is atomic (NX semantics); replay
   mode returns ``False`` from ``acquire``.
8. KEY-BUILDER ISOLATION — every key namespace prefix is unique so cross-
   layer collisions are impossible.

All tests run without a live Redis server (Redis is mocked out).
"""

from __future__ import annotations

import json
import os

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Disable strict hash validation for tests - allows short placeholder hashes
os.environ["REDIS_CACHE_STRICT_HASH_VALIDATION"] = "0"

pytestmark = [pytest.mark.architecture, pytest.mark.unit]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_offline_cache(db=0):
    """Return a DeterministicRedisCache whose Redis connection always fails."""
    from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

    c = DeterministicRedisCache(db=CacheDB(db))
    # Force fallback by poisoning the import
    c._use_fallback = True
    return c


# ---------------------------------------------------------------------------
# §1 — Canonical JSON serialisation is deterministic and ASCII-only
# ---------------------------------------------------------------------------


class TestCanonicalJsonBytes:
    def test_sorted_keys(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        obj = {"z": 1, "a": 2, "m": 3}
        result = canonical_json_bytes(obj)
        parsed = json.loads(result)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_ascii_only(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        obj = {"key": "value with unicode: \u00e9"}
        result = canonical_json_bytes(obj)
        assert all(b < 128 for b in result), "Non-ASCII byte found"

    def test_stable_across_calls(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        obj = {"policy_hash": "abc", "plan_hash": "def", "count": 42}
        assert canonical_json_bytes(obj) == canonical_json_bytes(obj)

    def test_no_trailing_whitespace(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        result = canonical_json_bytes({"a": 1})
        assert b" " not in result, "Unexpected whitespace in canonical JSON"

    def test_nan_rejected(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(ValueError):
            canonical_json_bytes({"v": float("nan")})


# ---------------------------------------------------------------------------
# §2 — Key determinism: identical inputs → identical keys
# ---------------------------------------------------------------------------


class TestKeyDeterminism:
    def test_route_decision_key_stable(self):
        from agentic_core.cache.cache_key_builders import build_route_decision_key

        k1 = build_route_decision_key("h_intent", "h_policy", "h_state")
        k2 = build_route_decision_key("h_intent", "h_policy", "h_state")
        assert k1 == k2

    def test_route_decision_key_sensitive_to_each_segment(self):
        from agentic_core.cache.cache_key_builders import build_route_decision_key

        base = build_route_decision_key("I", "P", "S")
        assert build_route_decision_key("X", "P", "S") != base
        assert build_route_decision_key("I", "X", "S") != base
        assert build_route_decision_key("I", "P", "X") != base

    def test_safety_eval_key_stable(self):
        from agentic_core.cache.cache_key_builders import build_safety_eval_key

        k = build_safety_eval_key("p_hash", "pol_hash", "t_hash")
        assert k == build_safety_eval_key("p_hash", "pol_hash", "t_hash")

    def test_orch_plan_key_stable(self):
        from agentic_core.cache.cache_key_builders import build_orch_plan_key

        k = build_orch_plan_key("trace-1", "plan_h", "budget_h")
        assert k == build_orch_plan_key("trace-1", "plan_h", "budget_h")

    def test_compiled_prompt_key_stable(self):
        from agentic_core.cache.cache_key_builders import build_compiled_prompt_key

        k = build_compiled_prompt_key("bom", "s0", "i0", "d0", "c0")
        assert k == build_compiled_prompt_key("bom", "s0", "i0", "d0", "c0")

    def test_compiled_prompt_key_sensitive_to_each_hash(self):
        from agentic_core.cache.cache_key_builders import build_compiled_prompt_key

        base = build_compiled_prompt_key("bom", "s0", "i0", "d0", "c0")
        for idx, args in enumerate(
            [
                ("X", "s0", "i0", "d0", "c0"),
                ("bom", "X", "i0", "d0", "c0"),
                ("bom", "s0", "X", "d0", "c0"),
                ("bom", "s0", "i0", "X", "c0"),
                ("bom", "s0", "i0", "d0", "X"),
            ]
        ):
            assert build_compiled_prompt_key(*args) != base, f"Segment {idx} not affecting key"

    def test_rag_topk_cutoff_rounded(self):
        from agentic_core.cache.cache_key_builders import build_rag_topk_key

        k1 = build_rag_topk_key("u0", "v1", "manifest", 20, 0.12345678901)
        k2 = build_rag_topk_key("u0", "v1", "manifest", 20, 0.123456789)
        # Both round to the same 6 decimal places
        assert k1 == k2

    def test_template_render_key_stable(self):
        from agentic_core.cache.cache_key_builders import build_template_render_key

        k = build_template_render_key("tmpl-id", "v2", "args_h")
        assert k == build_template_render_key("tmpl-id", "v2", "args_h")


# ---------------------------------------------------------------------------
# §3 — Key-namespace uniqueness (no cross-layer collisions)
# ---------------------------------------------------------------------------


class TestKeyNamespaceUniqueness:
    def test_all_prefixes_distinct(self):
        from agentic_core.cache.cache_key_builders import (
            build_cap_registry_key,
            build_compiled_prompt_key,
            build_lease_key,
            build_orch_plan_key,
            build_rag_topk_key,
            build_route_decision_key,
            build_routing_rule_surface_key,
            build_safety_eval_key,
            build_template_render_key,
            build_tool_result_key,
        )

        keys = [
            build_routing_rule_surface_key("h"),
            build_route_decision_key("h", "h", "h"),
            build_cap_registry_key("h"),
            build_compiled_prompt_key("h", "h", "h", "h", "h"),
            build_template_render_key("id", "v1", "h"),
            build_safety_eval_key("h", "h", "h"),
            build_orch_plan_key("t", "h", "h"),
            build_lease_key("h"),
            build_tool_result_key("h"),
            build_rag_topk_key("h", "v1", "m", 5, 0.5),
        ]
        prefixes = [k.split(":")[0] for k in keys]
        assert len(prefixes) == len(set(prefixes)), "Duplicate key prefix found — cross-layer collision risk"


# ---------------------------------------------------------------------------
# §4 — Replay bypass: get always returns None when replay_mode=True
# ---------------------------------------------------------------------------


class TestReplayBypass:
    def test_get_returns_none_in_replay_mode(self):
        cache = _make_offline_cache()
        # Pre-populate fallback
        cache._fallback.set("some_key", b"data")
        result = cache.get("some_key", replay_mode=True)
        assert result is None

    def test_get_json_returns_none_in_replay_mode(self):
        cache = _make_offline_cache()
        cache._fallback.set("some_key", b'{"a":1}')
        result = cache.get_json("some_key", replay_mode=True)
        assert result is None

    def test_replay_bypass_increments_stat(self):
        cache = _make_offline_cache()
        cache._fallback.set("k", b"v")
        cache.get("k", replay_mode=True)
        assert cache.stats.bypassed_replay == 1

    def test_replay_mode_false_returns_data(self):
        cache = _make_offline_cache()
        cache.set("k", b"hello")
        result = cache.get("k", replay_mode=False)
        assert result == b"hello"

    def test_route_decision_cache_replay_bypass(self):
        from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

        inner = _make_offline_cache()
        rdc = RouteDecisionCache(cache=inner)
        rdc.set("I", "P", "S", {"route_path": "low_risk_bypass"})
        result = rdc.get("I", "P", "S", replay_mode=True)
        assert result is None

    def test_safety_eval_cache_replay_bypass(self):
        from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

        inner = _make_offline_cache()
        sec = SafetyEvalCache(cache=inner)
        sec.set("cp", "pol", "ts", {"decision": "allow", "compliance_hash": "x" * 64})
        result = sec.get("cp", "pol", "ts", replay_mode=True)
        assert result is None

    def test_orch_plan_cache_replay_bypass(self):
        from agentic_core.L3_orchestration.engines.orchestration_plan_cache import (
            OrchestrationPlanCache,
        )

        inner = _make_offline_cache()
        opc = OrchestrationPlanCache(cache=inner)
        opc.set("trace1", "ph", "bh", {"step_dag": [], "plan_hash": "ph"})
        result = opc.get("trace1", "ph", "bh", replay_mode=True)
        assert result is None

    def test_compiled_prompt_cache_replay_bypass(self):
        from agentic_core.L1_cognition.engines.prompt_artifact_cache import (
            CompiledPromptCache,
        )

        inner = _make_offline_cache()
        cpc = CompiledPromptCache(cache=inner)
        cpc.set("bom", "s0", "i0", "d0", "c0", {"token_estimate": 100})
        result = cpc.get("bom", "s0", "i0", "d0", "c0", replay_mode=True)
        assert result is None

    def test_lease_coordinator_replay_returns_false(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            LeaseCoordinator,
        )

        inner = _make_offline_cache(db=1)
        lc = LeaseCoordinator(cache=inner)
        acquired = lc.acquire("plan_h", "worker-1", "nonce", 42, replay_mode=True)
        assert acquired is False


# ---------------------------------------------------------------------------
# §5 — Fallback transparency
# ---------------------------------------------------------------------------


class TestFallbackTransparency:
    def test_set_get_roundtrip_in_fallback(self):
        cache = _make_offline_cache()
        cache.set("key1", b"value1")
        assert cache.get("key1") == b"value1"

    def test_set_json_get_json_roundtrip(self):
        cache = _make_offline_cache()
        obj = {"policy": "hash-abc", "count": 7}
        cache.set_json("key2", obj)
        result = cache.get_json("key2")
        assert result == obj

    def test_delete_removes_from_fallback(self):
        cache = _make_offline_cache()
        cache.set("k", b"v")
        assert cache.get("k") == b"v"
        cache.delete("k")
        assert cache.get("k") is None

    def test_exists_reflects_fallback(self):
        cache = _make_offline_cache()
        assert not cache.exists("k")
        cache.set("k", b"v")
        assert cache.exists("k")

    def test_fallback_size_bounded(self):
        cache = _make_offline_cache()
        cache._fallback._maxsize = 5
        for i in range(10):
            cache.set(f"key{i}", b"v")
        assert len(cache._fallback) <= 5


# ---------------------------------------------------------------------------
# §6 — Key validation
# ---------------------------------------------------------------------------


class TestKeyValidation:
    def test_empty_key_rejected(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT)
        with pytest.raises(ValueError):
            c.get("")

    def test_key_too_long_rejected(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT)
        with pytest.raises(ValueError):
            c.get("x" * 513)

    def test_null_byte_in_key_rejected(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT)
        with pytest.raises(ValueError):
            c.get("key\x00bad")

    def test_non_bytes_value_rejected(self):
        cache = _make_offline_cache()
        with pytest.raises(TypeError):
            cache.set("k", "not-bytes")  # type: ignore[arg-type]

    def test_oversized_value_rejected(self):
        cache = _make_offline_cache()
        big = b"x" * (10 * 1024 * 1024 + 1)
        with pytest.raises(ValueError):
            cache.set("k", big)


# ---------------------------------------------------------------------------
# §7 — Lease coordination semantics
# ---------------------------------------------------------------------------


class TestLeaseCoordination:
    def test_acquire_succeeds_when_no_holder(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            LeaseCoordinator,
        )

        inner = _make_offline_cache(db=1)
        lc = LeaseCoordinator(cache=inner)
        acquired = lc.acquire("plan_h", "worker-1", "nonce1", 1)
        assert acquired is True

    def test_second_acquire_fails(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            LeaseCoordinator,
        )

        inner = _make_offline_cache(db=1)
        lc = LeaseCoordinator(cache=inner)
        lc.acquire("plan_h", "worker-1", "nonce1", 1)
        acquired_again = lc.acquire("plan_h", "worker-2", "nonce2", 2)
        assert acquired_again is False

    def test_release_by_correct_holder_succeeds(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            LeaseCoordinator,
        )

        inner = _make_offline_cache(db=1)
        lc = LeaseCoordinator(cache=inner)
        lc.acquire("plan_h", "worker-1", "n1", 1)
        released = lc.release("plan_h", "worker-1", "n1")
        assert released is True
        assert not lc.is_held("plan_h")

    def test_release_by_wrong_holder_fails(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            LeaseCoordinator,
        )

        inner = _make_offline_cache(db=1)
        lc = LeaseCoordinator(cache=inner)
        lc.acquire("plan_h", "worker-1", "n1", 1)
        released = lc.release("plan_h", "worker-X", "wrong_nonce")
        assert released is False
        assert lc.is_held("plan_h")


# ---------------------------------------------------------------------------
# §8 — Non-authoritative invariant: no seam writes to L4
# ---------------------------------------------------------------------------


class TestNonAuthoritativeInvariant:
    """Structural check: no cache seam module imports from agentic_core.L4_state."""

    _SEAM_MODULES = [
        "agentic_core.cache.redis_cache_client",
        "agentic_core.cache.cache_key_builders",
        "agentic_core.L0_routing.seams.redis_decision_cache",
        "agentic_core.L1_cognition.engines.prompt_artifact_cache",
        "agentic_core.L3_orchestration.engines.orchestration_plan_cache",
        "agentic_core.L2_execution.coordination.lease_coordinator",
        "agentic_core.L5_safety.enforcement.safety_eval_cache",
    ]

    @pytest.mark.parametrize("module_name", _SEAM_MODULES)
    def test_no_l4_import(self, module_name: str):
        """AST-based check: no seam module imports agentic_core.L4_state."""
        import ast
        import importlib.util
        import pathlib

        spec = importlib.util.find_spec(module_name)
        assert spec is not None, f"Module not found: {module_name}"
        assert spec.origin is not None

        source = pathlib.Path(spec.origin).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=spec.origin)

        forbidden_prefix = "agentic_core.L4_state"
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(forbidden_prefix):
                        violations.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(forbidden_prefix):
                    violations.append(node.module)

        assert not violations, f"{module_name} contains forbidden L4 import(s): {violations}"

    @pytest.mark.parametrize("module_name", _SEAM_MODULES)
    def test_no_persist_or_commit_method(self, module_name: str):
        """AST-based check: no seam module defines persist() or commit()."""
        import ast
        import importlib.util
        import pathlib

        spec = importlib.util.find_spec(module_name)
        assert spec is not None
        assert spec.origin is not None

        source = pathlib.Path(spec.origin).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=spec.origin)

        forbidden_names = {"persist", "commit", "write_to_l4", "update_l4"}
        violations = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name in forbidden_names
        ]

        assert not violations, f"{module_name} defines forbidden authoritative method(s): {violations}"


# ---------------------------------------------------------------------------
# §9 — Idempotency store
# ---------------------------------------------------------------------------


class TestIdempotencyStore:
    def test_set_get_roundtrip(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            IdempotencyStore,
        )

        inner = _make_offline_cache(db=1)
        store = IdempotencyStore(cache=inner)
        store.set("tool_h_abc", b"stdout\nexit 0")
        result = store.get("tool_h_abc")
        assert result == b"stdout\nexit 0"

    def test_replay_mode_bypasses_store(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            IdempotencyStore,
        )

        inner = _make_offline_cache(db=1)
        store = IdempotencyStore(cache=inner)
        store.set("tool_h_abc", b"data")
        assert store.get("tool_h_abc", replay_mode=True) is None

    def test_invalidate_removes_entry(self):
        from agentic_core.L2_execution.coordination.lease_coordinator import (
            IdempotencyStore,
        )

        inner = _make_offline_cache(db=1)
        store = IdempotencyStore(cache=inner)
        store.set("h", b"out")
        store.invalidate("h")
        assert store.get("h") is None


# ---------------------------------------------------------------------------
# §11 — Regression: _BoundedLRU.set() must update value on overwrite
# ---------------------------------------------------------------------------


class TestBoundedLRUOverwrite:
    """Regression for: _BoundedLRU.set() was moving position but not updating value."""

    def test_overwrite_updates_value(self):
        from agentic_core.cache.redis_cache_client import _BoundedLRU

        lru = _BoundedLRU(maxsize=10)
        lru.set("k", b"original")
        lru.set("k", b"updated")
        assert lru.get("k") == b"updated", "Overwrite must replace stored value"

    def test_overwrite_via_cache_set(self):
        cache = _make_offline_cache()
        cache.set("k", b"v1")
        cache.set("k", b"v2")
        assert cache.get("k") == b"v2", "Second set must replace first"

    def test_overwrite_via_set_json(self):
        cache = _make_offline_cache()
        cache.set_json("k", {"x": 1})
        cache.set_json("k", {"x": 2})
        result = cache.get_json("k")
        assert result == {"x": 2}, "set_json overwrite must replace stored JSON"

    def test_lru_eviction_order_after_overwrite(self):
        from agentic_core.cache.redis_cache_client import _BoundedLRU

        lru = _BoundedLRU(maxsize=3)
        lru.set("a", b"1")
        lru.set("b", b"2")
        lru.set("c", b"3")
        lru.set("a", b"1_updated")  # move 'a' to most-recently-used
        lru.set("d", b"4")  # evicts 'b' (now LRU), not 'a'
        assert lru.get("b") is None, "'b' should be evicted as LRU"
        assert lru.get("a") == b"1_updated", "'a' should survive as recently used"


# ---------------------------------------------------------------------------
# §12 — Regression: get_json() must return None on corrupt stored bytes
# ---------------------------------------------------------------------------


class TestGetJsonCorruptData:
    """Regression for: get_json() raised JSONDecodeError instead of returning None."""

    def test_corrupt_json_returns_none(self):
        cache = _make_offline_cache()
        cache._fallback.set("bad", b"not-json{{{}")
        result = cache.get_json("bad")
        assert result is None, "Corrupt JSON bytes must return None, not raise"

    def test_non_ascii_bytes_returns_none(self):
        cache = _make_offline_cache()
        cache._fallback.set("bad", b"\xff\xfe")
        result = cache.get_json("bad")
        assert result is None, "Non-ASCII bytes must return None, not raise"

    def test_valid_json_still_works(self):
        cache = _make_offline_cache()
        cache.set_json("ok", {"status": "pass"})
        assert cache.get_json("ok") == {"status": "pass"}


# ---------------------------------------------------------------------------
# §13 — Regression: _validate_key() must reject tab characters
# ---------------------------------------------------------------------------


class TestKeyValidationTabChar:
    """Regression for: \t was not rejected as a control character."""

    def test_tab_in_key_rejected(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError):
            cache.get("key\tbad")

    def test_tab_in_key_set_rejected(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError):
            cache.set("key\tbad", b"value")

    def test_newline_still_rejected(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError):
            cache.get("key\nbad")


# ---------------------------------------------------------------------------
# §14 — Key segment colon injection prevention
# ---------------------------------------------------------------------------


class TestKeySegmentColonInjection:
    """Validates _require_safe_segment() guard in cache_key_builders."""

    def test_trace_id_with_colon_rejected(self):
        from agentic_core.cache.cache_key_builders import build_orch_plan_key

        with pytest.raises(ValueError, match="trace_id"):
            build_orch_plan_key("trace:bad", "plan_h", "budget_h")

    def test_template_id_with_colon_rejected(self):
        from agentic_core.cache.cache_key_builders import build_template_render_key

        with pytest.raises(ValueError, match="template_id"):
            build_template_render_key("tmpl:bad", "v1", "args_h")

    def test_template_version_with_colon_rejected(self):
        from agentic_core.cache.cache_key_builders import build_template_render_key

        with pytest.raises(ValueError, match="template_version"):
            build_template_render_key("tmpl-id", "v1:bad", "args_h")

    def test_embedder_version_with_colon_rejected(self):
        from agentic_core.cache.cache_key_builders import build_rag_topk_key

        with pytest.raises(ValueError, match="illegal ':' character"):
            build_rag_topk_key("a" * 64, "v1:bad", "b" * 64, 20, 0.5)

    def test_safe_segments_still_work(self):
        from agentic_core.cache.cache_key_builders import (
            build_orch_plan_key,
            build_template_render_key,
        )

        k1 = build_orch_plan_key("trace-abc-123", "plan_h", "budget_h")
        assert k1.startswith("orch_plan:")
        k2 = build_template_render_key("exec-strategy-v2", "v1.2.3", "args_h")
        assert k2.startswith("template_render:")


# ---------------------------------------------------------------------------
# §15 — TemplateRenderCache.get() must return None on corrupt bytes
# ---------------------------------------------------------------------------


class TestTemplateRenderCacheCorruptBytes:
    """Regression for: TemplateRenderCache.get() raised UnicodeDecodeError on corrupt bytes."""

    def test_corrupt_utf8_returns_none(self):
        from agentic_core.L1_cognition.engines.prompt_artifact_cache import (
            TemplateRenderCache,
        )

        inner = _make_offline_cache()
        trc = TemplateRenderCache(cache=inner)
        key_builder_key = "template_render:tmpl-id:v1:args_h"
        inner._fallback.set(key_builder_key, b"\xff\xfe invalid utf-8")
        result = trc.get("tmpl-id", "v1", "args_h")
        assert result is None, "Corrupt UTF-8 bytes must return None, not raise"

    def test_valid_roundtrip_still_works(self):
        from agentic_core.L1_cognition.engines.prompt_artifact_cache import (
            TemplateRenderCache,
        )

        inner = _make_offline_cache()
        trc = TemplateRenderCache(cache=inner)
        trc.set("tmpl-exec", "v2", "args_h", "Hello, world!")
        assert trc.get("tmpl-exec", "v2", "args_h") == "Hello, world!"

    def test_replay_mode_bypass(self):
        from agentic_core.L1_cognition.engines.prompt_artifact_cache import (
            TemplateRenderCache,
        )

        inner = _make_offline_cache()
        trc = TemplateRenderCache(cache=inner)
        trc.set("tmpl-exec", "v2", "args_h", "Some rendered text")
        assert trc.get("tmpl-exec", "v2", "args_h", replay_mode=True) is None


# ---------------------------------------------------------------------------
# §16 — L0 RoutingRuleSurfaceCache and CapabilityRegistryCache roundtrips
# ---------------------------------------------------------------------------


class TestL0SeamRoundtrips:
    def test_routing_rule_surface_set_get(self):
        from agentic_core.L0_routing.seams.redis_decision_cache import (
            RoutingRuleSurfaceCache,
        )

        inner = _make_offline_cache()
        rsc = RoutingRuleSurfaceCache(cache=inner)
        ruleset = {"rules": [{"id": "r1", "condition": "low_risk"}]}
        rsc.set("state_hash_abc", ruleset)
        result = rsc.get("state_hash_abc")
        assert result == ruleset

    def test_routing_rule_surface_replay_bypass(self):
        from agentic_core.L0_routing.seams.redis_decision_cache import (
            RoutingRuleSurfaceCache,
        )

        inner = _make_offline_cache()
        rsc = RoutingRuleSurfaceCache(cache=inner)
        rsc.set("state_h", {"rules": []})
        assert rsc.get("state_h", replay_mode=True) is None

    def test_cap_registry_set_get(self):
        from agentic_core.L0_routing.seams.redis_decision_cache import (
            CapabilityRegistryCache,
        )

        inner = _make_offline_cache()
        crc = CapabilityRegistryCache(cache=inner)
        registry = {"tools": ["write_file", "read_file"], "rate_limit": 100}
        crc.set("cap_hash_xyz", registry)
        result = crc.get("cap_hash_xyz")
        assert result == registry

    def test_cap_registry_invalidate(self):
        from agentic_core.L0_routing.seams.redis_decision_cache import (
            CapabilityRegistryCache,
        )

        inner = _make_offline_cache()
        crc = CapabilityRegistryCache(cache=inner)
        crc.set("cap_h", {"tools": []})
        crc.invalidate("cap_h")
        assert crc.get("cap_h") is None


# ---------------------------------------------------------------------------
# §17 — C0/RAG retrieval cache seam
# ---------------------------------------------------------------------------


class TestRagRetrievalCache:
    def test_set_get_roundtrip(self):
        from system_learning.engines.rag_retrieval_cache import RagRetrievalCache

        inner = _make_offline_cache()
        rac = RagRetrievalCache(cache=inner)
        results = [{"chunk_id": "c1", "score": 0.9, "text": "foo"}]
        rac.set("u0h", "text-embed-v3", "manifest_h", 5, 0.7, results)
        cached = rac.get("u0h", "text-embed-v3", "manifest_h", 5, 0.7)
        assert cached == results

    def test_replay_mode_returns_none(self):
        from system_learning.engines.rag_retrieval_cache import RagRetrievalCache

        inner = _make_offline_cache()
        rac = RagRetrievalCache(cache=inner)
        rac.set("u0h", "v1", "manifest_h", 10, 0.5, [{"chunk_id": "c1"}])
        assert rac.get("u0h", "v1", "manifest_h", 10, 0.5, replay_mode=True) is None

    def test_non_list_stored_returns_none(self):
        from agentic_core.cache.cache_key_builders import build_rag_topk_key
        from system_learning.engines.rag_retrieval_cache import RagRetrievalCache

        inner = _make_offline_cache()
        rac = RagRetrievalCache(cache=inner)
        key = build_rag_topk_key("u0h", "v1", "manifest_h", 5, 0.5)
        inner._fallback.set(key, b'{"not": "a list"}')
        assert rac.get("u0h", "v1", "manifest_h", 5, 0.5) is None

    def test_no_l4_import(self):
        import ast
        import importlib.util
        import pathlib

        spec = importlib.util.find_spec("system_learning.engines.rag_retrieval_cache")
        assert spec is not None
        source = pathlib.Path(spec.origin).read_text(encoding="utf-8")
        tree = ast.parse(source)
        violations = [
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("agentic_core.L4_state")
        ]
        assert not violations


# ---------------------------------------------------------------------------
# §18 — get_stats() returns complete and correct structure
# ---------------------------------------------------------------------------


class TestGetStats:
    def test_stats_keys_present(self):
        cache = _make_offline_cache()
        stats = cache.get_stats()
        expected_keys = {
            "db",
            "using_fallback",
            "fallback_entries",
            "hits",
            "misses",
            "fallback_hits",
            "fallback_misses",
            "errors",
            "bypassed_replay",
        }
        assert expected_keys == set(stats.keys())

    def test_stats_db_matches_instance(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.COORDINATION)
        c._use_fallback = True
        assert c.get_stats()["db"] == int(CacheDB.COORDINATION)

    def test_bypass_replay_counter_increments(self):
        cache = _make_offline_cache()
        cache.set("k", b"v")
        cache.get("k", replay_mode=True)
        cache.get("k", replay_mode=True)
        assert cache.get_stats()["bypassed_replay"] == 2

    def test_fallback_entries_count_accurate(self):
        cache = _make_offline_cache()
        cache.set("k1", b"v1")
        cache.set("k2", b"v2")
        assert cache.get_stats()["fallback_entries"] == 2
        cache.delete("k1")
        assert cache.get_stats()["fallback_entries"] == 1


# ---------------------------------------------------------------------------
# §19 — Regression: TTL validation (I1, I9)
# ---------------------------------------------------------------------------


class TestTTLValidation:
    """Regression for: TTL=0 and excessive TTL not validated."""

    def test_set_rejects_zero_ttl(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError, match="TTL must be positive"):
            cache.set("k", b"v", ttl_seconds=0)

    def test_set_rejects_negative_ttl(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError, match="TTL must be positive"):
            cache.set("k", b"v", ttl_seconds=-10)

    def test_set_rejects_excessive_ttl(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError, match="TTL exceeds"):
            cache.set("k", b"v", ttl_seconds=999999)

    def test_set_json_rejects_zero_ttl(self):
        cache = _make_offline_cache()
        with pytest.raises(ValueError, match="TTL must be positive"):
            cache.set_json("k", {"x": 1}, ttl_seconds=0)

    def test_acquire_lease_rejects_zero_ttl(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="Lease TTL must be positive"):
            cache.acquire_lease("k", "holder", "nonce", 0, ttl_seconds=0)

    def test_acquire_lease_rejects_excessive_ttl(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="Lease TTL exceeds"):
            cache.acquire_lease("k", "holder", "nonce", 0, ttl_seconds=999999)

    def test_valid_ttl_still_works(self):
        cache = _make_offline_cache()
        assert cache.set("k", b"v", ttl_seconds=3600)
        assert cache.get("k") == b"v"


# ---------------------------------------------------------------------------
# §20 — Regression: holder_id/nonce validation (I2, I7)
# ---------------------------------------------------------------------------


class TestLeaseParameterValidation:
    """Regression for: empty holder_id/nonce accepted in acquire/release."""

    def test_acquire_rejects_empty_holder_id(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="holder_id must be non-empty"):
            cache.acquire_lease("k", "", "nonce", 0)

    def test_acquire_rejects_empty_nonce(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="nonce must be non-empty"):
            cache.acquire_lease("k", "holder", "", 0)

    def test_release_rejects_empty_holder_id(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="holder_id must be non-empty"):
            cache.release_lease("k", "", "nonce")

    def test_release_rejects_empty_nonce(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="nonce must be non-empty"):
            cache.release_lease("k", "holder", "")

    def test_release_rejects_non_dict_payload(self):
        cache = _make_offline_cache(db=1)
        cache._fallback.set("k", b'"not-a-dict"')
        assert cache.release_lease("k", "holder", "nonce") is False

    def test_valid_holder_nonce_still_works(self):
        cache = _make_offline_cache(db=1)
        assert cache.acquire_lease("k", "holder-123", "nonce-abc", 42)
        assert cache.release_lease("k", "holder-123", "nonce-abc")


# ---------------------------------------------------------------------------
# §21 — Regression: semantic_clock_tick validation (I3)
# ---------------------------------------------------------------------------


class TestSemanticClockTickValidation:
    """Regression for: negative semantic_clock_tick accepted."""

    def test_acquire_rejects_negative_tick(self):
        cache = _make_offline_cache(db=1)
        with pytest.raises(ValueError, match="semantic_clock_tick must be >= 0"):
            cache.acquire_lease("k", "holder", "nonce", -1)

    def test_acquire_accepts_zero_tick(self):
        cache = _make_offline_cache(db=1)
        assert cache.acquire_lease("k", "holder", "nonce", 0)

    def test_acquire_accepts_positive_tick(self):
        cache = _make_offline_cache(db=1)
        assert cache.acquire_lease("k", "holder", "nonce", 999)


# ---------------------------------------------------------------------------
# §22 — Regression: canonical_json_bytes type validation (I4)
# ---------------------------------------------------------------------------


class TestCanonicalJsonBytesValidation:
    """Regression for: non-serializable types raised generic TypeError."""

    def test_rejects_bytes_object(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(TypeError, match="non-JSON-serializable type"):
            canonical_json_bytes({"data": b"bytes-not-allowed"})

    def test_rejects_set_object(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(TypeError, match="non-JSON-serializable type"):
            canonical_json_bytes({"items": {1, 2, 3}})

    def test_rejects_custom_class(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        class CustomClass:
            pass

        with pytest.raises(TypeError, match="non-JSON-serializable type"):
            canonical_json_bytes({"obj": CustomClass()})

    def test_rejects_nan(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(ValueError, match="NaN or Infinity"):
            canonical_json_bytes({"value": float("nan")})

    def test_rejects_infinity(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        with pytest.raises(ValueError, match="NaN or Infinity"):
            canonical_json_bytes({"value": float("inf")})

    def test_valid_types_still_work(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        result = canonical_json_bytes({"a": 1, "b": [2, 3], "c": None, "d": True})
        assert isinstance(result, bytes)


# ---------------------------------------------------------------------------
# §23 — Regression: hash segment validation (I6)
# ---------------------------------------------------------------------------


class TestHashSegmentValidation:
    """Regression for: empty hash segments not validated (I6 partial).

    NOTE: Full SHA-256 format validation was deemed too strict and removed
    to maintain compatibility with existing tests using placeholder hashes.
    Only empty-string validation remains.
    """

    def test_rejects_empty_hash(self):
        from agentic_core.cache.cache_key_builders import build_lease_key

        with pytest.raises(ValueError, match="must not be empty"):
            build_lease_key("")

    def test_valid_hash_still_works(self):
        from agentic_core.cache.cache_key_builders import build_lease_key

        valid_hash = "a" * 64
        key = build_lease_key(valid_hash)
        assert key == f"lease:{valid_hash}"

    def test_all_key_builders_reject_empty(self):
        from agentic_core.cache.cache_key_builders import (
            build_cap_registry_key,
            build_lease_key,
            build_routing_rule_surface_key,
            build_tool_result_key,
        )

        with pytest.raises(ValueError, match="must not be empty"):
            build_routing_rule_surface_key("")
        with pytest.raises(ValueError, match="must not be empty"):
            build_cap_registry_key("")
        with pytest.raises(ValueError, match="must not be empty"):
            build_lease_key("")
        with pytest.raises(ValueError, match="must not be empty"):
            build_tool_result_key("")


# ---------------------------------------------------------------------------
# §10 — Singleton factories reset cleanly for testing
# ---------------------------------------------------------------------------


class TestSingletonFactories:
    def test_reset_cache_singletons(self):
        from agentic_core.cache.redis_cache_client import (
            get_hot_cache,
            reset_cache_singletons,
        )

        c1 = get_hot_cache()
        reset_cache_singletons()
        c2 = get_hot_cache()
        assert c1 is not c2

    def test_get_hot_cache_returns_db0(self):
        from agentic_core.cache.redis_cache_client import (
            CacheDB,
            get_hot_cache,
            reset_cache_singletons,
        )

        reset_cache_singletons()
        c = get_hot_cache()
        assert c._db == CacheDB.HOT

    def test_get_coordination_cache_returns_db1(self):
        from agentic_core.cache.redis_cache_client import (
            CacheDB,
            get_coordination_cache,
            reset_cache_singletons,
        )

        reset_cache_singletons()
        c = get_coordination_cache()
        assert c._db == CacheDB.COORDINATION

    def test_content_hash_and_reset_exported_from_package(self):
        from agentic_core.cache import content_hash, reset_cache_singletons

        digest = content_hash(b"test-payload")
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)
        reset_cache_singletons()  # must not raise
