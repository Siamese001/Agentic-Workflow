"""Multi-agent breadth-first classifier.

Per Anthropic's multi-agent research-system writeup, spinning up N subagents
is only beneficial when the task is *genuinely* breadth-first — i.e., the
problem decomposes into parallel, independent sub-queries whose results can
be merged. Using multi-agent for inherently sequential or narrow problems
multiplies cost (each agent incurs Anthropic token usage) without quality
gain, and frequently HURTS quality because synthesis across unrelated
sub-results is harder than a single coherent answer.

This module provides a heuristic classifier that scores a query/task for
"breadth-first-ness" and returns a recommended dispatch mode:

    BREADTH_FIRST  — parallel multi-agent (2+ subagents, merge results)
    SINGLE_AGENT   — one agent, sequential reasoning
    AMBIGUOUS      — score near the threshold; caller should defer to HITL
                      or use a cost-capped fallback to SINGLE_AGENT

Signals (each contributes to a 0..1 score, weighted sum clamped to [0, 1]):

    +1 listwise cues        : "list", "all", "each", "enumerate", "per"
    +1 parallel cues        : "compare", "across", "vs", "between"
    +1 corpus-fanout cues   : "all X", "every Y", plural nouns at high density
    +1 question-count cue   : multiple "?"
    -1 sequential cues      : "then", "after that", "first ... then", "step by step"
    -1 narrow cues          : "exactly", "the", "which one", "best"

Weights are intentionally simple and auditable — Anthropic's own guidance
is that the classifier doesn't need to be sophisticated, it needs to be
CONSERVATIVE (err toward single-agent because multi-agent is the expensive
side of the tradeoff).

Pure: no I/O, no model calls. Callers feed it a normalized query string
and optional metadata (e.g., ADG fan-out count).

References:
- Anthropic. How we built our multi-agent research system.
  https://www.anthropic.com/engineering/built-multi-agent-research-system
- Plan: .windsurf/plans/anthropic-rag-gaps-7f3c2a.md (phase P4.3)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Final

# Dispatch modes
MODE_SINGLE_AGENT: Final = "single_agent"
MODE_BREADTH_FIRST: Final = "breadth_first"
MODE_AMBIGUOUS: Final = "ambiguous"

# Thresholds. Default is CONSERVATIVE — breadth-first requires a clear signal.
DEFAULT_BREADTH_THRESHOLD = 0.60
DEFAULT_AMBIGUITY_BAND = 0.10  # ±band around threshold returns AMBIGUOUS

# Signal weights — tuned for conservative single-agent preference
_LISTWISE_PATTERNS = (
    r"\blist\b",
    r"\benumerate\b",
    r"\ball\s+\w+\b",
    r"\beach\s+\w+\b",
    r"\bevery\s+\w+\b",
    r"\bper\s+\w+\b",
)
_PARALLEL_PATTERNS = (
    r"\bcompare\b",
    r"\bacross\b",
    r"\bvs\.?\b",
    r"\bversus\b",
    r"\bbetween\s+\w+\s+and\b",
    r"\bdifferences?\s+(?:between|among)\b",
)
_SEQUENTIAL_PATTERNS = (
    r"\bthen\b",
    r"\bafter\s+(?:that|this)\b",
    r"\bstep\s+by\s+step\b",
    r"\bfirst\b.*\bthen\b",
    r"\bin\s+order\s+to\b",
    r"\bnext\b",
)
_NARROW_PATTERNS = (
    r"\bexactly\s+one\b",
    r"\bthe\s+(?:single|only|specific)\b",
    r"\bwhich\s+one\b",
    r"\bbest\s+(?:single|one)\b",
)

_SIGNAL_WEIGHT = 0.25  # each matched pattern shifts score by this


@dataclass(frozen=True)
class ClassificationResult:
    """Output of breadth-first classification.

    Attributes
    ----------
    mode:
        One of ``MODE_SINGLE_AGENT`` | ``MODE_BREADTH_FIRST`` | ``MODE_AMBIGUOUS``.
    score:
        Continuous breadth-first score in [0.0, 1.0]. Higher = more
        parallel-friendly.
    threshold:
        The threshold used for the decision.
    matched_signals:
        Tuple of signal category names matched in the query
        (``listwise``, ``parallel``, ``sequential``, ``narrow``,
        ``multi_question``, ``high_fanout``).
    reason:
        Human-readable explanation for telemetry/logging.
    """

    mode: str
    score: float
    threshold: float
    matched_signals: tuple[str, ...] = field(default_factory=tuple)
    reason: str = ""


def _count_pattern_matches(text: str, patterns: tuple[str, ...]) -> int:
    count = 0
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            count += 1
    return count


def classify_query(
    query: str,
    *,
    corpus_fanout: int | None = None,
    threshold: float = DEFAULT_BREADTH_THRESHOLD,
    ambiguity_band: float = DEFAULT_AMBIGUITY_BAND,
) -> ClassificationResult:
    """Score a query for breadth-first-ness.

    Parameters
    ----------
    query:
        Natural-language query / task description.
    corpus_fanout:
        Optional ADG-derived signal: how many distinct sub-areas would need
        to be inspected to answer. When >= 3, contributes a high-fanout
        boost. None means the caller has no structural signal.
    threshold:
        Score above which the result is BREADTH_FIRST (minus ambiguity_band)
        or SINGLE_AGENT (below threshold minus band). Default 0.60.
    ambiguity_band:
        Half-width of the ambiguity band around `threshold`. Scores within
        `[threshold - band, threshold + band]` return AMBIGUOUS. Default 0.10.
    """
    if not query or not query.strip():
        return ClassificationResult(
            mode=MODE_SINGLE_AGENT,
            score=0.0,
            threshold=threshold,
            reason="empty query; default to single-agent",
        )

    normalized = query.strip()

    listwise = _count_pattern_matches(normalized, _LISTWISE_PATTERNS)
    parallel = _count_pattern_matches(normalized, _PARALLEL_PATTERNS)
    sequential = _count_pattern_matches(normalized, _SEQUENTIAL_PATTERNS)
    narrow = _count_pattern_matches(normalized, _NARROW_PATTERNS)
    multi_q = normalized.count("?") >= 2
    high_fanout = corpus_fanout is not None and corpus_fanout >= 3

    score = 0.5  # neutral baseline
    signals: list[str] = []

    if listwise:
        score += _SIGNAL_WEIGHT * min(listwise, 2)
        signals.append("listwise")
    if parallel:
        score += _SIGNAL_WEIGHT * min(parallel, 2)
        signals.append("parallel")
    if multi_q:
        score += _SIGNAL_WEIGHT
        signals.append("multi_question")
    if high_fanout:
        score += _SIGNAL_WEIGHT
        signals.append("high_fanout")
    if sequential:
        score -= _SIGNAL_WEIGHT * min(sequential, 2)
        signals.append("sequential")
    if narrow:
        score -= _SIGNAL_WEIGHT * min(narrow, 2)
        signals.append("narrow")

    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))

    # Decide mode using threshold + ambiguity band
    upper = threshold + ambiguity_band
    lower = threshold - ambiguity_band
    if score >= upper:
        mode = MODE_BREADTH_FIRST
        reason = f"score {score:.2f} >= {upper:.2f} (threshold {threshold} + band {ambiguity_band})"
    elif score <= lower:
        mode = MODE_SINGLE_AGENT
        reason = f"score {score:.2f} <= {lower:.2f} (threshold {threshold} - band {ambiguity_band})"
    else:
        mode = MODE_AMBIGUOUS
        reason = f"score {score:.2f} within ambiguity band [{lower:.2f}, {upper:.2f}]"

    return ClassificationResult(
        mode=mode,
        score=score,
        threshold=threshold,
        matched_signals=tuple(signals),
        reason=reason,
    )


def is_breadth_first(query: str, *, corpus_fanout: int | None = None) -> bool:
    """Convenience boolean: True only when classifier is confidently breadth-first."""
    return classify_query(query, corpus_fanout=corpus_fanout).mode == MODE_BREADTH_FIRST


__all__ = [
    "MODE_SINGLE_AGENT",
    "MODE_BREADTH_FIRST",
    "MODE_AMBIGUOUS",
    "DEFAULT_BREADTH_THRESHOLD",
    "DEFAULT_AMBIGUITY_BAND",
    "ClassificationResult",
    "classify_query",
    "is_breadth_first",
]
