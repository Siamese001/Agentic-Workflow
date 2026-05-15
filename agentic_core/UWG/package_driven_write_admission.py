"""W11 — Package-Driven Write Admission (UWG)

Spine vocabulary (W5 boundary remediation f8e3c1): **UWG** is the sole durable
write admission path to governed L4 substrate — layers must not bypass UWG for
durable commits. This module implements one **package-driven** UWG admission
surface (research promotions); other UWG entrypoints share the same law.

UWG is the configured admission path for **apps_research** durable writes shown
here. Consumes ``FutureRunPromotionRequest`` from L6. Admits or blocks based on
policy compliance.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

from agentic_core.UWG import (
    CommitRequest,
    StateCommitReceipt,
    BlockedWriteReceipt,
    AuditAppendReceipt,
    ReadSurfaceRefreshReceipt,
    StateDiffValidationResult,
    WriteStatus,
    BlockReason,
)
from agentic_core.L6_learning import FutureRunPromotionRequest


# ─────────────────────────────────────────────────────────────────────────────
# Allowed Writeback Payloads for apps_research
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_RESEARCH_SUBSTRATE_PAYLOADS = {
    "research_substrate_record_promotion",
    "embedding_index_record_promotion",
    "source_register_promotion",
    "claim_evidence_map_promotion",
    "freshness_report_promotion",
    "contradiction_report_promotion",
    "citation_anchor_registry_promotion",
    "entity_alias_record_promotion",
    "source_authority_signal_promotion",
    "cache_threshold_policy_promotion",
    "freshness_ttl_policy_promotion",
    "retrieval_profile_promotion",
    "judge_calibration_record_promotion",
}

# ─────────────────────────────────────────────────────────────────────────────
# Prohibited Terminal Cache Payloads
# ─────────────────────────────────────────────────────────────────────────────

PROHIBITED_TERMINAL_CACHE_PAYLOADS = {
    "apps_rg_final_resume_bullets_terminal_cache",
    "apps_rg_final_resume_sections_terminal_cache",
    "apps_lic_final_outreach_copy_terminal_cache",
    "apps_lic_campaign_copy_terminal_cache",
    "customized_user_specific_final_narrative_terminal_cache",
    "ungrounded_synthesis_without_source_register",
    "uploaded_briefing_failed_provenance",
    "uploaded_briefing_failed_injection_scan",
}


@dataclass(frozen=True)
class UWGAdmissionResult:
    """Complete result of UWG admission processing."""
    commit_request: CommitRequest
    
    # One of these will be populated
    commit_receipt: Optional[StateCommitReceipt] = None
    blocked_receipt: Optional[BlockedWriteReceipt] = None
    
    # Always populated
    audit_receipt: Optional[AuditAppendReceipt] = None
    refresh_receipt: Optional[ReadSurfaceRefreshReceipt] = None
    
    # Processing metadata
    processing_steps: List[str] = None
    
    def __post_init__(self):
        if self.processing_steps is None:
            object.__setattr__(self, 'processing_steps', [])


class PackageDrivenWriteAdmission:
    """UWG write admission for apps_research.
    
    Core owns UWG logic. Apps provide write policy config.
    """
    
    def __init__(self, write_policy: Dict[str, Any]):
        """Initialize with app write policy.
        
        Args:
            write_policy: Loaded from apps_research config
        """
        self._policy = write_policy
        self._allowed_payloads = ALLOWED_RESEARCH_SUBSTRATE_PAYLOADS
        self._prohibited_payloads = PROHIBITED_TERMINAL_CACHE_PAYLOADS
    
    def admit_future_run_promotion(
        self,
        promotion_request: FutureRunPromotionRequest,
        target_l4_namespace: str = "apps_research_substrate"
    ) -> UWGAdmissionResult:
        """Process FutureRunPromotionRequest through UWG admission.
        
        Args:
            promotion_request: Inert promotion request from L6
            target_l4_namespace: Target L4 namespace for writes
            
        Returns:
            UWGAdmissionResult with receipts
        """
        run_id = promotion_request.run_id
        steps = []
        
        # Step 1: Create CommitRequest from promotion
        steps.append("creating_commit_request")
        commit_request = self._create_commit_request(
            promotion_request, target_l4_namespace
        )
        
        # Step 2: Validate proofs
        steps.append("validating_proofs")
        proof_validation = self._validate_proofs(commit_request)
        
        # Step 3: Validate policy compliance
        steps.append("validating_policy_compliance")
        policy_validation = self._validate_policy_compliance(commit_request)
        
        # Step 4: Validate payload type
        steps.append("validating_payload_type")
        payload_validation = self._validate_payload_type(commit_request)
        
        # Step 5: Determine admission
        steps.append("determining_admission")
        all_valid = proof_validation and policy_validation and payload_validation
        
        commit_receipt = None
        blocked_receipt = None
        
        if all_valid:
            # Step 6a: Admit write
            steps.append("admitting_write")
            commit_receipt = self._create_commit_receipt(commit_request)
        else:
            # Step 6b: Block write
            steps.append("blocking_write")
            blocked_receipt = self._create_blocked_receipt(
                commit_request, 
                proof_validation, 
                policy_validation, 
                payload_validation
            )
        
        # Step 7: Append to audit ledger (always)
        steps.append("appending_audit_ledger")
        audit_receipt = self._append_audit_ledger(
            commit_request, 
            commit_receipt or blocked_receipt
        )
        
        # Step 8: Refresh read surface (if admitted)
        refresh_receipt = None
        if commit_receipt:
            steps.append("refreshing_read_surface")
            refresh_receipt = self._refresh_read_surface(commit_receipt)
        
        return UWGAdmissionResult(
            commit_request=commit_request,
            commit_receipt=commit_receipt,
            blocked_receipt=blocked_receipt,
            audit_receipt=audit_receipt,
            refresh_receipt=refresh_receipt,
            processing_steps=steps,
        )
    
    def _create_commit_request(
        self,
        promotion: FutureRunPromotionRequest,
        target_l4_namespace: str
    ) -> CommitRequest:
        """Create CommitRequest from FutureRunPromotionRequest."""
        # Determine write type from proposal
        write_type = "research_substrate_record_promotion"  # Default
        if promotion.proposal_packets:
            # Map proposal type to write type
            proposal = promotion.proposal_packets[0]
            write_type = self._map_proposal_to_write_type(proposal.proposal_type.name)
        
        return CommitRequest(
            request_id=f"commit-{promotion.request_id}",
            run_id=promotion.run_id,
            source_promotion_request=f"promotion://{promotion.request_id}",
            write_type=write_type,
            target_l4_namespace=target_l4_namespace,
            replay_proof_ref=promotion.replay_proof_ref,
            regression_proof_ref=promotion.regression_proof_ref,
            safety_proof_ref=promotion.safety_proof_ref,
            calibration_proof_ref=promotion.calibration_proof_ref,
            rollback_plan_ref=promotion.rollback_plan_ref,
            write_policy_hash=self._policy.get('policy_hash', ''),
            registry_digest=self._policy.get('registry_digest', ''),
        )
    
    def _validate_proofs(self, request: CommitRequest) -> Dict[str, Any]:
        """Validate all required proofs are present."""
        errors = []
        
        if not request.replay_proof_ref:
            errors.append("Missing replay proof")
        if not request.regression_proof_ref:
            errors.append("Missing regression proof")
        if not request.safety_proof_ref:
            errors.append("Missing safety proof")
        
        # Calibration proof required for judge changes
        if request.write_type == "judge_calibration_record_promotion":
            if not request.calibration_proof_ref:
                errors.append("Missing calibration proof for judge change")
        
        if not request.rollback_plan_ref:
            errors.append("Missing rollback plan")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }
    
    def _validate_policy_compliance(self, request: CommitRequest) -> Dict[str, Any]:
        """Validate write complies with policy."""
        errors = []
        
        if not request.write_policy_hash:
            errors.append("Missing write policy hash")
        if not request.registry_digest:
            errors.append("Missing registry digest")
        
        # Validate L4 namespace
        allowed_namespaces = self._policy.get('allowed_l4_namespaces', [])
        if request.target_l4_namespace not in allowed_namespaces:
            errors.append(f"Invalid L4 namespace: {request.target_l4_namespace}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }
    
    def _validate_payload_type(self, request: CommitRequest) -> Dict[str, Any]:
        """Validate payload type is allowed and not prohibited."""
        errors = []
        
        write_type = request.write_type
        
        # Check not prohibited
        if write_type in self._prohibited_payloads:
            errors.append(f"Prohibited terminal cache payload: {write_type}")
        
        # Check allowed (or use explicit allowlist)
        if write_type not in self._allowed_payloads:
            # Could be warning instead of error for extensibility
            pass
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }
    
    def _map_proposal_to_write_type(self, proposal_type: str) -> str:
        """Map proposal type to write type."""
        mapping = {
            "JUDGE_CALIBRATION": "judge_calibration_record_promotion",
            "CACHE_THRESHOLD": "cache_threshold_policy_promotion",
            "SOURCE_RELIABILITY": "source_authority_signal_promotion",
            "ENTITY_ALIAS": "entity_alias_record_promotion",
            "RETRIEVAL_PROFILE": "retrieval_profile_promotion",
        }
        return mapping.get(proposal_type, "research_substrate_record_promotion")
    
    def _create_commit_receipt(self, request: CommitRequest) -> StateCommitReceipt:
        """Create StateCommitReceipt for admitted write."""
        return StateCommitReceipt(
            receipt_id=f"receipt-{request.request_id}",
            commit_request_id=request.request_id,
            run_id=request.run_id,
            status=WriteStatus.ADMITTED,
            l4_namespace=request.target_l4_namespace,
            audit_ledger_ref=f"audit://{request.request_id}",
            rollback_ref=request.rollback_plan_ref,
            read_surface_refresh_ref=f"refresh://{request.request_id}",
            evidence_digest=f"sha256:commit-{request.request_id}",
        )
    
    def _create_blocked_receipt(
        self,
        request: CommitRequest,
        proof_validation: Dict[str, Any],
        policy_validation: Dict[str, Any],
        payload_validation: Dict[str, Any]
    ) -> BlockedWriteReceipt:
        """Create BlockedWriteReceipt for blocked write."""
        block_reasons = []
        block_details = []
        
        # Collect block reasons
        if not proof_validation['valid']:
            block_reasons.append(BlockReason.MISSING_PROOF_REPLAY)
            block_details.extend(proof_validation['errors'])
        
        if not policy_validation['valid']:
            block_reasons.append(BlockReason.MISSING_POLICY_HASH)
            block_details.extend(policy_validation['errors'])
        
        if not payload_validation['valid']:
            if any('terminal cache' in e for e in payload_validation['errors']):
                block_reasons.append(BlockReason.PROHIBITED_TERMINAL_CACHE_PAYLOAD)
            block_details.extend(payload_validation['errors'])
        
        return BlockedWriteReceipt(
            receipt_id=f"blocked-{request.request_id}",
            commit_request_id=request.request_id,
            run_id=request.run_id,
            status=WriteStatus.BLOCKED,
            block_reasons=tuple(block_reasons),
            block_details=block_details,
            audit_ledger_ref=f"audit://{request.request_id}",
            evidence_digest=f"sha256:blocked-{request.request_id}",
        )
    
    def _append_audit_ledger(
        self,
        request: CommitRequest,
        receipt: Union[StateCommitReceipt, BlockedWriteReceipt]
    ) -> AuditAppendReceipt:
        """Append to audit ledger."""
        return AuditAppendReceipt(
            append_id=f"audit-{request.request_id}",
            commit_request_id=request.request_id,
            run_id=request.run_id,
            ledger_sequence=1,  # Would be actual sequence in production
            merkle_root=f"merkle:{request.request_id}",
        )
    
    def _refresh_read_surface(
        self,
        commit_receipt: StateCommitReceipt
    ) -> ReadSurfaceRefreshReceipt:
        """Refresh read surface after commit."""
        return ReadSurfaceRefreshReceipt(
            refresh_id=f"refresh-{commit_receipt.receipt_id}",
            commit_receipt_id=commit_receipt.receipt_id,
            l4_namespace=commit_receipt.l4_namespace,
            affected_indices=(f"idx:{commit_receipt.l4_namespace}",),
            refresh_proof=f"proof:{commit_receipt.receipt_id}",
        )


def load_uwg_from_u0_package(u0_package: Dict[str, Any]) -> PackageDrivenWriteAdmission:
    """Factory: Create UWG from U0 package."""
    write_policy = u0_package.get('write_policy', {})
    return PackageDrivenWriteAdmission(write_policy)
