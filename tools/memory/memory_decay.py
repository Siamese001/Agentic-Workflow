"""Memory decay, reinforcement, and near-duplicate detection for the Memory MCP store.

Design
------
Memento MCP and yuvalsuede/memory-mcp (two production Claude memory servers)
converged on the same pattern:

  1. Every entity/observation has a stored confidence in [0, 1].
  2. A type-scoped half-life decides how fast confidence decays when not
     reinforced. Architectural facts never decay; short-lived progress
     notes decay fast.
  3. Reinforcement (re-reference or duplicate insert) resets
     `last_reinforced` to now and may bump confidence.
  4. Reads filter on EFFECTIVE confidence — the decayed value at read
     time — not the stored value. Stored values are never mutated by a
     read. Nothing is deleted until a separate consolidation pass.

Formula
-------
    effective = stored * 0.5 ** ((now - last_reinforced) / half_life)

Half-life is looked up by `entity_type`. For protected types (rules,
ADRs, invariants) half-life is `math.inf`, which short-circuits to
`effective == stored`.

Configuration via env
---------------------
    MEMORY_CONFIDENCE_THRESHOLD  float, default 0.3 — reads filter below this
    MEMORY_DECAY_DISABLED        "1" to disable decay entirely (debug/tests)
    MEMORY_HALF_LIFE_OVERRIDE    "type1=days,type2=days" to override map
"""

from __future__ import annotations

import math
import os
import re
import time
from typing import Final

_SECONDS_PER_DAY: Final[float] = 86_400.0

# Type-scoped half-lives in days. Informed by yuvalsuede/memory-mcp lifespans.
# math.inf = never decays.
HALF_LIFE_DAYS_BY_TYPE: Final[dict[str, float]] = {
    # Permanent — structural/governance facts
    "ConstitutionalRule": math.inf,
    "ArchitectureLayer": math.inf,
    "ArchitecturalDecision": math.inf,
    "ProceduralPattern": math.inf,
    # Medium-lived — current project state
    "ProjectContext": 60.0,
    "EpisodicEvent": 30.0,
    # Short-lived — ephemeral scratch
    "general": 14.0,
}

# Effective confidence below this is hidden from reads but NOT deleted.
DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.3


def _load_half_life_overrides() -> dict[str, float]:
    """Parse MEMORY_HALF_LIFE_OVERRIDE env ('type1=days,type2=days')."""
    raw = os.environ.get("MEMORY_HALF_LIFE_OVERRIDE", "").strip()
    if not raw:
        return {}
    out: dict[str, float] = {}
    for chunk in raw.split(","):
        if "=" not in chunk:
            continue
        k, v = chunk.split("=", 1)
        k = k.strip()
        try:
            out[k] = float(v.strip())
        except ValueError:
            continue
    return out


def half_life_seconds(entity_type: str) -> float:
    """Half-life in seconds for a given entity type. Unknown types default to 'general'."""
    overrides = _load_half_life_overrides()
    if entity_type in overrides:
        days = overrides[entity_type]
    else:
        days = HALF_LIFE_DAYS_BY_TYPE.get(entity_type, HALF_LIFE_DAYS_BY_TYPE["general"])
    if math.isinf(days):
        return math.inf
    return days * _SECONDS_PER_DAY


def effective_confidence(
    stored_confidence: float,
    last_reinforced: float,
    entity_type: str,
    now: float | None = None,
) -> float:
    """Return decayed confidence at read time. Stored row is never mutated.

    Args:
        stored_confidence: The confidence value written to the DB, in [0, 1].
        last_reinforced:   Unix epoch seconds of last reinforcement.
        entity_type:       Drives the half-life lookup.
        now:               Current Unix epoch; defaults to time.time().

    Returns:
        Effective confidence in [0, 1]. Clamped.
    """
    if os.environ.get("MEMORY_DECAY_DISABLED") == "1":
        return float(max(0.0, min(1.0, stored_confidence)))
    if stored_confidence <= 0.0:
        return 0.0
    hl = half_life_seconds(entity_type)
    if math.isinf(hl):
        return float(max(0.0, min(1.0, stored_confidence)))
    if now is None:
        now = time.time()
    age = max(0.0, now - last_reinforced)
    decayed = stored_confidence * (0.5 ** (age / hl))
    return float(max(0.0, min(1.0, decayed)))


def confidence_threshold() -> float:
    """Current read-time threshold — rows below this are hidden."""
    raw = os.environ.get("MEMORY_CONFIDENCE_THRESHOLD", "").strip()
    if not raw:
        return DEFAULT_CONFIDENCE_THRESHOLD
    try:
        v: float = float(raw)
    except ValueError:
        return DEFAULT_CONFIDENCE_THRESHOLD
    return float(max(0.0, min(1.0, v)))


def reinforced_confidence(
    stored_confidence: float,
    last_reinforced: float,
    entity_type: str,
    now: float | None = None,
    bump: float = 0.1,
) -> float:
    """Compute the new stored confidence after a reinforcement event.

    Rule: take the CURRENT effective confidence (decayed), add a fixed bump,
    clamp to [0, 1]. Prevents infinite growth while rewarding use.
    """
    eff = effective_confidence(stored_confidence, last_reinforced, entity_type, now)
    return float(max(0.0, min(1.0, eff + bump)))


JACCARD_DEDUP_THRESHOLD: Final[float] = 0.60


def _tokenize(text: str) -> frozenset[str]:
    """Cheap tokenizer for Jaccard similarity.

    Lowercase, split on non-alphanumeric, drop tokens shorter than 3 chars
    (trivial stop-word filter — "a", "is", "of" don't carry signal).
    Returned as frozenset so the caller can cache for O(1) reuse.
    """
    if not text:
        return frozenset()
    tokens = re.split(r"[^a-z0-9]+", text.lower())
    return frozenset(t for t in tokens if len(t) >= 3)


def jaccard_similarity(a: str, b: str) -> float:
    """Jaccard similarity over tokenized texts.

    Returns 0.0 for empty inputs or disjoint sets; 1.0 for identical token
    sets after normalization. Cheap O(|a| + |b|) — no embedding required.

    Per yuvalsuede/memory-mcp: a 0.60 overlap threshold reliably catches
    restated facts while preserving genuinely-different observations.
    """
    sa = _tokenize(a)
    sb = _tokenize(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    if union == 0:
        return 0.0
    return inter / union


def jaccard_threshold() -> float:
    """Env-configurable Jaccard dedup threshold."""
    raw = os.environ.get("MEMORY_JACCARD_THRESHOLD", "").strip()
    if not raw:
        return JACCARD_DEDUP_THRESHOLD
    try:
        v: float = float(raw)
    except ValueError:
        return JACCARD_DEDUP_THRESHOLD
    return float(max(0.0, min(1.0, v)))


__all__ = [
    "HALF_LIFE_DAYS_BY_TYPE",
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "JACCARD_DEDUP_THRESHOLD",
    "confidence_threshold",
    "effective_confidence",
    "half_life_seconds",
    "jaccard_similarity",
    "jaccard_threshold",
    "reinforced_confidence",
]
