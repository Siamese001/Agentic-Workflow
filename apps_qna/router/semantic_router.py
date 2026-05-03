"""Semantic question router — unified BGE-M3 path via spine adapter.

W1.1 (apps-qna-dag-enhancements-e4c7b2): the previous implementation used a
stdlib BoW cosine over a BoW-flavored ``_route_corpus`` (joined tokens). The
sibling module ``apps_qna.router.route_seeding`` already embedded routes via
BGE-M3 using a natural-language ``_build_route_descriptor``. That drift meant
two different embedding surfaces gave different rankings for the same
interview prompt — paraphrases of "architecture" land on different routes
between the two surfaces.

Post-W1 this module delegates to ``spine_adapter.classify_section_topic``
(same primitive used by ``route_seeding.rank_routes_by_signal``) and shares
``build_route_descriptor`` for route-side input. The spine primitive:

  * Uses BGE-M3 when ``sentence-transformers`` is installed AND model weights
    are locally cached (or ``BGE_ALLOW_MODEL_DOWNLOAD=true``).
  * Gracefully degrades to a deterministic word-overlap fallback otherwise,
    so tests run without heavy dependencies.

Used by:
- ``python -m apps_qna route "<question>"`` — offline triage of a question
  against the registry.
- Eval harness — given a predicted-questions card (21), score whether the
  manifest routing logic would land each question on the expected route.

This is **not** a runtime LLM. It is a deterministic offline scorer used for
prep-time eval and rehearsal triage.
"""

from __future__ import annotations

from dataclasses import dataclass

from apps_qna.config.route_registry import RouteRegistry
from apps_qna.integrations.spine_adapter import classify_section_topic
from apps_qna.router.route_seeding import build_route_descriptor


# Abstain thresholds — mirror route_seeding._EMBEDDING_THRESHOLD /
# _KEYWORD_THRESHOLD so the router surface and seeding surface share a
# single admission policy. Under BGE-M3, random / nonsense text still
# gets a nonzero cosine against every descriptor (embedding magnitudes
# never truly zero out), so the keyword-mode "score == 0" abstain is
# insufficient for the embedding path.
_EMBEDDING_ABSTAIN_THRESHOLD: float = 0.40
_KEYWORD_ABSTAIN_THRESHOLD: float = 0.0


@dataclass(frozen=True)
class RouteScore:
    """One scored route candidate.

    ``mode`` is the spine primitive's classification mode for this score:
    ``"embedding"`` when BGE-M3 was used, ``"keyword"`` for the stdlib
    fallback, ``"empty"`` when input was empty. Defaults to ``"keyword"``
    for backward compatibility with any caller constructing RouteScore
    directly.
    """

    route_id: str
    route_name: str
    primary_card: str
    score: float
    mode: str = "keyword"


class SemanticRouter:
    """Score an incoming question against every route in a registry.

    Each route is rendered once as a natural-language descriptor and scored
    against the incoming question via the spine ``classify_section_topic``
    primitive (BGE-M3 when available, word-overlap fallback otherwise).
    """

    def __init__(self, registry: RouteRegistry) -> None:
        self._registry = registry
        self._descriptors: dict[str, str] = {
            route.id: build_route_descriptor(route) for route in registry.routes
        }

    def route(self, question: str, top_k: int = 3) -> list[RouteScore]:
        """Return the top_k routes by spine similarity (descending)."""
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        scored: list[RouteScore] = []
        for route in self._registry.routes:
            _topic, score, mode = classify_section_topic(
                question,
                {route.id: self._descriptors[route.id]},
            )
            scored.append(
                RouteScore(
                    route_id=route.id,
                    route_name=route.name,
                    primary_card=route.primary_card,
                    score=float(score),
                    mode=mode,
                )
            )
        scored.sort(key=lambda x: (x.score, x.route_id), reverse=True)
        return scored[:top_k]

    def best(self, question: str) -> RouteScore | None:
        """Return the single best route, or None when no route clears threshold.

        Abstain policy is mode-aware: under embedding mode, the spine
        primitive returns a cosine against every route (never exactly
        zero), so a fixed 0.40 floor filters out "no real signal" inputs.
        Under keyword mode, the overlap score is 0.0 iff there is literally
        no word overlap, which is the original abstain contract preserved.
        """
        ranked = self.route(question, top_k=1)
        if not ranked:
            return None
        top = ranked[0]
        threshold = (
            _EMBEDDING_ABSTAIN_THRESHOLD
            if top.mode == "embedding"
            else _KEYWORD_ABSTAIN_THRESHOLD
        )
        if top.score <= threshold:
            return None
        return top


__all__ = ["RouteScore", "SemanticRouter"]
