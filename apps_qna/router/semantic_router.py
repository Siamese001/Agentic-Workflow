"""Semantic question router — bag-of-words cosine over the route registry.

Wave 6 (post-bootstrap NEXT_STEP — embedding router). Pure-stdlib, no heavy
dependency. Embeds each route as a token frequency vector built from its
`name`, `triggers`, and `answer_shape`, then ranks candidate routes by cosine
similarity against an incoming question.

Used by:
- `python -m apps_qna route "<question>"` — offline triage of a question
  against the registry.
- Eval harness — given a predicted-questions card (21), score whether the
  manifest routing logic would land each question on the expected route.

This is **not** a runtime LLM. It is a deterministic offline scorer used for
prep-time eval and rehearsal triage.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from apps_qna.config.route_registry import Route, RouteRegistry

_TOKEN_RE = re.compile(r"\w+")

# Common English stopwords + interview-prompt fillers. Removing these lifts
# signal from interview phrasing like "tell me about a time when you ...".
_STOP: frozenset[str] = frozenset(
    {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "do", "does", "did", "doing", "have", "has", "had", "having",
        "i", "you", "your", "yours", "we", "us", "our", "they", "them", "their",
        "me", "my", "mine", "he", "she", "it", "his", "her", "its",
        "and", "or", "but", "if", "then", "than", "as", "so", "for", "of",
        "in", "on", "at", "to", "from", "with", "about", "into", "over",
        "this", "that", "these", "those", "there", "here",
        "what", "when", "where", "why", "how", "which", "who", "whom",
        "would", "could", "should", "will", "shall", "can", "may", "might",
        "tell", "give", "show", "walk", "explain", "describe", "make",
        "like", "just", "really", "very", "more", "most", "any", "some",
        "thing", "things", "stuff", "kind", "sort", "way",
        "before", "after", "during", "while",
        "yes", "no", "not", "do",
    }
)


@dataclass(frozen=True)
class RouteScore:
    """One scored route candidate."""

    route_id: str
    route_name: str
    primary_card: str
    score: float


def _tokenize(text: str) -> Counter[str]:
    """Lowercase, drop short tokens and stopwords, return Counter."""
    tokens = (t.lower() for t in _TOKEN_RE.findall(text))
    keep = [t for t in tokens if len(t) > 2 and t not in _STOP]
    return Counter(keep)


def _route_corpus(route: Route) -> str:
    """Concatenate the per-route signals that should dominate the embedding.

    Triggers are weighted by repetition because they are the most direct
    surface match for incoming questions.
    """
    triggers = " ".join(route.triggers)
    return " ".join(
        [
            route.name,
            triggers,
            triggers,  # double-weight triggers
            *route.answer_shape,
        ]
    )


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    """Cosine similarity between two token-frequency Counters."""
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    num = sum(a[t] * b[t] for t in common)
    a_mag = math.sqrt(sum(v * v for v in a.values()))
    b_mag = math.sqrt(sum(v * v for v in b.values()))
    if a_mag == 0.0 or b_mag == 0.0:
        return 0.0
    return num / (a_mag * b_mag)


class SemanticRouter:
    """Score an incoming question against every route in a registry.

    Construction is O(R * tokens-per-route). Per-question routing is
    O(R * common-tokens), well under 1 ms for the 9-route registry.
    """

    def __init__(self, registry: RouteRegistry) -> None:
        self._registry = registry
        self._route_vectors: dict[str, Counter[str]] = {
            route.id: _tokenize(_route_corpus(route)) for route in registry.routes
        }

    def route(self, question: str, top_k: int = 3) -> list[RouteScore]:
        """Return the top_k routes by cosine similarity (descending)."""
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        q_tokens = _tokenize(question)
        scored: list[RouteScore] = []
        for route in self._registry.routes:
            score = _cosine(q_tokens, self._route_vectors[route.id])
            scored.append(
                RouteScore(
                    route_id=route.id,
                    route_name=route.name,
                    primary_card=route.primary_card,
                    score=score,
                )
            )
        scored.sort(key=lambda x: (x.score, x.route_id), reverse=True)
        return scored[:top_k]

    def best(self, question: str) -> RouteScore | None:
        """Return the single best route, or None if no token overlap exists.

        Returns None instead of an arbitrary first route when the question
        shares zero tokens with every route corpus — a useful "abstain"
        signal for downstream callers.
        """
        ranked = self.route(question, top_k=1)
        if not ranked or ranked[0].score == 0.0:
            return None
        return ranked[0]
