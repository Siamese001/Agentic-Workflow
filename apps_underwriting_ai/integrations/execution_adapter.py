"""
Execution Adapter - Handles execution handoff to agentic_core.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from ..engines.underwriting_engine import UnderwritingResult
from ..types import UnderwritingRequest


def _model_to_dict(model: Optional[Any]) -> Dict[str, Any]:
    """Support both Pydantic v1 and v2 serialization APIs."""
    if model is None:
        return {}
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    return {}


# L1 retrieval wiring (Turn 2, Wave 11): Import creates ADG edge to L1_cognition

# L2 retrieval wiring (Turn 2, Wave 13): Import creates ADG edge to L2_execution

# L3 retrieval wiring (Turn 2, Wave 20): Import creates ADG edge to L3_orchestration

# L4 retrieval wiring (Turn 3, Wave 26): Import creates ADG edge to L4_state

# L5 retrieval wiring (Turn 3, Wave 33): Import creates ADG edge to L5_safety


@dataclass
class ExecutionRequest:
    """Request for execution handoff."""

    app_name: str = "apps_underwriting_ai"
    request_id: str = ""
    intent_type: str = "underwriting_decision"
    priority: str = "normal"
    sla_deadline: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)


class ExecutionAdapter:
    """
    Adapter for execution handoff to agentic_core L2 execution layer.

    Responsibilities:
    - Package execution request
    - Set appropriate priority and SLA
    - Prepare for L2 execution authority
    """

    def create_execution_request(
        self,
        request: UnderwritingRequest,
        result: UnderwritingResult,
    ) -> ExecutionRequest:
        """
        Create execution request for core handoff.

        Args:
            request: Original UnderwritingRequest
            result: UnderwritingResult from engine

        Returns:
            ExecutionRequest
        """
        exec_request = ExecutionRequest()
        exec_request.request_id = request.request_id
        exec_request.payload = {
            "domain_result": {
                "decision": result.decision,
                "confidence": result.confidence_score,
                "human_review_required": result.human_review_required,
                "human_review_reason": result.human_review_reason,
            },
            "decision_memo": _model_to_dict(result.decision_memo),
            "decision_packet": _model_to_dict(result.decision_packet),
            "audit_trace": _model_to_dict(result.audit_trace),
            "risk_features": _model_to_dict(result.risk_features),
        }

        # Set priority based on SLA
        if request.decision_constraints.turnaround_sla_hours <= 24:
            exec_request.priority = "high"
        elif request.decision_constraints.turnaround_sla_hours <= 48:
            exec_request.priority = "normal"
        else:
            exec_request.priority = "low"

        # Calculate SLA deadline
        deadline = datetime.now(timezone.utc) + timedelta(
            hours=request.decision_constraints.turnaround_sla_hours
        )
        exec_request.sla_deadline = deadline.isoformat()

        return exec_request

    def to_execution_payload(self, exec_request: ExecutionRequest) -> Dict[str, Any]:
        """Convert to execution payload format."""
        return {
            "app_source": exec_request.app_name,
            "request_id": exec_request.request_id,
            "intent_type": exec_request.intent_type,
            "priority": exec_request.priority,
            "sla_deadline": exec_request.sla_deadline,
            "payload": exec_request.payload,
        }
