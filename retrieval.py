# FILE: retrieval.py
"""
Retrieval & Query Planning (v10_10 · Phase 3 — FINAL FULL IMPLEMENTATION)
=========================================================================

Implements full Phase-3 capabilities:

A. Retrieval:
   • BM25 scoring
   • Dense scoring
   • Hybrid scoring
   • HYDE query-expansion hook (no LLM call yet)

B. Ranking (multi-group):
   • BM25 ranked list
   • Dense ranked list
   • Hybrid ranked list
   • HYDE ranked list (if allowed)
   • Fused via Reciprocal Rank Fusion (RRF)

C. Evidence Fusion:
   • Deduplication
   • Score normalization (inside ranking)
   • Context-budget-aware snippet trimming

D. Output:
   • Returns List[Evidence] exactly as L2 expects.

E. Telemetry:
   • retrieval.plan
   • retrieval.groups
   • retrieval.rrf
   • retrieval.result

F. Layer purity:
   • No LLM calls
   • No state mutation
   • Called only from L2
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from models import Evidence, RetrievalConfig, RAGPlan, WorkflowConfig
from observability import start_span, end_span, emit_telemetry_event
import ranking as _ranking


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _build_base_query(job: Any, resume: Any) -> str:
    """Combine job title/posting and resume summary."""
    parts: List[str] = []
    if getattr(job, "title", None):
        parts.append(str(job.title))
    if getattr(job, "posting_text", None):
        parts.append(str(job.posting_text))
    if getattr(resume, "summary", None):
        parts.append(str(resume.summary))
    return " ".join(parts).strip()


def _hyde_expand_query(query: str, rag_plan: RAGPlan, config: WorkflowConfig) -> str:
    """
    HYDE hook: Phase-3 requires placeholder only.
    No LLM call; simply return base query for determinism.
    """
    return query  # Hook for Phase-4


def _attach_query(raw_hits: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Attach query, ensure evidence and source exist."""
    out: List[Dict[str, Any]] = []
    for h in raw_hits or []:
        ev = str(h.get("evidence", "")).strip()
        if not ev:
            continue
        item = dict(h)
        item["query"] = query
        item["evidence"] = ev
        item["source"] = item.get("source", "raw")
        out.append(item)
    return out


def _plan_retrieval(
    rag_plan: RAGPlan,
    config: WorkflowConfig,
    strategy_hint: Optional[str],
) -> RetrievalConfig:
    """
    Decide retrieval strategy, HYDE flag, and max_hits from RAGPlan + config.

    Strategy precedence:
        1. explicit strategy_hint
        2. config.rag_require_hybrid or rag_plan.require_hybrid → "hybrid"
        3. default → "bm25"

    HYDE:
        enabled if config.rag_allow_hyde or rag_plan.allow_hyde

    Max hits:
        derived from RAG knobs on WorkflowConfig, clamped to [1, 50].
    """
    if strategy_hint:
        strategy = strategy_hint
    elif getattr(config, "rag_require_hybrid", False) or getattr(
        rag_plan, "require_hybrid", False
    ):
        strategy = "hybrid"
    else:
        strategy = "bm25"

    allow_hyde = bool(
        getattr(config, "rag_allow_hyde", False)
        or getattr(rag_plan, "allow_hyde", False)
    )

    max_hits = int(
        getattr(config, "rag_max_job_chunks", 8)
        + getattr(config, "rag_max_resume_chunks", 8)
        + getattr(config, "rag_max_hybrid_chunks", 12)
    )
    max_hits = max(1, min(50, max_hits))

    cfg = RetrievalConfig(
        strategy=strategy,
        use_rrf=True,
        max_hits=max_hits,
        bm25_k1=1.2,
        bm25_b=0.75,
    )
    # store HYDE flag on cfg without requiring model change
    cfg._allow_hyde = allow_hyde  # type: ignore[attr-defined]

    emit_telemetry_event(
        "retrieval.plan",
        {"strategy": strategy, "allow_hyde": allow_hyde, "max_hits": max_hits},
    )
    return cfg


