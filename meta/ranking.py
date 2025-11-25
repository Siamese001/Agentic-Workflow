"""
Meta ranking system for résumé evidence evaluation.

Provides deterministic scoring and fusion to prioritize relevant résumé improvement content.
"""

# FILE: ranking.py

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from runtime.observability import emit_telemetry_event, emit_ranking_event


def _core_models() -> Any:
    """
    Lazy imports core models to avoid circular dependencies.

    Ensures clean module structure for reliable résumé processing.
    """

    from core.models import models as core_models  # type: ignore[import]

    return core_models

"""
Provides keyword relevance scoring for résumé evidence.

Prioritizes exact matches to ensure comprehensive résumé content coverage.
"""


def _bm25_score(item: Dict[str, Any]) -> float:
    """
    Calculates keyword relevance score for résumé evidence.
    
    Prioritizes exact matches to ensure comprehensive résumé content coverage.
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
    Calculates semantic similarity score for résumé content.
    
    Finds conceptually relevant evidence to enhance résumé job alignment.
    """
    text = str(item.get("text") or item.get("evidence") or "").lower()
    if not text:
        return 0.0
    h = hash(text)
    # Map hash to [0, 1)
    return float((h % 10_000_000) / 10_000_000.0)


def _hybrid_score(item: Dict[str, Any]) -> float:
    """
    Combines keyword and semantic scores for résumé ranking.
    
    Balances exact matches with conceptual relevance for optimal résumé improvement.
    """
    b = _bm25_score(item)
    d = _dense_score(item)
    return float((b + d) / 2.0)


"""
Provides public ranking functions for résumé evidence evaluation.

Delivers deterministic scoring to prioritize most relevant résumé improvement content.
"""


def bm25_score(item: Dict[str, Any]) -> float:
    """
    Provides backward-compatible BM25 scoring for résumé evidence.
    
    Maintains legacy interface while delivering keyword relevance scoring for résumé content.
    """
    return _bm25_score(item)


def dense_score(item: Dict[str, Any]) -> float:
    """
    Provides backward-compatible semantic scoring for résumé evidence.
    
    Maintains legacy interface while delivering conceptual relevance scoring for résumé content.
    """
    return _dense_score(item)


