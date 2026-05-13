"""W10 — Future Run Proposal Builder (Core-Owned)

Builds inert proposal packets for future-run activation.
All proposals require UWG review and proof before activation.

Hard Rules:
- All proposals are inert
- Activation only for future runs
- Requires replay/regression/safety proof
- Rollback plan required
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

from agentic_core.L6_learning import (
    ProposalPacket,
    FutureRunPromotionRequest,
    ProposalType,
    ProofType,
    CompletedEvalRecord,
)


@dataclass(frozen=True)
class ProposalConfig:
    """Config for proposal building."""
    min_confidence_threshold: float = 0.7
    require_rollback_plan: bool = True
    auto_promote_high_confidence: bool = False  # Never auto-promote


class FutureRunProposalBuilder:
    """Builds inert future-run proposals.
    
    Core owns proposal logic. Apps provide proposal policy config.
    """
    
    def __init__(self, config: ProposalConfig):
        self._config = config
    
    def build_proposals(
        self,
        eval_record: CompletedEvalRecord
    ) -> List[ProposalPacket]:
        """Build proposal packets from completed eval record.
        
        Args:
            eval_record: Learning observations from completed run
            
        Returns:
            List of inert ProposalPackets
        """
        proposals = []
        
        # Entity alias proposals
        if eval_record.entity_alias_observations.get('alias_candidates'):
            proposals.append(self._build_entity_alias_proposal(eval_record))
        
        # Source reliability proposals
        if eval_record.source_reliability_signals:
            proposals.append(self._build_source_reliability_proposal(eval_record))
        
        # Cache threshold proposals
        cache_hints = eval_record.cache_threshold_proposals
        if cache_hints.get('threshold_adjustment_hint', 0) != 0:
            proposals.append(self._build_cache_threshold_proposal(eval_record))
        
        # Judge calibration proposals
        for dim, signal in eval_record.judge_calibration_signals.items():
            if signal.get('needs_recalibration'):
                proposals.append(self._build_judge_calibration_proposal(eval_record, dim))
        
        # Retrieval profile proposals
        if eval_record.retrieval_profile_tuning_hints:
            proposals.append(self._build_retrieval_profile_proposal(eval_record))
        
        return proposals
    
    def build_promotion_request(
        self,
        run_id: str,
        proposals: List[ProposalPacket],
        rollback_plan_ref: str
    ) -> FutureRunPromotionRequest:
        """Build promotion request for UWG review.
        
        Args:
            run_id: The completed run ID
            proposals: Inert proposals to promote
            rollback_plan_ref: Reference to rollback plan (required)
            
        Returns:
            FutureRunPromotionRequest for UWG
        """
        # Determine required proofs based on proposal types
        required_proofs = self._determine_required_proofs(proposals)
        
        return FutureRunPromotionRequest(
            request_id=f"promotion-{run_id}",
            run_id=run_id,
            proposal_packets=tuple(proposals),
            rollback_plan_ref=rollback_plan_ref,
            target_future_run_window="NEXT_RUN",
            auto_activate=False,  # Never auto-activate
            uwg_review_status="PENDING",
        )
    
    def _build_entity_alias_proposal(
        self,
        eval_record: CompletedEvalRecord
    ) -> ProposalPacket:
        """Build entity alias improvement proposal."""
        return ProposalPacket(
            proposal_id=f"prop-entity-alias-{eval_record.run_id}",
            run_id=eval_record.run_id,
            proposal_type=ProposalType.ENTITY_ALIAS,
            target_dimension="entity_aliases",
            proposed_change=eval_record.entity_alias_observations,
            rationale="Entity aliases observed in completed run require refinement",
            confidence=eval_record.entity_alias_observations.get('confidence', 0.5),
            required_proofs=(ProofType.REPLAY, ProofType.REGRESSION),
            safety_review_status="PENDING_UWG",
            activation_trigger="FUTURE_RUN_START",
        )
    
    def _build_source_reliability_proposal(
        self,
        eval_record: CompletedEvalRecord
    ) -> ProposalPacket:
        """Build source reliability tuning proposal."""
        return ProposalPacket(
            proposal_id=f"prop-source-rel-{eval_record.run_id}",
            run_id=eval_record.run_id,
            proposal_type=ProposalType.SOURCE_RELIABILITY,
            target_dimension="source_reliability",
            proposed_change=eval_record.source_reliability_signals,
            rationale="Source reliability signals indicate tier adjustment needed",
            confidence=0.75,
            required_proofs=(ProofType.REPLAY, ProofType.REGRESSION, ProofType.SAFETY),
            safety_review_status="PENDING_UWG",
            activation_trigger="FUTURE_RUN_START",
        )
    
    def _build_cache_threshold_proposal(
        self,
        eval_record: CompletedEvalRecord
    ) -> ProposalPacket:
        """Build cache threshold tuning proposal."""
        return ProposalPacket(
            proposal_id=f"prop-cache-thresh-{eval_record.run_id}",
            run_id=eval_record.run_id,
            proposal_type=ProposalType.CACHE_THRESHOLD,
            target_dimension="cache_threshold",
            proposed_change=eval_record.cache_threshold_proposals,
            rationale="Cache hit rate suggests threshold adjustment",
            confidence=0.7,
            required_proofs=(ProofType.REPLAY, ProofType.REGRESSION),
            safety_review_status="PENDING_UWG",
            activation_trigger="FUTURE_RUN_START",
        )
    
    def _build_judge_calibration_proposal(
        self,
        eval_record: CompletedEvalRecord,
        dimension: str
    ) -> ProposalPacket:
        """Build judge calibration proposal."""
        signal = eval_record.judge_calibration_signals.get(dimension, {})
        
        return ProposalPacket(
            proposal_id=f"prop-judge-cal-{dimension}-{eval_record.run_id}",
            run_id=eval_record.run_id,
            proposal_type=ProposalType.JUDGE_CALIBRATION,
            target_dimension=dimension,
            proposed_change=signal,
            rationale=f"Judge calibration drift detected for {dimension}",
            confidence=signal.get('confidence', 0.5),
            required_proofs=(ProofType.CALIBRATION, ProofType.REGRESSION, ProofType.SAFETY),
            safety_review_status="PENDING_UWG",
            activation_trigger="FUTURE_RUN_START",
        )
    
    def _build_retrieval_profile_proposal(
        self,
        eval_record: CompletedEvalRecord
    ) -> ProposalPacket:
        """Build retrieval profile tuning proposal."""
        return ProposalPacket(
            proposal_id=f"prop-retrieval-{eval_record.run_id}",
            run_id=eval_record.run_id,
            proposal_type=ProposalType.RETRIEVAL_PROFILE,
            target_dimension="retrieval_profile",
            proposed_change=eval_record.retrieval_profile_tuning_hints,
            rationale="Retrieval profile tuning suggested by coverage analysis",
            confidence=0.7,
            required_proofs=(ProofType.REPLAY, ProofType.REGRESSION),
            safety_review_status="PENDING_UWG",
            activation_trigger="FUTURE_RUN_START",
        )
    
    def _determine_required_proofs(
        self,
        proposals: List[ProposalPacket]
    ) -> Tuple[ProofType, ...]:
        """Determine required proofs from proposal types."""
        required = set()
        
        for proposal in proposals:
            for proof in proposal.required_proofs:
                required.add(proof)
        
        return tuple(required)


# Convenience function
def build_default_proposal_builder() -> FutureRunProposalBuilder:
    """Create proposal builder with default config."""
    return FutureRunProposalBuilder(ProposalConfig())
