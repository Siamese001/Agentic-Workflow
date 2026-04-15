"""Diagnostic: test if Rust bindings hang on query (not just add) on Windows."""

import sys
import time
import signal
import threading

CHROMA_PATH = "data/cache/chromadb"
TIMEOUT_SEC = 15


def _watchdog():
    """Kill process if query hangs past TIMEOUT_SEC."""
    time.sleep(TIMEOUT_SEC)
    print(f"\n*** WATCHDOG: query did not return after {TIMEOUT_SEC}s — confirmed HANG ***", flush=True)
    import os

    os._exit(99)


try:
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

print(f"ChromaDB {chromadb.__version__} | Rust bindings (default)")
print(f"Path: {CHROMA_PATH}")

# Start watchdog
wd = threading.Thread(target=_watchdog, daemon=True)
wd.start()

# ── Client init ──
print("\n[1] Creating PersistentClient (default Rust)...")
t0 = time.perf_counter()
client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False),
)
print(f"    Client ready in {time.perf_counter() - t0:.2f}s")

# ── List collections ──
print("\n[2] Listing collections...")
t0 = time.perf_counter()
cols = client.list_collections()
print(f"    {len(cols)} collections in {time.perf_counter() - t0:.2f}s")

# ── Count ──
print("\n[3] ext_authority count...")
t0 = time.perf_counter()
col = client.get_collection("ext_authority")
count = col.count()
print(f"    Count: {count} in {time.perf_counter() - t0:.2f}s")

# ── Query ──
print(f"\n[4] Querying ext_authority (watchdog={TIMEOUT_SEC}s)...")
t0 = time.perf_counter()
r = col.query(
    query_texts=["governance and safety enforcement in agentic AI systems"],
    n_results=2,
    include=["metadatas", "distances"],
)
elapsed = time.perf_counter() - t0
n = len(r["ids"][0])
print(f"    Returned {n} results in {elapsed:.2f}s")
for i in range(n):
    d = r["distances"][0][i]
    m = r["metadatas"][0][i]
    print(f"    [{i + 1}] dist={d:.4f} title={m.get('title', '?')[:60]}")
    print(f"         source_collection={m.get('source_collection', '?')}")

print("\nSUCCESS — Rust bindings query works on this system")
