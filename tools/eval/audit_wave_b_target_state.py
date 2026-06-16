"""Wave B external-only target-state audit + freeze gates.

Queries ext_authority ONLY across 20 semantically varied topics.
Runs Wave B metadata freeze gates on all 3 live collections.
Outputs markdown to docs/reports/wave_b_external_target_state_audit.md
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
EMBEDDING_MODEL = BGE_M3_MODEL_ID
OUT_PATH = REPO_ROOT / "docs" / "reports" / "wave_b_external_target_state_audit.md"

REQUIRED_FIELDS = {
    "source_collection",
    "source_band",
    "authority_tier",
    "normative_scope",
    "invalid_for_normative_use",
    "source_type",
    "topic_bucket",
    "doc_family",
    "source_url",
    "heading_path",
    "collapse_group",
    "title",
    "chunk_index",
    "canonical_digest",
}

# 20 semantically varied target-state queries (external knowledge only)
AUDIT_QUERIES = [
    {
        "id": "TS-01",
        "topic": "context_engineering",
        "text": "What is context engineering and how should context windows be managed in language model applications?",
    },
    {
        "id": "TS-02",
        "topic": "contextual_retrieval",
        "text": "How does contextual retrieval improve chunk-level relevance by adding context headers before embedding?",
    },
    {
        "id": "TS-03",
        "topic": "hybrid_retrieval",
        "text": "How should hybrid dense vector search and sparse BM25 retrieval be combined with score fusion?",
    },
    {
        "id": "TS-04",
        "topic": "reranking",
        "text": "How does cross-encoder reranking improve retrieval precision after initial vector search?",
    },
    {
        "id": "TS-05",
        "topic": "metadata_provenance",
        "text": "What metadata fields should be attached to retrieved chunks for provenance tracking and authority scoring?",
    },
    {
        "id": "TS-06",
        "topic": "chunking_strategy",
        "text": "What is the recommended chunking strategy for precision retrieval of technical documentation?",
    },
    {
        "id": "TS-07",
        "topic": "parent_child_expansion",
        "text": "When should parent-child chunk expansion be used and how does it work in retrieval pipelines?",
    },
    {
        "id": "TS-08",
        "topic": "evidence_shaping",
        "text": "How should retrieved evidence be shaped and filtered before grounding an agent response?",
    },
    {
        "id": "TS-09",
        "topic": "abstain_refine",
        "text": "When should an agent abstain from answering and what signals indicate insufficient evidence coverage?",
    },
    {
        "id": "TS-10",
        "topic": "routing_principles",
        "text": "What are the routing principles for directing queries to the appropriate retrieval source or collection?",
    },
    {
        "id": "TS-11",
        "topic": "agentic_architecture",
        "text": "What agentic architecture patterns define how agents reason plan and execute actions?",
    },
    {
        "id": "TS-12",
        "topic": "orchestrator_workers",
        "text": "How does the orchestrator-workers multi-agent pattern coordinate specialized sub-agents?",
    },
    {
        "id": "TS-13",
        "topic": "tool_contracts_mcp",
        "text": "How should Model Context Protocol MCP tools be defined registered and called from agents?",
    },
    {
        "id": "TS-14",
        "topic": "fastmcp_patterns",
        "text": "What is the FastMCP pattern for building MCP servers and how should tool schemas be structured?",
    },
    {
        "id": "TS-15",
        "topic": "agent_handoffs",
        "text": "How should agent handoffs be structured when transferring control between specialized agents?",
    },
    {
        "id": "TS-16",
        "topic": "safety_guardrails",
        "text": "What safety guardrails and constraints should govern autonomous agent behavior?",
    },
    {
        "id": "TS-17",
        "topic": "evaluator_optimizer",
        "text": "How does the evaluator-optimizer pattern improve agent output quality through iterative refinement?",
    },
    {
        "id": "TS-18",
        "topic": "single_vs_multi_agent",
        "text": "When should a single agent be used versus a multi-agent architecture for complex tasks?",
    },
    {
        "id": "TS-19",
        "topic": "embedding_model",
        "text": "What embedding model dimensions and distance metrics are recommended for agentic retrieval systems?",
    },
    {
        "id": "TS-20",
        "topic": "normative_requirements",
        "text": "What normative requirements must agentic systems satisfy for determinism provenance and safety?",
    },
]

STRONG_DIST = 0.35
ADEQUATE_DIST = 0.50


def grounding_verdict(dist_at_1: float, answer_support: bool) -> str:
    if dist_at_1 < STRONG_DIST and answer_support:
        return "STRONG"
    if dist_at_1 < ADEQUATE_DIST:
        return "ADEQUATE"
    if dist_at_1 < 0.70:
        return "WEAK"
    return "EMPTY"


def drift_risk(dist_at_1: float, answer_support: bool) -> str:
    if dist_at_1 < STRONG_DIST and answer_support:
        return "GROUNDED"
    if dist_at_1 < ADEQUATE_DIST:
        return "PARTIAL_DRIFT"
    return "DRIFT_RISK"


def answer_support_check(text: str, query: str) -> bool:
    stopwords = {
        "what",
        "how",
        "does",
        "the",
        "a",
        "an",
        "is",
        "are",
        "in",
        "and",
        "for",
        "of",
        "to",
        "it",
        "should",
        "when",
        "where",
        "which",
        "that",
        "this",
        "with",
        "by",
        "from",
    }
    tokens = [t.lower() for t in query.split() if len(t) > 3 and t.lower() not in stopwords]
    if not tokens:
        return True
    text_lower = text.lower()
    hits = sum(1 for t in tokens if t in text_lower)
    return hits >= min(2, len(tokens))


def run_audit() -> None:
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        import torch
    except ImportError as exc:
        raise SystemExit(f"Missing dependency: {exc}") from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {EMBEDDING_MODEL} on {device} ...", flush=True)
    t0 = time.time()
    model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    model.max_seq_length = 512
    print(f"Model ready ({time.time() - t0:.1f}s)", flush=True)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    available = {col.name for col in client.list_collections()}
    print(f"Collections available: {sorted(available)}", flush=True)

    # ── Phase 1: External-only target-state audit ─────────────────────────
    ext_col = client.get_collection("ext_authority")
    print(f"\next_authority: {ext_col.count()} chunks", flush=True)

    audit_results = []
    print(f"\nRunning {len(AUDIT_QUERIES)} target-state queries against ext_authority only ...", flush=True)

    for qi, q in enumerate(AUDIT_QUERIES, 1):
        print(f"  [{qi:02d}/{len(AUDIT_QUERIES)}] {q['id']}: {q['text'][:60]}...", flush=True)
        emb = model.encode(q["text"], normalize_embeddings=True, show_progress_bar=False).tolist()
        raw = ext_col.query(
            query_embeddings=[emb],
            n_results=5,
            include=["documents", "metadatas", "distances"],
        )
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]

        top5 = []
        for doc, meta, dist in zip(docs, metas, dists):
            top5.append(
                {
                    "dist": round(float(dist), 4),
                    "source_url": meta.get("source_url", ""),
                    "title": meta.get("title", "")[:80],
                    "heading_path": meta.get("heading_path", ""),
                    "authority_tier": meta.get("authority_tier", ""),
                    "source_band": meta.get("source_band", ""),
                    "topic_bucket": meta.get("topic_bucket", ""),
                    "collection": meta.get("source_collection", ""),
                    "text_snippet": doc[:200].replace("\n", " "),
                    "answer_support": answer_support_check(doc, q["text"]),
                }
            )

        d1 = top5[0]["dist"] if top5 else 2.0
        support = top5[0]["answer_support"] if top5 else False
        audit_results.append(
            {
                "query": q,
                "top5": top5,
                "dist_at_1": d1,
                "grounding": grounding_verdict(d1, support),
                "drift_risk": drift_risk(d1, support),
            }
        )

    # ── Phase 2: Wave B freeze gates ────────────────────────────────────────
    print("\nRunning Wave B freeze gates ...", flush=True)
    gates: dict[str, dict] = {}

    # G1: ext_authority C2 — invalid_for_normative_use must be False
    ext_all = ext_col.get(include=["metadatas"])
    ext_metas = ext_all["metadatas"]
    c2_bad = [m for m in ext_metas if m.get("invalid_for_normative_use") is not False]
    gates["G1_C2_ext_authority_normative_use"] = {
        "pass": len(c2_bad) == 0,
        "detail": f"{len(c2_bad)} chunks with invalid_for_normative_use != False",
        "count": len(ext_metas),
    }

    # G2: ext_authority C4 — source_url must start with https://
    c4_bad = [m for m in ext_metas if not m.get("source_url", "").startswith("https://")]
    gates["G2_C4_ext_authority_https_urls"] = {
        "pass": len(c4_bad) == 0,
        "detail": f"{len(c4_bad)} chunks with non-https source_url",
        "count": len(ext_metas),
    }

    # G3: ext_authority required fields completeness
    c_missing = [m for m in ext_metas if not REQUIRED_FIELDS.issubset(m.keys())]
    gates["G3_ext_authority_required_fields"] = {
        "pass": len(c_missing) == 0,
        "detail": f"{len(c_missing)} chunks missing required fields",
        "count": len(ext_metas),
    }

    if "repo_evidence" in available:
        repo_col = client.get_collection("repo_evidence")
        repo_metas = repo_col.get(include=["metadatas"])["metadatas"]

        # G4: repo_evidence C3 — invalid_for_normative_use must be True
        c3_bad = [m for m in repo_metas if m.get("invalid_for_normative_use") is not True]
        gates["G4_C3_repo_evidence_normative_gate"] = {
            "pass": len(c3_bad) == 0,
            "detail": f"{len(c3_bad)} chunks with invalid_for_normative_use != True",
            "count": len(repo_metas),
        }

        # G5: repo_evidence C5 — source_url must NOT start with https://
        c5_bad = [m for m in repo_metas if m.get("source_url", "").startswith("https://")]
        gates["G5_C5_repo_evidence_no_web_urls"] = {
            "pass": len(c5_bad) == 0,
            "detail": f"{len(c5_bad)} chunks with https:// source_url (should be local paths)",
            "count": len(repo_metas),
        }

        # G6: repo_evidence required fields
        r_missing = [m for m in repo_metas if not REQUIRED_FIELDS.issubset(m.keys())]
        gates["G6_repo_evidence_required_fields"] = {
            "pass": len(r_missing) == 0,
            "detail": f"{len(r_missing)} chunks missing required fields",
            "count": len(repo_metas),
        }
    else:
        gates["G4_C3_repo_evidence_normative_gate"] = {
            "pass": False,
            "detail": "repo_evidence missing",
            "count": 0,
        }
        gates["G5_C5_repo_evidence_no_web_urls"] = {
            "pass": False,
            "detail": "repo_evidence missing",
            "count": 0,
        }
        gates["G6_repo_evidence_required_fields"] = {
            "pass": False,
            "detail": "repo_evidence missing",
            "count": 0,
        }

    if "ext_raw" in available:
        raw_col = client.get_collection("ext_raw")
        raw_metas = raw_col.get(include=["metadatas"])["metadatas"]

        # G7: ext_raw C3 — invalid_for_normative_use must be True
        c3r_bad = [m for m in raw_metas if m.get("invalid_for_normative_use") is not True]
        gates["G7_C3_ext_raw_normative_gate"] = {
            "pass": len(c3r_bad) == 0,
            "detail": f"{len(c3r_bad)} chunks with invalid_for_normative_use != True",
            "count": len(raw_metas),
        }

        # G8: ext_raw C9 — no URL overlap with ext_authority
        ext_urls = {m["source_url"] for m in ext_metas if m.get("source_url")}
        c9_bad = [m for m in raw_metas if m.get("source_url") in ext_urls]
        gates["G8_C9_ext_raw_no_url_overlap"] = {
            "pass": len(c9_bad) == 0,
            "detail": f"{len(c9_bad)} chunks with source_url already in ext_authority",
            "count": len(raw_metas),
        }
    else:
        gates["G7_C3_ext_raw_normative_gate"] = {"pass": False, "detail": "ext_raw missing", "count": 0}
        gates["G8_C9_ext_raw_no_url_overlap"] = {"pass": False, "detail": "ext_raw missing", "count": 0}

    # G9: Route purity — target-state grounding from ext_authority is strong enough
    strong_count = sum(1 for r in audit_results if r["grounding"] == "STRONG")
    adequate_count = sum(1 for r in audit_results if r["grounding"] == "ADEQUATE")
    weak_count = sum(1 for r in audit_results if r["grounding"] == "WEAK")
    empty_count = sum(1 for r in audit_results if r["grounding"] == "EMPTY")
    gates["G9_target_state_retrieval_strength"] = {
        "pass": (strong_count + adequate_count) >= 15,
        "detail": f"Strong={strong_count} Adequate={adequate_count} Weak={weak_count} Empty={empty_count}",
        "count": len(AUDIT_QUERIES),
    }

    # G10: repo contamination = 0 for target-state audit (ext_authority only)
    repo_contam = sum(1 for r in audit_results for hit in r["top5"] if hit["collection"] != "ext_authority")
    gates["G10_repo_contamination_zero"] = {
        "pass": repo_contam == 0,
        "detail": f"{repo_contam} non-ext_authority chunks in target-state audit results",
        "count": sum(len(r["top5"]) for r in audit_results),
    }

    # G11: ext_raw contamination = 0 for target-state audit
    raw_contam = sum(1 for r in audit_results for hit in r["top5"] if hit["collection"] == "ext_raw")
    gates["G11_ext_raw_contamination_zero"] = {
        "pass": raw_contam == 0,
        "detail": f"{raw_contam} ext_raw chunks in target-state audit results",
        "count": sum(len(r["top5"]) for r in audit_results),
    }

    # ── Phase 3: Generate markdown report ────────────────────────────────────
    lines: list[str] = []
    lines.append("# Wave B External-Only Target-State Audit")
    lines.append("")
    lines.append("**Date**: " + time.strftime("%Y-%m-%d") + "  ")
    lines.append("**Collection**: `ext_authority` only (323 chunks, Lane A=112, Lane B=211)  ")
    lines.append(f"**Model**: {BGE_M3_MODEL_ID} (1024-dim, cosine)  ")
    lines.append("**Queries**: 20 semantically varied target-state topics  ")
    lines.append(
        "**Anti-drift rule**: Target state MUST come from ext_authority only. repo_evidence and ext_raw are EXCLUDED.  "
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Gate summary first
    lines.append("## 1. Wave B Freeze Gate Results")
    lines.append("")
    all_pass = all(g["pass"] for g in gates.values())
    lines.append(f"**Overall gate verdict**: {'PASS ✓' if all_pass else 'FAIL ✗'}  ")
    lines.append("")
    lines.append("| Gate | Description | Count | Result |")
    lines.append("|------|-------------|-------|--------|")
    gate_descriptions = {
        "G1_C2_ext_authority_normative_use": "C2: ext_authority invalid_for_normative_use=False",
        "G2_C4_ext_authority_https_urls": "C4: ext_authority source_url starts with https://",
        "G3_ext_authority_required_fields": "ext_authority all required fields present",
        "G4_C3_repo_evidence_normative_gate": "C3: repo_evidence invalid_for_normative_use=True",
        "G5_C5_repo_evidence_no_web_urls": "C5: repo_evidence no https:// source_url",
        "G6_repo_evidence_required_fields": "repo_evidence all required fields present",
        "G7_C3_ext_raw_normative_gate": "C3: ext_raw invalid_for_normative_use=True",
        "G8_C9_ext_raw_no_url_overlap": "C9: ext_raw no URL overlap with ext_authority",
        "G9_target_state_retrieval_strength": "Target-state retrieval: ≥15/20 queries Strong+Adequate",
        "G10_repo_contamination_zero": "Repo contamination in target-state audit = 0",
        "G11_ext_raw_contamination_zero": "ext_raw contamination in target-state audit = 0",
    }
    for gkey, gval in gates.items():
        status = "PASS ✓" if gval["pass"] else "FAIL ✗"
        desc = gate_descriptions.get(gkey, gkey)
        lines.append(f"| `{gkey}` | {desc} | {gval['count']} | **{status}** |")
        if not gval["pass"]:
            lines.append(f"| | ↳ {gval['detail']} | | |")
    lines.append("")

    # Audit results
    lines.append("## 2. External-Only Target-State Audit Results")
    lines.append("")
    lines.append(
        "Grounding thresholds: **STRONG** dist<0.35 + answer support · **ADEQUATE** dist<0.50 · **WEAK** dist<0.70 · **EMPTY** ≥0.70"
    )
    lines.append("")

    grounding_summary: dict[str, int] = {"STRONG": 0, "ADEQUATE": 0, "WEAK": 0, "EMPTY": 0}

    for r in audit_results:
        q = r["query"]
        grounding_summary[r["grounding"]] = grounding_summary.get(r["grounding"], 0) + 1
        status_icon = {"STRONG": "✅", "ADEQUATE": "🟡", "WEAK": "⚠️", "EMPTY": "❌"}.get(r["grounding"], "?")
        lines.append(
            f"### {q['id']} — {q['topic'].replace('_', ' ').title()} [{status_icon} {r['grounding']}]"
        )
        lines.append("")
        lines.append(f"**Query**: {q['text']}  ")
        lines.append(f"**Route class**: target_state / best_practice → `ext_authority`  ")
        lines.append(
            f"**dist@1**: {r['dist_at_1']:.4f} · **Grounding**: {r['grounding']} · **Drift risk**: {r['drift_risk']}  "
        )
        lines.append("")
        lines.append("| Rank | dist | Source | Authority tier | Source band | Topic |")
        lines.append("|------|------|--------|----------------|-------------|-------|")
        for i, hit in enumerate(r["top5"], 1):
            short_url = (
                hit["source_url"]
                .replace("https://raw.githubusercontent.com/", "gh://")
                .replace("https://", "")[:60]
            )
            lines.append(
                f"| {i} | {hit['dist']:.4f} | `{short_url}` | {hit['authority_tier']} | {hit['source_band']} | {hit['topic_bucket']} |"
            )
        if r["top5"]:
            lines.append("")
            lines.append(f"**Top result**: `{r['top5'][0]['heading_path']}`  ")
            lines.append(f"**Snippet**: {r['top5'][0]['text_snippet'][:200]}  ")
        lines.append("")

    # Grounding summary
    lines.append("## 3. Grounding Coverage Summary")
    lines.append("")
    total = len(audit_results)
    strong_pct = 100 * grounding_summary["STRONG"] // total if total else 0
    adequate_pct = 100 * grounding_summary["ADEQUATE"] // total if total else 0
    lines.append("| Grounding level | Count | % | Interpretation |")
    lines.append("|-----------------|-------|---|----------------|")
    lines.append(
        f"| STRONG | {grounding_summary['STRONG']} | {strong_pct}% | External retrieval is self-sufficient |"
    )
    lines.append(
        f"| ADEQUATE | {grounding_summary['ADEQUATE']} | {adequate_pct}% | Retrieval supports grounded guidance |"
    )
    lines.append(
        f"| WEAK | {grounding_summary['WEAK']} | {100 * grounding_summary['WEAK'] // total if total else 0}% | Gap — model memory supplement risk |"
    )
    lines.append(
        f"| EMPTY | {grounding_summary['EMPTY']} | {100 * grounding_summary['EMPTY'] // total if total else 0}% | Fail-closed — no valid guidance |"
    )
    lines.append("")
    covered = grounding_summary["STRONG"] + grounding_summary["ADEQUATE"]
    lines.append(f"**External coverage**: {covered}/{total} queries adequately grounded from ext_authority  ")
    if covered >= 15:
        lines.append(
            "**Gate G9**: PASS ✓ — ext_authority retrieval is strong enough to define external target-state baseline  "
        )
    else:
        lines.append(
            f"**Gate G9**: FAIL ✗ — only {covered}/20 queries grounded; gap topics need additional ext_authority sources  "
        )
    lines.append("")
    lines.append(
        "**Anti-drift compliance**: All results sourced exclusively from `ext_authority`. repo_evidence and ext_raw were not queried.  "
    )
    lines.append("")

    report = "\n".join(lines)
    print("\n" + "=" * 80)
    print(report[:3000], "...[truncated in stdout, see file]")
    print("=" * 80)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(f"\nAudit report written to {OUT_PATH}", flush=True)

    # Emit structured gate results for downstream use
    gate_out = REPO_ROOT / "docs" / "reports" / "wave_b_freeze_gates.json"
    gate_out.write_text(
        json.dumps(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "all_pass": all_pass,
                "grounding_summary": grounding_summary,
                "gates": {k: {"pass": v["pass"], "detail": v["detail"]} for k, v in gates.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Gate results written to {gate_out}", flush=True)

    if not all_pass:
        print("\n⚠ SOME GATES FAILED — see report for details", flush=True)
        sys.exit(1)
    else:
        print("\n✓ ALL GATES PASS — Wave B retrieval baseline is sound", flush=True)


if __name__ == "__main__":
    run_audit()
