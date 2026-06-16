"""B6 targeted validation — 8 blocking families.

Queries ext_authority with the proof queries for F06/F08/F09/F12/F13/F14/F17/F25.
Compares dist@1 and source provenance against B5R2 direct-proof baselines.
Saves results to artifacts/b6_validation_raw.json.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import json
import sys
import time
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "ext_authority"
EMBEDDING_MODEL = BGE_M3_MODEL_ID
TOP_K = 5

# B5R2 direct-proof dist@1 baselines (from artifacts/b5r_proof_raw.json)
BASELINES: dict[str, float] = {
    "F06": 0.4585,
    "F08": 0.4745,
    "F09": 0.5032,
    "F12": 0.5829,
    "F13": 0.5121,
    "F14": 0.4285,
    "F17": 0.4572,
    "F25": 0.5043,
}

# B6 new source domains to detect in top-k
B6_DOMAINS: set[str] = {
    "anthropics/anthropic-cookbook/main/misc/prompt_caching",
    "zilliztech/GPTCache",
    "deepset-ai/haystack",
    "UKPLab/sentence-transformers",
    "run-llama/llama_index",
    "openai/openai-cookbook/main/articles/techniques_to_improve_reliability",
    "openai/swarm",
}

TARGET_QUERIES: list[dict] = [
    {
        "family": "F06",
        "label": "L1 Abstain Planning",
        "query": "When should an AI agent abstain, clarify ambiguity, or simplify a plan rather than proceed with uncertain execution?",
        "b5r_grade": "WEAK",
        "baseline_dist": BASELINES["F06"],
    },
    {
        "family": "F08",
        "label": "R1A Exact Cache Route",
        "query": "How do AI systems implement deterministic response caching with policy-key short-circuit routing to avoid redundant LLM inference?",
        "b5r_grade": "MISSING",
        "baseline_dist": BASELINES["F08"],
    },
    {
        "family": "F09",
        "label": "R1B Semantic Cache Route",
        "query": "How do vector similarity-based semantic caches retrieve cached LLM responses for semantically equivalent queries without re-running inference?",
        "b5r_grade": "MISSING",
        "baseline_dist": BASELINES["F09"],
    },
    {
        "family": "F12",
        "label": "C0 Evidence Fetch (Hybrid)",
        "query": "How does hybrid dense and sparse retrieval combine BM25 lexical search with vector embeddings for evidence fetching with parent-child chunk expansion?",
        "b5r_grade": "MISSING",
        "baseline_dist": BASELINES["F12"],
    },
    {
        "family": "F13",
        "label": "C0 Evidence Shaping (Rerank)",
        "query": "How do cross-encoder reranking models reorder and prune retrieved evidence chunks to improve relevance before context assembly?",
        "b5r_grade": "MISSING",
        "baseline_dist": BASELINES["F13"],
    },
    {
        "family": "F14",
        "label": "C0 Evidence Contract",
        "query": "How do AI retrieval systems determine when retrieved evidence is insufficient and signal that the agent should refine its query or abstain?",
        "b5r_grade": "WEAK",
        "baseline_dist": BASELINES["F14"],
    },
    {
        "family": "F17",
        "label": "R5 Fallback/Abstain Route",
        "query": "How do AI agent frameworks implement graceful fallback routing and explicit abstain signals when no safe action is available?",
        "b5r_grade": "WEAK",
        "baseline_dist": BASELINES["F17"],
    },
    {
        "family": "F25",
        "label": "Healing/Escalation Tiers",
        "query": "How do agentic systems implement confidence-scored tiered healing dispatch routing failures through local rules, model retry, and human escalation?",
        "b5r_grade": "MISSING",
        "baseline_dist": BASELINES["F25"],
    },
]


def _domain_hit(source_url: str) -> str | None:
    for dom in B6_DOMAINS:
        if dom in source_url:
            return dom
    return None


def main() -> None:
    sys.path.insert(0, str(REPO_ROOT))

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    try:
        import torch as _torch

        device = "cuda" if _torch.cuda.is_available() else "cpu"
    except ImportError:
        device = "cpu"

    print(f"Loading {EMBEDDING_MODEL} on {device} ...")
    model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    model.max_seq_length = 512
    print("Model loaded.")

    print(f"Connecting to {CHROMA_PATH} ...")
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    col = client.get_collection(COLLECTION_NAME)
    print(f"Collection count: {col.count()}")

    results: list[dict] = []
    THRESHOLD_RELEVANT = 0.50
    THRESHOLD_STRONG = 0.35

    for tq in tqdm(TARGET_QUERIES, desc="B6 validation queries", unit="query"):
        fid = tq["family"]
        print(f"\n--- {fid}: {tq['label']} ---")
        t0 = time.time()
        emb = model.encode([tq["query"]], normalize_embeddings=True).tolist()
        raw = col.query(
            query_embeddings=emb,
            n_results=TOP_K,
            include=["metadatas", "distances", "documents"],
        )
        elapsed = time.time() - t0

        distances = raw["distances"][0]
        metas = raw["metadatas"][0]
        docs = raw["documents"][0]

        dist_at_1 = distances[0] if distances else 1.0
        n_relevant = sum(1 for d in distances if d < THRESHOLD_RELEVANT)
        n_strong = sum(1 for d in distances if d < THRESHOLD_STRONG)

        # Detect B6 source hits
        b6_hits: list[dict] = []
        for i, (d, m) in enumerate(zip(distances, metas)):
            src = m.get("source_url", "")
            dom = _domain_hit(src)
            if dom:
                b6_hits.append(
                    {
                        "rank": i + 1,
                        "dist": round(d, 4),
                        "domain": dom,
                        "heading": m.get("heading_path", "")[:80],
                    }
                )

        # Improvement vs baseline
        baseline = tq["baseline_dist"]
        improved = dist_at_1 < baseline - 0.02  # meaningful improvement if dist@1 drops by ≥0.02
        delta = round(baseline - dist_at_1, 4)

        # Grade
        if dist_at_1 < THRESHOLD_STRONG and n_relevant >= 4:
            live_grade = "STRONG"
        elif dist_at_1 < THRESHOLD_RELEVANT and n_relevant >= 3:
            live_grade = "ADEQUATE"
        elif dist_at_1 < THRESHOLD_RELEVANT:
            live_grade = "ADEQUATE (marginal)"
        else:
            live_grade = "MISSING"

        top_hits = []
        for i in range(min(TOP_K, len(distances))):
            src = metas[i].get("source_url", "")
            top_hits.append(
                {
                    "rank": i + 1,
                    "dist": round(distances[i], 4),
                    "source_url": src[:120],
                    "heading_path": metas[i].get("heading_path", "")[:80],
                    "b6_hit": _domain_hit(src) is not None,
                }
            )

        rec = {
            "family": fid,
            "label": tq["label"],
            "b5r_grade": tq["b5r_grade"],
            "live_grade_b6": live_grade,
            "dist_at_1": round(dist_at_1, 4),
            "baseline_dist": baseline,
            "delta": delta,
            "improved": improved,
            "n_relevant_lt050": n_relevant,
            "n_strong_lt035": n_strong,
            "b6_source_in_top5": len(b6_hits) > 0,
            "b6_hits": b6_hits,
            "top_hits": top_hits,
            "elapsed_s": round(elapsed, 3),
        }
        results.append(rec)

        status = "IMPROVED" if improved else ("SAME" if delta >= -0.005 else "WORSE")
        b6_flag = f"  B6-SOURCE-IN-TOP5: {b6_hits[0]['domain']}" if b6_hits else ""
        print(f"  dist@1={dist_at_1:.4f}  baseline={baseline:.4f}  delta={delta:+.4f}  {status}")
        print(f"  live_grade={live_grade}  rel={n_relevant}/5  strong={n_strong}/5  {b6_flag}")
        print(f"  top1: {top_hits[0]['source_url'][:80]} | {top_hits[0]['heading_path']}")

    # Contamination check
    cont_other = 0
    for rec in results:
        for hit in rec["top_hits"]:
            if (
                "ext_authority" not in hit["source_url"]
                and "github" not in hit["source_url"]
                and hit["source_url"]
            ):
                cont_other += 1

    out = {
        "collection": COLLECTION_NAME,
        "collection_count_post_b6": col.count(),
        "contamination_other": cont_other,
        "families": results,
    }

    out_path = REPO_ROOT / "artifacts" / "b6_validation_raw.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nSaved: {out_path}")

    # Summary table
    print("\n=== B6 TARGETED VALIDATION SUMMARY ===")
    print(
        f"{'Family':<6} {'B5R Grade':<12} {'B6 Grade':<22} {'dist@1':>7} {'baseline':>9} {'delta':>7} {'B6 hit':>7} {'Status'}"
    )
    print("-" * 95)
    for rec in results:
        b6_hit = "YES" if rec["b6_source_in_top5"] else "no"
        status = "IMPROVED" if rec["improved"] else "no change"
        print(
            f"{rec['family']:<6} {rec['b5r_grade']:<12} {rec['live_grade_b6']:<22} "
            f"{rec['dist_at_1']:>7.4f} {rec['baseline_dist']:>9.4f} {rec['delta']:>+7.4f} "
            f"{b6_hit:>7} {status}"
        )
    print("-" * 95)
    n_improved = sum(1 for r in results if r["improved"])
    n_b6_hit = sum(1 for r in results if r["b6_source_in_top5"])
    print(f"Improved: {n_improved}/8   B6 source in top-5: {n_b6_hit}/8")


if __name__ == "__main__":
    main()
