"""
Phase A: Concrete Context Completeness Scorer implementation.

Scores retrieved evidence for the five context dimensions:
  - condition     (if/when/unless/provided that)
  - action        (the main operation — implicit if content is non-empty)
  - exception     (except/unless/however/but/note/warning/error)
  - scope         (only/all/none/within/for/applies to)
  - temporal      (as of/until/since/before/after/deprecated/effective)

Detection is keyword-based with configurable keyword sets.
This is intentionally simple and deterministic — no randomness, no wall-clock.

C0 RULE: All scores are informational only. Never mutates routing or safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.evaluation.retrieval.completeness import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ContextCompletenessScore,
    GroundedDocument,
    IContextCompletenessScorer,
)
from agentic_core.evaluation.retrieval.interfaces import Document

# ---------------------------------------------------------------------------
# Default keyword sets (deterministic, stable)
# ---------------------------------------------------------------------------

_CONDITION_KEYWORDS: frozenset[str] = frozenset(
    {
        "if",
        "when",
        "unless",
        "provided",
        "assuming",
        "given that",
        "in case",
        "only if",
        "whenever",
        "on condition",
        "where",
        "requires",
    }
)

_EXCEPTION_KEYWORDS: frozenset[str] = frozenset(
    {
        "except",
        "however",
        "but",
        "note",
        "warning",
        "error",
        "caution",
        "not applicable",
        "does not apply",
        "excluded",
        "unless",
        "except when",
        "exception",
        "caveat",
        "limitation",
        "constraint",
        "restriction",
    }
)

_SCOPE_KEYWORDS: frozenset[str] = frozenset(
    {
        "only",
        "all",
        "none",
        "within",
        "for",
        "applies to",
        "limited to",
        "specific to",
        "in scope",
        "out of scope",
        "includes",
        "excludes",
        "version",
        "release",
        "edition",
        "tier",
        "plan",
        "configuration",
    }
)

_TEMPORAL_KEYWORDS: frozenset[str] = frozenset(
    {
        "as of",
        "until",
        "since",
        "before",
        "after",
        "deprecated",
        "effective",
        "from",
        "through",
        "by",
        "no longer",
        "starting",
        "ending",
        "valid",
        "expires",
        "current",
        "legacy",
        "future",
    }
)


# ---------------------------------------------------------------------------
# Scorer Config
# ---------------------------------------------------------------------------


@dataclass
class CompletenessScorerConfig:
    """Configuration for the KeywordCompletetenessScorer.

    All keyword sets are frozensets for deterministic membership checks.
    """

    condition_keywords: frozenset[str] = field(default_factory=lambda: _CONDITION_KEYWORDS)
    exception_keywords: frozenset[str] = field(default_factory=lambda: _EXCEPTION_KEYWORDS)
    scope_keywords: frozenset[str] = field(default_factory=lambda: _SCOPE_KEYWORDS)
    temporal_keywords: frozenset[str] = field(default_factory=lambda: _TEMPORAL_KEYWORDS)
    dimension_weight: float = 0.25


# ---------------------------------------------------------------------------
# Concrete Implementation
# ---------------------------------------------------------------------------


class KeywordCompletenessScorer(IContextCompletenessScorer):
    """Keyword-based context completeness scorer.

    Detects missing context dimensions by checking whether the query contains
    signals for that dimension AND the chunk/parent content does NOT address it.

    Scoring logic:
      1. Determine which dimensions the QUERY signals (query_signals).
      2. For each signaled dimension, check if the CHUNK (+ parent) contains
         at least one keyword from that dimension's set.
      3. missing_X = query signals X AND chunk does not address X.
      4. completeness_score = 1 - (missing_count / max(1, signaled_count)).

    C0 RULE: Pure function — no side effects, no mutation, no wall-clock.
    """

    def __init__(self, config: CompletenessScorerConfig | None = None) -> None:
        self._cfg = config or CompletenessScorerConfig()

    def score(
        self,
        query_id: str,
        query: str,
        chunk: Document | GroundedDocument,
    ) -> ContextCompletenessScore:
        query_lower = query.lower()
        chunk_text = chunk.content.lower()

        if isinstance(chunk, GroundedDocument) and chunk.parent_content:
            chunk_text = chunk_text + " " + chunk.parent_content.lower()

        chunk_id = chunk.doc_id
        parent_id = chunk.parent_section_id if isinstance(chunk, GroundedDocument) else ""

        signals = self._detect_query_signals(query_lower)
        missing = self._detect_missing(signals, chunk_text)

        completeness = self._compute_completeness(signals, missing)

        return ContextCompletenessScore(
            query_id=query_id,
            chunk_id=chunk_id,
            parent_section_id=parent_id,
            relevance_score=round(float(chunk.score), 6),
            completeness_score=round(completeness, 6),
            missing_condition=missing["condition"],
            missing_exception=missing["exception"],
            missing_scope=missing["scope"],
            missing_temporal_qualifier=missing["temporal"],
            confidence=self._compute_confidence(signals),
        )

    def score_batch(
        self,
        query_id: str,
        query: str,
        chunks: list[Document | GroundedDocument],
    ) -> list[ContextCompletenessScore]:
        return [self.score(query_id, query, chunk) for chunk in chunks]

    # ------------------------------------------------------------------
    # Internal helpers — all deterministic, no side effects
    # ------------------------------------------------------------------

    def _detect_query_signals(self, query_lower: str) -> dict[str, bool]:
        """Detect which context dimensions the query signals."""
        return {
            "condition": self._has_keyword(query_lower, self._cfg.condition_keywords),
            "exception": self._has_keyword(query_lower, self._cfg.exception_keywords),
            "scope": self._has_keyword(query_lower, self._cfg.scope_keywords),
            "temporal": self._has_keyword(query_lower, self._cfg.temporal_keywords),
        }

    def _detect_missing(self, signals: dict[str, bool], chunk_text: str) -> dict[str, bool]:
        """For each signaled dimension, check if chunk addresses it."""
        return {
            "condition": signals["condition"]
            and not self._has_keyword(chunk_text, self._cfg.condition_keywords),
            "exception": signals["exception"]
            and not self._has_keyword(chunk_text, self._cfg.exception_keywords),
            "scope": signals["scope"] and not self._has_keyword(chunk_text, self._cfg.scope_keywords),
            "temporal": signals["temporal"]
            and not self._has_keyword(chunk_text, self._cfg.temporal_keywords),
        }

    def _compute_completeness(self, signals: dict[str, bool], missing: dict[str, bool]) -> float:
        signaled = sum(1 for v in signals.values() if v)
        if signaled == 0:
            return 1.0
        missing_count = sum(1 for v in missing.values() if v)
        return max(0.0, 1.0 - missing_count / signaled)

    def _compute_confidence(self, signals: dict[str, bool]) -> float:
        """Confidence is higher when more dimensions are signaled."""
        signaled = sum(1 for v in signals.values() if v)
        return min(1.0, 0.5 + 0.125 * signaled)

    @staticmethod
    def _has_keyword(text: str, keywords: frozenset[str]) -> bool:
        return any(kw in text for kw in keywords)


__all__ = [
    "CompletenessScorerConfig",
    "KeywordCompletenessScorer",
]
