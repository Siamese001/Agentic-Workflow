from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from core.models.models import CouncilVote, Evidence, RAGResult, RetrievalConfig


def _apply_council_weights(evidence: Sequence[Evidence], council: Optional[CouncilVote]) -> List[Evidence]:
    """Apply QA-council post-fusion weighting to Evidence scores.

    Selected id receives a small boost; all others are slightly demoted.
    This mirrors the behavior previously implemented in retrieval.py
    but lives here so that all evidence-level ranking logic is contained
    within the META retrieval/ranking layer.
    """

    if council is None or not council.selected_id:
        return list(evidence)

    sel = council.selected_id
    BOOST = 1.12
    DEMOTE = 0.94

    adjusted: List[Evidence] = []
    for ev in evidence:
        factor = BOOST if sel in ev.text else DEMOTE
        adjusted.append(ev.model_copy(update={"score": ev.score * factor}))
    return adjusted


def _canonical_key(ev: Evidence) -> Tuple[str, str]:
    """Canonical key for deduplication across retrievers."""

    source = str(ev.source or "")
    doc_id = str((ev.metadata or {}).get("doc_id", ""))
    if doc_id:
        return (source, doc_id)
    return (source, ev.text)


def _fuse_groups_rrf(groups: Sequence[Sequence[Evidence]], cfg: RetrievalConfig) -> List[Evidence]:
    """Evidence-level Reciprocal Rank Fusion.

    score(ev) = Σ_i w_i / (k + rank_i)
    where weights come from cfg.rrf_weights if present; otherwise 1.0.
    """

    if not groups:
        return []

    # Default configuration
    rrf_k = getattr(cfg, "rrf_k", 60) or 60
    raw_weights = list(getattr(cfg, "rrf_weights", []) or [])

    def _weight_for_group(idx: int) -> float:
        if not raw_weights:
            return 1.0
        if idx < len(raw_weights):
            try:
                return float(raw_weights[idx])
            except Exception:  # pragma: no cover - defensive
                return 1.0
        # Repeat last weight for extra groups
        try:
            return float(raw_weights[-1])
        except Exception:  # pragma: no cover - defensive
            return 1.0

    scores: Dict[Tuple[str, str], float] = {}
    reprs: Dict[Tuple[str, str], Evidence] = {}

    for g_idx, group in enumerate(groups):
        w = _weight_for_group(g_idx)
        for rank_idx, ev in enumerate(group or []):
            key = _canonical_key(ev)
            if key not in reprs:
                reprs[key] = ev
            r = rank_idx + 1
            scores[key] = scores.get(key, 0.0) + (w / float(rrf_k + r))

    fused: List[Evidence] = []
    for key, score in scores.items():
        ev = reprs[key]
        fused.append(ev.model_copy(update={"score": float(score)}))

    fused.sort(key=lambda e: e.score, reverse=True)
    return fused


def fuse_and_rank(
    lex_results: Iterable[Evidence],
    dense_results: Iterable[Evidence],
    cfg: RetrievalConfig,
    *,
    council_vote: Optional[CouncilVote] = None,
    used_hyde: bool = False,
) -> RAGResult:
    """Fuse lexical and dense retrieval results and return a RAGResult.

    Responsibilities:
        * RRF fusion of lexical and dense groups.
        * Evidence-level deduplication and sorting.
        * Truncation according to RetrievalConfig.max_hits.
        * Optional QA-council post-fusion weighting.
    """

    groups: List[List[Evidence]] = [list(lex_results), list(dense_results)]
    groups = [g for g in groups if g]

    fused = _fuse_groups_rrf(groups, cfg)
    fused = _apply_council_weights(fused, council_vote)

    max_hits = getattr(cfg, "max_hits", None)
    if isinstance(max_hits, int) and max_hits > 0:
        fused = fused[: max_hits]

    return RAGResult(evidence=fused, used_hyde=used_hyde)

