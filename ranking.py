"""Ranking Utilities - Meta Layer

This module provides deterministic ranking and fusion functions.

Layer: Meta
Responsibilities:
- BM25 ranking
- Dense ranking
- Hybrid ranking
- RRF fusion
- Evidence normalization and deduplication
- Deterministic, side-effect-free operations

Non-responsibilities:
- LLM calls
- State mutation
- Retrieval execution
- Orchestration
"""

# FILE: ranking.py

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from core.models.models import Evidence, RetrievalConfig, RAGPlan, RAGResult, RankingEvent
from runtime.observability import emit_telemetry_event, emit_ranking_event

# =============================================================================
# 1. INTERNAL HELPERS (DICT-BASED SCORING)
# =============================================================================


def _bm25_score(item: Dict[str, Any]) -> float:
    """
    Simple, deterministic BM25-like score based on term frequencies.

    This is intentionally non-production but deterministic for testing:
        • Lowercase text.
        • Count "important" tokens.
        • Apply a fixed formula to derive a score.
    """
    text = str(item.get("text") or item.get("evidence") or "").lower()
    if not text:
        return 0.0

    tokens = text.split()
    length = len(tokens)
    bonus = 0.0

    # crude "importance" bonus for certain tokens
    important = {"llm", "resume", "experience", "impact", "owner", "lead"}
    for t in tokens:
        if t in important:
            bonus += 0.75

    # BM25-esque scoring: bonus / sqrt(length)
    base = bonus / (1.0 + (length / 50.0))
    return float(base)


def _dense_score(item: Dict[str, Any]) -> float:
    """
    Simple, deterministic dense-like score based on hash of text.

    This simulates a semantic scoring function in a reproducible way.
    """
    text = str(item.get("text") or item.get("evidence") or "").lower()
    if not text:
        return 0.0
    h = hash(text)
    # Map hash to [0, 1)
    return float((h % 10_000_000) / 10_000_000.0)


def _hybrid_score(item: Dict[str, Any]) -> float:
    """
    Combine BM25 and dense scores into a single hybrid score.
    """
    b = _bm25_score(item)
    d = _dense_score(item)
    return float((b + d) / 2.0)


# =============================================================================
# 2. PUBLIC DICT-BASED RANKING API
# =============================================================================


def bm25(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic BM25-style ranking."""
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


def rank_documents(
    items: List[Dict[str, Any]],
    *,
    strategy: str = "hybrid",
) -> List[Dict[str, Any]]:
    """
    Rank arbitrary documents using the requested strategy.
    """
    strat = (strategy or "hybrid").lower()
    if strat == "bm25":
        return bm25(items)
    if strat == "dense":
        return dense(items)
    return hybrid(items)


# =============================================================================
# 3. FUSION / RRF SUPPORT (DICT-BASED)
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
    if cfg is None or not getattr(cfg, "rrf_weights", None):
        return [1.0] * max(1, n_groups)

    raw = cfg.rrf_weights
    if not isinstance(raw, (list, tuple)):
        return [1.0] * max(1, n_groups)

    w_list: List[float] = []
    for w in raw:
        try:
            w_list.append(float(w))
        except Exception:
            continue

    if not w_list:
        return [1.0] * max(1, n_groups)

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
    from typing import Tuple

    if not groups:
        return []

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
            "ranking.rrf_fusion",
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


def fuse_ranked_groups_for_strategy(
    groups: List[List[Dict[str, Any]]],
    *,
    strategy: str = "hybrid",
    cfg: Optional[RetrievalConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience wrapper that applies the right ranking method to each group
    and then fuses them.

    Each group is expected to already contain a "rank" field. This function
    is retained mainly for backward compatibility and non-RAG call sites.
    """
    use_rrf = True
    return fuse_ranked_groups(groups, use_rrf=use_rrf, cfg=cfg)


# =============================================================================
# 5. EVIDENCE-LEVEL RANKING / FUSION (RAG)
# =============================================================================


def _canonical_evidence_key(ev: Evidence) -> Tuple[str, str]:
    """
    Canonical key for evidence deduplication.

    We attempt to use a (source, doc_id) pair if present in metadata; if not,
    we fall back to (source, text).
    """
    src = str(ev.source)
    doc_id = str(ev.metadata.get("doc_id", "") if ev.metadata else "")
    if doc_id:
        return (src, doc_id)
    return (src, ev.text)


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
        key = _canonical_evidence_key(ev)
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    return out


def rank_evidence(
    evidence: Sequence[Evidence],
    *,
    top_k: Optional[int] = None,
    normalize: bool = True,
    max_chars: int = 0,
    strategy: str = "hybrid",
) -> List[Evidence]:
    """
    Rank Evidence items using the dict-based ranking functions underneath.
    """
    if not evidence:
        return []

    # Convert to dicts, re-use dict-based rankers, then map back
    items: List[Dict[str, Any]] = []
    for ev in evidence:
        items.append(
            {
                "text": ev.text,
                "evidence": ev.text,
                "source": ev.source,
                "rank": 1,
                "score": ev.score,
            }
        )

    ranked_dicts = rank_documents(items, strategy=strategy)
    ranked: List[Evidence] = []
    for d in ranked_dicts:
        ranked.append(
            Evidence(
                id="",
                text=str(d.get("evidence", "")),
                score=float(d.get("score", 0.0)),
                source=str(d.get("source", "")),
                metadata={},
            )
        )

    if normalize:
        ranked = normalize_evidence_scores(ranked)

    if max_chars > 0:
        trimmed: List[Evidence] = []
        total_chars = 0
        for e in ranked:
            total_chars += len(e.text)
            if total_chars > max_chars:
                break
            trimmed.append(e)
        ranked = trimmed

    if top_k is not None and top_k > 0:
        ranked = ranked[:top_k]

    return ranked


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
            key = _canonical_evidence_key(ev)
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


def fuse_ranked_groups_rrf(
    groups: Sequence[Sequence[Evidence]],
    *,
    rrf_weights: Optional[List[float]] = None,
    workflow_id: Optional[str] = None,
    rrf_k: int = 60,
) -> List[Evidence]:
    """Wrapper used by retrieval.py for Evidence-level weighted RRF.

    This function adapts the raw `rrf_weights` list (coming from
    RetrievalConfig.rrf_weights) into a minimal RetrievalConfig instance
    and delegates to `fuse_evidence_groups_rrf`.

    It exists solely to preserve the existing retrieval.py call-site:

        ranking.fuse_ranked_groups_rrf(
            groups=groups,
            rrf_weights=retrieval_cfg.rrf_weights,
            workflow_id=workflow_id,
        )

    The `workflow_id` is accepted for signature compatibility but is
    not used here; telemetry is emitted inside `fuse_evidence_groups_rrf`.
    """
    cfg: Optional[RetrievalConfig] = None
    if rrf_weights is not None:
        cfg = RetrievalConfig()
        cfg.rrf_weights = list(rrf_weights)

    return fuse_evidence_groups_rrf(groups, cfg=cfg, rrf_k=rrf_k)


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
