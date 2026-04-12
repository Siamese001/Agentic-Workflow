"""End-to-end cutover trace for Phase 2a P0 code/symbol retrieval."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "agentic_core" / "L4_state" / "utils"))

import chromadb
from agentic_core.L1_cognition.reasoning.query_router import QueryRouter
from agentic_core.embeddings.bge_runtime import bge_embed_query

STORE = str(REPO_ROOT / "data" / "cache" / "chromadb")
client = chromadb.PersistentClient(path=STORE)
live = [c.name for c in client.list_collections()]
router = QueryRouter()
all_pass = True


def trace_routing(label: str, query: str) -> list[str]:
    decision = router.route_query(query, live)
    hit = decision.primary_collections + decision.secondary_collections
    print(f"\n--- ROUTING: {label} ---")
    print(f"  query_type : {decision.query_type}")
    print(f"  primary    : {decision.primary_collections}")
    print(f"  secondary  : {decision.secondary_collections}")
    return hit


async def trace_retrieval(label: str, query: str, collections: list[str]) -> None:
    global all_pass
    print(f"\n--- RETRIEVAL: {label} ---")
    emb = bge_embed_query(query)
    print(f"  embedding_dim: {len(emb)}")
    if len(emb) != 1024:
        print(f"  [FAIL] Expected 1024, got {len(emb)}")
        all_pass = False
    else:
        print(f"  [OK] embedding_dim=1024 (BGE-M3)")

    for cname in collections:
        if cname not in live:
            print(f"  [SKIP] {cname!r} not in live store")
            continue
        try:
            col = client.get_collection(cname)
            results = col.query(
                query_embeddings=[emb],
                n_results=3,
                include=["documents", "metadatas", "distances"],
            )
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]
            print(f"  [{cname}] -> {len(docs)} results")
            for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
                name_val = meta.get("name") or meta.get("symbol_name") or ""
                fp = str(meta.get("file_path", ""))[:55]
                dig = meta.get("canonical_digest", "MISSING")
                preview = (doc or "")[:90].strip().replace("\n", " ")
                print(f"    [{i}] dist={dist:.4f} name={name_val!r} file={fp!r}")
                print(f"         digest={dig!r}  preview={preview!r}")
            if not docs:
                print(f"  [FAIL] {cname}: no results")
                all_pass = False
        except (chromadb.errors.InvalidCollectionException, ValueError, RuntimeError) as e:
            print(f"  [ERROR] {cname}: {e}")
            all_pass = False


async def main() -> None:
    global all_pass

    q_code = "how does the query router select collections for code questions"
    routing_code = trace_routing("CODE_KNOWLEDGE", q_code)
    legacy_code = [c for c in routing_code if c in ("repo_code_chunks", "repo_symbols")]

    if "code_chunks" in routing_code:
        print("  [OK] CODE_KNOWLEDGE -> code_chunks")
    else:
        print("  [FAIL] CODE_KNOWLEDGE does NOT route to code_chunks")
        all_pass = False

    if legacy_code:
        print(f"  [FAIL] Legacy still in routing: {legacy_code}")
        all_pass = False
    else:
        print("  [OK] No legacy repo_code_chunks/repo_symbols in CODE_KNOWLEDGE routing")

    await trace_retrieval("CODE_KNOWLEDGE", q_code, ["code_chunks"])

    q_sym = "QueryRouter route_query collection_mappings class structure"
    routing_sym = trace_routing("STRUCTURAL_ANALYSIS", q_sym)
    legacy_sym = [c for c in routing_sym if c in ("repo_symbols", "repo_code_chunks")]

    if "symbols" in routing_sym:
        print("  [OK] STRUCTURAL_ANALYSIS -> symbols")
    else:
        print("  [FAIL] STRUCTURAL_ANALYSIS does NOT route to symbols")
        all_pass = False

    if legacy_sym:
        print(f"  [FAIL] Legacy still in routing: {legacy_sym}")
        all_pass = False
    else:
        print("  [OK] No legacy repo_symbols in STRUCTURAL_ANALYSIS routing")

    await trace_retrieval("STRUCTURAL_ANALYSIS", q_sym, ["symbols"])

    print()
    print("=== CUTOVER VERDICT:", "PASS" if all_pass else "FAIL", "===")
    sys.exit(0 if all_pass else 1)


asyncio.run(main())
