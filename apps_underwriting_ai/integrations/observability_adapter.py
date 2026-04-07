"""
Observability Adapter - Emits app-specific telemetry fields.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ..types import DecisionMemo, UnderwritingRequest


@dataclass
class UnderwritingTelemetry:
    """Telemetry data for underwriting request."""
    request_id: str = ""
    product_type: str = ""
    decision_type: str = ""
    doc_count: int = 0
    contradiction_count: int = 0
    policy_exception_count: int = 0
    recommended_decision: str = ""
    confidence_score: float = 0.0
    review_required: bool = False
    timestamp: str = ""
    duration_ms: Optional[int] = None


class ObservabilityAdapter:
    """
    Adapter for observability and telemetry.

    Emits:
    - request_id
    - product_type
    - decision_type
    - doc_count
    - contradiction_count
    - policy_exception_count
    - recommended_decision
    - confidence_score
    - review_required

    Does not replace existing L6 observability.
    """

    def emit_telemetry(
        self,
        request: UnderwritingRequest,
        memo: DecisionMemo,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UnderwritingTelemetry:
        """
        Emit underwriting-specific telemetry.

        Args:
            request: UnderwritingRequest
            memo: DecisionMemo
            metadata: Optional processing metadata

        Returns:
            UnderwritingTelemetry
        """
        telemetry = UnderwritingTelemetry()
        telemetry.request_id = request.request_id
        telemetry.product_type = request.product_type
        telemetry.decision_type = request.decision_type
        telemetry.doc_count = request.documents.total_doc_count
        telemetry.recommended_decision = memo.recommended_decision
        telemetry.confidence_score = memo.confidence_score
        telemetry.review_required = memo.human_review_reason is not None
        telemetry.timestamp = datetime.now().isoformat()

        if metadata:
            telemetry.contradiction_count = metadata.get("contradiction_count", 0)
            telemetry.policy_exception_count = metadata.get("policy_exception_count", 0)
            telemetry.duration_ms = metadata.get("duration_ms")

        return telemetry

    def to_metrics_dict(self, telemetry: UnderwritingTelemetry) -> Dict[str, Any]:
        """Convert telemetry to metrics dictionary for emission."""
        return {
            "metric_type": "underwriting_decision",
            "request_id": telemetry.request_id,
            "dimensions": {
                "product_type": telemetry.product_type,
                "decision_type": telemetry.decision_type,
                "recommended_decision": telemetry.recommended_decision,
                "review_required": telemetry.review_required,
            },
            "metrics": {
                "doc_count": telemetry.doc_count,
                "contradiction_count": telemetry.contradiction_count,
                "policy_exception_count": telemetry.policy_exception_count,
                "confidence_score": telemetry.confidence_score,
                "duration_ms": telemetry.duration_ms,
            },
            "timestamp": telemetry.timestamp,
        }
