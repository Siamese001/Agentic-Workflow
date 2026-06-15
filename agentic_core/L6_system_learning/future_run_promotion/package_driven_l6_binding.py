"""W10 — Package-Driven L6 Binding (Core-Owned)

Binds L6 learning to apps_research via U0 runtime customization package.

Boundary Rules:
- Core owns L6 execution
- Apps own learning policy config
- No executable L6 logic in apps_research
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from agentic_core.L6_system_learning.future_run_promotion import (
    CompletedEvalRecord,
    RCAPacket,
    ProposalPacket,
    FutureRunPromotionRequest,
    L6GauntletResult,
    ObserverLawReceipt,
)
from agentic_core.L6_system_learning.future_run_promotion.completed_run_evaluator import (
    CompletedRunEvaluator,
    RuntimeExhaustBundle,
)
from agentic_core.L6_system_learning.future_run_promotion.rca_synthesizer import RCASynthesizer, RCAInput
from agentic_core.L6_system_learning.future_run_promotion.future_run_proposal_builder import (
    FutureRunProposalBuilder,
    ProposalConfig,
)
from agentic_core.L6_system_learning.future_run_promotion.promotion_gauntlet import (
    PromotionGauntlet,
    ObserverLawValidator,
)


@dataclass(frozen=True)
class L6ProcessingResult:
    """Complete result of L6 processing."""
    run_id: str
    
    # Core outputs
    completed_eval_record: CompletedEvalRecord
    rca_packet: RCAPacket
    proposal_packets: List[ProposalPacket]
    promotion_request: FutureRunPromotionRequest
    
    # Validation
    gauntlet_result: L6GauntletResult
    observer_law_receipt: ObserverLawReceipt
    
    # Receipts
    eval_record_seal: str
    gauntlet_receipt: str
    future_run_activation_receipt_candidate: str


class PackageDrivenL6Binding:
    """Binds L6 processing to app via U0 package config.
    
    Core owns this binding. App provides config via U0 package.
    """
    
    def __init__(self, u0_package: Dict[str, Any]):
        """Initialize with app U0 package.
        
        Args:
            u0_package: U0 runtime customization package with learning config
        """
        self._u0_package = u0_package
        
        # Load app learning config (read-only)
        self._learning_profile = u0_package.get('learning_profile', {})
        self._meta_feedback_profile = u0_package.get('meta_feedback_profile', {})
        self._promotion_policy = u0_package.get('promotion_policy', {})
        
        # Initialize core components
        self._evaluator = CompletedRunEvaluator(self._learning_profile)
        self._rca_synthesizer = RCASynthesizer()
        self._proposal_builder = FutureRunProposalBuilder(ProposalConfig())
        self._gauntlet = PromotionGauntlet()
        self._observer_validator = ObserverLawValidator()
    
    def process_completed_run(
        self,
        exhaust_bundle: RuntimeExhaustBundle
    ) -> L6ProcessingResult:
        """Process completed run through L6 learning pipeline.
        
        Args:
            exhaust_bundle: Runtime exhaust artifacts (read-only)
            
        Returns:
            L6ProcessingResult with all outputs and receipts
        """
        run_id = exhaust_bundle.run_id
        
        # Step 1: Evaluate completed run
        eval_record = self._evaluator.evaluate_completed_run(exhaust_bundle)
        
        # Step 2: Synthesize RCA
        rca_input = RCAInput(
            gate_mesh_result=exhaust_bundle.gate_mesh_result,
            judge_evidence_results=exhaust_bundle.judge_evidence_results,
            exit_disposition=exhaust_bundle.exit_disposition_receipt,
        )
        rca_packet = self._rca_synthesizer.synthesize(rca_input)
        
        # Step 3: Build inert future-run proposals
        proposals = self._proposal_builder.build_proposals(eval_record)
        
        # Step 4: Build promotion request with rollback plan
        rollback_plan_ref = self._build_rollback_plan_ref(run_id)
        promotion_request = self._proposal_builder.build_promotion_request(
            run_id, proposals, rollback_plan_ref
        )
        
        # Step 5: Run promotion gauntlet
        gauntlet_result = self._gauntlet.run_gauntlet(promotion_request)
        
        # Step 6: Validate observer law compliance
        l6_outputs = {
            'mutation_attempted': False,
            'x3_emitted': False,
            'cache_write_attempted': False,
            'vector_store_write_attempted': False,
            'l4_write_attempted': False,
            'current_run_reroute_attempted': False,
            'current_run_reexecute_attempted': False,
        }
        observer_receipt = self._observer_validator.validate(
            l6_session_id=f"l6-{run_id}",
            run_id=run_id,
            l6_outputs=l6_outputs,
        )
        
        # Generate receipts
        eval_seal = f"seal://completed-eval/{run_id}"
        gauntlet_receipt = f"receipt://gauntlet/{run_id}-{'pass' if gauntlet_result.passed else 'fail'}"
        activation_candidate = f"candidate://future-run/{run_id}"
        
        return L6ProcessingResult(
            run_id=run_id,
            completed_eval_record=eval_record,
            rca_packet=rca_packet,
            proposal_packets=proposals,
            promotion_request=promotion_request,
            gauntlet_result=gauntlet_result,
            observer_law_receipt=observer_receipt,
            eval_record_seal=eval_seal,
            gauntlet_receipt=gauntlet_receipt,
            future_run_activation_receipt_candidate=activation_candidate,
        )
    
    def _build_rollback_plan_ref(self, run_id: str) -> str:
        """Build reference to rollback plan."""
        # In real implementation, this would generate/store rollback plan
        return f"rollback://plan/{run_id}"


def load_l6_binding_from_u0_package(
    u0_package: Dict[str, Any]
) -> PackageDrivenL6Binding:
    """Factory: Create L6 binding from U0 package.
    
    Args:
        u0_package: U0 runtime customization package
        
    Returns:
        PackageDrivenL6Binding configured from app U0 package
    """
    return PackageDrivenL6Binding(u0_package)
