"""B6.1 targeted validation — F12 / F14 / F17 / F25 only.

Compares dist@1 and source provenance against B6 baselines (not B5R2).
Saves results to artifacts/b61_validation_raw.json.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time

from tqdm import tqdm

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

CHROMA_PATH = os.path.join("data", "cache", "chromadb")
COLLECTION = "ext_authority"
EMBEDDING_MODEL = BGE_M3_MODEL_ID
TOP_K = 5
OUTPUT = os.path.join("artifacts", "b61_validation_raw.json")

# ── B6.1 target queries ───────────────────────────────────────────────────────
TARGET_QUERIES = [
    {
        "family": "F12",
        "name": "C0 evidence fetch: dense/sparse/cache/metadata/parent-child",
        "b5r_grade": "WEAK",
        "b6_baseline_dist": 0.4943,
        "query": (
            "How does hybrid dense and sparse retrieval combine BM25 lexical search "
            "with vector embeddings for evidence fetching with parent-child chunk expansion?"
        ),
    },
    {
        "family": "F14",
        "name": "C0 evidence contract: verified chunks/cited spans/refine-abstain",
        "b5r_grade": "WEAK",
        "b6_baseline_dist": 0.4230,
        "query": (
            "How do AI retrieval systems determine when retrieved evidence is insufficient "
            "and signal that the agent should refine its query or abstain?"
        ),
    },
    {
        "family": "F17",
        "name": "R5 fallback/clarify/abstain route",
        "b5r_grade": "WEAK",
        "b6_baseline_dist": 0.4547,
        "query": (
            "How do AI agent frameworks implement graceful fallback routing and explicit "
            "abstain signals when no safe action is available?"
        ),
    },
    {
        "family": "F25",
        "name": "Healing/remediation/escalation tiers",
        "b5r_grade": "WEAK",
        "b6_baseline_dist": 0.5043,
        "query": (
            "How do agentic systems implement confidence-scored tiered healing dispatch "
            "routing failures through local rules, model retry, and human escalation?"
        ),
    },
]

# ── B6.1 domain fingerprints ──────────────────────────────────────────────────
B61_DOMAINS = {
    "weaviate": ["weaviate/weaviate", "weaviate.io"],
    "ragas": ["explodinggradients/ragas", "explodinggradients"],
    "guardrails_ai": ["guardrails-ai/guardrails", "guardrailsai"],
    "temporal": ["temporalio/sdk-python", "temporal.io"],
}

B6_DOMAINS = {
    "anthropic_caching": ["anthropic-cookbook/main/misc/prompt_caching"],
    "gptcache": ["GPTCache"],
    "haystack": ["deepset-ai/haystack"],
    "sentence_transformers": ["UKPLab/sentence-transformers"],
    "llamaindex": ["run-llama/llama_index"],
    "openai_cookbook": ["openai/openai-cookbook"],
    "openai_swarm": ["openai/swarm"],
}

ALL_DOMAINS = {**B61_DOMAINS, **B6_DOMAINS}


def _domain_hit(url: str) -> str | None:
    for label, patterns in ALL_DOMAINS.items():
        if any(p.lower() in url.lower() for p in patterns):
            return label
    return None


def _live_grade(dist: float, n_rel: int) -> str:
    if dist < 0.35:
        return "STRONG"
    if dist < 0.45:
        return "ADEQUATE"
    if dist < 0.55:
        if n_rel >= 2:
            return "ADEQUATE (marginal)"
        return "WEAK"
    return "MISSING"


# ── Setup ─────────────────────────────────────────────────────────────────────
print("=" * 65)
logging.info("C3 write receipt: tools/diag/b61_targeted_validation.py write side effect recorded")
print("B6.1 Targeted Validation — F12 / F14 / F17 / F25")
print("=" * 65)

print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
try:
    import torch as _torch

    _device = "cuda" if _torch.cuda.is_available() else "cpu"
except ImportError:
    _device = "cpu"
print(f"Device: {_device}")

try:
    from sentence_transformers import SentenceTransformer

    t0 = time.perf_counter()
    embedder = SentenceTransformer(EMBEDDING_MODEL, device=_device)
    print(f"Model loaded in {time.perf_counter() - t0:.1f}s")
except ImportError as exc:
    print(f"FATAL: cannot import SentenceTransformer: {exc}")
    sys.exit(1)

print(f"\nOpening ChromaDB: {CHROMA_PATH}")
try:
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    col = client.get_collection(COLLECTION)
    print(f"Collection '{COLLECTION}' — {col.count()} docs")
except (
    OSError,
    ValueError,
    RuntimeError,
) as exc:  # guardian: allow-broad-exception -- ChromaDB raises OSError/ValueError/RuntimeError at startup; catching all three avoids an uncaught propagation chain
    print(f"FATAL: ChromaDB open failed: {exc}")
    sys.exit(1)

# ── Run queries ───────────────────────────────────────────────────────────────
results: list[dict] = []

for tq in tqdm(TARGET_QUERIES, desc="B6.1 validation queries", unit="query"):
    fid = tq["family"]
    query_text = tq["query"]
    print(f"\n{'─' * 60}")
    print(f"[{fid}] {tq['name']}")
    print(f"  Query: {query_text[:90]}...")

    t0 = time.perf_counter()
    embedding = embedder.encode(query_text, normalize_embeddings=True).tolist()
    t_embed = time.perf_counter() - t0

    t0 = time.perf_counter()
    res = col.query(
        query_embeddings=[embedding],
        n_results=TOP_K,
        include=["distances", "metadatas", "documents"],
    )
    t_query = time.perf_counter() - t0

    distances = res["distances"][0]
    metas = res["metadatas"][0]
    docs = res["documents"][0]
    ids = res["ids"][0]

    b61_hits: list[dict] = []
    top_hits: list[dict] = []

    for i in range(min(TOP_K, len(distances))):
        d = distances[i]
        m = metas[i]
        src = m.get("source_url", "")
        dom = _domain_hit(src)
        is_b61 = dom in B61_DOMAINS if dom else False
        top_hits.append(
            {
                "rank": i + 1,
                "dist": round(d, 4),
                "source_url": src[:120],
                "heading_path": m.get("heading_path", "")[:80],
                "source_collection": m.get("source_collection", ""),
                "authority_tier": m.get("authority_tier", ""),
                "b61_hit": is_b61,
                "domain_label": dom,
            }
        )
        if is_b61:
            b61_hits.append(
                {
                    "rank": i + 1,
                    "dist": round(d, 4),
                    "domain": dom,
                    "heading": m.get("heading_path", "")[:80],
                }
            )

    dist_at_1 = distances[0] if distances else 9.0
    n_relevant = sum(1 for d in distances if d < 0.50)
    n_strong = sum(1 for d in distances if d < 0.40)
    b61_source_in_top5 = len(b61_hits) > 0

    baseline = tq["b6_baseline_dist"]
    delta = baseline - dist_at_1
    improved = delta > 0.01
    live_grade = _live_grade(dist_at_1, n_relevant)

    print(f"  dist@1={dist_at_1:.4f}  baseline={baseline:.4f}  delta={delta:+.4f}")
    print(f"  n_rel<0.50={n_relevant}  n_strong<0.40={n_strong}")
    print(f"  B6.1 src in top-{TOP_K}: {'YES' if b61_source_in_top5 else 'no'}")
    if b61_hits:
        for h in b61_hits:
            print(f"    rank={h['rank']}  domain={h['domain']}  heading={h['heading'][:60]}")
    print(f"  Live grade: {live_grade}")

    rec = {
        "family": fid,
        "name": tq["name"],
        "b5r_grade": tq["b5r_grade"],
        "b6_baseline_dist": baseline,
        "dist_at_1": round(dist_at_1, 4),
        "delta": round(delta, 4),
        "improved": improved,
        "n_relevant_lt050": n_relevant,
        "n_strong_lt040": n_strong,
        "live_grade_b61": live_grade,
        "b61_source_in_top5": b61_source_in_top5,
        "b61_hits": b61_hits,
        "embed_s": round(t_embed, 3),
        "query_s": round(t_query, 3),
        "top_hits": top_hits,
    }
    results.append(rec)

# ── Contamination check ───────────────────────────────────────────────────────
cont_other = sum(
    1
    for rec in results
    for hit in rec["top_hits"]
    if hit["source_collection"] not in ("ext_authority", "") and hit["source_collection"]
)

# ── Summary table ─────────────────────────────────────────────────────────────
print("\n" + "=" * 95)
print("B6.1 TARGETED VALIDATION SUMMARY")
print("=" * 95)
print(f"{'Family':<6} {'Grade':<22} {'dist@1':>7} {'B6 base':>8} {'delta':>7} {'B6.1 hit':>8} {'Status'}")
print("-" * 95)
for rec in results:
    b61_hit = "YES" if rec["b61_source_in_top5"] else "no"
    status = "IMPROVED" if rec["improved"] else "no-change"
    print(
        f"{rec['family']:<6} {rec['live_grade_b61']:<22} {rec['dist_at_1']:>7.4f}"
        f" {rec['b6_baseline_dist']:>8.4f} {rec['delta']:>+7.4f}"
        f" {b61_hit:>8} {status}"
    )
print("-" * 95)
n_improved = sum(1 for r in results if r["improved"])
n_b61_hit = sum(1 for r in results if r["b61_source_in_top5"])
print(f"Improved vs B6: {n_improved}/{len(results)}  B6.1 source in top-{TOP_K}: {n_b61_hit}/{len(results)}")
print(f"Contamination (non-ext_authority in results): {cont_other}")

# ── Save raw JSON ─────────────────────────────────────────────────────────────
os.makedirs("artifacts", exist_ok=True)
out = {
    "run_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "collection": COLLECTION,
    "embedding_model": EMBEDDING_MODEL,
    "chroma_path": CHROMA_PATH,
    "n_families_targeted": len(results),
    "n_improved": n_improved,
    "n_b61_hit": n_b61_hit,
    "contamination_other": cont_other,
    "results": results,
}
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved: {OUTPUT}")
