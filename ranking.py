# FILE: ranking.py
"""
Ranking Utilities (v10_10 · Phase 3 — FINAL)
============================================

Responsibilities:
    • Provide deterministic, side-effect-free ranking functions.
    • Dict-based API (backward-compatible):
          - bm25(items)
          - dense(items)
          - hybrid(items)
          - fuse_ranked_groups(groups, ...)
          - rank_documents(items, strategy=...)
    • Evidence-based API (for RAG):
          - normalize_evidence_scores(...)
          - deduplicate_evidence(...)
          - rank_evidence(...)
          - fuse_evidence_groups_rrf(...)
          - build_rag_result(...)

Phase-3 Enhancements:
    • Weighted Reciprocal Rank Fusion (RRF) driven by RetrievalConfig.rrf_weights
      when provided; falls back to uniform weights otherwise.
    • Emits typed RankingEvent telemetry for:
          - RRF fusion
          - Final evidence ranking

Non-Responsibilities:
    • No LLM calls.
    • No retrieval (see retrieval.py).
    • No orchestration (L3).
    • No state mutation (L4).
    • No safety decisions (L5).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from models import Evidence, RetrievalConfig, RAGPlan, RAGResult, RankingEvent
from observability import emit_telemetry_event, emit_ranking_event


# =============================================================================
# 1. INTERNAL HELPERS (DICT-BASED SCORING)
# =============================================================================


def _tokenize(text: str) -> List[str]:
    return [t for t in str(text).lower().split() if t.strip()]


def _bm25_score(item: Dict[str, Any]) -> float:
    """
    Simple BM25-like approximation for dict-based ranking.

    Expects:
        item["query"]:    str
        item["evidence"]: str
    """
    query = str(item.get("query", ""))
    evidence = str(item.get("evidence", ""))

    q_tokens = set(_tokenize(query))
    e_tokens = set(_tokenize(evidence))

    if not q_tokens or not e_tokens:
        return 0.0

    overlap = len(q_tokens & e_tokens)
    norm = max(1, len(q_tokens))
    return overlap / norm


def _dense_score(item: Dict[str, Any]) -> float:
    """
    Dense-score approximation using deterministic hash-based pseudo-similarity.

    This is a non-ML, purely deterministic heuristic.
    """
    query = str(item.get("query", ""))
    evidence = str(item.get("evidence", ""))

    q_hash = hash(query) & 0xFFFFFFFF
    e_hash = hash(evidence) & 0xFFFFFFFF

    diff = abs(q_hash - e_hash) / float(0xFFFFFFFF or 1)
    return max(0.0, 1.0 - diff)


def _hybrid_score(item: Dict[str, Any]) -> float:
    """Hybrid score = average of bm25-like and dense scores."""
    b = _bm25_score(item)
    d = _dense_score(item)
    return (b + d) / 2.0


# =============================================================================
# 2. STRATEGY ROUTING (DICT-BASED API)
# =============================================================================


def bm25(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    BM25-like ranking over dict items.

    Each item should contain:
        - "query":    str
        - "evidence": str
    """
    scored: List[Dict[str, Any]] = []
    for it in items or []:
        new_it = dict(it)
        new_it["score"] = _bm25_score(new_it)
        scored.append(new_it)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    for idx, it in enumerate(scored):
        it["rank"] = idx + 1
    return scored


