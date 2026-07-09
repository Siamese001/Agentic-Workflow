"""
B5R Direct Proof Runner
=======================
Queries ext_authority directly for all 31 B5R families.
Produces: artifacts/b5r_proof_raw.json

Rules:
- Sequential only (no threading, no batching)
- query_embeddings= only (never query_texts=)
- source_collection provenance captured for every chunk
- No code changes, no source additions
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

CHROMA_PATH = str(REPO_ROOT / "data" / "cache" / "chromadb")
MODEL_NAME = BGE_M3_MODEL_ID
COLLECTION = "ext_authority"
TOP_K = 5
OUT_PATH = REPO_ROOT / "artifacts" / "b5r_proof_raw.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.info("C3 write receipt: tools/diag/b5r_direct_proof_runner.py write side effect recorded")

# ─── Family-to-Query Map ─────────────────────────────────────────────────────
# TS-xx = reused from existing audit basis; NEW = net-new query for B5R
FAMILIES: list[dict] = [
    {
        "id": "F01",
        "name": "Request-source modes / bounded ingress",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-11",
        "query_status": "REUSED-TS-11",
        "query": "How do agentic AI systems handle multiple request sources and enforce bounded ingress from queues, APIs, and events?",
    },
    {
        "id": "F02",
        "name": "Identity/quota/schema/normalization/ingress contract",
        "grade_claim": "WEAK",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-16, TS-20",
        "query_status": "REUSED-TS-20",
        "query": "How do AI agent systems enforce identity verification, quota limits, and schema validation at the system ingress boundary?",
    },
    {
        "id": "F03",
        "name": "L1 intent framing and work classification",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-01, TS-11",
        "query_status": "REUSED-TS-01",
        "query": "How do AI agent frameworks classify incoming requests and frame user intent into structured work units?",
    },
    {
        "id": "F04",
        "name": "L1 priors/policy/example loading",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-01, TS-11",
        "query_status": "REUSED-TS-11",
        "query": "How do agentic systems load prior context, policy constraints, and few-shot examples before generating a plan?",
    },
    {
        "id": "F05",
        "name": "L1 decomposition/dependency/proposed-route drafting",
        "grade_claim": "STRONG",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-12, TS-18",
        "query_status": "REUSED-TS-18",
        "query": "How do AI agents decompose complex tasks into subtasks with dependency ordering and propose execution routes?",
    },
    {
        "id": "F06",
        "name": "L1 validation/simplify/clarify/abstain planning",
        "grade_claim": "WEAK",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "TS-09 WEAK, TS-17",
        "query_status": "REUSED-TS-09",
        "query": "When should an AI agent abstain, clarify ambiguity, or simplify a plan rather than proceed with uncertain execution?",
    },
    {
        "id": "F07",
        "name": "L0 route authority/prefilters/freshness/ACL",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-10, TS-11",
        "query_status": "REUSED-TS-10",
        "query": "How does an agentic system implement route authority, access control lists, and freshness prefilters at the L0 dispatch layer?",
    },
    {
        "id": "F08",
        "name": "R1A exact cache route",
        "grade_claim": "MISSING",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "None",
        "query_status": "NEW",
        "query": "How do AI systems implement deterministic response caching with policy-key short-circuit routing to avoid redundant LLM inference?",
    },
    {
        "id": "F09",
        "name": "R1B semantic cache route",
        "grade_claim": "MISSING",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "None",
        "query_status": "NEW",
        "query": "How do vector similarity-based semantic caches retrieve cached LLM responses for semantically equivalent queries without re-running inference?",
    },
    {
        "id": "F10",
        "name": "R3 grounded-context decision",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-02, TS-10",
        "query_status": "REUSED-TS-02",
        "query": "How do AI agents decide when retrieved external context is required to ground a factual or policy-driven response?",
    },
    {
        "id": "F11",
        "name": "C0 retrieval planning/scoping",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-01, TS-02",
        "query_status": "REUSED-TS-01",
        "query": "How do agentic retrieval systems plan and scope collection selection, freshness constraints, and query mode before fetching evidence?",
    },
    {
        "id": "F12",
        "name": "C0 evidence fetch: dense/sparse/cache/metadata/parent-child",
        "grade_claim": "WEAK",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "TS-03 WEAK, TS-07 WEAK, TS-19 WEAK",
        "query_status": "REUSED-TS-03",
        "query": "How does hybrid dense and sparse retrieval combine BM25 lexical search with vector embeddings for evidence fetching with parent-child chunk expansion?",
    },
    {
        "id": "F13",
        "name": "C0 evidence shaping: dedup/rerank/prune/conflicts",
        "grade_claim": "WEAK",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "TS-04 WEAK, TS-08 ADEQUATE",
        "query_status": "REUSED-TS-04",
        "query": "How do cross-encoder reranking models reorder and prune retrieved evidence chunks to improve relevance before context assembly?",
    },
    {
        "id": "F14",
        "name": "C0 evidence contract: verified chunks/cited spans/refine-abstain",
        "grade_claim": "WEAK",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "TS-05 ADEQUATE, TS-09 WEAK",
        "query_status": "REUSED-TS-09",
        "query": "How do AI retrieval systems determine when retrieved evidence is insufficient and signal that the agent should refine its query or abstain?",
    },
    {
        "id": "F15",
        "name": "Prompt assembly: load/slot/budget/contract",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-01, TS-08",
        "query_status": "REUSED-TS-08",
        "query": "How do agentic systems assemble prompts by loading templates, slotting retrieved context, and enforcing token budget constraints?",
    },
    {
        "id": "F16",
        "name": "R4 external action route",
        "grade_claim": "STRONG",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-13, TS-14",
        "query_status": "REUSED-TS-13",
        "query": "How do AI agents dispatch external tool calls, API actions, and compute tasks with payload validation and state mutation tracking?",
    },
    {
        "id": "F17",
        "name": "R5 fallback/clarify/abstain route",
        "grade_claim": "WEAK",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "TS-09 (0.510)",
        "query_status": "REUSED-TS-09",
        "query": "How do AI agent frameworks implement graceful fallback routing and explicit abstain signals when no safe action is available?",
    },
    {
        "id": "F18",
        "name": "Governance invocation and authority context",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-16, TS-11",
        "query_status": "REUSED-TS-16",
        "query": "How do agentic systems invoke governance checks and load authority context before executing high-risk or policy-sensitive operations?",
    },
    {
        "id": "F19",
        "name": "Structure/registry/classification/policy chokepoint",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-13 STRONG, TS-16",
        "query_status": "REUSED-TS-13",
        "query": "How do AI agent frameworks enforce policy chokepoints through registry validation and risk-tier classification of agent actions?",
    },
    {
        "id": "F20",
        "name": "Sovereign egress/compliance artifacts/capability token/sandbox",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-13 STRONG, TS-16",
        "query_status": "REUSED-TS-13",
        "query": "How do agentic systems enforce capability tokens, sandbox envelopes, and compliance artifact generation at the egress boundary?",
    },
    {
        "id": "F21",
        "name": "Replay envelope and freeze propagation",
        "grade_claim": "OUT OF SCOPE",
        "blocks_b6": False,
        "scope": "INTERNAL",
        "ts_ref": "None",
        "query_status": "NEW-INTERNAL-PROBE",
        "query": "How do deterministic replay systems implement freeze signal propagation across architectural layers with policy hash verification?",
    },
    {
        "id": "F22",
        "name": "Replay guard: time/entropy/identity/network/reads/writes",
        "grade_claim": "OUT OF SCOPE",
        "blocks_b6": False,
        "scope": "INTERNAL",
        "ts_ref": "None",
        "query_status": "NEW-INTERNAL-PROBE",
        "query": "How do deterministic replay guards intercept wall-clock time, seeded entropy sources, and network calls to ensure reproducible agent execution?",
    },
    {
        "id": "F23",
        "name": "Determinism digest and replay verification",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "Mixed",
        "ts_ref": "TS-05",
        "query_status": "REUSED-TS-05",
        "query": "How do AI systems generate and verify audit trail digests for agent decisions with provenance metadata and cited source attribution?",
    },
    {
        "id": "F24",
        "name": "L2 execution lifecycle E1-E5",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-12 STRONG, TS-15 STRONG",
        "query_status": "REUSED-TS-15",
        "query": "How do agentic execution frameworks manage the full tool dispatch lifecycle including validation, bounded execution, and output sealing?",
    },
    {
        "id": "F25",
        "name": "Healing/remediation/escalation tiers",
        "grade_claim": "WEAK",
        "blocks_b6": True,
        "scope": "ext_authority",
        "ts_ref": "TS-12 partial",
        "query_status": "NEW",
        "query": "How do agentic systems implement confidence-scored tiered healing dispatch routing failures through local rules, model retry, and human escalation?",
    },
    {
        "id": "F26",
        "name": "Current-run exit review and explicit dispositions",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-17, TS-16",
        "query_status": "REUSED-TS-17",
        "query": "How do AI agent frameworks evaluate outputs against quality rubrics and emit explicit ALLOW, DENY, ESCALATE, or COMMIT dispositions at run exit?",
    },
    {
        "id": "F27",
        "name": "HITL airlock and L5 re-clearance",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-11, TS-16",
        "query_status": "REUSED-TS-11",
        "query": "How do human-in-the-loop review workflows pause agent execution, collect human approval, and re-authorize the agent to continue?",
    },
    {
        "id": "F28",
        "name": "UWG/state sovereignty/write governance/read-surface refresh",
        "grade_claim": "WEAK",
        "blocks_b6": False,
        "scope": "Mixed",
        "ts_ref": "TS-16, TS-11 tangential",
        "query_status": "REUSED-TS-16",
        "query": "How do agentic systems enforce single-writer state sovereignty with RBAC blast-radius controls and serialized write governance gates?",
    },
    {
        "id": "F29",
        "name": "L6 observability/verify spine/control buses/evidence bundle",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-17, TS-05, tracing docs",
        "query_status": "REUSED-TS-17",
        "query": "How do AI agent frameworks implement observability with tracing spans, evaluation metrics like Recall@K and MRR, and structured evidence bundles?",
    },
    {
        "id": "F30",
        "name": "Shadow evaluation/RCA/promotion pipeline",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-17, TS-11",
        "query_status": "REUSED-TS-17",
        "query": "How do agentic learning systems run shadow evaluations, generate root cause analyses, and promote validated rules through a quality gate pipeline?",
    },
    {
        "id": "F31",
        "name": "Capability/tool/model/network/memory/write access-control plane",
        "grade_claim": "ADEQUATE",
        "blocks_b6": False,
        "scope": "ext_authority",
        "ts_ref": "TS-13 STRONG, TS-16",
        "query_status": "REUSED-TS-13",
        "query": "How do AI agent frameworks implement access control for tools, models, network calls, and memory writes through capability tokens and invocation records?",
    },
]

# ─── Step 1: Prove live ChromaDB path ───────────────────────────────────────
print(f"[PROOF] ChromaDB path: {CHROMA_PATH}", flush=True)
print(f"[PROOF] Collection: {COLLECTION}", flush=True)
print(f"[PROOF] Model: {MODEL_NAME}", flush=True)

import chromadb
from chromadb.config import Settings

t_client_start = time.perf_counter()
client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False),
)
t_client_end = time.perf_counter()
print(f"[PROOF] Client init: {t_client_end - t_client_start:.3f}s", flush=True)

col = client.get_collection(COLLECTION)
col_count = col.count()
col_meta = col.metadata or {}
print(f"[PROOF] ext_authority count: {col_count}", flush=True)
print(f"[PROOF] ext_authority metadata: {col_meta}", flush=True)

assert col_meta.get("embedding_model") == MODEL_NAME, (
    f"Collection model mismatch: {col_meta.get('embedding_model')} != {MODEL_NAME}"
)
assert col_meta.get("embedding_dim") == 1024, (
    f"Collection dim mismatch: {col_meta.get('embedding_dim')} != 1024"
)

# ─── Step 2: Load embedding model ───────────────────────────────────────────
print(f"\n[EMBED] Loading {MODEL_NAME}...", flush=True)
from sentence_transformers import SentenceTransformer

t_model_start = time.perf_counter()
model = SentenceTransformer(MODEL_NAME, local_files_only=True)
t_model_end = time.perf_counter()
assert model.get_sentence_embedding_dimension() == 1024
print(f"[EMBED] Model loaded in {t_model_end - t_model_start:.2f}s, dim=1024", flush=True)

# ─── Step 3: Run 31 sequential queries ──────────────────────────────────────
results_out: list[dict] = []
contamination: dict[str, int] = {"ext_authority": 0, "repo_evidence": 0, "ext_raw": 0, "other": 0}

print(f"\n[PROOF] Running {len(FAMILIES)} sequential queries against {COLLECTION}...\n", flush=True)

for fam in FAMILIES:
    fid = fam["id"]
    query_text = fam["query"]

    t0 = time.perf_counter()
    emb = model.encode([query_text], normalize_embeddings=True, show_progress_bar=False).tolist()
    t_embed = time.perf_counter() - t0

    t1 = time.perf_counter()
    raw = col.query(
        query_embeddings=emb,
        n_results=TOP_K,
        include=["metadatas", "distances", "documents"],
    )
    t_query = time.perf_counter() - t1

    ids_returned = raw.get("ids", [[]])[0]
    dists = raw.get("distances", [[]])[0]
    metas = raw.get("metadatas", [[]])[0]
    docs = raw.get("documents", [[]])[0]

    hits: list[dict] = []
    for i in range(len(ids_returned)):
        m = metas[i] if i < len(metas) else {}
        d = dists[i] if i < len(dists) else None
        doc = (docs[i] or "")[:300] if i < len(docs) else ""

        sc = m.get("source_collection", "unknown")
        if sc == "ext_authority":
            contamination["ext_authority"] += 1
        elif sc == "repo_evidence":
            contamination["repo_evidence"] += 1
        elif sc == "ext_raw":
            contamination["ext_raw"] += 1
        else:
            contamination["other"] += 1

        hits.append(
            {
                "rank": i + 1,
                "id": ids_returned[i],
                "distance": round(float(d), 4) if d is not None else None,
                "source_url": m.get("source_url", ""),
                "source_collection": sc,
                "source_band": m.get("source_band", ""),
                "authority_tier": m.get("authority_tier", ""),
                "title": m.get("title", ""),
                "heading_path": m.get("heading_path", ""),
                "doc_family": m.get("doc_family", ""),
                "topic_bucket": m.get("topic_bucket", ""),
                "invalid_for_normative_use": m.get("invalid_for_normative_use", False),
                "doc_snippet": doc,
            }
        )

    dist_at_1 = dists[0] if dists else 9.0
    n_relevant = sum(1 for d in dists if d < 0.50)
    n_strong = sum(1 for d in dists if d < 0.40)
    all_ext_authority = all(h["source_collection"] == "ext_authority" for h in hits)

    results_out.append(
        {
            "family": fam,
            "query_text": query_text,
            "embed_s": round(t_embed, 3),
            "query_s": round(t_query, 3),
            "n_hits": len(hits),
            "dist_at_1": round(dist_at_1, 4),
            "n_relevant_lt050": n_relevant,
            "n_strong_lt040": n_strong,
            "all_source_collection_ext_authority": all_ext_authority,
            "hits": hits,
        }
    )

    # Classify from live evidence
    if dist_at_1 < 0.35:
        live_grade = "STRONG"
    elif dist_at_1 < 0.50 and n_relevant >= 2:
        live_grade = "ADEQUATE"
    elif dist_at_1 < 0.55 and n_relevant >= 1:
        live_grade = "WEAK"
    else:
        live_grade = "MISSING"

    if fam["scope"] == "INTERNAL":
        live_grade = "INTERNAL/OUT-OF-SCOPE"

    results_out[-1]["live_grade"] = live_grade

    status = "✓" if live_grade in ("STRONG", "ADEQUATE") else ("~" if live_grade == "WEAK" else "✗")
    print(
        f"  {status} {fid} {fam['name'][:42]:<42} "
        f"dist@1={dist_at_1:.4f} rel={n_relevant}/5 "
        f"live={live_grade:<22} claim={fam['grade_claim']:<10} "
        f"embed={t_embed:.2f}s qry={t_query:.3f}s",
        flush=True,
    )

# ─── Save JSON ───────────────────────────────────────────────────────────────
out = {
    "proof_meta": {
        "chroma_path": CHROMA_PATH,
        "collection": COLLECTION,
        "collection_count": col_count,
        "collection_metadata": col_meta,
        "model": MODEL_NAME,
        "top_k": TOP_K,
        "total_families": len(FAMILIES),
        "relevance_thresh": 0.50,
        "strong_thresh": 0.35,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    },
    "contamination_summary": contamination,
    "family_results": results_out,
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"\n[DONE] Results saved to {OUT_PATH}", flush=True)
print(f"[DONE] Contamination: {contamination}", flush=True)
