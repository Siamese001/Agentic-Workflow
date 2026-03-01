"""HealingConfidenceScorer — maps healing attempt outcomes to ACCEPT/REJECT/ESCALATE."""

from __future__ import annotations

import hashlib
import json

from system_learning.engines.confidence.types import (
    ConfidenceDecision,
    ConfidenceReport,
    HealingAttempt,
)


class HealingConfidenceScorer:
    """Score a batch of HealingAttempts and produce a ConfidenceReport."""

    _OUTCOME_MAP = {
        "SUCCESS": ("ACCEPT", 1.0),
        "PARTIAL": ("ESCALATE", 0.5),
        "FAILURE": ("ESCALATE", 0.3),
        "FAIL": ("REVIEW", 0.1),
    }

    def score(self, attempts: list[HealingAttempt]) -> ConfidenceReport:
        if not isinstance(attempts, list):
            raise TypeError(f"attempts must be a list, got {type(attempts).__name__}")
        for attempt in attempts:
            if not isinstance(attempt, HealingAttempt):
                raise TypeError(f"each attempt must be HealingAttempt, got {type(attempt).__name__}")
        sorted_attempts = sorted(attempts, key=lambda a: a.attempt_id)
        decisions = []
        for attempt in sorted_attempts:
            action, confidence = self._OUTCOME_MAP.get(attempt.outcome, ("REVIEW", 0.1))
            decisions.append(
                ConfidenceDecision(
                    attempt_id=attempt.attempt_id,
                    action=action,
                    confidence=confidence,
                )
            )
        canonical = json.dumps(
            {
                "decisions": [
                    {"attempt_id": d.attempt_id, "action": d.action, "confidence": d.confidence}
                    for d in decisions
                ]
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        canonical_bytes = canonical.encode("ascii")
        fingerprint = hashlib.sha256(canonical_bytes).hexdigest()
        return ConfidenceReport(
            decisions=decisions, confidence_fingerprint=fingerprint, canonical_bytes=canonical_bytes
        )
