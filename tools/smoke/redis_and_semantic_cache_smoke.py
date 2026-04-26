"""Smoke test: prove (1) Redis exact-match cache and (2) GPTCache-equivalent
semantic cache (NativePersistentCacheClient) are both alive end-to-end.

Run:
    python tools/smoke/redis_and_semantic_cache_smoke.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def test_redis_exact_match() -> dict:
    """Use the canonical DeterministicRedisCache (DB 0 hot cache)."""
    section("[1/2] Redis exact-match cache (DeterministicRedisCache, DB 0)")
    from agentic_core.cache.redis_cache_client import get_hot_cache

    cache = get_hot_cache()
    key = "smoke:redis:exact:demo"
    payload = {"q": "what is the capital of france?", "a": "Paris", "ts": time.time()}

    # Write
    t0 = time.perf_counter()
    cache.set(key, json.dumps(payload), ttl_seconds=60)
    write_ms = (time.perf_counter() - t0) * 1000.0

    # Exact-match read (HIT)
    t0 = time.perf_counter()
    raw = cache.get(key)
    read_ms = (time.perf_counter() - t0) * 1000.0
    hit = raw is not None and json.loads(raw)["a"] == "Paris"

    # Exact-match read of non-existent key (MISS)
    miss_raw = cache.get("smoke:redis:exact:does-not-exist-xyz")
    miss = miss_raw is None

    # Direct ping via the underlying client to prove TCP liveness
    client = cache._get_client()  # noqa: SLF001 — smoke test
    pong = client.ping() if client is not None else False

    print(f"  redis.ping()        -> {pong}")
    print(f"  SET {key!r}  ({write_ms:.2f} ms)")
    print(f"  GET (exact hit)     -> {raw!r}  ({read_ms:.2f} ms)")
    print(f"  GET (exact miss)    -> {miss_raw!r}")
    print(f"  hit={hit}  miss={miss}")

    return {
        "ping": bool(pong),
        "exact_hit": hit,
        "exact_miss_returns_none": miss,
        "write_ms": write_ms,
        "read_ms": read_ms,
    }


def test_semantic_cache() -> dict:
    """Use NativePersistentCacheClient — the GPTCache-equivalent semantic layer."""
    section("[2/2] Semantic cache (NativePersistentCacheClient — SQLite + ChromaDB + BGE-M3)")
    from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient

    # Use a dedicated smoke directory so we don't pollute the live cache
    smoke_dir = REPO_ROOT / "artifacts" / "_smoke_semantic_cache"
    cli = NativePersistentCacheClient(
        cache_dir=str(smoke_dir),
        similarity_threshold=0.80,  # generous so paraphrase will hit
        max_entries=128,
    )

    if cli._cache != "real":  # noqa: SLF001 — smoke test
        print("  WARN: cache is in mock mode — ChromaDB unavailable")
        return {"mode": "mock"}

    print(f"  cache_dir            = {smoke_dir}")
    print(f"  similarity_threshold = {cli.similarity_threshold}")
    print(f"  embedding_model      = {cli.embedding_model}")

    # Seed
    q1 = "How do I configure Redis for high availability?"
    a1 = "Use Redis Sentinel or Cluster with at least 3 masters."
    t0 = time.perf_counter()
    cli.set(q1, a1, tenant_id="smoke", embedding_model_id="bge-m3", ttl_seconds=300)
    set_ms = (time.perf_counter() - t0) * 1000.0
    print(f"  SET seed query       ({set_ms:.1f} ms)")

    # Exact-query hit
    t0 = time.perf_counter()
    exact = cli.get(q1, tenant_id="smoke", embedding_model_id="bge-m3")
    exact_ms = (time.perf_counter() - t0) * 1000.0
    print(f"  GET exact            -> {exact!r}  ({exact_ms:.1f} ms)")

    # Paraphrased query (the whole point of semantic caching)
    paraphrase = "What's the recommended way to make Redis highly available?"
    t0 = time.perf_counter()
    sim = cli.search_similar(paraphrase, tenant_id="smoke", embedding_model_id="bge-m3")
    sim_ms = (time.perf_counter() - t0) * 1000.0
    top = sim[0] if sim else None
    score = top["score"] if top else None
    print(f"  Paraphrase query     -> {paraphrase!r}")
    print(f"  search_similar top   -> score={score}  payload={top!r}  ({sim_ms:.1f} ms)")

    # Unrelated query -> miss
    unrelated = "What's the airspeed velocity of an unladen swallow?"
    t0 = time.perf_counter()
    miss = cli.search_similar(unrelated, tenant_id="smoke", embedding_model_id="bge-m3")
    miss_ms = (time.perf_counter() - t0) * 1000.0
    print(f"  Unrelated query      -> {len(miss)} results  ({miss_ms:.1f} ms)")

    stats = cli.get_stats()
    print(f"  stats                -> {stats}")

    return {
        "mode": "real",
        "exact_hit": exact == a1,
        "paraphrase_hit": bool(top) and score >= cli.similarity_threshold,
        "paraphrase_score": score,
        "unrelated_returns_no_hit": len(miss) == 0,
        "stats": stats,
    }


def main() -> int:
    overall = {"redis": None, "semantic": None, "errors": []}
    try:
        overall["redis"] = test_redis_exact_match()
    except Exception as exc:  # noqa: BLE001 — smoke test boundary
        overall["errors"].append(f"redis: {exc}")
        traceback.print_exc()

    try:
        overall["semantic"] = test_semantic_cache()
    except Exception as exc:  # noqa: BLE001 — smoke test boundary
        overall["errors"].append(f"semantic: {exc}")
        traceback.print_exc()

    section("SUMMARY")
    print(json.dumps(overall, indent=2, default=str))

    redis_ok = bool(overall["redis"] and overall["redis"].get("ping") and overall["redis"].get("exact_hit"))
    sem_ok = bool(
        overall["semantic"]
        and overall["semantic"].get("mode") == "real"
        and overall["semantic"].get("exact_hit")
        and overall["semantic"].get("paraphrase_hit")
    )
    print(f"\nRedis exact-match cache : {'PASS' if redis_ok else 'FAIL'}")
    print(f"Semantic cache          : {'PASS' if sem_ok else 'FAIL'}")
    return 0 if (redis_ok and sem_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
