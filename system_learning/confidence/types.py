"""Healing confidence scoring types for deterministic escalation decisions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True)
class HealingAttempt:
    """A healing attempt for confidence scoring."""

    attempt_id: str
    healer_id: str
    outcome: str  # SUCCESS, PARTIAL, FAIL
    severity: int
    signals: dict[str, str]
    cost: float

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        data = {
            "attempt_id": self.attempt_id,
            "healer_id": self.healer_id,
            "outcome": self.outcome,
            "severity": self.severity,
            "signals": {k: str(v) for k, v in sorted(self.signals.items())},
            "cost": self.cost,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ConfidenceDecision:
    """Confidence decision for a healing attempt."""

    attempt_id: str
    confidence: float
    action: str  # ESCALATE, REVIEW, ACCEPT


@dataclass(frozen=True)
class HealingConfidenceReport:
    """Report of healing confidence scoring with deterministic fingerprint."""

    decisions: list[ConfidenceDecision]
    confidence_fingerprint: str
    canonical_bytes: bytes

    @classmethod
    def from_canonical_bytes(
        cls,
        decisions: list[ConfidenceDecision],
        canonical_bytes: bytes,
    ) -> HealingConfidenceReport:
        """Create report from canonical bytes."""
        confidence_fingerprint = hashlib.sha256(canonical_bytes).hexdigest()
        return cls(
            decisions=decisions,
            confidence_fingerprint=confidence_fingerprint,
            canonical_bytes=canonical_bytes,
        )
