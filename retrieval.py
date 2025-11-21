# FILE: retrieval.py
"""
Retrieval & Query Planning (v10_10 · Phase 3 Patch)
===================================================

Phase-3 responsibilities, consolidated and made consistent with the
Phase-0 models, Phase-2 prompt system, and the current L2/L3 wiring:

    • Plan retrieval strategy from RAGPlan + WorkflowConfig.
    • Score in-memory evidence chunks (BM25, dense-like, hybrid).
    • Provide a single entrypoint:

          run_rag_retrieval(
              rag_plan=...,
              job=...,
              resume=...,
              config=...,
              strategy_hint=...,
              sandbox=...,
              raw_hits=[{ "evidence": ..., "source": ... }, ...],
          ) -> List[Evidence]

    • Emit coarse observability events via observability.emit_telemetry_event.
    • Remain side-effect-free and deterministic (no external DB/vector calls).

Non-responsibilities:
    • No LLM calls (HYDE is intentionally omitted in this in-memory variant).
    • No DAG orchestration (L3 only).
    • No state mutation (L4 only).
    • No safety enforcement (L5 only).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from models import Evidence, RetrievalConfig, RAGPlan, WorkflowConfig
from observability import start_span, end_span, emit_telemetry_event
import ranking as _ranking


# =============================================================================
# INTERNAL HELPERS
# =============================================================================


def _build_query(job: Any, resume: Any) -> str:
    """
    Construct a simple retrieval query string from job + resume artifacts.

    This is intentionally conservative and deterministic; it does not
    call out to any LLM or external service.
    """
    parts: List[str] = []

    title = getattr(job, "title", None)
    posting = getattr(job, "posting_text", None)
    summary = getattr(resume, "summary", None)

    if title:
        parts.append(str(title))
    if posting:
        parts.append(str(posting))
    if summary:
        parts.append(str(summary))

    return " ".join(parts).strip()


def _attach_query(raw_hits: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Ensure each raw hit dict has the keys expected by the ranking module:

        • "query"
        • "evidence"
        • "source"
    """
    items: List[Dict[str, Any]] = []
    for h in raw_hits or []:
        evidence_text = str(h.get("evidence", ""))
        source = str(h.get("source", "unknown"))
        item = dict(h)
        item["query"] = query
        item["evidence"] = evidence_text
        item["source"] = source
        items.append(item)
    return items


def _plan_retrieval(
    rag_plan: RAGPlan,
    config: WorkflowConfig,
    strategy_hint: Optional[str] = None,
) -> RetrievalConfig:
    """
    Build a RetrievalConfig from RAGPlan + WorkflowConfig, plus an optional
    explicit strategy hint.

    Rules:
        • Strategy priority:
              1) explicit strategy_hint, if provided
              2) config.rag_require_hybrid → "hybrid"
              3) fallback "hybrid" (balanced default)
        • Max hits:
              - derived from job+resume chunk limits
              - clamped to a reasonable upper bound (50)
        • use_rrf:
              - enabled by default (Phase-3 requirement)
    """
    if strategy_hint:
        strategy = strategy_hint
    elif getattr(config, "rag_require_hybrid", False):
        strategy = "hybrid"
    else:
        strategy = "hybrid"

    max_hits = int(
        getattr(config, "rag_max_job_chunks", 8)
        + getattr(config, "rag_max_resume_chunks", 8)
        + getattr(config, "rag_max_hybrid_chunks", 12)
    )
    if max_hits <= 0:
        max_hits = 10
    max_hits = min(max_hits, 50)

    return RetrievalConfig(strategy=strategy, use_rrf=True, max_hits=max_hits)


def _dicts_to_evidence(items: List[Dict[str, Any]], top_k: int) -> List[Evidence]:
    """
    Convert ranked dict items from ranking.py into Evidence objects,
    respecting top_k.
    """
    if not items:
        return []

    out: List[Evidence] = []
    for it in items[:top_k]:
        text = str(it.get("evidence", ""))
        score = float(it.get("score", 0.0))
        source = str(it.get("source", "unknown"))
        meta = {
            k: v
            for k, v in it.items()
            if k not in {"query", "evidence", "score", "rank"}
        }
        out.append(Evidence(text=text, score=score, source=source, metadata=meta))
    return out


# =============================================================================
# PUBLIC ENTRYPOINT (used by L2)
# =============================================================================


def run_rag_retrieval(
    *,
    rag_plan: RAGPlan,
    job: Any,
    resume: Any,
    config: WorkflowConfig,
    strategy_hint: Optional[str] = None,
    sandbox: Any = None,  # reserved for future use
    raw_hits: List[Dict[str, Any]],
) -> List[Evidence]:
    """
    Deterministic in-memory retrieval + ranking.

    This is the only function called by L2._execute_retrieval(). It:

        1. Builds a query string from job+resume artifacts.
        2. Attaches that query to each raw hit dict.
        3. Plans retrieval strategy (bm25 / dense / hybrid) via RetrievalConfig.
        4. Applies the chosen ranking strategy using ranking.py.
        5. Emits coarse-grained telemetry.
        6. Returns a list[Evidence] sorted by descending score.
    """
    span = start_span("retrieval.run", ctx=None)
    try:
        query = _build_query(job, resume)
        items = _attach_query(raw_hits, query)
        cfg = _plan_retrieval(rag_plan, config, strategy_hint)

        emit_telemetry_event(
            "retrieval.plan",
            {
                "strategy": cfg.strategy,
                "use_rrf": cfg.use_rrf,
                "max_hits": cfg.max_hits,
                "raw_hits": len(items),
            },
        )

        # Strategy selection is delegated to ranking.apply_strategy()
        ranked = _ranking.rank_documents(items, strategy=cfg.strategy)

        emit_telemetry_event(
            "retrieval.rank",
            {
                "strategy": cfg.strategy,
                "items_in": len(items),
                "items_out": len(ranked),
            },
        )

        evidence = _dicts_to_evidence(ranked, top_k=cfg.max_hits)

        emit_telemetry_event(
            "retrieval.result",
            {
                "strategy": cfg.strategy,
                "evidence_count": len(evidence),
            },
        )
        return evidence
    finally:
        end_span(span)
