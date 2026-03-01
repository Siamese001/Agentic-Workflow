"""HealingConfidenceScorer types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class HealingAttempt:
    attempt_id: str
    outcome: Literal["SUCCESS", "FAILURE", "PARTIAL", "FAIL"]
    severity: int
    cost: float
    healer_id: str = ""
    signals: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConfidenceDecision:
    attempt_id: str
    action: Literal["ACCEPT", "REJECT", "ESCALATE", "REVIEW"]
    confidence: float


@dataclass(frozen=True)
class ConfidenceReport:
    decisions: list[ConfidenceDecision]
    confidence_fingerprint: str = ""
    canonical_bytes: bytes = b""
