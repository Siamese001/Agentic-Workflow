"""HealingConfidenceScorer types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class HealingAttempt:
    attempt_id: str
    outcome: Literal["SUCCESS", "FAILURE", "PARTIAL"]
    severity: int
    cost: float


@dataclass(frozen=True)
class ConfidenceDecision:
    attempt_id: str
    action: Literal["ACCEPT", "REJECT", "ESCALATE"]
    confidence: float


@dataclass(frozen=True)
class ConfidenceReport:
    decisions: list[ConfidenceDecision]
