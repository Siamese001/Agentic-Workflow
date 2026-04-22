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
