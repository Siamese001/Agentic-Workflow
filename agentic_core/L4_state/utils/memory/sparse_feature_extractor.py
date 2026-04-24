"""Sparse feature extraction for R1B hybrid semantic cache reuse.

Implements G1 (hybrid dense+sparse fusion at reuse time) per Author-Gate
decision 2026-04-23, Option A (Per-row sparse features).

At ``learn()`` time, a cached query's high-signal tokens (entities, cardinal
numbers, ISO dates, acronyms, proper-noun runs) are extracted and stored in
``_metadata.sparse_features``. At ``recall()`` time, the same extraction is
run over the incoming query and a Jaccard overlap score is computed against
the cached features. The fused score

    fused = dense_weight * cosine + sparse_weight * jaccard

is then compared to the hybrid threshold before the cache is allowed to
short-circuit.

Design contract (R1B §R1B.2-R1B.3 failure modes it must prevent):
- "annual" vs "monthly" — different content words.
- "Q3 2025" vs "Q4 2025" — different cardinal/quarter tokens.
- "Okta" vs "Auth0" — different proper-noun entities.

The extractor is deterministic, dependency-free (stdlib `re` only), and
fail-safe: empty feature sets collapse hybrid scoring back to pure dense
(backward-compatible with pre-G1 rows). No PII risk — extraction runs AFTER
``PII_Sanitizer.sanitize`` has already redacted sensitive values.
"""

from __future__ import annotations

import re
from typing import Iterable

_RE_NUMBER = re.compile(r"\b(?:Q[1-4]|\d+(?:\.\d+)?)\b")
_RE_DATE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|20\d{2})\b",
)
_RE_ALL_CAPS = re.compile(r"\b[A-Z]{2,}(?:[0-9]+)?\b")
_RE_PROPER = re.compile(r"\b[A-Z][a-zA-Z]*(?:[0-9]+|-[A-Z0-9]+)?\b")

_STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "of", "to", "and", "or", "for", "on", "in", "at", "by", "with", "as",
        "it", "this", "that", "these", "those", "do", "does", "did",
        "how", "what", "which", "who", "when", "where", "why",
    },
)

_MAX_FEATURES: int = 64


def extract_features(text: str) -> list[str]:
    """Extract the deterministic sparse-feature set from *text*.

    Returns a lowercase-normalized, sorted, de-duplicated list of
    high-signal tokens. Empty input → empty list. Callers should treat an
    empty list as a signal to fall back to pure dense scoring.
    """
    if not text:
        return []
    features: set[str] = set()
    for pattern in (_RE_NUMBER, _RE_DATE, _RE_ALL_CAPS, _RE_PROPER):
        for match in pattern.findall(text):
            token = match.strip()
            if not token:
                continue
            normalized = token.lower()
            if normalized in _STOPWORDS:
                continue
            if len(normalized) < 2:
                continue
            features.add(normalized)
    return sorted(features)[:_MAX_FEATURES]


def jaccard_overlap(left: Iterable[str], right: Iterable[str]) -> float:
    """Compute Jaccard similarity in [0.0, 1.0] between two feature sets."""
    left_set = set(left) if not isinstance(left, set) else left
    right_set = set(right) if not isinstance(right, set) else right
    if not left_set or not right_set:
        return 0.0
    intersection = left_set & right_set
    if not intersection:
        return 0.0
    union = left_set | right_set
    return len(intersection) / len(union)


def fused_score(
    dense_score: float,
    sparse_score: float,
    dense_weight: float = 0.7,
    sparse_weight: float = 0.3,
) -> float:
    """Combine dense cosine and sparse Jaccard into a single reuse score."""
    return dense_weight * float(dense_score) + sparse_weight * float(sparse_score)


__all__ = ["extract_features", "fused_score", "jaccard_overlap"]
