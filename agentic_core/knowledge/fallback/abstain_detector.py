"""Abstain Detector.

Insufficient support detection, grounding verification, and abstain vs clarify decision logic.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class AbstainAction(Enum):
    """Action to take when abstaining."""
    ABSTAIN = "abstain"
    CLARIFY = "clarify"
    FALLBACK = "fallback"


@dataclass
class AbstainDecision:
    """Decision to abstain or proceed."""
    should_abstain: bool
    action: AbstainAction
    reason: str
    confidence: float
    support_score: float
    grounding_verified: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class AbstainDetector:
    """Detects when to abstain from answering.

    The AbstainDetector evaluates evidence support and grounding to
    determine when the system should abstain or request clarification.
    """

    def __init__(
        self,
        min_support_score: float = 0.3,
        min_confidence: float = 0.5,
        grounding_threshold: float = 0.6,
    ):
        """Initialize the abstain detector.

        Args:
            min_support_score: Minimum evidence support required
            min_confidence: Minimum confidence threshold
            grounding_threshold: Minimum grounding score
        """
        self.min_support_score = min_support_score
        self.min_confidence = min_confidence
        self.grounding_threshold = grounding_threshold

        log.info(f"AbstainDetector initialized (min_support={min_support_score})")

    def evaluate(
        self,
        query: str,
        evidence_contract: Any,
        query_context: dict[str, Any],
    ) -> AbstainDecision:
        """Evaluate whether to abstain.

        Args:
            query: Original query
            evidence_contract: Evidence contract with citations
            query_context: Query context

        Returns:
            AbstainDecision with recommendation
        """
        trace_id = f"abstain_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "AbstainDetector.evaluate",
        )

        # Extract support score
        support_score = getattr(evidence_contract, 'support_score', 0.0)

        # Check grounding
        grounding_verified = getattr(evidence_contract, 'provenance_verified', False)

        # Calculate confidence
        confidence = self._calculate_confidence(support_score, grounding_verified)

        # Determine if should abstain
        should_abstain = False
        reason = "Sufficient support available"
        action = AbstainAction.ABSTAIN

        if support_score < self.min_support_score:
            should_abstain = True
            reason = f"Insufficient support: {support_score:.2f} < {self.min_support_score}"

            # Decide between abstain and clarify
            if self._should_clarify(query, query_context):
                action = AbstainAction.CLARIFY
            else:
                action = AbstainAction.ABSTAIN

        elif not grounding_verified and confidence < self.min_confidence:
            should_abstain = True
            reason = "Grounding not verified and low confidence"
            action = AbstainAction.FALLBACK

        decision = AbstainDecision(
            should_abstain=should_abstain,
            action=action,
            reason=reason,
            confidence=confidence,
            support_score=support_score,
            grounding_verified=grounding_verified,
            metadata={
                "min_support_score": self.min_support_score,
                "grounding_threshold": self.grounding_threshold,
            },
        )

        _emit_records_telemetry_event(
            "abstain_decision",
            f"{action.value}_{'abstain' if should_abstain else 'proceed'}",
        )

        log.debug(f"Abstain decision: {action.value} (should_abstain={should_abstain})")
        return decision

    def _calculate_confidence(self, support_score: float, grounding_verified: bool) -> float:
        """Calculate overall confidence."""
        base_confidence = support_score

        if grounding_verified:
            base_confidence *= 1.2  # Boost for verified grounding

        return min(base_confidence, 1.0)

    def _should_clarify(self, query: str, context: dict[str, Any]) -> bool:
        """Determine if clarification should be requested."""
        # Clarify if query is ambiguous or vague
        vague_indicators = ['something', 'anything', 'whatever', 'etc']

        query_lower = query.lower()
        vague_count = sum(1 for w in vague_indicators if w in query_lower)

        return vague_count > 0 or len(query.split()) < 3


# Global instance
_global_detector: AbstainDetector | None = None


def get_abstain_detector() -> AbstainDetector:
    """Get or create the global abstain detector."""
    global _global_detector
    if _global_detector is None:
        _global_detector = AbstainDetector()
    return _global_detector
