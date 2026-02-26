"""ArbitrationEngine types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArbitrationCandidate:
    id: str
    score: float
    cost: float
    kind: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ArbitrationPolicy:
    max_winners: int = 1
    min_score: float = 0.0
    prefer_lower_cost: bool = False


@dataclass(frozen=True)
class ArbitrationDecision:
    winner_ids: list[str]
    policy_digest: str