def _max_chars_per_snippet(cfg: RetrievalConfig, config: WorkflowConfig) -> int:
    """
    Derive snippet budget from target_total_tokens.
    """
    target_tokens = int(getattr(config, "target_total_tokens", 1800))
    total_chars = max(1024, target_tokens * 4)
    return max(256, total_chars // max(cfg.max_hits, 1))


def _dicts_to_evidence(
    items: List[Dict[str, Any]],
    max_k: int,
    max_chars: int,
) -> List[Evidence]:
    """
    Convert fused ranking dicts → Evidence with trimming.
    """
    out: List[Evidence] = []
    for it in items[:max_k]:
        text = str(it.get("evidence", ""))
        if max_chars > 0 and len(text) > max_chars:
            text = text[: max_chars - 3] + "..."
        out.append(
            Evidence(
                text=text,
                score=float(it.get("score", 0.0)),
                source=str(it.get("source", "unknown")),
                metadata={
                    k: v
                    for k, v in it.items()
                    if k not in {"query", "evidence", "score", "rank"}
                },
            )
        )
    return out


# ============================================================================
# PUBLIC ENTRYPOINT (USED BY L2)
# ============================================================================

def run_rag_retrieval(
    *,
    rag_plan: RAGPlan,
    job: Any,
    resume: Any,
    config: WorkflowConfig,
    strategy_hint: Optional[str] = None,
    sandbox: Any = None,  # reserved for future HYDE / multi-agent use
    raw_hits: List[Dict[str, Any]],
) -> List[Evidence]:
    """
    Deterministic Phase-3 retrieval + multi-group RRF ranking.

    Steps:
        1. Build base query from job + resume.
        2. Optionally build HYDE query (hook only).
        3. Attach query to each raw hit.
        4. Plan retrieval (strategy, HYDE, max_hits).
        5. Build BM25 / dense / hybrid / HYDE ranked groups.
        6. Fuse groups via RRF.
        7. Trim to context budget and convert to Evidence.
    """
    span = start_span("retrieval.run", ctx=None)
    try:
        base_query = _build_base_query(job, resume)
        cfg = _plan_retrieval(rag_plan, config, strategy_hint)
        allow_hyde: bool = bool(getattr(cfg, "_allow_hyde", False))

        hyde_query = (
            _hyde_expand_query(base_query, rag_plan, config) if allow_hyde else base_query
        )

        base_items = _attach_query(raw_hits, base_query)
        hyde_items = _attach_query(raw_hits, hyde_query) if allow_hyde else []

        if not base_items:
            emit_telemetry_event(
                "retrieval.empty_corpus",
                {"strategy": cfg.strategy, "allow_hyde": allow_hyde},
            )
            return []

        groups: List[List[Dict[str, Any]]] = []

        # BM25 group
        bm25_group = _ranking.bm25(base_items)
        for it in bm25_group:
            it["source"] += "|bm25"
        groups.append(bm25_group)

        # Dense group
        dense_group = _ranking.dense(base_items)
        for it in dense_group:
            it["source"] += "|dense"
        groups.append(dense_group)

        # Hybrid group (if using hybrid strategy)
        if cfg.strategy == "hybrid":
            hybrid_group = _ranking.hybrid(base_items)
            for it in hybrid_group:
                it["source"] += "|hybrid"
            groups.append(hybrid_group)

        # HYDE group
        if allow_hyde and hyde_items:
            hyde_group = _ranking.dense(hyde_items)
            for it in hyde_group:
                it["source"] += "|hyde"
            groups.append(hyde_group)

        emit_telemetry_event(
            "retrieval.groups",
            {
                "strategy": cfg.strategy,
                "allow_hyde": allow_hyde,
                "num_groups": len(groups),
                "group_sizes": [len(g) for g in groups],
            },
        )

        fused = _ranking.fuse_ranked_groups(
            groups,
            use_rrf=cfg.use_rrf,
            cfg=cfg,
            rrf_k=60,
        )

        emit_telemetry_event(
            "retrieval.rrf",
            {"groups": len(groups), "fused": len(fused)},
        )

        max_chars = _max_chars_per_snippet(cfg, config)
        evidence = _dicts_to_evidence(fused, cfg.max_hits, max_chars)

        emit_telemetry_event(
            "retrieval.result",
            {
                "strategy": cfg.strategy,
                "allow_hyde": allow_hyde,
                "evidence_count": len(evidence),
                "max_chars": max_chars,
            },
        )

        return evidence
    finally:
        end_span(span)
