"""Phase 2a P0 smoke tests — code_chunks and symbols collections."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import chromadb
from agentic_core.embeddings.bge_runtime import bge_embed_query

STORE = REPO_ROOT / "data" / "cache" / "chromadb"
client = chromadb.PersistentClient(path=str(STORE))

all_pass = True


def smoke(collection_name: str, query: str, n: int = 3) -> bool:
    print(f"\n=== SMOKE: {collection_name!r} | query: {query!r} ===")
    emb = bge_embed_query(query)
    col = client.get_collection(collection_name)
    results = col.query(query_embeddings=[emb], n_results=n, include=["documents", "metadatas", "distances"])
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    if not docs:
        print("  [FAIL] No results returned")
        return False
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
        dist_str = f"{dist:.4f}"
        file_str = str(meta.get("file_path", ""))[:60]
        name_str = str(meta.get("name", meta.get("symbol_name", "")))[:50]
        preview = (doc or "")[:100].strip().replace("\n", " ")
        print(f"  [{i}] dist={dist_str}  file={file_str!r}  name={name_str!r}")
        print(f"       preview: {preview!r}")
    print(f"  [OK] {len(docs)} results, non-empty")
    return True


all_pass = (
    smoke("code_chunks", "how does the query router select collections for code questions") and all_pass
)
all_pass = smoke("symbols", "QueryRouter route_query collection_mappings") and all_pass

print("\n=== SMOKE RESULT:", "PASS" if all_pass else "FAIL", "===")
sys.exit(0 if all_pass else 1)
