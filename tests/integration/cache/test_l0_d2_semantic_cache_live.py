"""End-to-end proof that the L0 semantic cache stack is operational.

Covers plan `semcache-make-live-7a2d4b` W4. Asserts:

- L1 write path: `SemanticCacheManager.learn()` produces a Redis `memory:<hash>` key.
- L1 read path: `SemanticCacheManager.recall()` returns the learned payload.
- L0 write wiring: `ExecutionOrchestrator._populate_d2_cache()` calls `learn` on
  a synthetic successful Path-D orchestration result.

The L2 (ChromaDB + BGE-M3) path is exercised by a separate marker so default
CI does not download the model.  Each test skips cleanly when Redis is absent.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any
from unittest.mock import MagicMock

import pytest


def _redis_available() -> bool:
    try:
        import redis  # noqa: PLC0415
    except ImportError:
        return False
    url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    try:
        redis.from_url(url, decode_responses=True).ping()
    except (ConnectionError, TimeoutError, OSError, ValueError):
        return False
    return True


pytestmark = pytest.mark.skipif(not _redis_available(), reason="Redis not reachable at REDIS_URL")


@pytest.fixture(autouse=True)
def _clean_singleton() -> None:
    """Reset singleton before and after each test so env overrides take effect."""
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    SemanticCacheManager.reset_instance()
    yield
    SemanticCacheManager.reset_instance()


@pytest.fixture
def _l1_only_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "0")
    monkeypatch.setenv("HIVE_MIND_STRICT_MODE", "false")
    monkeypatch.setenv("HIVE_MIND_TRACE_SAMPLING_RATE", "1.0")


@pytest.fixture
def _d1_and_d2_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    monkeypatch.setenv("EXACT_CACHE_D1_ENABLED", "1")
    monkeypatch.setenv("HIVE_MIND_STRICT_MODE", "false")
    monkeypatch.setenv("HIVE_MIND_TRACE_SAMPLING_RATE", "1.0")


def test_l1_write_and_read_cycle(_l1_only_env: None) -> None:
    """learn() → Redis key exists → recall() returns same payload."""
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    mgr = SemanticCacheManager.get_instance()
    assert mgr.redis_enabled is True
    assert mgr.gptcache_enabled is False  # L1-only

    ctx = f"semcache-live-test-{uuid.uuid4()}"
    ns = "test_l0_d2"
    payload = {"answer": 42, "evidence_ids": ["e1"], "embedding_model_id": "bge-m3-v1"}

    mgr.learn(ctx, ns, payload)
    # Redis direct probe
    import redis  # noqa: PLC0415

    client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
    ctx_hash = mgr._compute_hash(ctx, ns)
    raw = client.get(f"memory:{ctx_hash}")
    assert raw is not None, "learn() did not persist to Redis"
    stored = json.loads(raw)
    assert stored["answer"] == 42
    assert stored["_metadata"]["namespace"] == ns

    # Now recall — must return same payload (with metadata) via Redis L1
    hit = mgr.recall(ctx, ns)
    assert hit is not None
    assert hit["answer"] == 42
    stats = mgr.get_statistics()
    assert stats["redis_hits"] >= 1
    # Cleanup
    client.delete(f"memory:{ctx_hash}")


def test_l0_populate_d2_cache_wires_learn(_l1_only_env: None) -> None:
    """ExecutionOrchestrator._populate_d2_cache() writes via SemanticCacheManager.learn().

    Uses minimal seams — no real path router, no L3 — so we can directly invoke
    the helper with a synthesized Path-D L3 result.
    """
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    orch = ExecutionOrchestrator(
        assembler=MagicMock(),
        path_router=MagicMock(),
        d0_engine=MagicMock(),
        risk_gate=MagicMock(),
        cid_registry=MagicMock(),
        reentry_loop=MagicMock(),
        vigilance_dispatcher=MagicMock(),
        meta_bus=MagicMock(),
    )

    ctx = f"l0-d2-populate-{uuid.uuid4()}"
    ns = "test_l0_populate"
    path_obj = MagicMock()
    path_obj.value = "D"
    l3_result: dict[str, Any] = {
        "path": path_obj,
        "risk": MagicMock(),
        "cycle": MagicMock(),
        "state": "success",
        "orchestration": {
            "completed": True,
            "stage": "final",
            "signals": [],
            "metadata": {"evidence_ids": ["a", "b"], "grounding_complete": True, "feedback_score": 0.9},
        },
    }

    orch._populate_d2_cache(ctx, ns, tenant_id="", l3_result=l3_result)

    mgr = SemanticCacheManager.get_instance()
    import redis  # noqa: PLC0415

    client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
    ctx_hash = mgr._compute_hash(ctx, ns)
    raw = client.get(f"memory:{ctx_hash}")
    assert raw is not None, "_populate_d2_cache did not write L1"
    stored = json.loads(raw)
    assert stored["state"] == "success"
    assert stored["path"] == "D"
    assert stored["orchestration"]["completed"] is True

    # recall() must return the same payload
    hit = mgr.recall(ctx, ns)
    assert hit is not None
    assert hit["state"] == "success"

    client.delete(f"memory:{ctx_hash}")


def test_l1_scope_mismatch_suppresses_hit(_l1_only_env: None) -> None:
    """Redis row whose _metadata.tenant_id/corpus/policy differs from the
    caller MUST be treated as a miss (v11 R1B isolation on fast path)."""
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    mgr = SemanticCacheManager.get_instance()
    assert mgr.redis_enabled is True

    ctx = f"scope-mismatch-{uuid.uuid4()}"
    ns = "test_scope_iso"
    payload = {"answer": "tenantA-only", "evidence_ids": ["e1"]}
    mgr.learn(ctx, ns, payload, tenant_id="tenantA", corpus_version="corpus_v1", policy_version="pol_v1")

    # Same-scope MUST hit
    hit_same = mgr.recall(ctx, ns, tenant_id="tenantA", corpus_version="corpus_v1", policy_version="pol_v1")
    assert hit_same is not None
    assert hit_same["answer"] == "tenantA-only"

    # Cross-tenant MUST miss
    assert mgr.recall(ctx, ns, tenant_id="tenantB") is None
    # Cross-corpus MUST miss
    assert mgr.recall(ctx, ns, tenant_id="tenantA", corpus_version="corpus_v2") is None
    # Cross-policy MUST miss
    assert mgr.recall(ctx, ns, tenant_id="tenantA", policy_version="pol_v2") is None

    import redis  # noqa: PLC0415

    client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
    ctx_hash = mgr._compute_hash(ctx, ns)
    client.delete(f"memory:{ctx_hash}")


def test_populate_d2_cache_writes_isolation_fields(_d1_and_d2_env: None) -> None:
    """_populate_d2_cache now mirrors corpus_version + policy_version into
    the Redis _metadata payload so the new read-side scope check can enforce
    isolation on the fast path."""
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator
    from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

    orch = ExecutionOrchestrator(
        assembler=MagicMock(),
        path_router=MagicMock(),
        d0_engine=MagicMock(),
        risk_gate=MagicMock(),
        cid_registry=MagicMock(),
        reentry_loop=MagicMock(),
        vigilance_dispatcher=MagicMock(),
        meta_bus=MagicMock(),
    )
    mgr = SemanticCacheManager.get_instance()

    ctx = f"isolation-{uuid.uuid4()}"
    ns = "test_isolation"
    path_obj = MagicMock()
    path_obj.value = "D"
    l3_result = {
        "path": path_obj,
        "risk": MagicMock(),
        "cycle": MagicMock(),
        "state": "success",
        "orchestration": {
            "completed": True,
            "stage": "final",
            "signals": [],
            "metadata": {"evidence_ids": ["e"], "grounding_complete": True, "feedback_score": 0.9},
        },
    }
    orch._populate_d2_cache(
        ctx, ns, "tenantX", l3_result, corpus_version="corpus_a", policy_version="policy_a"
    )

    import redis as _r  # noqa: PLC0415

    client = _r.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
    ctx_hash = mgr._compute_hash(ctx, ns)
    raw = client.get(f"memory:{ctx_hash}")
    assert raw is not None
    stored = json.loads(raw)
    meta = stored["_metadata"]
    assert meta["tenant_id"] == "tenantX"
    assert meta["corpus_version"] == "corpus_a"
    assert meta["policy_version"] == "policy_a"
    assert meta["embedding_model_id"]  # auto-filled from _get_model_id()

    # Same-scope recall hits
    assert (
        mgr.recall(ctx, ns, tenant_id="tenantX", corpus_version="corpus_a", policy_version="policy_a")
        is not None
    )
    # Cross-corpus recall misses
    assert (
        mgr.recall(ctx, ns, tenant_id="tenantX", corpus_version="corpus_b", policy_version="policy_a") is None
    )

    client.delete(f"memory:{ctx_hash}")


def test_r1a_writeback_and_d1_hit(_d1_and_d2_env: None) -> None:
    """After _populate_d1_cache runs, the next check_d1_exact_cache call
    with the same canonical request MUST hit, short-circuiting as R1A."""
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator
    from agentic_core.L0_routing.reasoning.route_gates import (
        canonical_request_hash,
        check_d1_exact_cache,
    )
    from agentic_core.L4_state.utils.memory.l1_exact_cache import get_global_l1_cache

    orch = ExecutionOrchestrator(
        assembler=MagicMock(),
        path_router=MagicMock(),
        d0_engine=MagicMock(),
        risk_gate=MagicMock(),
        cid_registry=MagicMock(),
        reentry_loop=MagicMock(),
        vigilance_dispatcher=MagicMock(),
        meta_bus=MagicMock(),
    )

    # Use a unique request so we don't collide with other tests
    unique_token = str(uuid.uuid4())
    request = {"q": "who is the CEO?", "unique": unique_token}
    # _populate_d1_cache stores under the canonical_request_hash of the dict
    # when called through check_d1_exact_cache. But the orchestrator passes
    # payload_key (a string); we match that shape in the writeback call too.
    payload_key = canonical_request_hash(request)

    path_obj = MagicMock()
    path_obj.value = "D"
    l3_result = {
        "path": path_obj,
        "state": "success",
        "orchestration": {"completed": True, "answer": "Alice", "unique": unique_token},
    }
    orch._populate_d1_cache(payload_key, l3_result)

    # Now a D1 check for the same canonical request MUST hit
    cache = get_global_l1_cache()
    hit = cache.get(payload_key)
    assert hit is not None, "D1 writeback didn't land in L1ExactCache"
    # And the payload roundtrips as JSON
    payload = json.loads(hit.response)
    assert payload["state"] == "success"
    assert payload["orchestration"]["answer"] == "Alice"
    assert payload["orchestration"]["unique"] == unique_token

    # check_d1_exact_cache uses canonical_request_hash(request) as the key.
    # Our writeback used the same hash, so it MUST be returned by the gate.
    gate_hit = check_d1_exact_cache(request)
    assert gate_hit is not None, "check_d1_exact_cache didn't find the writeback"
    # check_d1_exact_cache wraps the parsed payload under "response"
    assert gate_hit["response"]["state"] == "success"
    assert gate_hit["response"]["orchestration"]["answer"] == "Alice"

    # Cleanup
    cache.delete(payload_key)


def test_execute_short_circuits_on_r1a_cache_hit(_d1_and_d2_env: None) -> None:
    """End-to-end proof: ExecutionOrchestrator.execute() runs the pipeline once,
    writes R1A/R1B, and the 2nd identical call short-circuits via route_gates
    WITHOUT calling _delegate_to_l3 (proving R1A and R1B are alive at the top
    of the execute() flow, not just in isolated helpers)."""
    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator
    from agentic_core.L0_routing.reasoning.route_gates import canonical_request_hash
    from agentic_core.L4_state.utils.memory.l1_exact_cache import get_global_l1_cache

    # Minimal mocks — enough for execute() to reach L3 delegation.
    class _Path:
        value = "D"

    class _Risk:
        allow = True

    class _Cycle:
        pass

    class _Payload:
        d0_injections = {}

    assembler = MagicMock()
    assembler.assemble.return_value = _Payload()

    path_router = MagicMock()
    path_router.select_path.return_value = _Path()

    d0_engine = MagicMock()
    d0_engine.render_d0.return_value = {}

    risk_gate = MagicMock()
    risk_gate.evaluate.return_value = _Risk()

    cid_registry = MagicMock()
    cid_registry.new_cycle.return_value = _Cycle()

    reentry_loop = MagicMock()

    # _delegate_to_l3 — first call returns a complete Path-D success.
    l3_call_count = {"n": 0}

    def _fake_delegate(path, payload, cycle, risk):  # noqa: ARG001
        l3_call_count["n"] += 1
        return {
            "path": _Path(),
            "risk": risk,
            "cycle": cycle,
            "state": "success",
            "orchestration": {
                "completed": True,
                "stage": "final",
                "signals": [],
                "answer": "live-e2e",
                "metadata": {
                    "evidence_ids": ["ev1"],
                    "grounding_complete": True,
                    "feedback_score": 0.95,
                },
            },
        }

    orch = ExecutionOrchestrator(
        assembler=assembler,
        path_router=path_router,
        d0_engine=d0_engine,
        risk_gate=risk_gate,
        cid_registry=cid_registry,
        reentry_loop=reentry_loop,
        vigilance_dispatcher=MagicMock(),
        meta_bus=MagicMock(),
    )
    orch._delegate_to_l3 = _fake_delegate  # type: ignore[method-assign]

    # Pre-clean: remove any prior writeback for this exact request
    unique = str(uuid.uuid4())
    intent = {
        "q": "what is the meaning of life?",
        "unique": unique,
        "tenant_id": "e2e_tenant",
        "namespace": "e2e_test",
        "corpus_version": "e2e_cv",
        "policy_version": "e2e_pv",
    }
    d1_key = canonical_request_hash(intent)
    l1 = get_global_l1_cache()
    l1.delete(d1_key)

    # === First call — pipeline runs end-to-end, writeback happens ===
    result1 = orch.execute(intent)
    assert l3_call_count["n"] == 1, "First call must invoke L3"
    assert result1.get("state") == "success", f"First call failed: {result1}"
    assert result1["orchestration"]["answer"] == "live-e2e"

    # Writeback verification
    l1_hit = l1.get(d1_key)
    assert l1_hit is not None, "R1A writeback did not land in L1ExactCache"

    # === Second call (identical intent) — MUST short-circuit via route_gates ===
    result2 = orch.execute(intent)
    assert l3_call_count["n"] == 1, (
        f"R1A short-circuit FAILED: _delegate_to_l3 was called "
        f"{l3_call_count['n']} times (should be 1 — second call must hit cache)"
    )
    assert result2.get("state") == "cache_hit", f"2nd call did not report cache_hit: {result2}"
    assert result2.get("selected_route") in ("R1A", "R1B"), (
        f"Unexpected route label: {result2.get('selected_route')}"
    )
    # R1A is checked first in check_route_gates, so this MUST be R1A
    assert result2["selected_route"] == "R1A", (
        f"Expected R1A (D1 is cheaper than D2), got {result2['selected_route']}"
    )
    # The cached payload survived the round-trip
    assert isinstance(result2["result"], dict)

    # Cleanup
    l1.delete(d1_key)


def test_d1_writeback_disabled_by_default() -> None:
    """With EXACT_CACHE_D1_ENABLED unset, _populate_d1_cache must no-op."""
    import os as _os

    _os.environ.pop("EXACT_CACHE_D1_ENABLED", None)

    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator
    from agentic_core.L0_routing.reasoning.route_gates import canonical_request_hash
    from agentic_core.L4_state.utils.memory.l1_exact_cache import get_global_l1_cache

    orch = ExecutionOrchestrator(
        assembler=MagicMock(),
        path_router=MagicMock(),
        d0_engine=MagicMock(),
        risk_gate=MagicMock(),
        cid_registry=MagicMock(),
        reentry_loop=MagicMock(),
        vigilance_dispatcher=MagicMock(),
        meta_bus=MagicMock(),
    )
    request = {"q": "disabled-default", "uid": str(uuid.uuid4())}
    payload_key = canonical_request_hash(request)
    path_obj = MagicMock()
    path_obj.value = "D"
    l3_result = {"path": path_obj, "state": "success", "orchestration": {"completed": True, "answer": "nope"}}

    orch._populate_d1_cache(payload_key, l3_result)
    cache = get_global_l1_cache()
    assert cache.get(payload_key) is None, "D1 writeback should be disabled when flag unset"
