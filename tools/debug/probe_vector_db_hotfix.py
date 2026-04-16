"""Validate the vector_db hotfix at the same code path the MCP adapter uses.

Instantiates VectorRetrievalService (the singleton the MCP adapter calls),
triggers the prewarm helper (same as the __main__ block), and runs:
  1. readiness check (non-blocking)
  2. cold first query (measured)
  3. warm second query (measured)
  4. concurrent query pair (cancel-safety smoke)

Emits phase timings from the logger injected in vector_service.query_collection.
Temporary diagnostic script — safe to delete after hotfix closeout.
"""

from __future__ import annotations

import logging
import sys
import threading
import time
from pathlib import Path

# Ensure repo root on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Stream vector_service INFO logs to stdout so we see QUERY_PHASE lines
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s", stream=sys.stdout)

from tools.mcp import vector_db_server  # noqa: E402
from tools.retrieval.vector_service import get_vector_service  # noqa: E402

QUERY = "normative requirements specification for the agentic routing system"
COLLECTION = "repo_evidence"


def section(label: str) -> None:
    print(f"\n===== {label} =====")


def main() -> None:
    section("1. STARTUP PREWARM (same as __main__)")
    t0 = time.monotonic()
    vector_db_server._start_background_prewarm()
    print(f"prewarm_dispatched_s={round(time.monotonic() - t0, 4)}")

    section("2. READINESS while warming")
    svc = get_vector_service()
    ready = svc.readiness()
    print(
        f"chroma_ready={ready.chroma_ready} chroma_loading={ready.chroma_loading}"
        f" model_ready={ready.embedding_model_ready} model_loading={ready.embedding_model_loading}"
        f" prewarm_enabled={ready.background_prewarm_enabled}"
    )

    # Give prewarm a chance to finish (bounded wait)
    for _ in range(60):
        r = svc.readiness()
        if r.chroma_ready and r.embedding_model_ready:
            break
        time.sleep(0.5)
    r = svc.readiness()
    print(f"post_wait chroma_ready={r.chroma_ready} model_ready={r.embedding_model_ready}")

    section("3. FIRST QUERY (should be fast now — prewarm already warmed)")
    t0 = time.monotonic()
    # Use default include (metadatas, documents, distances) — NOT passing `include`
    # on purpose to hit the default path. The hit-assembly in query_collection
    # iterates documents; passing include=["distances"] alone would return hits=0
    # (pre-existing issue, out of scope for this hotfix).
    report = svc.query_collection(COLLECTION, QUERY, n_results=3)
    first_s = time.monotonic() - t0
    print(f"first_query_total_s={round(first_s, 3)}")
    print(f"  embed_s={round(report.embedding_time_s, 3)} chroma_s={round(report.query_time_s, 3)}")
    print(f"  hits={len(report.hits)}")
    if report.hits:
        h0 = report.hits[0]
        print(f"  top_hit_dist={h0.distance:.4f}")
        meta = h0.metadata or {}
        print(f"  top_hit_file={meta.get('file_path')}")

    section("4. SECOND QUERY (warm — should be sub-second)")
    t0 = time.monotonic()
    report2 = svc.query_collection(COLLECTION, QUERY, n_results=3)
    second_s = time.monotonic() - t0
    print(f"second_query_total_s={round(second_s, 3)}")
    print(f"  embed_s={round(report2.embedding_time_s, 3)} chroma_s={round(report2.query_time_s, 3)}")
    print(f"  hits={len(report2.hits)}")

    section("5. CONCURRENT QUERY PAIR (cancel-safety + serialization smoke)")
    results: list[tuple[str, float, object]] = []
    barrier = threading.Barrier(2)

    def _worker(name: str, q: str) -> None:
        barrier.wait()
        wt0 = time.monotonic()
        try:
            r = svc.query_collection(COLLECTION, q, n_results=3)  # default include
            first = r.hits[0] if r.hits else None
            info = f"hits={len(r.hits)} dist0={first.distance:.4f}" if first else f"hits=0"
            results.append((name, time.monotonic() - wt0, info))
        except Exception as exc:  # guardian: allow-broad-exception -- diagnostic probe must capture ALL failure modes (encode lock starvation, timeout, chroma error) to prove cancel-safety; surface raw type/message for debugging
            results.append((name, time.monotonic() - wt0, f"ERROR: {type(exc).__name__}: {exc}"))

    threads = [
        threading.Thread(target=_worker, args=("A", QUERY), daemon=True),
        threading.Thread(target=_worker, args=("B", "F25-int healing dispatch routing"), daemon=True),
    ]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=10)
    for name, elapsed, info in results:
        print(f"  worker {name}: elapsed_s={round(elapsed, 3)} {info}")

    section("6. SUMMARY")
    print(f"model_warm_after_prewarm={r.embedding_model_ready}")
    print(f"first_query_fast={first_s < 3.0}  (target <3s with prewarm)")
    print(f"second_query_fast={second_s < 1.0}  (target <1s warm)")
    print(f"concurrent_both_succeeded={len([r for r in results if 'ERROR' not in r[2]]) == 2}")


if __name__ == "__main__":
    main()
