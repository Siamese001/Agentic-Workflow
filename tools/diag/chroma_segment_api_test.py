"""Diagnostic: test SegmentAPI workaround for ChromaDB Rust hang on Windows."""

import sys
import time

try:
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

CHROMA_PATH = "data/cache/chromadb"

print(f"ChromaDB version: {chromadb.__version__}")
print(f"Path: {CHROMA_PATH}")

# ── Test 1: SegmentAPI client init ──
print("\n[1] Creating PersistentClient with SegmentAPI...")
t0 = time.perf_counter()
client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(
        anonymized_telemetry=False,
        chroma_api_impl="chromadb.api.segment.SegmentAPI",
    ),
)
print(f"    Client ready in {time.perf_counter() - t0:.2f}s")

# ── Test 2: list collections ──
print("\n[2] Listing collections...")
cols = client.list_collections()
print(f"    Found {len(cols)} collections:")
for c in cols:
    print(f"      - {c.name}")

# ── Test 3: ext_authority count ──
print("\n[3] Getting ext_authority collection...")
col = client.get_collection("ext_authority")
count = col.count()
meta = col.metadata
print(f"    Count: {count}")
print(f"    Metadata: {meta}")

# ── Test 4: query with query_texts (uses Chroma default EF) ──
print("\n[4] Querying ext_authority with query_texts (default EF)...")
t0 = time.perf_counter()
try:
    r = col.query(
        query_texts=["How do agentic AI systems implement governance and safety enforcement?"],
        n_results=3,
        include=["metadatas", "distances", "documents"],
    )
    elapsed = time.perf_counter() - t0
    n = len(r["ids"][0])
    print(f"    Returned {n} results in {elapsed:.2f}s")
    for i in range(n):
        d = r["distances"][0][i]
        m = r["metadatas"][0][i]
        doc_snippet = (r["documents"][0][i] or "")[:80]
        print(f"    [{i + 1}] dist={d:.4f}")
        for k in ["source_url", "source_collection", "authority_tier", "doc_family", "title"]:
            print(f"        {k}: {m.get(k, '<missing>')}")
        print(f"        doc: {doc_snippet}...")
except (RuntimeError, ValueError, KeyError, TypeError) as exc:  # chroma query errors
    print(f"    FAIL: {exc}", file=sys.stderr)

print("\nDONE")