def dense(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic dense-score ranking (hash-based pseudo-embedding)."""
    scored: List[Dict[str, Any]] = []
    for it in items or []:
        new_it = dict(it)
        new_it["score"] = _dense_score(new_it)
        scored.append(new_it)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    for idx, it in enumerate(scored):
        it["rank"] = idx + 1
    return scored


def hybrid(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Combined ranking (BM25 + dense), averaging the two scores."""
    scored: List[Dict[str, Any]] = []
    for it in items or []:
        new_it = dict(it)
        new_it["score"] = _hybrid_score(new_it)
        scored.append(new_it)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    for idx, it in enumerate(scored):
        it["rank"] = idx + 1
    return scored


def apply_strategy(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Apply a ranking strategy:

        strategy:
            "bm25"
            "dense"
            "hybrid"

    Returns a NEW list of dicts with "score" and "rank" populated.
    """
    if not items:
        return []

    strategy = (strategy or "hybrid").lower()

    if strategy == "bm25":
        return bm25(items)
    if strategy == "dense":
        return dense(items)
    # Default (and "hybrid"):
    return hybrid(items)


# =============================================================================
# 3. RRF-BASED FUSION (DICT-BASED)
# =============================================================================


def _rrf_weights_from_config(
    cfg: Optional[RetrievalConfig],
    n_groups: int,
) -> List[float]:
    """
    Compute weights for weighted RRF.

    Phase-3 requirement:
        "Weighted RRF (if config specifies)"

    Implementation:
        • If cfg.rrf_weights exists and is a sequence of floats, use it.
          - If shorter than n_groups, last weight is repeated.
          - If longer, excess weights are ignored.
        • Otherwise, fall back to uniform weights (=1.0).
    """
    if n_groups <= 0:
        return []
    if cfg is None:
        return [1.0] * n_groups

    weights = getattr(cfg, "rrf_weights", None)
    if not isinstance(weights, Iterable):
        return [1.0] * n_groups

    w_list = [float(w) for w in weights]  # type: ignore[arg-type]
    if not w_list:
        return [1.0] * n_groups

    if len(w_list) >= n_groups:
        return w_list[:n_groups]

    # Extend by repeating the last weight
    last = w_list[-1]
    return w_list + [last] * (n_groups - len(w_list))


def fuse_ranked_groups(
    groups: List[List[Dict[str, Any]]],
    *,
    use_rrf: bool = True,
    cfg: Optional[RetrievalConfig] = None,
    rrf_k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Fuse multiple pre-ranked lists into a single deterministic list.

    If use_rrf is True:
        • Apply weighted Reciprocal Rank Fusion:
              score(doc) = Σ_i w_i / (rrf_k + rank_i)
          where w_i are driven by RetrievalConfig.rrf_weights if provided.

    If use_rrf is False:
        • Fall back to minimal-rank fusion:
            1. Flatten.
            2. Deduplicate by (query, evidence).
            3. Sort by minimal rank across groups, then alphabetical evidence.
            4. Re-assign ranks.
    """
    if not groups:
        return []

    # ----- Non-RRF path (minimal rank) -----
    if not use_rrf:
        flattened: List[Dict[str, Any]] = []
        seen: set[Tuple[str, str]] = set()

        for group in groups or []:
            for item in group or []:
                key = (str(item.get("query", "")), str(item.get("evidence", "")))
                if key not in seen:
                    seen.add(key)
                    flattened.append(dict(item))

        flattened.sort(
            key=lambda x: (
                int(x.get("rank", 9_999_999)),
                str(x.get("evidence", "")).lower(),
            )
        )
        for idx, item in enumerate(flattened):
            item["rank"] = idx + 1

        emit_telemetry_event(
            "ranking.fuse.minrank",
            {
                "strategy": "min_rank",
                "groups": len(groups),
                "items_in": sum(len(g or []) for g in groups),
                "items_out": len(flattened),
            },
        )
        return flattened

    # ----- RRF path -----
    weights = _rrf_weights_from_config(cfg, len(groups))
    doc_scores: Dict[Tuple[str, str], float] = {}
    doc_repr: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for g_idx, group in enumerate(groups):
        w = weights[g_idx] if g_idx < len(weights) else 1.0
        for rank_idx, item in enumerate(group or []):
            key = (str(item.get("query", "")), str(item.get("evidence", "")))
            if key not in doc_repr:
                doc_repr[key] = dict(item)
            r = rank_idx + 1
            doc_scores[key] = doc_scores.get(key, 0.0) + (w / float(rrf_k + r))

    fused: List[Dict[str, Any]] = []
    for key, score in doc_scores.items():
        item = dict(doc_repr[key])
        item["score"] = score
        fused.append(item)

    fused.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    for idx, item in enumerate(fused):
        item["rank"] = idx + 1

    # Typed ranking event
    if cfg is not None:
        evt = RankingEvent(
            stage="rrf_fusion",
            strategy=cfg.strategy,
            use_rrf=True,
            metadata={
                "rrf_k": rrf_k,
                "groups": len(groups),
                "items_in": sum(len(g or []) for g in groups),
                "items_out": len(fused),
                "weights": weights,
            },
        )
        emit_ranking_event(evt)
    else:
        emit_telemetry_event(
            "ranking.rrf",
            {
                "rrf_k": rrf_k,
                "groups": len(groups),
                "items_in": sum(len(g or []) for g in groups),
                "items_out": len(fused),
                "weights": weights,
            },
        )

    return fused


# =============================================================================
# 4. HIGH-LEVEL DICT API (BACKWARD COMPATIBLE)
# =============================================================================


def rank_documents(
    items: List[Dict[str, Any]],
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Top-level ranking helper used by dict-based RAG components.

        items:
            list[{ query, evidence, ... }]

        strategy:
            "bm25" | "dense" | "hybrid"

    Returns ranked+sorted list with final deterministic ordering.
    """
    if not items:
        return []

    ranked = apply_strategy(items, strategy=strategy)

    ranked.sort(
        key=lambda x: (
            int(x.get("rank", 9_999_999)),
            str(x.get("evidence", "")).lower(),
        )
    )

    emit_telemetry_event(
        "ranking.dict.final",
        {
            "strategy": strategy,
            "items": len(ranked),
        },
    )
    return ranked


# =============================================================================
# 5. EVIDENCE-BASED RANKING (PRIMARY RAG PATH)
# =============================================================================


def _evidence_key(ev: Evidence) -> Tuple[str, str]:
    """
    Canonical deduplication key for Evidence.

    Prefer a stable document identifier from metadata if present; else
    fall back to (source, text).
    """
    meta = ev.metadata or {}
    doc_id = str(meta.get("document_id") or meta.get("id") or "")
    if doc_id:
        return (ev.source, doc_id)
    return (ev.source, ev.text)


def normalize_evidence_scores(evidence: Sequence[Evidence]) -> List[Evidence]:
    """Normalize scores across Evidence items to [0, 1]."""
    if not evidence:
        return []

    scores = [e.score for e in evidence]
    max_score = max(scores)
    min_score = min(scores)

    if max_score == min_score:
        return [e.model_copy(update={"score": 1.0}) for e in evidence]

    span = max_score - min_score
    out: List[Evidence] = []
    for e in evidence:
        norm = (e.score - min_score) / span
        out.append(e.model_copy(update={"score": float(norm)}))
    return out


def deduplicate_evidence(evidence: Sequence[Evidence]) -> List[Evidence]:
    """Deduplicate Evidence items by canonical key, preserving first."""
    seen: set[Tuple[str, str]] = set()
    out: List[Evidence] = []
    for ev in evidence or []:
        key = _evidence_key(ev)
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    return out


def _trim_evidence_text(ev: Evidence, max_chars: int) -> Evidence:
    if max_chars <= 0 or len(ev.text) <= max_chars:
        return ev
    trimmed = ev.text[: max_chars - 3] + "..."
    return ev.model_copy(update={"text": trimmed})


def rank_evidence(
    raw_hits: Sequence[Evidence],
    *,
    top_k: Optional[int] = None,
    normalize: bool = True,
    max_chars: int = 0,
    strategy: str = "hybrid",
) -> List[Evidence]:
    """
    Rank Evidence by score, with optional normalization, truncation, and trimming.

        • normalize: if True, rescale scores to [0, 1].
        • top_k: if provided, truncate to that many Evidence items.
        • max_chars: if > 0, trim evidence text to this many characters.
    """
    if not raw_hits:
        return []

    hits: List[Evidence] = list(raw_hits)

    if normalize:
        hits = normalize_evidence_scores(hits)

    hits = deduplicate_evidence(hits)
    hits.sort(key=lambda e: e.score, reverse=True)

    if top_k is not None and top_k > 0:
        hits = hits[:top_k]

    if max_chars > 0:
        hits = [_trim_evidence_text(ev, max_chars) for ev in hits]

    # Emit typed ranking event
    evt = RankingEvent(
        stage="evidence_final",
        strategy=strategy,
        use_rrf=False,
        metadata={
            "items_out": len(hits),
            "top_k": top_k,
            "max_chars": max_chars,
        },
    )
    emit_ranking_event(evt)

    return hits


def fuse_evidence_groups_rrf(
    groups: Sequence[Sequence[Evidence]],
    *,
    cfg: Optional[RetrievalConfig] = None,
    rrf_k: int = 60,
) -> List[Evidence]:
    """
    Evidence-level Reciprocal Rank Fusion.

        score(ev) = Σ_i w_i / (rrf_k + rank_i)
    """
    if not groups:
        return []

    weights = _rrf_weights_from_config(cfg, len(groups))
    scores: Dict[Tuple[str, str], float] = {}
    reprs: Dict[Tuple[str, str], Evidence] = {}

    for g_idx, group in enumerate(groups):
        w = weights[g_idx] if g_idx < len(weights) else 1.0
        for rank_idx, ev in enumerate(group or []):
            key = _evidence_key(ev)
            if key not in reprs:
                reprs[key] = ev
            r = rank_idx + 1
            scores[key] = scores.get(key, 0.0) + (w / float(rrf_k + r))

    fused: List[Evidence] = []
    for key, score in scores.items():
        ev = reprs[key]
        fused.append(ev.model_copy(update={"score": float(score)}))

    fused.sort(key=lambda e: e.score, reverse=True)

    evt = RankingEvent(
        stage="evidence_rrf",
        strategy=cfg.strategy if cfg is not None else "unknown",
        use_rrf=True,
        metadata={
            "rrf_k": rrf_k,
            "groups": len(groups),
            "items_in": sum(len(g or []) for g in groups),
            "items_out": len(fused),
            "weights": weights,
        },
    )
    emit_ranking_event(evt)

    return fused


def build_rag_result(
    groups: Sequence[Sequence[Evidence]],
    *,
    cfg: Optional[RetrievalConfig] = None,
    rag_plan: Optional[RAGPlan] = None,
    top_k: Optional[int] = None,
    max_chars: int = 0,
    used_hyde: bool = False,
) -> RAGResult:
    """
    High-level helper to fuse and rank Evidence sets and produce a RAGResult.

    If cfg.use_rrf is True:
        • Apply evidence-level RRF across groups, then truncate/trim.
    Otherwise:
        • Concatenate groups, deduplicate, rank by score, truncate/trim.
    """
    cfg = cfg or RetrievalConfig()

    if cfg.use_rrf:
        flat = fuse_evidence_groups_rrf(groups, cfg=cfg)
    else:
        all_hits: List[Evidence] = []
        for g in groups or []:
            all_hits.extend(list(g or []))
        flat = deduplicate_evidence(all_hits)

        emit_telemetry_event(
            "ranking.evidence.simple_fuse",
            {
                "strategy": cfg.strategy,
                "groups": len(groups),
                "items_in": len(all_hits),
                "items_out": len(flat),
            },
        )

    ranked = rank_evidence(
        flat,
        top_k=top_k or cfg.max_hits,
        normalize=True,
        max_chars=max_chars,
        strategy=cfg.strategy,
    )

    evt = RankingEvent(
        stage="rag_result",
        strategy=cfg.strategy,
        use_rrf=cfg.use_rrf,
        metadata={
            "items_out": len(ranked),
            "used_hyde": used_hyde,
        },
    )
    emit_ranking_event(evt)

    return RAGResult(evidence=ranked, used_hyde=used_hyde)
