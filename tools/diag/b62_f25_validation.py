"""B6.2 F25-only targeted validation."""

from __future__ import annotations

import json
import logging
import os
import sys
import time

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

CHROMA_PATH = os.path.join("data", "cache", "chromadb")
COLLECTION = "ext_authority"
MODEL = BGE_M3_MODEL_ID
TOP_K = 5
B61_BASELINE_DIST = 0.5043

F25_QUERY = (
    "How do agentic systems implement confidence-scored tiered healing dispatch "
    "routing failures through local rules, model retry, and human escalation?"
)

P13_PATTERNS = ["libs/langgraph", "langgraph_core"]
P12_PATTERNS = ["temporalio/sdk-python", "temporal.io"]

print("=== B6.2 F25 Targeted Validation ===")
logging.info("C3 write receipt: tools/diag/b62_f25_validation.py write side effect recorded")
print(f"Model: {MODEL}  |  Collection: {COLLECTION}  |  TopK: {TOP_K}")

try:
    import torch as _t

    device = "cuda" if _t.cuda.is_available() else "cpu"
except ImportError:
    device = "cpu"

from sentence_transformers import SentenceTransformer

t0 = time.perf_counter()
emb = SentenceTransformer(MODEL, device=device)
print(f"Model loaded ({device}) in {time.perf_counter() - t0:.1f}s")

import chromadb

client = chromadb.PersistentClient(path=CHROMA_PATH)
col = client.get_collection(COLLECTION)
print(f"Collection: {col.count()} docs")

t0 = time.perf_counter()
vec = emb.encode(F25_QUERY, normalize_embeddings=True).tolist()
t_embed = time.perf_counter() - t0

t0 = time.perf_counter()
res = col.query(
    query_embeddings=[vec],
    n_results=TOP_K,
    include=["distances", "metadatas", "documents"],
)
t_query = time.perf_counter() - t0

distances = res["distances"][0]
metas = res["metadatas"][0]

print(f"\nF25 Query: {F25_QUERY[:100]}...")
print(f"Embed: {t_embed:.3f}s  Query: {t_query:.3f}s")
print()

p13_in_top5 = False
p12_in_top5 = False

for i, (d, m) in enumerate(zip(distances, metas)):
    url = m.get("source_url", "")
    cg = m.get("collapse_group", "")
    hp = m.get("heading_path", "")[:70]
    is_p13 = any(p in url for p in P13_PATTERNS) or any(p in cg for p in P13_PATTERNS)
    is_p12 = any(p in url for p in P12_PATTERNS)
    tag = " <-- P13 (B6.2)" if is_p13 else (" <-- P12 (Temporal)" if is_p12 else "")
    if is_p13:
        p13_in_top5 = True
    if is_p12:
        p12_in_top5 = True
    print(f"  Rank {i + 1}: dist={d:.4f}  cg={cg:<22}  heading={hp}{tag}")
    print(f"          url={url[:100]}")

dist_at_1 = distances[0]
n_rel = sum(1 for d in distances if d < 0.50)
delta = B61_BASELINE_DIST - dist_at_1

if dist_at_1 < 0.35:
    grade = "STRONG"
elif dist_at_1 < 0.45:
    grade = "ADEQUATE"
elif dist_at_1 < 0.55:
    grade = "ADEQUATE (marginal)" if n_rel >= 2 else "WEAK"
else:
    grade = "MISSING"

p13_str = "YES" if p13_in_top5 else "no"
p12_str = "YES" if p12_in_top5 else "no"
improved_str = "YES" if delta > 0.01 else "no"

print()
print("=== F25 Result Summary ===")
print(f"  dist@1    : {dist_at_1:.4f}  (B6.1 baseline: {B61_BASELINE_DIST:.4f})")
print(f"  delta     : {delta:+.4f}")
print(f"  n_rel<0.50: {n_rel}")
print(f"  P13 top-{TOP_K} : {p13_str}")
print(f"  P12 top-{TOP_K} : {p12_str}")
print(f"  Grade     : {grade}")
print(f"  Improved  : {improved_str}")

os.makedirs("artifacts", exist_ok=True)
top_hits = [
    {
        "rank": i + 1,
        "dist": round(d, 4),
        "source_url": m.get("source_url", ""),
        "heading_path": m.get("heading_path", ""),
        "collapse_group": m.get("collapse_group", ""),
    }
    for i, (d, m) in enumerate(zip(distances, metas))
]
out = {
    "run_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "wave": "B6.2",
    "collection": COLLECTION,
    "collection_count": col.count(),
    "embedding_model": MODEL,
    "query": F25_QUERY,
    "b61_baseline_dist": B61_BASELINE_DIST,
    "dist_at_1": round(dist_at_1, 4),
    "delta": round(delta, 4),
    "n_rel_lt050": n_rel,
    "p13_in_top5": p13_in_top5,
    "grade": grade,
    "improved": delta > 0.01,
    "top_hits": top_hits,
}
with open("artifacts/b62_f25_validation_raw.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print("\nSaved: artifacts/b62_f25_validation_raw.json")
