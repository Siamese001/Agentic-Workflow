"""Healing confidence scoring engine for deterministic escalation decisions."""

from __future__ import annotations

import json
from typing import Sequence

from .types import ConfidenceDecision, HealingAttempt, HealingConfidenceReport
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class HealingConfidenceScorer:
    """Deterministic healing confidence scorer for escalation decisions."""

    def __init__(self):
        """Initialize confidence scorer with deterministic parameters."""
        self._outcome_scores = {"SUCCESS": 0.8, "PARTIAL": 0.5, "FAIL": 0.2}
        # guardian: allow-magic-config
        self._escalate_threshold = 0.33
        # guardian: allow-magic-config
        self._review_threshold = 0.66

    def score(self, attempts: Sequence[HealingAttempt]) -> HealingConfidenceReport:
        """Score healing attempts and generate confidence report."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingConfidenceScorer.score")

        if attempts is None:
            raise TypeError("Attempts cannot be None")
        if not attempts:
            return HealingConfidenceReport.from_canonical_bytes([], b"{}")
        for attempt in attempts:
            if not isinstance(attempt, HealingAttempt):
                raise TypeError(f"All attempts must be HealingAttempt objects, got {type(attempt)}")
            if not attempt.attempt_id:
                raise ValueError("Attempt ID cannot be empty")
            if attempt.outcome not in self._outcome_scores:
                raise ValueError(f"Unknown outcome: {attempt.outcome}")
        sorted_attempts = sorted(attempts, key=lambda a: a.attempt_id)
        decisions = []
        for attempt in sorted_attempts:
            confidence = self._calculate_confidence(attempt)
            action = self._map_confidence_to_action(confidence)
            decisions.append(
                ConfidenceDecision(attempt_id=attempt.attempt_id, confidence=confidence, action=action)
            )
        canonical_data = {
            "decisions": [
                {"attempt_id": d.attempt_id, "confidence": d.confidence, "action": d.action}
                for d in decisions
            ]
        }
        canonical_bytes = json.dumps(canonical_data, separators=(",", ":"), sort_keys=True).encode("ascii")
        return HealingConfidenceReport.from_canonical_bytes(decisions, canonical_bytes)

    def _calculate_confidence(self, attempt: HealingAttempt) -> float:
        """Calculate confidence score for a single attempt."""
        base_score = self._outcome_scores[attempt.outcome]
        severity_penalty = min(attempt.severity * 0.1, 0.5)
        cost_penalty = min(attempt.cost * 0.05, 0.3)
        confidence = base_score - severity_penalty - cost_penalty
        if attempt.outcome == "SUCCESS":
            min_confidence = self._outcome_scores["PARTIAL"] - 0.1
            confidence = max(confidence, min_confidence)
        elif attempt.outcome == "FAIL":
            max_confidence = self._outcome_scores["PARTIAL"] + 0.1
            confidence = min(confidence, max_confidence)
        return max(0.0, min(1.0, confidence))

    def _map_confidence_to_action(self, confidence: float) -> str:
        """Map confidence score to action deterministically."""
        if confidence < self._escalate_threshold:
            return "ESCALATE"
        elif confidence < self._review_threshold:
            return "REVIEW"
        else:
            return "ACCEPT"