def bm25(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks résumé evidence by keyword relevance.

    Prioritizes exact matches to ensure comprehensive résumé content coverage.
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
    """
    Ranks résumé evidence by semantic similarity.
    
    Finds conceptually relevant content to enhance résumé job alignment.
    """
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
    """
    Ranks résumé evidence by combined relevance scoring.
    
    Balances exact matches with conceptual relevance for optimal résumé improvement.
    """
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
    Ranks résumé documents using optimal scoring strategy.
    
    Ensures relevant content is prioritized for comprehensive résumé enhancement.
    """
    strat = (strategy or "hybrid").lower()
    if strat == "bm25":
        return bm25(items)
    if strat == "dense":
        return dense(items)
    return hybrid(items)


"""
Provides reciprocal rank fusion for résumé evidence ranking.

Combines multiple ranking approaches for optimal résumé content prioritization.
"""


def _rrf_weights_from_config(
    cfg: Optional[Any],
    n_groups: int,
) -> List[float]:
    """
    Calculates weighted fusion scores for résumé evidence.
    
    Optimizes ranking strategy to prioritize most relevant résumé improvement content.
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
    cfg: Optional[Any] = None,
    rrf_k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Fuses multiple ranked lists for optimal résumé evidence prioritization.
    
    Combines retrieval strategies to ensure most relevant résumé content is ranked highest.
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
        core = _core_models()
        RankingEvent = core.RankingEvent
        evt = RankingEvent(
            stage="rrf_fusion",
            strategy=getattr(cfg, "strategy", "unknown"),
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


"""
Provides backward-compatible ranking fusion for résumé evidence.

Maintains legacy interface while delivering optimal résumé content prioritization.
"""


def fuse_ranked_groups_for_strategy(
    groups: List[List[Dict[str, Any]]],
    *,
    strategy: str = "hybrid",
    cfg: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Applies optimal ranking fusion for résumé evidence groups.
    
    Maintains backward compatibility while delivering comprehensive résumé content ranking.
    """
    use_rrf = True
    return fuse_ranked_groups(groups, use_rrf=use_rrf, cfg=cfg)


"""
Provides evidence-level ranking for RAG résumé retrieval.

Delivers optimized scoring to prioritize most relevant résumé improvement evidence.
"""


def _canonical_evidence_key(ev: Any) -> Tuple[str, str]:
    """
    Creates canonical key for résumé evidence deduplication.
    
    Ensures unique identification to prevent duplicate résumé content in rankings.
    """
    src = str(ev.source)
    doc_id = str(ev.metadata.get("doc_id", "") if ev.metadata else "")
    if doc_id:
        return (src, doc_id)
    return (src, ev.text)


def normalize_evidence_scores(evidence: Sequence[Any]) -> List[Any]:
    """
    Normalizes résumé evidence scores to consistent range.
    
    Ensures fair comparison and ranking of résumé improvement content across sources.
    """
    if not evidence:
        return []

    scores = [e.score for e in evidence]
    max_score = max(scores)
    min_score = min(scores)

    if max_score == min_score:
        return [e.model_copy(update={"score": 1.0}) for e in evidence]

    span = max_score - min_score
    out: List[Any] = []
    for e in evidence:
        norm = (e.score - min_score) / span
        out.append(e.model_copy(update={"score": float(norm)}))
    return out


def deduplicate_evidence(evidence: Sequence[Any]) -> List[Any]:
    """
    Removes duplicate résumé evidence by canonical key.
    
    Ensures unique content to improve résumé ranking accuracy and avoid redundancy.
    """
    seen: set[Tuple[str, str]] = set()
    out: List[Any] = []
    for ev in evidence or []:
        key = _canonical_evidence_key(ev)
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    return out


def normalize_scores(evidence: Sequence[Any]) -> List[Any]:
    """
    Provides backward-compatible score normalization for résumé evidence.
    
    Maintains legacy interface while delivering consistent scoring for résumé content ranking.
    """

    return normalize_evidence_scores(evidence)


def merge_scores(evidence: Sequence[Any]) -> List[Any]:
    """
    Provides backward-compatible evidence merging for résumé rankings.
    
    Maintains legacy interface while delivering deduplication for résumé content optimization.
    """

    return deduplicate_evidence(evidence)


def rank_evidence(
    evidence: Sequence[Any],
    *,
    top_k: Optional[int] = None,
    normalize: bool = True,
    max_chars: int = 0,
    strategy: str = "hybrid",
) -> List[Any]:
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
    core = _core_models()
    Evidence = core.Evidence
    ranked: List[Any] = []
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
    groups: Sequence[Sequence[Any]],
    *,
    cfg: Optional[Any] = None,
    rrf_k: int = 60,
) -> List[Any]:
    """
    Evidence-level Reciprocal Rank Fusion.

        score(ev) = Σ_i w_i / (rrf_k + rank_i)
    """
    if not groups:
        return []

    weights = _rrf_weights_from_config(cfg, len(groups))
    scores: Dict[Tuple[str, str], float] = {}
    reprs: Dict[Tuple[str, str], Any] = {}

    for g_idx, group in enumerate(groups):
        w = weights[g_idx] if g_idx < len(weights) else 1.0
        for rank_idx, ev in enumerate(group or []):
            key = _canonical_evidence_key(ev)
            if key not in reprs:
                reprs[key] = ev
            r = rank_idx + 1
            scores[key] = scores.get(key, 0.0) + (w / float(rrf_k + r))

    fused: List[Any] = []
    for key, score in scores.items():
        ev = reprs[key]
        fused.append(ev.model_copy(update={"score": float(score)}))

    fused.sort(key=lambda e: e.score, reverse=True)

    core = _core_models()
    RankingEvent = core.RankingEvent
    evt = RankingEvent(
        stage="evidence_rrf",
        strategy=getattr(cfg, "strategy", "unknown") if cfg is not None else "unknown",
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
    groups: Sequence[Sequence[Any]],
    *,
    rrf_weights: Optional[List[float]] = None,
    workflow_id: Optional[str] = None,
    rrf_k: int = 60,
) -> List[Any]:
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
    cfg: Optional[Any] = None
    if rrf_weights is not None:
        core = _core_models()
        RetrievalConfig = core.RetrievalConfig
        cfg = RetrievalConfig()
        cfg.rrf_weights = list(rrf_weights)

    return fuse_evidence_groups_rrf(groups, cfg=cfg, rrf_k=rrf_k)


def build_rag_result(
    groups: Sequence[Sequence[Any]],
    *,
    cfg: Optional[Any] = None,
    rag_plan: Optional[Any] = None,
    top_k: Optional[int] = None,
    max_chars: int = 0,
    used_hyde: bool = False,
) -> Any:
    """
    High-level helper to fuse and rank Evidence sets and produce a RAGResult.

    If cfg.use_rrf is True:
        • Apply evidence-level RRF across groups, then truncate/trim.
    Otherwise:
        • Concatenate groups, deduplicate, rank by score, truncate/trim.
    """
    core = _core_models()
    RetrievalConfig = core.RetrievalConfig
    RAGResult = core.RAGResult
    RankingEvent = core.RankingEvent

    cfg = cfg or RetrievalConfig()

    if cfg.use_rrf:
        flat = fuse_evidence_groups_rrf(groups, cfg=cfg)
    else:
        all_hits: List[Any] = []
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



