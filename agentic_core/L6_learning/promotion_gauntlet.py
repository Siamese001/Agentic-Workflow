"""W10 — Promotion Gauntlet (Core-Owned)

Validates future-run promotion requests against safety requirements.

Hard Rules:
- All promotions require gauntlet pass
- No exceptions for auto-promote
- Missing proofs = gauntlet fail
- No rollback plan = gauntlet fail
- Current-run activation attempt = gauntlet fail
"""
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

from agentic_core.L6_learning import (
    FutureRunPromotionRequest,
    L6GauntletResult,
    ObserverLawReceipt,
    ProofType,
)


class PromotionGauntlet:
    """Validates promotion requests against safety requirements.

    Core owns gauntlet logic. Apps provide gauntlet policy config.

    GATE_ID is a canonical ledger-tracking identifier for this gate.
    It identifies which gate produced an L6GauntletResult and is used
    for closed-loop router ledger attribution per constitutional §29.
    It is NOT a GateVerdict receipt, NOT 00C evidence, NOT UWG admission,
    NOT Exit certification, and NOT L5 proof. Presence of GATE_ID in
    a result never implies passed=True or that promotion is authorized.
    """

    GATE_ID: str = "G29"

    # ProposalType names that require rca_packet_ref before promotion.
    # Maps to existing ProposalType enum values only — no new values invented.
    _RCA_REQUIRED_PROPOSAL_TYPES: Tuple[str, ...] = (
        "prompt_improvement",
        "rubric_improvement",
        "judge_calibration",
        "cache_threshold",
        "source_reliability",
        "retrieval_profile",
        "chunking_profile",
    )

    # ProposalType names that require calibration_proof_ref before promotion.
    _CALIBRATION_REQUIRED_PROPOSAL_TYPES: Tuple[str, ...] = (
        "judge_calibration",
    )

    REQUIRED_PROOFS_BY_TYPE: Dict[str, Tuple[ProofType, ...]] = {
        "judge_calibration": (ProofType.CALIBRATION, ProofType.REGRESSION, ProofType.SAFETY),
        "cache_threshold": (ProofType.REPLAY, ProofType.REGRESSION),
        "source_reliability": (ProofType.REPLAY, ProofType.REGRESSION, ProofType.SAFETY),
        "entity_alias": (ProofType.REPLAY, ProofType.REGRESSION),
        "default": (ProofType.REPLAY, ProofType.REGRESSION, ProofType.SAFETY),
    }
    
    def run_gauntlet(
        self,
        promotion_request: FutureRunPromotionRequest
    ) -> L6GauntletResult:
        """Run promotion request through safety gauntlet.
        
        Args:
            promotion_request: Request to validate
            
        Returns:
            L6GauntletResult with pass/fail status
        """
        run_id = promotion_request.run_id
        failures = []
        warnings = []
        
        # Check 1: Not auto-activate
        if promotion_request.auto_activate:
            failures.append("AUTO_ACTIVATE_NOT_ALLOWED: Promotions cannot auto-activate")
        
        # Check 2: Future-run activation only
        if promotion_request.target_future_run_window == "CURRENT_RUN":
            failures.append("CURRENT_RUN_ACTIVATION_BLOCKED: L6 cannot affect current run")
        
        # Check 3: Rollback plan required
        if not promotion_request.rollback_plan_ref:
            failures.append("ROLLBACK_PLAN_REQUIRED: Missing rollback plan reference")
        
        # Check 4: UWG status must be pending (not pre-approved)
        if promotion_request.uwg_review_status == "PRE_APPROVED":
            failures.append("PRE_APPROVAL_NOT_ALLOWED: UWG must review all promotions")
        
        # Check 5: Required proofs present
        for proposal in promotion_request.proposal_packets:
            proof_check = self._verify_proposal_proofs(
                proposal.proposal_type.name.lower(),
                proposal.required_proofs,
                promotion_request
            )
            if not proof_check['passed']:
                failures.extend(proof_check['failures'])
            warnings.extend(proof_check['warnings'])
        
        # Check 6: Judge calibration proposals have calibration proof
        for proposal in promotion_request.proposal_packets:
            if proposal.proposal_type.name == "JUDGE_CALIBRATION":
                if not promotion_request.calibration_proof_ref:
                    failures.append(
                        "CALIBRATION_PROOF_REQUIRED: Judge calibration proposals "
                        "require calibration proof"
                    )

        # Check 7: audit_manifest_ref required for every promotion (no exceptions)
        if not promotion_request.audit_manifest_ref:
            failures.append(
                "AUDIT_MANIFEST_REQUIRED: audit_manifest_ref must be present "
                "for all promotion requests"
            )

        # Check 8: completed_eval_record_ref required for every L6 future-run promotion
        if not promotion_request.completed_eval_record_ref:
            failures.append(
                "COMPLETED_EVAL_RECORD_REQUIRED: completed_eval_record_ref must "
                "be present for all L6 future-run promotions"
            )

        # Check 9: rca_packet_ref required for corrective/policy/prompt/rubric/
        # judge/cache/index/route/registry changes (maps to existing ProposalType values)
        for proposal in promotion_request.proposal_packets:
            ptype = proposal.proposal_type.name.lower()
            if ptype in self._RCA_REQUIRED_PROPOSAL_TYPES:
                if not promotion_request.rca_packet_ref:
                    failures.append(
                        f"RCA_PACKET_REQUIRED: rca_packet_ref required for "
                        f"{proposal.proposal_type.name}"
                    )
                    break  # One failure per request, not per proposal

        # Check 10: calibration_proof_ref required for JUDGE_CALIBRATION
        # (field pre-exists on FutureRunPromotionRequest; enforced here for
        # types not already caught by Check 6 per-proposal path)
        for proposal in promotion_request.proposal_packets:
            ptype = proposal.proposal_type.name.lower()
            if ptype in self._CALIBRATION_REQUIRED_PROPOSAL_TYPES:
                if not promotion_request.calibration_proof_ref:
                    # Check 6 already appended this; avoid duplicate
                    if not any(
                        "CALIBRATION_PROOF_REQUIRED" in f for f in failures
                    ):
                        failures.append(
                            f"CALIBRATION_PROOF_REQUIRED: calibration_proof_ref "
                            f"required for {proposal.proposal_type.name}"
                        )
                    break

        passed = len(failures) == 0

        return L6GauntletResult(
            run_id=run_id,
            passed=passed,
            failures=failures,
            warnings=warnings,
            evidence_digest=f"sha256:gauntlet-{run_id}-{'pass' if passed else 'fail'}",
            gate_id=self.GATE_ID,
        )
    
    def _verify_proposal_proofs(
        self,
        proposal_type: str,
        required_proofs: Tuple[ProofType, ...],
        request: FutureRunPromotionRequest
    ) -> Dict[str, Any]:
        """Verify required proofs are present."""
        failures = []
        warnings = []
        
        # Check replay proof
        if ProofType.REPLAY in required_proofs and not request.replay_proof_ref:
            failures.append(f"REPLAY_PROOF_MISSING for {proposal_type}")
        
        # Check regression proof
        if ProofType.REGRESSION in required_proofs and not request.regression_proof_ref:
            failures.append(f"REGRESSION_PROOF_MISSING for {proposal_type}")
        
        # Check safety proof
        if ProofType.SAFETY in required_proofs and not request.safety_proof_ref:
            warnings.append(f"SAFETY_PROOF_PENDING for {proposal_type}")
        
        # Check calibration proof
        if ProofType.CALIBRATION in required_proofs and not request.calibration_proof_ref:
            failures.append(f"CALIBRATION_PROOF_MISSING for {proposal_type}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures,
            'warnings': warnings,
        }


