# FILE: retrieval.py
"""
Retrieval & Query Planning (v10_10 · Phase 3 — FINAL COMPLETE VERSION)
======================================================================

Implements ALL Phase-3 requirements:

A. Retrieval:
   • BM25 scoring
   • Dense scoring
   • Hybrid scoring
   • HYDE query-expansion hook (placeholder, deterministic)
   • Retriever-level failure-mode fallback (per-retriever isolation)

B. Ranking (multi-retriever):
   • BM25 ranked group
   • Dense ranked group
   • Hybrid ranked group
   • HYDE ranked group (if enabled)
   • Fully weighted Reciprocal Rank Fusion (RRF)

C. Evidence Fusion:
   • Deduplication
   • Score normalization
   • Context-budget–aware snippet trimming

D. Output:
   • Returns List[Evidence] (L2 contract)

E. Telemetry:
   • RetrievalAttemptEvent
   • RetrievalSuccessEvent
   • RetrievalFailureEvent
   • Spans:
        – retrieval.run
        – bm25_retrieval
        – dense_retrieval
        – hybrid_retrieval
        – hyde_retrieval
        – ranking_rrf
   • Ranking events emitted indirectly via ranking.fuse_ranked_groups
   • Group-level failure telemetry for per-retriever failures

F. Layer purity:
   • No LLM calls
   • No state mutation
   • Called only from L2._execute_retrieval()

G. Multi-agent hooks:
   • HYDE hook is surfaced but deterministic (no LLM calls yet).
   • Router and QA-council evidence weighting hooks (identity pass-throughs).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from models import (
    Evidence,
    RetrievalConfig,
    RAGPlan,
    WorkflowConfig,
    RetrievalAttemptEvent,
    RetrievalSuccessEvent,
    RetrievalFailureEvent,
)
from observability import (
    start_span,
    end_span,
    emit_telemetry_event,
    emit_retrieval_attempt,
    emit_retrieval_success,
    emit_retrieval_failure,
)
import ranking as _ranking


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _build_base_query(job: Any, resume: Any) -> str:
    """Combine job title/posting and resume summary deterministically."""
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
    HYDE hook (Phase-3 placeholder).
    No LLM call is allowed here.
    """
    return query  # deterministic placeholder


def _attach_query(raw_hits: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Attach query to raw evidence items; ensure evidence text and source exist."""
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
    Build RetrievalConfig from RAGPlan + WorkflowConfig.

    Strategy precedence:
        1) explicit strategy_hint
        2) config.rag_require_hybrid or rag_plan.require_hybrid → "hybrid"
        3) else default "bm25"

    HYDE enablement:
        • config.rag_allow_hyde OR rag_plan.allow_hyde

    Max hits:
        • rag_max_job_chunks + rag_max_resume_chunks + rag_max_hybrid_chunks
        • clamped [1, 50]
    """
    if strategy_hint:
        strategy = strategy_hint
    elif getattr(config, "rag_require_hybrid", False) or getattr(rag_plan, "require_hybrid", False):
        strategy = "hybrid"
    else:
        strategy = "bm25"

    allow_hyde = bool(
        getattr(config, "rag_allow_hyde", False)
        or getattr(rag_plan, "allow_hyde", False)
    )

    max_hits = (
        getattr(config, "rag_max_job_chunks", 8)
        + getattr(config, "rag_max_resume_chunks", 8)
        + getattr(config, "rag_max_hybrid_chunks", 12)
    )
    max_hits = max(1, min(50, int(max_hits)))

    cfg = RetrievalConfig(
        strategy=strategy,
        use_rrf=True,
        max_hits=max_hits,
        bm25_k1=1.2,
        bm25_b=0.75,
        rrf_weights=None,  # uniform unless set by ExecutionProfile
    )
    # Attach non-schema flag for HYDE enablement (Phase-3 behavior).
    cfg._allow_hyde = allow_hyde  # type: ignore[attr-defined]

    emit_telemetry_event(
        "retrieval.plan",
        {"strategy": strategy, "allow_hyde": allow_hyde, "max_hits": max_hits},
    )
    return cfg


def _max_chars_per_snippet(cfg: RetrievalConfig, config: WorkflowConfig) -> int:
    """
    Derive snippet trimming budget from WorkflowConfig.target_total_tokens.
    """
    target_tokens = int(getattr(config, "target_total_tokens", 1800))
    total_chars = target_tokens * 4
    return max(256, total_chars // max(cfg.max_hits, 1))


def _dicts_to_evidence(
    items: List[Dict[str, Any]],
    max_k: int,
    max_chars: int,
) -> List[Evidence]:
    """Convert dict ranking outputs → Evidence with snippet trimming."""
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
                metadata={k: v for k, v in it.items() if k not in {"query", "evidence", "score", "rank"}},
            )
        )
    return out


