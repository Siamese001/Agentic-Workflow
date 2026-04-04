"""
Decision Packet Assembler - Merges hypothesis, features, validators into decision outputs.
"""
from typing import List, Optional
from dataclasses import dataclass, field

from ..types import (
    UnderwritingRequest,
    RiskFeatures,
    DecisionMemo,
    DecisionPacket,
    AuditTrace,
    EvidenceItem,
    DecisionState,
)
from ..engines.evidence_register_engine import EvidenceRegister

# L4 retrieval wiring (Turn 3, Wave 37): Import creates ADG edge to L4_state


@dataclass
class AssemblerInput:
    """Input for decision packet assembly."""
    request: UnderwritingRequest
    features: RiskFeatures
    recommended_decision: DecisionState
    conditions: List[str] = field(default_factory=list)
    covenants: List[str] = field(default_factory=list)
    key_strengths: List[str] = field(default_factory=list)
    key_risks: List[str] = field(default_factory=list)
    policy_exceptions: List[str] = field(default_factory=list)
    missing_info: List[str] = field(default_factory=list)
    evidence_register: Optional[EvidenceRegister] = None
    human_review_reason: Optional[str] = None
    confidence_score: float = 0.0


class DecisionPacketAssembler:
    """
    Assembles final decision outputs from all underwriting components.

    Creates:
    - DecisionMemo (human-readable recommendation)
    - DecisionPacket (machine-readable output)
    - AuditTrace (compliance record)
    """

    def assemble(
        self,
        input_data: AssemblerInput
    ) -> tuple[DecisionMemo, DecisionPacket, AuditTrace]:
        """
        Assemble all decision outputs.

        Args:
            input_data: AssemblerInput with all components

        Returns:
            Tuple of (DecisionMemo, DecisionPacket, AuditTrace)
        """
        # Build DecisionMemo
        memo = self._build_decision_memo(input_data)

        # Build DecisionPacket
        packet = self._build_decision_packet(input_data)

        # Build AuditTrace
        trace = self._build_audit_trace(input_data)

        return memo, packet, trace

    def _build_decision_memo(self, input_data: AssemblerInput) -> DecisionMemo:
        """Build human-readable decision memo."""
        request = input_data.request
        features = input_data.features

        # Build evidence items from register
        evidence_items = []
        if input_data.evidence_register:
            for entry in input_data.evidence_register.entries:
                evidence_items.append(EvidenceItem(
                    claim_id=entry.entry_id,
                    claim_text=entry.claim_text,
                    evidence_type=entry.evidence_type,
                    source_ref=entry.evidence_source,
                    source_excerpt=entry.supporting_excerpt,
                    confidence=entry.confidence
                ))

        memo = DecisionMemo(
            request_id=request.request_id,
            recommended_decision=input_data.recommended_decision,
            recommended_amount=request.requested_amount if input_data.recommended_decision in ["APPROVE", "APPROVE_WITH_CONDITIONS", "COUNTER_OFFER"] else None,
            recommended_term_months=request.requested_term_months if input_data.recommended_decision in ["APPROVE", "APPROVE_WITH_CONDITIONS", "COUNTER_OFFER"] else None,
            conditions_precedent=input_data.conditions,
            covenants=input_data.covenants,
            key_strengths=input_data.key_strengths,
            key_risks=input_data.key_risks,
            policy_exceptions=input_data.policy_exceptions,
            missing_information=input_data.missing_info,
            evidence_register=evidence_items,
            confidence_score=input_data.confidence_score,
            human_review_reason=input_data.human_review_reason
        )

        return memo

    def _build_decision_packet(self, input_data: AssemblerInput) -> DecisionPacket:
        """Build machine-readable decision packet."""
        request = input_data.request

        # Build recommended structure
        recommended_structure = {
            "amount": request.requested_amount if input_data.recommended_decision in ["APPROVE", "APPROVE_WITH_CONDITIONS", "COUNTER_OFFER"] else None,
            "term_months": request.requested_term_months if input_data.recommended_decision in ["APPROVE", "APPROVE_WITH_CONDITIONS", "COUNTER_OFFER"] else None,
            "amortization_months": request.requested_structure.amortization_months,
            "interest_type": request.requested_structure.interest_type,
            "collateral_required": request.requested_structure.collateral_required,
            "guarantor_required": request.requested_structure.guarantor_required,
        }

        # Determine if human review is required
        review_required = (
            input_data.recommended_decision == "ESCALATE_TO_HUMAN" or
            input_data.human_review_reason is not None
        )

        packet = DecisionPacket(
            request_id=request.request_id,
            decision_state=input_data.recommended_decision,
            recommended_structure=recommended_structure,
            conditions=input_data.conditions,
            covenants=input_data.covenants,
            exception_flags=input_data.policy_exceptions,
            confidence_score=input_data.confidence_score,
            review_required=review_required,
            review_reason=input_data.human_review_reason
        )

        return packet

    def _build_audit_trace(self, input_data: AssemblerInput) -> AuditTrace:
        """Build compliance audit trace."""
        request = input_data.request

        # Build evidence references
        evidence_refs = []
        if input_data.evidence_register:
            for entry in input_data.evidence_register.entries:
                evidence_refs.append({
                    "entry_id": entry.entry_id,
                    "claim_category": entry.claim_category,
                    "evidence_source": entry.evidence_source,
                    "confidence": entry.confidence
                })

        trace = AuditTrace(
            request_id=request.request_id,
            trace_id=f"trace-{request.request_id}",  # Would be set by core
            policy_hash=request.policy_context.policy_version if request.policy_context else None,
            derived_features=input_data.features,
            evidence_refs=evidence_refs,
            validators_run=[],  # Would be populated by validator execution
            routing_outcome=None,  # Would be set by core
            decision_proposal=input_data.recommended_decision,
            human_review_triggered=input_data.human_review_reason is not None,
            determinism_digest=None  # Would be set by core
        )

        return trace
