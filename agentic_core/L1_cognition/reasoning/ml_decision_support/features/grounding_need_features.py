"""Grounding-need heuristic classifier — W1.P2 deposit.

Plan: ``.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` W1.P2.

Per Anthropic *Building Effective Agents* (2024), routing classifiers
should start as heuristic rules before promoting to an LLM classifier:

    "Routing works well for complex tasks where there are distinct
    categories that are better handled separately, and where
    classification can be handled accurately, either by an LLM or a
    more traditional classification model/algorithm."

This module is the **traditional** entry point. It emits a single scalar
score in ``[0.0, 1.0]`` indicating how strongly the request benefits from
grounded retrieval (the Vertex AI "dynamic retrieval prediction score"
analog). W3 will wire the score into ``PathRouter`` as the primary R3
gate; W0 already calibrated a target threshold of ``~0.72`` against the
shipped fixtures.

Algorithm (deterministic, no network, no LLM calls):

1. Normalize the query to lowercase, strip whitespace, collapse runs of
   whitespace.
2. Count **grounding-indicative** tokens — words/phrases that signal the
   answer depends on external facts (``latest``, ``today``, ``current``,
   ``price``, ``policy``, ``regulation``, ``as of``, ...).
3. Count **creative / reformat** tokens — words that signal the request
   is self-contained (``summarize``, ``rewrite``, ``draft``,
   ``brainstorm``, ...).
4. Apply a ``WorkClass`` multiplier — ``factual``/``compare``/``analyze``
   push upward; ``generate``/``summarize`` push downward.
5. Squash the linear combination through a sigmoid so the output is
   bounded, smooth, and never exactly 0 or 1.

The exact coefficients are intentionally mild — overfitting is
impossible with this signal vocabulary, and the whole point of the W0
harness is to re-tune on real traces. Do not over-invest in the
heuristic; its job is to be *defensibly better than payload-shape* and
*cheap to run everywhere*.

Parity: :func:`classify_grounding_need` returns a score that the
``r3_grounding.json`` fixture's labels should broadly agree with when
fed via the W0 harness. See
``tests/unit/agentic_core/L1_cognition/test_grounding_need_features.py``.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from agentic_core.runtime.contracts.routing_features import WorkClass

__all__ = [
    "DEFAULT_INTERCEPT",
    "GroundingNeedClassification",
    "classify_grounding_need",
    "classify_work_class",
]


# ---------------------------------------------------------------------------
# Keyword vocabularies
# ---------------------------------------------------------------------------

# Grounding-indicative terms — presence in the query nudges the score UP.
# Curated from: Vertex AI sample prompts (docs.cloud.google.com), Anthropic
# retrieval cookbook, and the R3 fixture positive-class examples (W0.P1).
_GROUNDING_TOKENS: frozenset[str] = frozenset(
    {
        "latest",
        "current",
        "today",
        "yesterday",
        "recent",
        "now",
        "2024",
        "2025",
        "2026",
        "price",
        "prices",
        "cost",
        "costs",
        "policy",
        "policies",
        "regulation",
        "regulations",
        "law",
        "laws",
        "news",
        "weather",
        "stock",
        "release",
        "released",
        "launched",
        "version",
        "update",
        "changelog",
        "documentation",
        "specification",
        "rfc",
        "standard",
        "compliance",
        "real-time",
        "realtime",
        "live",
    }
)

# Multi-word grounding phrases — matched as substrings after normalization.
_GROUNDING_PHRASES: tuple[str, ...] = (
    "as of",
    "up to date",
    "up-to-date",
    "according to",
    "what does the documentation",
    "compare the two",
    "fact check",
    "fact-check",
    "cite source",
    "with citations",
)

# Non-grounding / self-contained tokens — nudge the score DOWN.
_REFORMAT_TOKENS: frozenset[str] = frozenset(
    {
        "summarize",
        "summarise",
        "summary",
        "rewrite",
        "reword",
        "paraphrase",
        "rephrase",
        "draft",
        "brainstorm",
        "outline",
        "bullet",
        "bullets",
        "reformat",
        "format",
        "translate",
        "translation",
        "fiction",
        "poem",
        "poetry",
        "story",
        "creative",
        "imagine",
    }
)

# Work class → score multiplier (applied to positive evidence only — never
# drags a creative query upward). Tuned against the R3 fixture.
_WORK_CLASS_MULTIPLIER: dict[WorkClass, float] = {
    WorkClass.FACTUAL: 1.00,
    WorkClass.COMPARE: 0.95,
    WorkClass.ANALYZE: 0.85,
    WorkClass.ACT: 0.60,
    WorkClass.SUMMARIZE: 0.35,
    WorkClass.GENERATE: 0.20,
    WorkClass.UNKNOWN: 0.65,
}

# Linear-combination coefficients. Held modest on purpose — see module
# docstring. The intercept biases slightly below neutral so an
# evidence-free query on an unknown work class falls into R5/R1B territory
# rather than forcing grounding.
DEFAULT_INTERCEPT: float = -0.6
_GROUNDING_TOKEN_WEIGHT: float = 0.75
_GROUNDING_PHRASE_WEIGHT: float = 1.25
_REFORMAT_TOKEN_WEIGHT: float = 0.90
_WORK_CLASS_WEIGHT: float = 1.80


_TOKENIZER_RE = re.compile(r"[a-z0-9][a-z0-9\-]*")


@dataclass(frozen=True)
class GroundingNeedClassification:
    """Structured output of :func:`classify_grounding_need`.

    Fields:
        score: The final grounding-need score in ``(0.0, 1.0)`` after
            sigmoid. Exact 0 or 1 is impossible by construction.
        grounding_token_hits: Count of tokens that matched
            :data:`_GROUNDING_TOKENS`.
        grounding_phrase_hits: Count of matches from
            :data:`_GROUNDING_PHRASES`.
        reformat_token_hits: Count of tokens that matched
            :data:`_REFORMAT_TOKENS`.
        work_class: The :class:`WorkClass` enum used for the multiplier.
        linear_logit: The pre-sigmoid linear combination — useful for
            debugging and for threshold calibration that prefers logit
            over probability.
    """

    score: float
    grounding_token_hits: int
    grounding_phrase_hits: int
    reformat_token_hits: int
    work_class: WorkClass
    linear_logit: float


def _normalize(query: str) -> str:
    """Lowercase + collapse whitespace."""
    return re.sub(r"\s+", " ", query.strip().lower())


def _tokenize(normalized_query: str) -> list[str]:
    """Regex word tokenizer — keeps hyphens, drops punctuation."""
    return _TOKENIZER_RE.findall(normalized_query)


def _count_phrase_hits(normalized_query: str) -> int:
    return sum(1 for phrase in _GROUNDING_PHRASES if phrase in normalized_query)


def _sigmoid(x: float) -> float:
    """Numerically stable logistic. Clamped outside [-30, 30] to avoid overflow."""
    if x >= 30.0:
        return 1.0 - 1e-12
    if x <= -30.0:
        return 1e-12
    return 1.0 / (1.0 + math.exp(-x))


def classify_work_class(query: str) -> WorkClass:
    """Best-effort heuristic ``WorkClass`` detection from raw query text.

    This is a **fallback** — the authoritative source of ``work_class`` is
    L1's ``I3`` output. Use this only when L1 did not emit one (i.e.
    back-compat with older plan producers that don't set the field yet).

    Returns :attr:`WorkClass.UNKNOWN` when no keyword is decisive.
    """
    normalized = _normalize(query)
    tokens = set(_tokenize(normalized))

    # Order matters — more specific patterns first.
    if any(t in tokens for t in ("summarize", "summarise", "summary", "tldr")):
        return WorkClass.SUMMARIZE
    if any(t in tokens for t in ("compare", "versus", "vs", "vs.", "difference", "differences")):
        return WorkClass.COMPARE
    if any(t in tokens for t in ("analyze", "analyse", "analysis", "evaluate", "assess")):
        return WorkClass.ANALYZE
    if any(
        t in tokens
        for t in (
            "create",
            "make",
            "do",
            "run",
            "execute",
            "deploy",
            "apply",
            "submit",
            "send",
            "file",
        )
    ):
        # Heuristic — "create" / "make" collide with GENERATE; tie-break
        # on whether an obvious external action verb fires.
        if any(t in tokens for t in ("deploy", "execute", "run", "submit", "send", "apply")):
            return WorkClass.ACT
    if any(t in tokens for t in ("what", "when", "who", "where", "how", "why", "is", "does")):
        # Question words lean factual unless also creative.
        if any(t in tokens for t in ("imagine", "fiction", "story", "poem")):
            return WorkClass.GENERATE
        return WorkClass.FACTUAL
    if any(t in tokens for t in ("write", "draft", "brainstorm", "generate", "compose")):
        return WorkClass.GENERATE
    return WorkClass.UNKNOWN


def classify_grounding_need(
    query: str,
    work_class: WorkClass | None = None,
    *,
    intercept: float = DEFAULT_INTERCEPT,
) -> GroundingNeedClassification:
    """Score how strongly ``query`` benefits from grounded retrieval.

    Args:
        query: Raw request text. Empty strings are allowed and produce a
            neutral-low score (signals absent, bias pushes below 0.5).
        work_class: L1's ``WorkClass`` if known, else ``None`` to invoke
            the heuristic :func:`classify_work_class` fallback.
        intercept: Linear-combination bias. Defaults to
            :data:`DEFAULT_INTERCEPT`; callers can shift globally via
            W2.P1 configuration without retraining.

    Returns:
        :class:`GroundingNeedClassification` with score in ``(0,1)``.
    """
    if query is None:
        raise ValueError("query must not be None — pass an empty string instead")

    normalized = _normalize(query)
    tokens = _tokenize(normalized)
    token_set = set(tokens)

    grounding_hits = sum(1 for t in token_set if t in _GROUNDING_TOKENS)
    reformat_hits = sum(1 for t in token_set if t in _REFORMAT_TOKENS)
    phrase_hits = _count_phrase_hits(normalized)

    if work_class is None:
        work_class = classify_work_class(query)

    work_multiplier = _WORK_CLASS_MULTIPLIER.get(work_class, 0.65)

    # Cap the positive evidence at 3 to avoid pathological long queries
    # dominating. Reformat evidence is not capped — creative queries
    # SHOULD be able to drive the score arbitrarily low.
    capped_grounding = min(grounding_hits, 3)
    capped_phrase = min(phrase_hits, 3)

    logit = (
        intercept
        + _GROUNDING_TOKEN_WEIGHT * capped_grounding
        + _GROUNDING_PHRASE_WEIGHT * capped_phrase
        - _REFORMAT_TOKEN_WEIGHT * reformat_hits
        + _WORK_CLASS_WEIGHT * (work_multiplier - 0.5)
    )
    score = _sigmoid(logit)

    return GroundingNeedClassification(
        score=round(score, 6),
        grounding_token_hits=grounding_hits,
        grounding_phrase_hits=phrase_hits,
        reformat_token_hits=reformat_hits,
        work_class=work_class,
        linear_logit=round(logit, 6),
    )
