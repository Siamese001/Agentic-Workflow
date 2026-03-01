"""ArbitrationEngine types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ArbitrationCandidate:
    id: str
    score: float
    cost: float
    kind: str
    payload: dict[str, Any]
    provenance: str = ""


@dataclass(frozen=True)
class ArbitrationPolicy:
    max_winners: int = 1
    min_score: float = 0.0
    prefer_lower_cost: bool = False
    weights: dict[str, float] = field(default_factory=dict)
    caps: dict[str, int] = field(default_factory=dict)
    thresholds: dict[str, float] = field(default_factory=dict)
    allowed_kinds: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ArbitrationDecision:
    winner_ids: tuple[str, ...]
    policy_digest: str
    deterministic_fingerprint: str = ""
    canonical_bytes: bytes = b""
