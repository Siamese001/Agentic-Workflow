"""HealingConfidenceScorer â€” maps healing attempt outcomes to ACCEPT/REJECT/ESCALATE."""

from __future__ import annotations

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
        "FAILURE": ("REJECT", 0.0),
    }

    def score(self, attempts: list[HealingAttempt]) -> ConfidenceReport:
        decisions = []
        for attempt in attempts:
            action, confidence = self._OUTCOME_MAP.get(attempt.outcome, ("REJECT", 0.0))
            decisions.append(
                ConfidenceDecision(
                    attempt_id=attempt.attempt_id,
                    action=action,
                    confidence=confidence,
                )
            )
        return ConfidenceReport(decisions=decisions)
