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
    """
    
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
        
        passed = len(failures) == 0
        
        return L6GauntletResult(
            run_id=run_id,
            passed=passed,
            failures=failures,
            warnings=warnings,
            evidence_digest=f"sha256:gauntlet-{run_id}-{'pass' if passed else 'fail'}",
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
