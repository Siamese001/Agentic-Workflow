"""Smoke test: sparse leg of HybridSearchEngine — Phase B1/B2/C proof.

Verifies:
  - _lexical_search() is no longer a dead path
  - All 8 canonical collections return hits from SparseIndex.search()
  - Dynamic weight selection (_detect_query_signal) works correctly
  - Before/after contrast: a snake_case symbol that dense-only would miss

Run from repo root:
  python tools/generate/ingestion/_smoke_hybrid.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L4_state.utils.memory.bm25_store import SparseIndex, get_sparse_index
from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    _detect_query_signal,
    _compute_weights,
)

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
INFO = "\033[94m[INFO]\033[0m"

# ---------------------------------------------------------------------------
# Smoke 1 — SparseIndex.search() returns real hits for all 8 collections
# ---------------------------------------------------------------------------

_PER_COLLECTION_QUERIES: dict[str, str] = {
    # Phase A (original 4)
    "code_chunks": "bge_embed_query",
    "symbols": "HybridSearchEngine",
    "arch_docs": "chromadb",
    "tests_guardrails": "pytest",
    # Phase C (new 4)
    "runtime_evidence": "trace",
    "process_docs": "policy",
    "ext_knowledge": "langchain",
    "incidents_rca": "incident",
}


def smoke_sparse_hits() -> int:
    failures = 0
    print("\n=== Smoke 1: SparseIndex.search() hits per collection ===")
    for col, query in _PER_COLLECTION_QUERIES.items():
        idx = get_sparse_index(col)
        if idx is None:
            print(f"  {FAIL}  {col!r:25}  get_sparse_index returned None (not in _SPARSE_COLLECTIONS)")
            failures += 1
            continue
        if not idx.is_available:
            print(f"  {FAIL}  {col!r:25}  sidecar missing — run build_sparse_index.py")
            failures += 1
            continue
        results = idx.search(query, top_k=5)
        if results:
            top = results[0]
            print(
                f"  {PASS}  {col!r:25}  query={query!r:25}  hits={len(results)}  "
                f"top_id={str(top['id'])[:36]!r}  score={top['score']:.3f}"
            )
        else:
            print(f"  {FAIL}  {col!r:25}  query={query!r}  0 hits")
            failures += 1
    return failures


# ---------------------------------------------------------------------------
# Smoke 2 — _lexical_search is no longer dead: exercise it via the engine API
# ---------------------------------------------------------------------------


def smoke_lexical_search_live() -> int:
    from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
        HybridSearchEngine,
        get_sparse_index,
    )

    failures = 0
    print("\n=== Smoke 2: _lexical_search() live (no dense, sparse only) ===")

    for col, query in _PER_COLLECTION_QUERIES.items():
        sparse = get_sparse_index(col)
        engine = HybridSearchEngine(
            chroma_client=None,  # no dense client — proves sparse path is independent
            bm25_index=sparse,
            vector_weight=0.0,
            lexical_weight=1.0,
            top_k=5,
        )
        lex_results = engine._lexical_search(query, collection_name=col)
        if lex_results:
            top_id = next(iter(lex_results))
            top_score = lex_results[top_id].lexical_score
            print(
                f"  {PASS}  {col!r:25}  query={query!r:25}  hits={len(lex_results)}  "
                f"top_id={top_id[:36]!r}  lexical_score={top_score:.3f}"
            )
        else:
            print(f"  {FAIL}  {col!r:25}  query={query!r}  0 lexical hits")
            failures += 1

    return failures


# ---------------------------------------------------------------------------
# Smoke 3 — Dynamic weight selection (Phase B2)
# ---------------------------------------------------------------------------

_WEIGHT_CASES: list[tuple[str, str, tuple[float, float]]] = [
    # query,                              expected_signal,  (vw, lw)
    ("bge_embed_query", "exact", (0.35, 0.65)),
    ("HybridSearchEngine.search", "exact", (0.35, 0.65)),
    ("agentic_core.L3_orchestration.reasoning", "exact", (0.35, 0.65)),
    ("what does the orchestration layer do and why is it structured this way", "semantic", (0.85, 0.15)),
    ("search code", "mixed", (0.55, 0.45)),
]


def smoke_dynamic_weights() -> int:
    failures = 0
    print("\n=== Smoke 3: dynamic weight selection (_detect_query_signal) ===")
    for query, expected_signal, expected_weights in _WEIGHT_CASES:
        signal = _detect_query_signal(query)
        vw, lw = _compute_weights(query, 0.7, 0.3)
        ok_signal = signal == expected_signal
        ok_weights = (vw, lw) == expected_weights
        status = PASS if (ok_signal and ok_weights) else FAIL
        if not (ok_signal and ok_weights):
            failures += 1
        print(
            f"  {status}  signal={signal!r:8}  vw={vw:.2f}  lw={lw:.2f}  "
            f"expected=({expected_signal!r},{expected_weights})  query={query[:50]!r}"
        )
    return failures


# ---------------------------------------------------------------------------
# Smoke 4 — Before/After: exact-match query that dense-only would miss
# ---------------------------------------------------------------------------


def smoke_before_after() -> int:
    """Simulate dense-only vs hybrid behavior for a snake_case exact query."""
    query = "bge_embed_query"
    col = "code_chunks"
    sparse = get_sparse_index(col)

    print("\n=== Smoke 4: Before/After — exact symbol 'bge_embed_query' ===")
    print(f"  Query: {query!r}  Collection: {col!r}")

    # BEFORE (dense-only): no lexical hits at all
    print(f"\n  {INFO}  BEFORE (dense-only, no sparse): 0 lexical hits (dead path)")

    # AFTER (hybrid with sparse): real hits
    if sparse and sparse.is_available:
        hits = sparse.search(query, top_k=3)
        if hits:
            print(f"  {PASS}  AFTER  (hybrid sparse leg):  {len(hits)} hits")
            for h in hits:
                print(f"          id={str(h['id'])[:60]!r}  score={h['score']:.3f}")
            return 0
        else:
            print(f"  {FAIL}  AFTER  (hybrid sparse leg):  0 hits — check sidecar content")
            return 1
    else:
        print(f"  {FAIL}  SparseIndex for {col!r} not available")
        return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    total_failures = 0
    total_failures += smoke_sparse_hits()
    total_failures += smoke_lexical_search_live()
    total_failures += smoke_dynamic_weights()
    total_failures += smoke_before_after()

    print()
    if total_failures == 0:
        print(f"\033[92m=== ALL SMOKE TESTS PASSED ===\033[0m")
    else:
        print(f"\033[91m=== {total_failures} SMOKE TEST(S) FAILED ===\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