# ---------------------------------------------------------------------------
# MULTI-AGENT WEIGHTING HOOKS (PLACEHOLDERS · IDENTITY)
# ---------------------------------------------------------------------------

def apply_router_weights(
    evidence: List[Evidence],
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Evidence]:
    """
    Placeholder for multi-agent router evidence weighting.

    Phase-3 requirement:
        • This function must exist as a hook surface.
        • It must currently behave as an identity function (no-op).

    Args:
        evidence: Ranked evidence list.
        metadata: Optional context (strategy, HYDE, RAGPlan identifiers, etc.).

    Returns:
        The input evidence list unchanged.
    """
    return evidence


def apply_qa_council_weights(
    evidence: List[Evidence],
) -> List[Evidence]:
    """
    Placeholder for QA council evidence weighting.

    Phase-3 requirement:
        • This function must exist as a hook surface.
        • It must currently behave as an identity function (no-op).

    Args:
        evidence: Evidence list post-router weighting.

    Returns:
        The input evidence list unchanged.
    """
    return evidence


# ---------------------------------------------------------------------------
# PUBLIC ENTRYPOINT (USED BY L2)
# ---------------------------------------------------------------------------

def run_rag_retrieval(
    *,
    rag_plan: RAGPlan,
    job: Any,
    resume: Any,
    config: WorkflowConfig,
    strategy_hint: Optional[str] = None,
    sandbox: Any = None,
    raw_hits: List[Dict[str, Any]],
) -> List[Evidence]:
    """
    END-TO-END Phase-3 retrieval pipeline executed by L2:

        1. Build base + HYDE query
        2. Build BM25 / dense / hybrid / HYDE groups (each in spans)
        3. Per-group failure isolation with fallback across retrievers
        4. Weighted RRF fusion across successful groups
        5. Convert fused groups → Evidence
        6. Apply multi-agent weighting hooks (router + QA council)
        7. Emit typed retrieval events
        8. Return List[Evidence]
    """
    span = start_span("retrieval.run", ctx=None)
    base_query = _build_base_query(job, resume)
    cfg = _plan_retrieval(rag_plan, config, strategy_hint)
    allow_hyde = bool(getattr(cfg, "_allow_hyde", False))

    # ----------------------------------------------------------
    # Emit Attempt Event
    # ----------------------------------------------------------
    attempt_evt = RetrievalAttemptEvent(
        name="retrieval",
        ts_ms=int(time.time() * 1000),
        attributes={"strategy": cfg.strategy, "allow_hyde": allow_hyde},
        method=cfg.strategy,
        query=base_query,
    )
    emit_retrieval_attempt(attempt_evt)

    try:
        # ----------------------------------------------------------
        # Prepare queries
        # ----------------------------------------------------------
        hyde_query = _hyde_expand_query(base_query, rag_plan, config) if allow_hyde else base_query

        base_items = _attach_query(raw_hits, base_query)
        hyde_items = _attach_query(raw_hits, hyde_query) if allow_hyde else []

        if not base_items:
            # No corpus to search at all → hard failure.
            failure_evt = RetrievalFailureEvent(
                name="retrieval",
                ts_ms=int(time.time() * 1000),
                attributes={"strategy": cfg.strategy, "reason": "empty_corpus"},
                method=cfg.strategy,
                query=base_query,
                error="empty_corpus",
            )
            emit_retrieval_failure(failure_evt)
            return []

        # ----------------------------------------------------------
        # BUILD RETRIEVAL GROUPS (WITH SPANS + FAILURE ISOLATION)
        # ----------------------------------------------------------
        groups: List[List[Dict[str, Any]]] = []
        group_failures: Dict[str, str] = {}

        # BM25
        bm25_span = start_span("bm25_retrieval", ctx=None)
        try:
            bm25_group = _ranking.bm25(base_items)
            for it in bm25_group:
                it["source"] += "|bm25"
            groups.append(bm25_group)
        except Exception as exc:  # noqa: BLE001
            group_failures["bm25"] = str(exc)
            emit_telemetry_event(
                "retrieval.group_failure",
                {"group": "bm25", "strategy": cfg.strategy, "error": str(exc)},
            )
        finally:
            end_span(bm25_span)

        # Dense
        dense_span = start_span("dense_retrieval", ctx=None)
        try:
            dense_group = _ranking.dense(base_items)
            for it in dense_group:
                it["source"] += "|dense"
            groups.append(dense_group)
        except Exception as exc:  # noqa: BLE001
            group_failures["dense"] = str(exc)
            emit_telemetry_event(
                "retrieval.group_failure",
                {"group": "dense", "strategy": cfg.strategy, "error": str(exc)},
            )
        finally:
            end_span(dense_span)

        # Hybrid (only when requested)
        if cfg.strategy == "hybrid":
            hybrid_span = start_span("hybrid_retrieval", ctx=None)
            try:
                hybrid_group = _ranking.hybrid(base_items)
                for it in hybrid_group:
                    it["source"] += "|hybrid"
                groups.append(hybrid_group)
            except Exception as exc:  # noqa: BLE001
                group_failures["hybrid"] = str(exc)
                emit_telemetry_event(
                    "retrieval.group_failure",
                    {"group": "hybrid", "strategy": cfg.strategy, "error": str(exc)},
                )
            finally:
                end_span(hybrid_span)

        # HYDE extra path (optional)
        if allow_hyde and hyde_items:
            hyde_span = start_span("hyde_retrieval", ctx=None)
            try:
                hyde_group = _ranking.dense(hyde_items)
                for it in hyde_group:
                    it["source"] += "|hyde"
                groups.append(hyde_group)
            except Exception as exc:  # noqa: BLE001
                group_failures["hyde"] = str(exc)
                emit_telemetry_event(
                    "retrieval.group_failure",
                    {"group": "hyde", "strategy": cfg.strategy, "error": str(exc)},
                )
            finally:
                end_span(hyde_span)

        emit_telemetry_event(
            "retrieval.groups",
            {
                "strategy": cfg.strategy,
                "allow_hyde": allow_hyde,
                "num_groups": len(groups),
                "group_sizes": [len(g) for g in groups],
                "group_failures": group_failures,
            },
        )

        # If *all* retrievers failed (no successful groups), emit failure and bail.
        if not groups:
            failure_evt = RetrievalFailureEvent(
                name="retrieval",
                ts_ms=int(time.time() * 1000),
                attributes={
                    "strategy": cfg.strategy,
                    "reason": "all_retrievers_failed",
                    "group_failures": group_failures,
                },
                method=cfg.strategy,
                query=base_query,
                error="all_retrievers_failed",
            )
            emit_retrieval_failure(failure_evt)
            return []

        # ----------------------------------------------------------
        # RRF FUSION
        # ----------------------------------------------------------
        rrf_span = start_span("ranking_rrf", ctx=None)
        try:
            fused = _ranking.fuse_ranked_groups(
                groups,
                use_rrf=cfg.use_rrf,
                cfg=cfg,
                rrf_k=60,
            )
        finally:
            end_span(rrf_span)

        max_chars = _max_chars_per_snippet(cfg, config)
        evidence = _dicts_to_evidence(fused, cfg.max_hits, max_chars)

        # ----------------------------------------------------------
        # MULTI-AGENT WEIGHTING HOOKS (IDENTITY FOR PHASE 3)
        # ----------------------------------------------------------
        router_metadata: Dict[str, Any] = {
            "strategy": cfg.strategy,
            "allow_hyde": allow_hyde,
            "group_failures": group_failures,
            "rag_plan_id": getattr(rag_plan, "plan_id", None),
        }
        evidence = apply_router_weights(evidence, router_metadata)
        evidence = apply_qa_council_weights(evidence)

        emit_telemetry_event(
            "retrieval.result",
            {
                "strategy": cfg.strategy,
                "allow_hyde": allow_hyde,
                "evidence_count": len(evidence),
                "max_chars": max_chars,
            },
        )

        # ----------------------------------------------------------
        # SUCCESS EVENT
        # ----------------------------------------------------------
        success_evt = RetrievalSuccessEvent(
            name="retrieval",
            ts_ms=int(time.time() * 1000),
            attributes={
                "strategy": cfg.strategy,
                "allow_hyde": allow_hyde,
                "evidence_count": len(evidence),
            },
            method=cfg.strategy,
            query=base_query,
            count=len(evidence),
        )
        emit_retrieval_success(success_evt)

        return evidence

    except Exception as exc:  # noqa: BLE001
        # ----------------------------------------------------------
        # FAILURE EVENT (UNEXPECTED ERROR PATH)
        # ----------------------------------------------------------
        failure_evt = RetrievalFailureEvent(
            name="retrieval",
            ts_ms=int(time.time() * 1000),
            attributes={"strategy": cfg.strategy, "error": str(exc)},
            method=cfg.strategy,
            query=base_query,
            error=str(exc),
        )
        emit_retrieval_failure(failure_evt)
        return []

    finally:
        end_span(span)
