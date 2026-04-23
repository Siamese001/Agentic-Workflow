"""Ad-hoc probe: prove the full L2 (ChromaDB + SQLite) path works end-to-end.

Run from repo root:
    python tools/debug/_probe_semantic_cache_l2.py

Requires Redis reachable via REDIS_URL (default redis://localhost:6379).
"""
from __future__ import annotations

import asyncio
import os
import os.path
import sqlite3
import sys


def main() -> int:
    os.environ["SEMANTIC_CACHE_D2_ENABLED"] = "1"
    os.environ["SEMANTIC_CACHE_PROMOTE_ENABLED"] = "1"
    os.environ["HIVE_MIND_STRICT_MODE"] = "false"
    os.environ["HIVE_MIND_TRACE_SAMPLING_RATE"] = "1.0"

    from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
        SemanticCacheManager,
    )

    SemanticCacheManager.reset_instance()
    mgr = SemanticCacheManager.get_instance()
    print(f"redis_enabled={mgr.redis_enabled} gptcache_enabled={mgr.gptcache_enabled}")
    if not mgr.gptcache_enabled:
        print("ChromaDB not initialized - skipping L2 proof")
        return 0

    ctx = "What is the capital of France?"
    ns = "l2_proof"
    payload = {"answer": "Paris", "evidence_ids": ["geo1"], "grounding_complete": True}
    # learn() first so isolation metadata is captured in Redis, then promote
    mgr.learn(ctx, ns, payload, feedback_score=0.9,
              tenant_id="", corpus_version="cv1", policy_version="pv1")
    asyncio.run(
        mgr.promote_to_long_term(ctx, ns, payload, feedback_score=0.9)
    )
    print("[1] promote_to_long_term done")

    con = sqlite3.connect("artifacts/gptcache/l2_cache.db")
    rows = con.execute(
        "SELECT id, substr(query,1,40), substr(response,1,60), tenant_id, "
        "embedding_model_id, corpus_version FROM l2_cache"
    ).fetchall()
    print(f"[2] SQLite l2_cache rows: {len(rows)}")
    for r in rows[-3:]:
        print("   ", r)

    chroma_db = "artifacts/gptcache/chroma/chroma.sqlite3"
    size = os.path.getsize(chroma_db) if os.path.exists(chroma_db) else 0
    print(f"[3] chroma.sqlite3 size: {size} bytes")

    import redis  # noqa: PLC0415

    rc = redis.from_url(
        os.environ.get("REDIS_URL", "redis://localhost:6379"), decode_responses=True
    )
    ctx_hash = mgr._compute_hash(ctx, ns)  # noqa: SLF001
    rc.delete(f"memory:{ctx_hash}")
    print("[4] Redis L1 manually evicted")

    hit = mgr.recall(ctx, ns, corpus_version="cv1", policy_version="pv1")
    got = hit.get("answer") if hit else None
    print(f"[5] recall same-context: hit={hit is not None} answer={got}")

    raw = rc.get(f"memory:{ctx_hash}")
    print(f"[6] L2->L1 writeback: {raw is not None}")

    rc.delete(f"memory:{ctx_hash}")
    mgr.invalidate_cache(corpus_version="cv1")
    print("[7] cleanup done")

    ok = (hit is not None) and (got == "Paris") and (raw is not None) and (size > 0)
    print("SEMANTIC CACHE L2 PATH:", "FULLY OPERATIONAL" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
