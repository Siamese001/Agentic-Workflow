"""
Core Adapter - Packages app results for handoff to agentic_core.
"""

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from ..types import AuditTrace, DecisionMemo, DecisionPacket, UnderwritingRequest


def _model_to_dict(model: Optional[Any]) -> Dict[str, Any]:
    """Support both Pydantic v1 and v2 serialization APIs."""
    if model is None:
        return {}
    if hasattr(model, "model_dump"):
        return model.model_dump()
    if hasattr(model, "dict"):
        return model.dict()
    return {}


@dataclass
class CoreHandoffPayload:
    """Payload prepared for handoff to agentic_core."""

    app_name: str = "apps_underwriting_ai"
    request_id: str = ""
    domain_recommendation: str = ""
    confidence_score: float = 0.0
    decision_packet: Optional[Dict[str, Any]] = None
    audit_metadata: Dict[str, Any] = field(default_factory=dict)
    routing_hints: Dict[str, Any] = field(default_factory=dict)
    governance_context: Dict[str, Any] = field(default_factory=dict)


class CoreAdapter:
    """
    Adapter for handoff to agentic_core routing, governance, and execution.

    Responsibilities:
    - Package app result into consumable form
    - Separate app-level recommendation from core-level authority
    - Prepare metadata for observability and trace systems
    - Do not duplicate trace_id or policy_hash issuance
    """

    @traces_execute(layer="L4_STATE")
    def prepare_handoff(
        self,
        request: UnderwritingRequest,
        memo: DecisionMemo,
        packet: DecisionPacket,
        trace: AuditTrace,
    ) -> CoreHandoffPayload:
        """
        Prepare handoff payload for agentic_core.

        Args:
            request: Original UnderwritingRequest
            memo: DecisionMemo
            packet: DecisionPacket
            trace: AuditTrace

        Returns:
            CoreHandoffPayload
        """
        payload = CoreHandoffPayload()
        payload.request_id = request.request_id
        payload.domain_recommendation = memo.recommended_decision
        payload.confidence_score = memo.confidence_score

        # Convert packet to dict for serialization
        payload.decision_packet = self._packet_to_dict(packet)

        # Build audit metadata
        payload.audit_metadata = {
            "derived_features": _model_to_dict(trace.derived_features),
            "evidence_count": len(trace.evidence_refs),
            "validators_run": trace.validators_run,
            "human_review_triggered": trace.human_review_triggered,
        }

        # Build routing hints
        payload.routing_hints = {
            "product_type": request.product_type,
            "decision_type": request.decision_type,
            "requested_amount": request.requested_amount,
            "risk_grade": trace.derived_features.composite.normalized_risk_grade
            if trace.derived_features
            else None,
            "review_required": packet.review_required,
        }

        # Build governance context
        payload.governance_context = {
            "policy_version": trace.policy_hash,
            "exception_count": len(memo.policy_exceptions),
            "conditions_count": len(memo.conditions_precedent),
            "covenants_count": len(memo.covenants),
        }

        return payload

    def _packet_to_dict(self, packet: DecisionPacket) -> Dict[str, Any]:
        """Convert DecisionPacket to dictionary."""
        return {
            "request_id": packet.request_id,
            "decision_state": packet.decision_state,
            "recommended_structure": packet.recommended_structure,
            "pricing_adjustment_bps": packet.pricing_adjustment_bps,
            "conditions": packet.conditions,
            "covenants": packet.covenants,
            "exception_flags": packet.exception_flags,
            "confidence_score": packet.confidence_score,
            "review_required": packet.review_required,
            "review_reason": packet.review_reason,
        }

    def create_domain_request_payload(
        self,
        request: UnderwritingRequest,
    ) -> Dict[str, Any]:
        """Create L1 domain request payload for core routing."""
        return {
            "intent_type": "underwriting_decision",
            "app_source": "apps_underwriting_ai",
            "request_id": request.request_id,
            "payload_type": "UnderwritingRequest",
            "payload_summary": {
                "borrower": request.borrower.legal_name,
                "amount": request.requested_amount,
                "product": request.product_type,
                "decision_type": request.decision_type,
            },
        }


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.integrations.core_adapter', "module_loaded")