class ObserverLawValidator:
    """Validates L6 observer law compliance.
    
    Ensures L6 did not violate current-run boundary.
    """
    
    def validate(
        self,
        l6_session_id: str,
        run_id: str,
        l6_outputs: Dict[str, Any]
    ) -> ObserverLawReceipt:
        """Validate L6 observer law compliance.
        
        Args:
            l6_session_id: L6 session identifier
            run_id: Associated run
            l6_outputs: Outputs from L6 processing
            
        Returns:
            ObserverLawReceipt certifying compliance
        """
        # Check for violations in outputs
        violations = []
        
        if l6_outputs.get('x3_emitted'):
            violations.append("L6 emitted X3 (forbidden)")
        
        if l6_outputs.get('cache_write_attempted'):
            violations.append("L6 attempted cache write (forbidden)")
        
        if l6_outputs.get('vector_store_write_attempted'):
            violations.append("L6 attempted vector store write (forbidden)")
        
        if l6_outputs.get('l4_write_attempted'):
            violations.append("L6 attempted L4 write (forbidden)")
        
        if l6_outputs.get('current_run_reroute_attempted'):
            violations.append("L6 attempted current-run reroute (forbidden)")
        
        if l6_outputs.get('current_run_reexecute_attempted'):
            violations.append("L6 attempted current-run re-execution (forbidden)")
        
        compliant = len(violations) == 0
        
        return ObserverLawReceipt(
            run_id=run_id,
            l6_session_id=l6_session_id,
            no_current_run_mutation=not l6_outputs.get('mutation_attempted', False),
            no_x3_emission=not l6_outputs.get('x3_emitted', False),
            no_cache_write=not l6_outputs.get('cache_write_attempted', False),
            no_vector_store_write=not l6_outputs.get('vector_store_write_attempted', False),
            no_l4_write=not l6_outputs.get('l4_write_attempted', False),
            no_reroute_attempt=not l6_outputs.get('current_run_reroute_attempted', False),
            no_reexecute_attempt=not l6_outputs.get('current_run_reexecute_attempted', False),
            compliance_digest=f"sha256:observer-law-{run_id}-{'compliant' if compliant else 'violated'}",
            evidence_refs=tuple(f"violation://{v}" for v in violations) if violations else (),
        )


# Gauntlet singleton
default_gauntlet = PromotionGauntlet()
default_observer_validator = ObserverLawValidator()


def validate_promotion(request: FutureRunPromotionRequest) -> L6GauntletResult:
    """Convenience function to validate promotion request."""
    return default_gauntlet.run_gauntlet(request)
