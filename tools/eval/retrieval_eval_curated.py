"""Retrieval quality benchmark: repo_evidence vs ext_raw vs ext_authority.

Runs 40 golden queries across 8 categories, computes 9 metrics per query per
collection, identifies worst 10 queries, and emits a markdown report.

Usage:
    python tools/eval/retrieval_eval_curated.py [--k 5] [--out docs/reports/retrieval_eval.md]

No ground-truth labels required — uses metadata signals and distance as proxies.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
EMBEDDING_MODEL = BGE_M3_MODEL_ID

# Distance below which a result is "relevant" (cosine, 0=identical, 2=opposite)
RELEVANCE_THRESH = 0.50
HIGH_REL_THRESH = 0.35

COLLECTIONS = ["repo_evidence", "ext_raw", "ext_authority"]

# Query categories that require normative authority (arch_docs must NOT appear in curated top-K)
_NORMATIVE_CATS: frozenset[str] = frozenset({"policy", "tooling", "standards"})

# ─────────────────────────────────────────────────────────────────────────────
# 40 Golden queries across 8 categories × 5 each
# ─────────────────────────────────────────────────────────────────────────────
GOLDEN_QUERIES: list[dict] = [
    # ── 1. Architecture invariants (ARCH) ────────────────────────────────────
    {
        "id": "ARCH-01",
        "text": "What are the layer boundaries in the agentic workflow?",
        "cat": "architecture",
    },
    {
        "id": "ARCH-02",
        "text": "Describe the L0 through L5 architecture layers and their responsibilities",
        "cat": "architecture",
    },
    {
        "id": "ARCH-03",
        "text": "What is the Exit Spine and how does it evaluate agent responses?",
        "cat": "architecture",
    },
    {
        "id": "ARCH-04",
        "text": "What are the determinism requirements for agentic decision-making?",
        "cat": "architecture",
    },
    {
        "id": "ARCH-05",
        "text": "How does the governed-app contract enforce layer contracts?",
        "cat": "architecture",
    },
    # ── 2. Layer terminology (LAYER) ─────────────────────────────────────────
    {"id": "LAYER-01", "text": "What does L0 routing do in the agentic process map?", "cat": "layer"},
    {"id": "LAYER-02", "text": "Explain the L1 reasoning and plan emission phase", "cat": "layer"},
    {"id": "LAYER-03", "text": "What is the L5 policy plane responsible for?", "cat": "layer"},
    {"id": "LAYER-04", "text": "How does L4 state management work in the agentic system?", "cat": "layer"},
    {
        "id": "LAYER-05",
        "text": "What is the L2 execution layer and how does it dispatch actions?",
        "cat": "layer",
    },
    # ── 3. UWG / Exit Spine / C0 / determinism / policy_hash (POLICY) ───────
    {
        "id": "POLICY-01",
        "text": "What is the Unstructured Write Gate UWG and when does it fire?",
        "cat": "policy",
    },
    {"id": "POLICY-02", "text": "How does policy_hash verification work for agent outputs?", "cat": "policy"},
    {"id": "POLICY-03", "text": "What triggers the exit spine and bounded autonomy check?", "cat": "policy"},
    {
        "id": "POLICY-04",
        "text": "How is determinism enforced and what is C0 content filter gate?",
        "cat": "policy",
    },
    {
        "id": "POLICY-05",
        "text": "What are the constitutional hard constraints for agent behavior?",
        "cat": "policy",
    },
    # ── 4. legacy editor hooks / MCP / tooling (TOOLING) ──────────────────────────
    {
        "id": "TOOL-01",
        "text": "How do legacy editor MCP servers work and what is the FastMCP pattern?",
        "cat": "tooling",
    },
    {
        "id": "TOOL-02",
        "text": "How to configure a legacy editor hook with command and working_directory?",
        "cat": "tooling",
    },
    {"id": "TOOL-03", "text": "What is the ADG SQLite MCP server and how is it queried?", "cat": "tooling"},
    {
        "id": "TOOL-04",
        "text": "How does the vector_db MCP tool add documents and query collections?",
        "cat": "tooling",
    },
    {
        "id": "TOOL-05",
        "text": "What is the DeferredLoader pattern for MCP server model loading?",
        "cat": "tooling",
    },
    # ── 5. Retrieval / embedding / Chroma (RETRIEVAL) ────────────────────────
    {
        "id": "RETR-01",
        "text": "How does hybrid search combine vector and lexical results with score fusion?",
        "cat": "retrieval",
    },
    {
        "id": "RETR-02",
        "text": "What embedding model is used for ChromaDB and what is its dimension?",
        "cat": "retrieval",
    },
    {
        "id": "RETR-03",
        "text": "What is the authority_level metadata field and how is it used for reranking?",
        "cat": "retrieval",
    },
    {
        "id": "RETR-04",
        "text": "How does the section-aware chunking policy work for architecture documents?",
        "cat": "retrieval",
    },
    {
        "id": "RETR-05",
        "text": "What collections are authoritative for agentic architecture queries?",
        "cat": "retrieval",
    },
    # ── 6. Standards / design patterns / eval / safety (STANDARDS) ───────────
    {
        "id": "STD-01",
        "text": "What are the repository coding and architecture standards?",
        "cat": "standards",
    },
    {
        "id": "STD-02",
        "text": "How does the evaluator-optimizer pattern work for agent quality?",
        "cat": "standards",
    },
    {
        "id": "STD-03",
        "text": "What are the guardrails and safety rules for agent behavior?",
        "cat": "standards",
    },
    {
        "id": "STD-04",
        "text": "How does the orchestrator-workers multi-agent pattern work?",
        "cat": "standards",
    },
    {
        "id": "STD-05",
        "text": "What observability and tracing hooks are available for agents?",
        "cat": "standards",
    },
    # ── 7. Historical version / ADR lookups (HISTORY) ────────────────────────
    {
        "id": "HIST-01",
        "text": "What was decided in ADR-0043 about structural conformance checks?",
        "cat": "history",
    },
    {
        "id": "HIST-02",
        "text": "What does ADR-018 say about ChromaDB as the canonical vector store?",
        "cat": "history",
    },
    {"id": "HIST-03", "text": "What is the skills consolidation ADR about?", "cat": "history"},
    {
        "id": "HIST-04",
        "text": "What changed in the latest agentic process mapping version?",
        "cat": "history",
    },
    {
        "id": "HIST-05",
        "text": "What interface-first design principle does ADR-002 establish?",
        "cat": "history",
    },
    # ── 8. Single-agent vs multi-agent choice (MULTIAGENT) ───────────────────
    {
        "id": "MA-01",
        "text": "When should I use a single agent versus multi-agent architecture?",
        "cat": "multiagent",
    },
    {
        "id": "MA-02",
        "text": "What are the handoff patterns for transferring control between agents?",
        "cat": "multiagent",
    },
    {
        "id": "MA-03",
        "text": "How to choose between orchestrator pattern and sub-agent delegation?",
        "cat": "multiagent",
    },
    {
        "id": "MA-04",
        "text": "What are the criteria for agent function tool use versus handoff?",
        "cat": "multiagent",
    },
    {
        "id": "MA-05",
        "text": "How does the agent framework handle parallel tool execution?",
        "cat": "multiagent",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Per-result signal extraction (graceful across schema differences)
# ─────────────────────────────────────────────────────────────────────────────

_ARCH_SOURCE_AREAS = {"arch", "adr", "contract", "spec"}
_ARCH_DOC_FAMILIES = {"adr", "architecture", "contract", "spec", "standard"}
_TOOLING_PATTERNS = re.compile(r"\.(py|json|yaml|sh)$|/test|ops_script|tools/mcp|tools/generate", re.I)

# High-signal domains in ext_knowledge (used for authority proxy)
_EXT_HIGH_SIGNAL_DOMAINS = {
    "raw.githubusercontent.com",
    "openai.github.io",
    "docs.anthropic.com",
    "platform.openai.com",
    "openai-agents-python",
}


def _is_arch_relevant(meta: dict) -> bool:
    sa = meta.get("source_area", "")
    df = meta.get("doc_family", "")
    fp = meta.get("file_path", "")
    at = meta.get("artifact_type", "")
    if sa in _ARCH_SOURCE_AREAS or df in _ARCH_DOC_FAMILIES:
        return True
    if at == "arch_doc" and not _TOOLING_PATTERNS.search(fp):
        return True
    return False


def _is_best_practice_relevant(meta: dict) -> bool:
    tb = meta.get("topic_bucket", "")
    df = meta.get("doc_family", "")
    if tb in {"arch_standards", "orchestration", "safety_eval", "rag_retrieval"}:
        return True
    if df in {"reference", "guide", "standard", "adr"}:
        return True
    return False


def _is_tooling_contamination(meta: dict) -> bool:
    fp = meta.get("file_path", "")
    at = meta.get("artifact_type", "")
    sa = meta.get("source_area", "")
    if sa == "code":
        return True
    if at in {"code_chunk", "test_chunk", "script_chunk"}:
        return True
    if _TOOLING_PATTERNS.search(fp) and at != "arch_doc":
        return True
    return False


def _authority_level(meta: dict) -> float:
    if "authority_level" in meta:
        return float(meta["authority_level"])
    # Infer for arch_docs
    if meta.get("artifact_type") == "arch_doc":
        fp = meta.get("file_path", "")
        if "/adr/" in fp or fp.startswith("docs/"):
            return 0.70
    # Infer for ext_knowledge by domain
    domain = meta.get("domain", "")
    if any(hsd in domain for hsd in _EXT_HIGH_SIGNAL_DOMAINS):
        return 0.65
    return 0.40


def _is_canonical(meta: dict) -> bool:
    """Return True when the chunk is from an authoritative, canonical source.

    Phase 4: chunks with invalid_for_normative_use=True are never canonical —
    they are implementation evidence only (arch_docs post-Phase-0 rebuild).
    """
    if meta.get("invalid_for_normative_use"):
        return False
    if "canonical" in meta:
        return bool(meta["canonical"])
    # Legacy inference: arch ADRs have partial canonical value (pre-Phase-0 chunks)
    if meta.get("artifact_type") == "arch_doc" and "/adr/" in meta.get("file_path", ""):
        return True
    return False


def _answer_support(text: str, query: str) -> bool:
    """Proxy: at least 2 non-trivial query tokens appear in the result text."""
    stopwords = {"what", "how", "does", "the", "a", "an", "is", "are", "in", "and", "for", "of", "to", "it"}
    tokens = [t.lower() for t in re.split(r"\W+", query) if len(t) > 3 and t.lower() not in stopwords]
    if not tokens:
        return True
    text_lower = text.lower()
    hits = sum(1 for t in tokens if t in text_lower)
    return hits >= min(2, len(tokens))


def _doc_family(meta: dict) -> str:
    df = meta.get("doc_family", "")
    if df:
        return df
    at = meta.get("artifact_type", "")
    if at == "arch_doc":
        fp = meta.get("file_path", "")
        if "/adr/" in fp:
            return "adr"
        if "docs/" in fp:
            return "arch"
    if at == "ext_knowledge":
        return "web"
    return meta.get("doc_type", "unknown")


# ─────────────────────────────────────────────────────────────────────────────
# Metrics dataclass
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class QueryMetrics:
    collection: str
    query_id: str
    cat: str
    result_count: int
    # Distance signals (lower = better)
    dist_at_1: float = 2.0
    mean_dist_at_k: float = 2.0
    # Authority signals (higher = better)
    canonical_hit_rate: float = 0.0
    mean_authority: float = 0.0
    # Content quality signals
    arch_depth: float = 0.0
    bp_relevance: float = 0.0
    answer_support: float = 0.0
    # Contamination / diversity
    tooling_contamination: float = 0.0
    arch_docs_contamination: int = 0  # count of chunks with source_collection=arch_docs in top-K
    source_diversity: int = 0
    redundancy_rate: float = 0.0
    # Derived
    p_at_k: float = 0.0
    mrr: float = 0.0

    @property
    def win_score(self) -> float:
        """Composite score for win/loss determination (higher = better collection)."""
        return (
            (1 - self.dist_at_1 / 2.0) * 0.30
            + self.canonical_hit_rate * 0.20
            + self.mean_authority * 0.15
            + self.answer_support * 0.15
            + self.arch_depth * 0.10
            + self.p_at_k * 0.10
        )


def compute_metrics(
    query_text: str,
    query_id: str,
    cat: str,
    collection_name: str,
    results: dict,
    k: int,
) -> QueryMetrics:
    docs = results.get("documents", [[]])[0][:k]
    metas = results.get("metadatas", [[]])[0][:k]
    dists = results.get("distances", [[]])[0][:k]

    n = len(docs)
    m = QueryMetrics(
        collection=collection_name,
        query_id=query_id,
        cat=cat,
        result_count=n,
    )
    if n == 0:
        return m

    m.dist_at_1 = float(dists[0])
    m.mean_dist_at_k = float(sum(dists) / n)

    seen_sources: set[str] = set()
    duplicate_count = 0
    families: set[str] = set()
    arch_contam_count = 0

    relevant_count = 0
    highly_relevant_rank = None

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
        # Phase 4: record source_collection provenance for contamination gate
        if meta.get("source_collection", "") == "repo_evidence":
            arch_contam_count += 1

        # Redundancy = same source URL appears multiple times in top-K (same-doc concentration)
        src = meta.get("source_url", meta.get("file_path", f"__unknown_{i}"))
        if src in seen_sources:
            duplicate_count += 1
        else:
            seen_sources.add(src)

        families.add(_doc_family(meta))

        if _is_canonical(meta):
            m.canonical_hit_rate += 1
        m.mean_authority += _authority_level(meta)

        if _is_arch_relevant(meta):
            m.arch_depth += 1
        if _is_best_practice_relevant(meta):
            m.bp_relevance += 1
        if _is_tooling_contamination(meta):
            m.tooling_contamination += 1
        if _answer_support(doc, query_text):
            m.answer_support += 1

        if dist < RELEVANCE_THRESH:
            relevant_count += 1
        if dist < HIGH_REL_THRESH and highly_relevant_rank is None:
            highly_relevant_rank = i + 1

    m.canonical_hit_rate /= n
    m.mean_authority /= n
    m.arch_depth /= n
    m.bp_relevance /= n
    m.tooling_contamination /= n
    m.answer_support /= n
    m.redundancy_rate = duplicate_count / n
    m.source_diversity = len(families)
    m.p_at_k = relevant_count / n
    m.mrr = (1.0 / highly_relevant_rank) if highly_relevant_rank else 0.0
    m.arch_docs_contamination = arch_contam_count

    return m


# ─────────────────────────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────────────────────────


def _fmt(v: float) -> str:
    return f"{v:.3f}"


def generate_report(
    all_metrics: list[QueryMetrics],
    k: int,
    elapsed: float,
    live_path: bool = False,
) -> str:
    lines: list[str] = []
    mode_tag = " — live-path (authority-rerank + collapse-dedup)" if live_path else ""
    lines.append(f"# Retrieval Quality Benchmark — repo_evidence vs ext_raw vs ext_authority{mode_tag}")
    lines.append(
        f"\n**Queries**: {len(set(m.query_id for m in all_metrics))} · **K**: {k} · **Elapsed**: {elapsed:.1f}s\n"
    )

    # ── 1. Side-by-side collection-level metrics ──────────────────────────
    lines.append("## 1. Collection-Level Metrics (mean over all 40 queries)\n")
    col_metrics: dict[str, list[QueryMetrics]] = {}
    for m in all_metrics:
        col_metrics.setdefault(m.collection, []).append(m)

    header = f"| Metric                | {'repo_evidence':>18} | {'ext_raw':>18} | {'ext_authority':>20} |"
    separator = "|" + "-" * 23 + "|" + "-" * 20 + "|" + "-" * 20 + "|" + "-" * 22 + "|"
    lines.append(header)
    lines.append(separator)

    def avg(cname: str, attr: str) -> float:
        vals = [getattr(m, attr) for m in col_metrics.get(cname, [])]
        return sum(vals) / len(vals) if vals else 0.0

    def win_col(attr: str, lower_is_better: bool = False) -> str:
        vals = {c: avg(c, attr) for c in COLLECTIONS if c in col_metrics}
        if not vals:
            return ""
        best = min(vals, key=vals.__getitem__) if lower_is_better else max(vals, key=vals.__getitem__)
        return best

    metric_rows = [
        ("P@K (dist<0.5)", "p_at_k", False),
        ("MRR (dist<0.35)", "mrr", False),
        ("Mean dist@1", "dist_at_1", True),
        ("Mean dist@K", "mean_dist_at_k", True),
        ("Canonical hit rate", "canonical_hit_rate", False),
        ("Mean authority", "mean_authority", False),
        ("Arch depth", "arch_depth", False),
        ("BP relevance", "bp_relevance", False),
        ("Answer support", "answer_support", False),
        ("Redundancy rate", "redundancy_rate", True),
        ("Source diversity", "source_diversity", False),
        ("Tooling contam.", "tooling_contamination", True),
    ]

    for label, attr, lib in metric_rows:
        best = win_col(attr, lib)
        vals = []
        for c in COLLECTIONS:
            v = avg(c, attr)
            marker = " ✓" if c == best else ""
            vals.append(f"{_fmt(v)}{marker}")
        lines.append(f"| {label:<21} | {vals[0]:>18} | {vals[1]:>18} | {vals[2]:>20} |")
    lines.append("")

    # ── 2. Per-category win rates ─────────────────────────────────────────
    lines.append("## 2. Per-Category Win Rate\n")
    cats = sorted({m.cat for m in all_metrics})
    lines.append("| Category     | repo_evidence wins | ext_raw wins | ext_authority wins |")
    lines.append("|--------------|-------------------|--------------|-------------------|")
    for cat in cats:
        # Group by query_id, pick winner per query by win_score
        query_ids = {m.query_id for m in all_metrics if m.cat == cat}
        wins: dict[str, int] = {c: 0 for c in COLLECTIONS}
        for qid in query_ids:
            qm = {m.collection: m for m in all_metrics if m.query_id == qid and m.cat == cat}
            if qm:
                winner = max(qm, key=lambda c: qm[c].win_score)
                wins[winner] += 1
        total = len(query_ids)

        def pct(c: str) -> str:
            return f"{wins[c]}/{total}"

        lines.append(
            f"| {cat:<12} | {pct('repo_evidence'):>17} | {pct('ext_raw'):>12} | {pct('ext_authority'):>18} |"
        )
    lines.append("")

    # ── 3. Query-by-query win/loss table ─────────────────────────────────
    lines.append("## 3. Query-by-Query Win/Loss Summary\n")
    lines.append(
        "| QID       | Category     | Winner               | repo dist@1 | raw dist@1 | authority dist@1 | Notes |"
    )
    lines.append(
        "|-----------|--------------|----------------------|-------------|------------|------------------|-------|"
    )
    query_ids_sorted = sorted({m.query_id for m in all_metrics})
    query_notes: dict[str, str] = {}  # filled below
    for qid in query_ids_sorted:
        qm = {m.collection: m for m in all_metrics if m.query_id == qid}
        cat = next(iter(qm.values())).cat if qm else "?"
        winner = max(qm, key=lambda c: qm[c].win_score) if qm else "?"
        d1 = {c: _fmt(qm[c].dist_at_1) if c in qm else "N/A" for c in COLLECTIONS}
        notes = ""
        if "ext_authority" in qm:
            cm = qm["ext_authority"]
            if cm.tooling_contamination > 0.3:
                notes = "tooling contam"
            elif cm.dist_at_1 > 0.6:
                notes = "low relevance"
            elif cm.redundancy_rate > 0.4:
                notes = "high redundancy"
        query_notes[qid] = notes
        lines.append(
            f"| {qid:<9} | {cat:<12} | {winner:<20} | {d1['repo_evidence']:>11} | {d1['ext_raw']:>10} | {d1['ext_authority']:>16} | {notes} |"
        )
    lines.append("")

    # ── 4. Worst 10 queries for curated collection ────────────────────────
    lines.append("## 4. Worst 10 Queries for ext_authority (RCA)\n")
    curated_metrics = sorted(
        [m for m in all_metrics if m.collection == "ext_authority"],
        key=lambda m: m.win_score,
    )[:10]
    lines.append("| Rank | QID       | Category     | win_score | dist@1 | P@K   | Canonical | Auth  | RCA |")
    lines.append("|------|-----------|--------------|-----------|--------|-------|-----------|-------|-----|")
    for rank, m in enumerate(curated_metrics, 1):
        rca = _worst_query_rca(m)
        lines.append(
            f"| {rank:>4} | {m.query_id:<9} | {m.cat:<12} | {_fmt(m.win_score):>9} | "
            f"{_fmt(m.dist_at_1):>6} | {_fmt(m.p_at_k):>5} | "
            f"{_fmt(m.canonical_hit_rate):>9} | {_fmt(m.mean_authority):>5} | {rca} |"
        )
    lines.append("")

    # ── 5. Architecture-query and best-practice-query win rates ──────────
    arch_cats = {"architecture", "layer", "policy", "history"}
    bp_cats = {"standards", "retrieval", "multiagent"}
    tooling_cats = {"tooling"}

    def win_rate_for_cats(target_col: str, cat_set: set[str]) -> str:
        wins, total = 0, 0
        for qid in {m.query_id for m in all_metrics if m.cat in cat_set}:
            qm = {m.collection: m for m in all_metrics if m.query_id == qid}
            if qm:
                winner = max(qm, key=lambda c: qm[c].win_score)
                if winner == target_col:
                    wins += 1
                total += 1
        return f"{wins}/{total} ({100 * wins // total if total else 0}%)"

    lines.append("## 5. Win Rate Summary by Query Group\n")
    lines.append("| Group                  | repo_evidence | ext_raw | ext_authority |")
    lines.append("|------------------------|---------------|---------|---------------|")
    for label, cat_set in [
        ("Architecture/Policy/History", arch_cats),
        ("Best-practice/Standards/MA", bp_cats),
        ("Tooling/MCP queries", tooling_cats),
        ("All queries", set(m.cat for m in all_metrics)),
    ]:
        lines.append(
            f"| {label:<22} | {win_rate_for_cats('repo_evidence', cat_set):>13} | "
            f"{win_rate_for_cats('ext_raw', cat_set):>7} | "
            f"{win_rate_for_cats('ext_authority', cat_set):>13} |"
        )
    lines.append("")

    # ── 6. Phase 4 — arch_docs contamination gate (normative query classes) ─────
    lines.append("## 6. Wave B3 — repo_evidence Contamination Gate\n")
    lines.append(
        "**Normative classes**: `policy` · `tooling` · `standards`  \n"
        "**Pass condition**: repo_evidence chunk count = 0 for all normative queries in ext_authority  \n"
        "**Mechanism**: source_collection metadata field on each returned chunk (set at ingest time)\n"
    )
    lines.append("| QID       | Category  | repo_evidence chunks in ext_authority top-5 | Status   |")
    lines.append("|-----------|-----------|---------------------------------------------|----------|")

    total_contamination = 0
    normative_query_count = 0
    gate_failures: list[str] = []

    for qid in query_ids_sorted:
        cat_val = next((m.cat for m in all_metrics if m.query_id == qid), "?")
        if cat_val not in _NORMATIVE_CATS:
            continue
        normative_query_count += 1
        curated_m = next(
            (m for m in all_metrics if m.query_id == qid and m.collection == "ext_authority"),
            None,
        )
        contam = curated_m.arch_docs_contamination if curated_m else 0
        total_contamination += contam
        status = "PASS" if contam == 0 else f"**FAIL ({contam})**"
        if contam > 0:
            gate_failures.append(qid)
        lines.append(f"| {qid:<9} | {cat_val:<9} | {contam:>33} | {status:<8} |")

    lines.append("")
    lines.append(
        f"**Normative queries checked**: {normative_query_count} · "
        f"**repo_evidence chunks in ext_authority results**: {total_contamination}  "
    )
    if gate_failures:
        lines.append(f"\n**Gate verdict**: **FAIL** ✗ — contamination found in: {', '.join(gate_failures)}\n")
    else:
        lines.append(
            "\n**Gate verdict**: **PASS** ✓ — repo_contamination = 0 across all normative query classes\n"
        )
    lines.append("")

    # ── 7. v4 → v5 Regression Comparison (live-path runs only) ─────────────────
    if live_path:
        lines.append("## 7. v4 → v5 Regression Comparison\n")
        # v4 baseline (hardcoded from docs/reports/retrieval_eval_curated_v4.md)
        V4 = {
            "overall_wins": (38, 40),
            "arch_policy_history": (18, 20),
            "bp_standards_ma": (15, 15),
            "tooling": (5, 5),
            "canonical_hit_rate": 1.000,
            "tooling_contamination": 0.000,
        }

        def _wrate(target_col: str, cat_set: set[str]) -> tuple[int, int]:
            wins, total = 0, 0
            for q in {m.query_id for m in all_metrics if m.cat in cat_set}:
                qm = {m.collection: m for m in all_metrics if m.query_id == q}
                if qm:
                    if max(qm, key=lambda c: qm[c].win_score) == target_col:
                        wins += 1
                    total += 1
            return wins, total

        v5_all = _wrate("ext_authority", set(m.cat for m in all_metrics))
        v5_arch = _wrate("ext_authority", {"architecture", "policy", "history"})
        v5_bp = _wrate("ext_authority", {"standards", "retrieval", "multiagent"})
        v5_tool = _wrate("ext_authority", {"tooling"})
        curated_all = [m for m in all_metrics if m.collection == "ext_authority"]
        v5_canon = sum(m.canonical_hit_rate for m in curated_all) / len(curated_all) if curated_all else 0.0
        v5_contam = (
            sum(m.tooling_contamination for m in curated_all) / len(curated_all) if curated_all else 0.0
        )
        norm_contam_total = sum(m.arch_docs_contamination for m in curated_all if m.cat in _NORMATIVE_CATS)

        def _gate(v5_val: float, v4_val: float, lower_better: bool = False) -> str:
            return "PASS ✓" if (v5_val <= v4_val if lower_better else v5_val >= v4_val) else "FAIL ✗"

        def _wr_str(t: tuple[int, int]) -> str:
            return f"{t[0]}/{t[1]} ({100 * t[0] // t[1] if t[1] else 0}%)"

        lines.append("| Metric | v4 baseline | v5 result | Gate |")
        lines.append("|--------|-------------|-----------|------|")
        lines.append(
            f"| Overall win rate | {_wr_str(V4['overall_wins'])} | {_wr_str(v5_all)} | "
            f"{_gate(v5_all[0] / v5_all[1] if v5_all[1] else 0, V4['overall_wins'][0] / V4['overall_wins'][1])} |"
        )
        lines.append(
            f"| Arch/Policy/History wins | {_wr_str(V4['arch_policy_history'])} | {_wr_str(v5_arch)} | "
            f"{_gate(v5_arch[0] / v5_arch[1] if v5_arch[1] else 0, V4['arch_policy_history'][0] / V4['arch_policy_history'][1])} |"
        )
        lines.append(
            f"| Best-practice/Standards/MA | {_wr_str(V4['bp_standards_ma'])} | {_wr_str(v5_bp)} | "
            f"{_gate(v5_bp[0] / v5_bp[1] if v5_bp[1] else 0, V4['bp_standards_ma'][0] / V4['bp_standards_ma'][1])} |"
        )
        lines.append(
            f"| Tooling/MCP wins | {_wr_str(V4['tooling'])} | {_wr_str(v5_tool)} | "
            f"{_gate(v5_tool[0] / v5_tool[1] if v5_tool[1] else 0, V4['tooling'][0] / V4['tooling'][1])} |"
        )
        lines.append(
            f"| canonical_hit_rate | {_fmt(V4['canonical_hit_rate'])} | {_fmt(v5_canon)} | "
            f"{_gate(v5_canon, V4['canonical_hit_rate'])} |"
        )
        lines.append(
            f"| tooling_contamination | {_fmt(V4['tooling_contamination'])} | {_fmt(v5_contam)} | "
            f"{_gate(v5_contam, V4['tooling_contamination'], lower_better=True)} |"
        )
        lines.append(
            f"| repo_contamination (normative) | N/A (not tracked) | {norm_contam_total} | "
            f"{'PASS ✓' if norm_contam_total == 0 else 'FAIL ✗'} |"
        )
        lines.append("")

        # ── 8. Final verdict ───────────────────────────────────────────────────────
        lines.append("## 8. Final Verdict\n")
        regression_pass = (
            v5_all[0] / v5_all[1] >= 0.95
            and v5_canon >= 1.000 - 1e-6
            and v5_contam <= 1e-6
            and norm_contam_total == 0
        )
        if regression_pass:
            lines.append(
                "**PASS — Wave B3 eval complete.**  \n"
                "All four regression gates cleared: overall win rate ≥ 95%, "
                "canonical_hit_rate = 1.000, tooling_contamination = 0.000, "
                "repo_contamination = 0 for all normative query classes.  \n"
                "Authority enforcement is live and verified by the real eval harness.\n"
            )
        else:
            failing = []
            if v5_all[0] / v5_all[1] < 0.95:
                failing.append(f"overall win rate {_wr_str(v5_all)} < 95%")
            if v5_canon < 1.000 - 1e-6:
                failing.append(f"canonical_hit_rate {_fmt(v5_canon)} < 1.000")
            if v5_contam > 1e-6:
                failing.append(f"tooling_contamination {_fmt(v5_contam)} > 0")
            if norm_contam_total > 0:
                failing.append(f"repo_contamination {norm_contam_total} > 0")
            lines.append(f"**FAIL — Wave B3 eval blocked.**  \nFailing gates: {'; '.join(failing)}.\n")
        lines.append("")

    return "\n".join(lines)


def _worst_query_rca(m: QueryMetrics) -> str:
    if m.result_count == 0:
        return "collection empty or missing"
    if m.dist_at_1 > 0.8:
        return "no semantically similar docs in collection"
    if m.dist_at_1 > 0.6:
        return "vocabulary gap — query terms not in corpus"
    if m.tooling_contamination > 0.4:
        return "tooling docs polluting results"
    if m.redundancy_rate > 0.5:
        return "high duplicate rate — insufficient diversity"
    if m.answer_support < 0.3:
        return "text matches but lacks query-specific content"
    if m.arch_depth < 0.2 and m.cat in ("architecture", "layer", "policy"):
        return "arch docs under-represented for this query type"
    return "competitive — marginal loss"


# ─────────────────────────────────────────────────────────────────────────────
# Live-path simulation
# ─────────────────────────────────────────────────────────────────────────────


def _apply_live_path_postprocess(
    results: dict,
    k: int,
    authority_bonus: float = 0.15,
    collapse_max: int = 2,
) -> dict:
    """Simulate HybridSearchEngine live-path on oversampled ChromaDB results.

    Steps:
    1. Convert cosine distance to score (1 - dist), add authority_bonus * authority_level.
    2. Sort by boosted score descending.
    3. Apply collapse_group_dedup: keep at most collapse_max per collapse_group.
    4. Truncate to k, returning original distances for metric computation.
    """
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    n = min(len(docs), len(metas), len(dists))
    if n == 0:
        return results

    items: list[tuple[float, float, str, dict]] = []
    for i in range(n):
        dist = float(dists[i])
        meta = metas[i] if isinstance(metas[i], dict) else {}
        auth = float(meta.get("authority_level", 0.5))
        boosted = max(1e-9, 1.0 - dist) + authority_bonus * auth
        items.append((boosted, dist, docs[i], meta))

    items.sort(key=lambda x: x[0], reverse=True)

    group_counts: dict[str, int] = {}
    filtered: list[tuple[float, float, str, dict]] = []
    for item in items:
        group = str(item[3].get("collapse_group") or "_ungrouped")
        count = group_counts.get(group, 0)
        if group == "_ungrouped" or count < collapse_max:
            filtered.append(item)
            group_counts[group] = count + 1

    top_k = filtered[:k]
    return {
        "documents": [[item[2] for item in top_k]],
        "metadatas": [[item[3] for item in top_k]],
        "distances": [[item[1] for item in top_k]],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main runner
# ─────────────────────────────────────────────────────────────────────────────


def run_eval(k: int = 5, out_path: Path | None = None, live_path: bool = False) -> None:
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
    missing = [c for c in COLLECTIONS if c not in available]
    if missing:
        print(f"WARNING: collections not found: {missing}", flush=True)

    mode_label = " [live-path]" if live_path else ""
    k_fetch = k + 3 if live_path else k
    print(
        f"\nRunning {len(GOLDEN_QUERIES)} queries × {len(COLLECTIONS)} collections (K={k}{mode_label}) ...",
        flush=True,
    )

    all_metrics: list[QueryMetrics] = []
    t_start = time.time()

    for qi, qinfo in enumerate(GOLDEN_QUERIES, 1):
        qid = qinfo["id"]
        qtext = qinfo["text"]
        cat = qinfo["cat"]
        print(f"  [{qi:02d}/{len(GOLDEN_QUERIES)}] {qid}: {qtext[:55]}...", flush=True)

        emb = model.encode(qtext, normalize_embeddings=True, show_progress_bar=False).tolist()

        for cname in COLLECTIONS:
            if cname not in available:
                m = QueryMetrics(collection=cname, query_id=qid, cat=cat, result_count=0)
                all_metrics.append(m)
                continue
            col = client.get_collection(cname)
            try:
                raw = col.query(
                    query_embeddings=[emb],
                    n_results=k_fetch,
                    include=["documents", "metadatas", "distances"],
                )
            except Exception as exc:  # guardian: allow-broad — catch all Chroma errors gracefully
                print(f"    ERROR querying {cname}: {exc}", file=sys.stderr)
                all_metrics.append(QueryMetrics(collection=cname, query_id=qid, cat=cat, result_count=0))
                continue
            results = _apply_live_path_postprocess(raw, k) if live_path else raw
            m = compute_metrics(qtext, qid, cat, cname, results, k)
            all_metrics.append(m)

    elapsed = time.time() - t_start
    print(f"\nEval complete in {elapsed:.1f}s — generating report ...", flush=True)

    report = generate_report(all_metrics, k, elapsed, live_path=live_path)
    print("\n" + "=" * 80)
    print(report)

    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to {out_path}")

    # Emit raw metrics JSON alongside report
    raw_path = out_path.with_suffix(".json") if out_path else None
    if raw_path:
        raw = [
            {
                "collection": m.collection,
                "query_id": m.query_id,
                "cat": m.cat,
                "result_count": m.result_count,
                "dist_at_1": m.dist_at_1,
                "mean_dist_at_k": m.mean_dist_at_k,
                "canonical_hit_rate": m.canonical_hit_rate,
                "mean_authority": m.mean_authority,
                "arch_depth": m.arch_depth,
                "bp_relevance": m.bp_relevance,
                "answer_support": m.answer_support,
                "tooling_contamination": m.tooling_contamination,
                "arch_docs_contamination": m.arch_docs_contamination,
                "source_diversity": m.source_diversity,
                "redundancy_rate": m.redundancy_rate,
                "p_at_k": m.p_at_k,
                "mrr": m.mrr,
                "win_score": m.win_score,
            }
            for m in all_metrics
        ]
        raw_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        print(f"Raw JSON written to {raw_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrieval quality benchmark for ext_authority vs repo_evidence vs ext_raw"
    )
    parser.add_argument("--k", type=int, default=5, help="Top-K results per query (default: 5)")
    parser.add_argument("--out", type=Path, default=None, help="Write markdown report to this path")
    parser.add_argument(
        "--live-path",
        action="store_true",
        help="Simulate HybridSearchEngine live-path: oversample k+3, apply authority rerank "
        "and collapse_group_dedup(max=2) before computing metrics",
    )
    args = parser.parse_args()
    run_eval(k=args.k, out_path=args.out, live_path=args.live_path)


if __name__ == "__main__":
    main()
