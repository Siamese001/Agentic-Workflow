"""Route relevance seeding from research-brief signal.

Wave 2 phase 2.3 of the apps_qna spine integration plan
(``apps-qna-spine-integration-e8f3a1``).

Given a parsed research brief — interviewer lens text, role areas of
focus, industry trends — and the canonical route registry, this module
ranks the 9 routes by relevance to the interviewer signal and emits
``LikelyQuestionGroup`` entries in priority order. Each emitted group has
an empty ``questions`` list; the operator (or a later L2 synthesis wave)
fills questions per route.

Why this exists
---------------
Hand-curated ``research.likely_questions`` is the right artifact (deeply
contextualized questions per interviewer), but starting from a blank YAML
forces the operator to also pick **which** routes the interviewer will
probe before they have signal. This module front-loads that decision: it
embeds the interviewer's lens + hot buttons + role areas + trends as a
single signal document, embeds each route's name + triggers + answer
shape as a route document, and ranks routes by cosine similarity. The
operator then writes questions for the top-ranked routes first.

Spine routing
-------------
Embeddings flow through ``apps_qna.integrations.spine_adapter`` —
specifically the same BGE-M3 path used by ``classify_section_topic`` in
W2.1. When BGE is unavailable the keyword-overlap fallback governs both,
so this module is environment-symmetric with the rest of W2.

Constitutional alignment
------------------------
- §22 (graph-layer evidence): seeding is a build-time decision tied to
  the route registry — no runtime dispatch involved.
- §23 (canonical invariants): apps_qna domain (route registry, question
  taxonomy) sits on top of spine primitives (BGE-M3 embeddings); layer
  gravity preserved.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from apps_qna.integrations.spine_adapter import classify_section_topic
from apps_qna.types.qna_types import LikelyQuestionGroup

if TYPE_CHECKING:
    from apps_qna.config.route_registry import Route, RouteRegistry

_log = logging.getLogger(__name__)

# Number of routes to surface in seeded ``likely_questions``. We seed
# strictly the top-N because the paste-budget compression in the builder
# already prefers routes declared in the YAML; below the cutoff the
# routes still load via load_strategy, just without operator-curated
# questions.
_SEED_TOP_N: int = 6

# Per-mode score thresholds — below these the route is considered
# unranked (insufficient signal). The thresholds match
# from_research_brief._EMBEDDING_THRESHOLD / _KEYWORD_THRESHOLD intent:
# admit moderate matches on the embedding path; require stronger
# overlap on the keyword path because keyword scores are coarser.
_EMBEDDING_THRESHOLD: float = 0.40
_KEYWORD_THRESHOLD: float = 0.10

# When the ranker can't decide, fall back to this hand-curated default
# ordering (approximates the most common interviewer mix for senior
# leadership roles, biased towards behavioral / executive-fit dominated
# panels). Keeps the YAML never-empty for the operator's first pass.
_FALLBACK_ROUTE_ORDER: tuple[str, ...] = (
    "executive_fit",
    "behavioral",
    "architecture",
    "productization",
    "global_engineering",
    "rca",
    "cross_exam",
    "ds_to_platform",
    "governance",
)


def build_route_descriptor(route: "Route") -> str:
    """Concatenate route signals into a single descriptor for embedding.

    Natural-language free-text descriptor suitable for BGE-M3 (preferred over
    space-joined tokens). W1.2: single canonical route descriptor builder
    shared by ``semantic_router.SemanticRouter`` and
    ``route_seeding.rank_routes_by_signal`` — eliminates the prior BoW
    ``_route_corpus`` vs NL ``_build_route_descriptor`` drift.
    """
    parts = [route.name]
    if route.triggers:
        parts.append("Triggers: " + "; ".join(route.triggers))
    if route.answer_shape:
        parts.append("Answer shape: " + "; ".join(route.answer_shape))
    return ". ".join(parts)


# W1.2 back-compat: preserve the legacy private alias for any stray import.
_build_route_descriptor = build_route_descriptor


def _build_signal_document(
    interviewer_lenses: dict[str, str],
    role_areas: list[str],
    industry_trends: list[str],
) -> str:
    """Concatenate interviewer/role/trend signals into one ranking input."""
    parts: list[str] = []
    if interviewer_lenses:
        parts.append("Interviewer lens: " + " ".join(interviewer_lenses.values()))
    if role_areas:
        parts.append("Role areas of focus: " + "; ".join(role_areas))
    if industry_trends:
        parts.append("Industry trends: " + "; ".join(industry_trends))
    return "\n\n".join(parts)


def rank_routes_by_signal(
    *,
    registry: "RouteRegistry",
    signal: str,
    top_n: int = _SEED_TOP_N,
    rerank: bool = True,
) -> list[tuple[str, float, str]]:
    """Rank routes against an interviewer signal document.

    Returns ``[(route_id, score, mode), ...]`` sorted by score descending.
    ``mode`` is one of ``{"embedding", "keyword", "empty"}`` (see
    ``classify_section_topic``).

    W2.3 (``apps-qna-dag-enhancements-e4c7b2``): the bi-encoder ranking is
    optionally refined by a cross-encoder reranker (``apps_qna.router.reranker``).
    The reranker pass is env-gated via ``APPS_QNA_RERANKER`` — when the
    flag is unset, it returns the bi-encoder order unchanged and logs a
    ``rerank_pass`` row with ``mode="bi_encoder_passthrough"`` and
    ``rerank_delta=0`` to ``apps_qna_pack_lifecycle``. Callers can suppress
    the reranker pass entirely by passing ``rerank=False``.

    When ``signal`` is empty or ``registry`` has no routes, returns an
    empty list — caller should fall back to a hand-curated default order.
    """
    if not signal.strip() or not registry.routes:
        return []
    candidates = {
        route.id: build_route_descriptor(route)
        for route in registry.routes
    }
    # Embed each candidate against the signal individually. We invert the
    # classify_section_topic contract here — section becomes the signal,
    # candidates are routes — so the same primitive ranks each route's
    # descriptor against the signal text.
    ranked: list[tuple[str, float, str]] = []
    for route_id, descriptor in candidates.items():
        topic, score, mode = classify_section_topic(
            signal,
            {route_id: descriptor},
        )
        ranked.append((route_id, score, mode))
    ranked.sort(key=lambda r: r[1], reverse=True)
    bi_encoder_top = ranked[:top_n]

    if not rerank or not bi_encoder_top:
        return bi_encoder_top

    # W2.3: cross-encoder pass over the bi-encoder top-K. Fail-soft —
    # any reranker error returns the bi-encoder order unchanged.
    try:
        from apps_qna.router.reranker import rerank_candidate_scores  # noqa: PLC0415

        reranked, _mode, _delta = rerank_candidate_scores(
            query=signal,
            candidates=bi_encoder_top,
            descriptors=candidates,
            top_n=top_n,
        )
        return reranked if reranked else bi_encoder_top
    except (ImportError, RuntimeError, ValueError) as exc:
        _log.debug("rank_routes_by_signal rerank pass failed: %r", exc)
        return bi_encoder_top


def seed_likely_questions_from_research(
    *,
    registry: "RouteRegistry",
    interviewer_lenses: dict[str, str],
    role_areas: list[str],
    industry_trends: list[str],
    top_n: int = _SEED_TOP_N,
    bandit: "object | None" = None,
) -> list[LikelyQuestionGroup]:
    """Emit empty ``LikelyQuestionGroup`` entries in priority order.

    Three-stage decision (W4.1):
      1. **Bandit path** (when ``bandit`` is provided AND the cell has
         cleared cold-start): ``AppsQnaRouteBandit.choose_routes_for_signal``
         returns Thompson-sampled top-N ordering grounded in accumulated
         post-rehearsal outcomes. Emits constitutional §29 paired
         ``ROUTER_DECISION:`` markers + ledger writes.
      2. **Embedding/keyword ranking** (W2.3): when bandit is None or
         cold-start, BGE-M3 / keyword cosine ranking against the
         interviewer signal drives ordering.
      3. **Fallback ordering**: hand-curated default order fills any
         remaining slots after threshold filtering.

    Each emitted group has an empty ``questions`` list; the operator
    (or a later L2 synthesis wave) fills questions per route. Existing
    operator-authored questions in a YAML are preserved by the caller's
    merge contract — this function is only invoked when the brief has
    no prior ``likely_questions``.

    The ``bandit`` parameter is typed as ``object | None`` rather than
    ``AppsQnaRouteBandit | None`` to keep this module's import surface
    free of the L0_routing dependency at module load time. The actual
    ``choose_routes_for_signal`` method is duck-typed.
    """
    signal = _build_signal_document(
        interviewer_lenses=interviewer_lenses,
        role_areas=role_areas,
        industry_trends=industry_trends,
    )

    # Stage 1: bandit path (W4.1).
    if bandit is not None and signal.strip():
        try:
            bandit_result = bandit.choose_routes_for_signal(signal, top_n=top_n)
        except (AttributeError, TypeError, ValueError, RuntimeError) as exc:
            _log.debug("bandit choose_routes_for_signal failed: %r", exc)
            bandit_result = None
        if bandit_result is not None and bandit_result:
            _log.info(
                "route seeding: bandit path active, %d routes ranked",
                len(bandit_result),
            )
            return [
                LikelyQuestionGroup(route_id=sel.route_id, questions=[])
                for sel in bandit_result
            ]

    # Stage 2: embedding/keyword ranking (W2.3) — bandit cold-start or absent.
    ranked = rank_routes_by_signal(
        registry=registry,
        signal=signal,
        top_n=top_n,
    )

    # Per-mode threshold filter. Routes below threshold drop out of the
    # ranked output; the fallback order fills the remaining slots.
    accepted: list[str] = []
    for route_id, score, mode in ranked:
        threshold = (
            _EMBEDDING_THRESHOLD if mode == "embedding" else _KEYWORD_THRESHOLD
        )
        if score >= threshold:
            accepted.append(route_id)
            _log.debug(
                "route-seeded: id=%s score=%.3f mode=%s",
                route_id,
                score,
                mode,
            )

    # Fill remaining slots from the fallback order (preserving registry
    # validity — only emit ids that exist in the registry).
    valid_ids = {r.id for r in registry.routes}
    fallback_pool = [
        rid for rid in _FALLBACK_ROUTE_ORDER if rid in valid_ids and rid not in accepted
    ]
    # Plus any registry routes not in fallback order (newly added routes).
    fallback_pool.extend(
        rid
        for rid in (r.id for r in registry.routes)
        if rid not in accepted and rid not in fallback_pool
    )

    final_order: list[str] = []
    final_order.extend(accepted)
    while len(final_order) < min(top_n, len(valid_ids)) and fallback_pool:
        final_order.append(fallback_pool.pop(0))

    return [
        LikelyQuestionGroup(route_id=route_id, questions=[])
        for route_id in final_order
    ]


__all__ = [
    "build_route_descriptor",
    "rank_routes_by_signal",
    "seed_likely_questions_from_research",
]
