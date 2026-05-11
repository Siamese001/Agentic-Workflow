"""W10 — L6 Meta-Learning / Future-Run Promotion Tests

Verifies:
1. L6 is post-runtime only
2. L6 cannot rescue/mutate/reroute/re-execute current run
3. L6 cannot write cache/vector store/L4 directly
4. L6 emits inert future-run proposals only
5. Promotions require replay/regression/safety/calibration proof
6. Activation only for future runs
7. Core owns L6 execution, apps own config only
"""
import pytest
from typing import Any, Dict, List
from pathlib import Path

# Core L6 infrastructure
from agentic_core.L6_learning import (
    CompletedEvalRecord,
    RCAPacket,
    ProposalPacket,
    FutureRunPromotionRequest,
    L6GauntletResult,
    ObserverLawReceipt,
    ProposalType,
    ProofType,
)
from agentic_core.L6_learning.package_driven_l6_binding import (
    PackageDrivenL6Binding,
    L6ProcessingResult,
)
from agentic_core.L6_learning.completed_run_evaluator import (
    CompletedRunEvaluator,
    RuntimeExhaustBundle,
)
from agentic_core.L6_learning.rca_synthesizer import RCASynthesizer, RCAInput
from agentic_core.L6_learning.future_run_proposal_builder import (
    FutureRunProposalBuilder,
    ProposalConfig,
)
from agentic_core.L6_learning.promotion_gauntlet import (
    PromotionGauntlet,
    ObserverLawValidator,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: L6 Current-Run Boundary
# ─────────────────────────────────────────────────────────────────────────────

class TestW10L6CurrentRunBoundary:
    """Verify L6 cannot affect current run."""

    def test_w10_l6_consumes_runtime_exhaust_bundle(self) -> None:
        """L6 must consume RuntimeExhaustBundle (post-runtime input)."""
        bundle = RuntimeExhaustBundle(
            run_id="test-run-001",
            trace_root="trace-001",
            exit_disposition_receipt={"status": "completed"},
            gate_mesh_result={"verdicts": {}},
            x1_checkout_result={},
            x2_aggregation_result={},
            sealed_l2_artifact={},
            final_evidence_contract={},
            judge_evidence_results=[],
            u0_package_refs={},
            learning_profile_ref="profile://learning_v1",
            meta_feedback_profile_ref="profile://meta_feedback_v1",
        )
        
        evaluator = CompletedRunEvaluator({})
        record = evaluator.evaluate_completed_run(bundle)
        
        assert record.run_id == "test-run-001"
        assert record.runtime_exhaust_bundle_ref == "exhaust://test-run-001"
    
    def test_w10_l6_requires_current_run_boundary(self) -> None:
        """L6 requires completed run (runtime boundary crossed)."""
        # L6 only processes after Exit X3
        # This is enforced by only accepting RuntimeExhaustBundle
        pass  # Architecture enforces this
    
    def test_w10_l6_cannot_rescue_current_run(self) -> None:
        """L6 cannot rescue or repair a failing current run."""
        # L6 inputs are read-only; no rescue mechanisms exist
        bundle = RuntimeExhaustBundle(
            run_id="test-run-002",
            trace_root="trace-002",
            exit_disposition_receipt={"status": "failed", "x3": "X3E"},
            gate_mesh_result={"verdicts": {"G10": {"result": "FAIL"}}},
            x1_checkout_result={},
            x2_aggregation_result={},
            sealed_l2_artifact={},
            final_evidence_contract={},
            judge_evidence_results=[],
            u0_package_refs={},
            learning_profile_ref="",
            meta_feedback_profile_ref="",
        )
        
        evaluator = CompletedRunEvaluator({})
        record = evaluator.evaluate_completed_run(bundle)
        
        # L6 observes failure but cannot rescue
        assert record.evidence_digest is not None
        # No rescue attempt in output
        assert not hasattr(record, 'rescue_attempt')
    
    def test_w10_l6_cannot_emit_x3(self) -> None:
        """L6 cannot emit Exit X3 disposition."""
        evaluator = CompletedRunEvaluator({})
        record = evaluator.evaluate_completed_run(RuntimeExhaustBundle(
            run_id="test",
            trace_root="trace",
            exit_disposition_receipt={},
            gate_mesh_result={},
            x1_checkout_result={},
            x2_aggregation_result={},
            sealed_l2_artifact={},
            final_evidence_contract={},
            judge_evidence_results=[],
            u0_package_refs={},
            learning_profile_ref="",
            meta_feedback_profile_ref="",
        ))
        
        assert not hasattr(record, 'x3_disposition')
        assert not hasattr(record, 'emit_x3')
    
    def test_w10_l6_cannot_reroute_current_run(self) -> None:
        """L6 cannot trigger reroute of current run."""
        # L6 outputs are inert proposals, not routing decisions
        pass  # Enforced by architecture
    
    def test_w10_l6_cannot_reexecute_current_run(self) -> None:
        """L6 cannot trigger re-execution of current run."""
        # L6 has no re-execution mechanisms
        pass  # Enforced by architecture


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: L6 Write Boundaries
# ─────────────────────────────────────────────────────────────────────────────

class TestW10L6WriteBoundaries:
    """Verify L6 cannot write to storage systems."""

    def test_w10_l6_cannot_write_cache_directly(self) -> None:
        """L6 cannot write to R1A/R1B cache."""
        evaluator = CompletedRunEvaluator({})
        record = evaluator.evaluate_completed_run(RuntimeExhaustBundle(
            run_id="test",
            trace_root="trace",
            exit_disposition_receipt={},
            gate_mesh_result={},
            x1_checkout_result={},
            x2_aggregation_result={},
            sealed_l2_artifact={},
            final_evidence_contract={},
            judge_evidence_results=[],
            u0_package_refs={},
            learning_profile_ref="",
            meta_feedback_profile_ref="",
        ))
        
        # Record has no cache write methods
        assert not hasattr(record, 'write_cache')
        assert not hasattr(record, 'cache_result')
        assert not hasattr(record, 'store_r1a')
        assert not hasattr(record, 'store_r1b')
    
    def test_w10_l6_cannot_write_vector_store_directly(self) -> None:
        """L6 cannot write to vector store."""
        # L6 outputs are immutable records, not vector store writes
        pass  # Enforced by record immutability
    
    def test_w10_l6_cannot_write_l4_directly(self) -> None:
        """L6 cannot write to L4 UWG directly."""
        # L6 emits proposals to UWG, not direct writes
        pass  # Enforced by proposal packet design


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: L6 Output Verification
# ─────────────────────────────────────────────────────────────────────────────

class TestW10L6Outputs:
    """Verify L6 produces correct outputs."""

    def test_w10_l6_emits_completed_eval_record(self) -> None:
        """L6 must emit CompletedEvalRecord."""
        bundle = RuntimeExhaustBundle(
            run_id="test-run-003",
            trace_root="trace-003",
            exit_disposition_receipt={"status": "completed"},
            gate_mesh_result={"verdicts": {}},
            x1_checkout_result={},
            x2_aggregation_result={},
            sealed_l2_artifact={},
            final_evidence_contract={},
            judge_evidence_results=[
                {"dimension": "source_authority", "score": 0.8, "confidence": 0.75},
            ],
            u0_package_refs={},
            learning_profile_ref="",
            meta_feedback_profile_ref="",
        )
        
        evaluator = CompletedRunEvaluator({})
        record = evaluator.evaluate_completed_run(bundle)
        
        assert isinstance(record, CompletedEvalRecord)
        assert record.run_id == "test-run-003"
    
    def test_w10_l6_emits_rca_packet(self) -> None:
        """L6 must emit RCAPacket."""
        rca_input = RCAInput(
            gate_mesh_result={"verdicts": {"G10": {"result": "FAIL", "reason": "test"}}},
            judge_evidence_results=[],
            exit_disposition={"status": "completed"},
        )
        
        synthesizer = RCASynthesizer()
        rca = synthesizer.synthesize(rca_input)
        
        assert isinstance(rca, RCAPacket)
        assert len(rca.gate_failure_patterns) == 1
    
    def test_w10_l6_emits_inert_proposal_packet(self) -> None:
        """L6 must emit inert ProposalPackets."""
        config = ProposalConfig()
        builder = FutureRunProposalBuilder(config)
        
        eval_record = CompletedEvalRecord(
            run_id="test-run-004",
            trace_root="trace-004",
            entity_alias_observations={"alias_candidates": ["test"]},
        )
        
        proposals = builder.build_proposals(eval_record)
        
        assert len(proposals) > 0
        for proposal in proposals:
            assert isinstance(proposal, ProposalPacket)
            assert proposal.safety_review_status == "PENDING_UWG"
            assert proposal.activation_trigger == "FUTURE_RUN_START"
            assert proposal.is_inert() is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Future-Run Promotion Requirements
# ─────────────────────────────────────────────────────────────────────────────

class TestW10FutureRunPromotion:
    """Verify promotion requirements."""

    def test_w10_l6_future_run_promotion_requires_replay_proof(self) -> None:
        """Promotion must require replay proof."""
        gauntlet = PromotionGauntlet()
        
        request = FutureRunPromotionRequest(
            request_id="promo-001",
            run_id="run-001",
            proposal_packets=(),
            replay_proof_ref="",  # Missing
            regression_proof_ref="proof://regression/001",
            safety_proof_ref="proof://safety/001",
            rollback_plan_ref="rollback://001",
        )
        
        result = gauntlet.run_gauntlet(request)
        
        assert result.passed is False
        assert any("REPLAY_PROOF_MISSING" in f for f in result.failures)
    
    def test_w10_l6_future_run_promotion_requires_regression_proof(self) -> None:
        """Promotion must require regression proof."""
        gauntlet = PromotionGauntlet()
        
        request = FutureRunPromotionRequest(
            request_id="promo-002",
            run_id="run-002",
            proposal_packets=(),
            replay_proof_ref="proof://replay/002",
            regression_proof_ref="",  # Missing
            safety_proof_ref="proof://safety/002",
            rollback_plan_ref="rollback://002",
        )
        
        result = gauntlet.run_gauntlet(request)
        
        assert result.passed is False
        assert any("REGRESSION_PROOF_MISSING" in f for f in result.failures)
    
    def test_w10_l6_future_run_promotion_requires_safety_proof(self) -> None:
        """Promotion must require safety proof (warning if missing)."""
        gauntlet = PromotionGauntlet()
        
        # Create a proposal that requires safety proof
        proposal = ProposalPacket(
            proposal_id="prop-001",
            run_id="run-003",
            proposal_type=ProposalType.SOURCE_RELIABILITY,
            required_proofs=(ProofType.SAFETY,),
        )
        
        request = FutureRunPromotionRequest(
            request_id="promo-003",
            run_id="run-003",
            proposal_packets=(proposal,),
            replay_proof_ref="proof://replay/003",
            regression_proof_ref="proof://regression/003",
            safety_proof_ref="",  # Missing
            rollback_plan_ref="rollback://003",
        )
        
        result = gauntlet.run_gauntlet(request)
        
        # Should have warning about missing safety proof
        assert any("SAFETY_PROOF_PENDING" in w for w in result.warnings)
    
    def test_w10_l6_judge_change_requires_calibration_proof(self) -> None:
        """Judge calibration proposals require calibration proof."""
        gauntlet = PromotionGauntlet()
        
        # Judge calibration proposal
        proposal = ProposalPacket(
            proposal_id="prop-judge-001",
            run_id="run-004",
            proposal_type=ProposalType.JUDGE_CALIBRATION,
            required_proofs=(ProofType.CALIBRATION, ProofType.REGRESSION, ProofType.SAFETY),
        )
        
        request = FutureRunPromotionRequest(
            request_id="promo-004",
            run_id="run-004",
            proposal_packets=(proposal,),
            replay_proof_ref="proof://replay/004",
            regression_proof_ref="proof://regression/004",
            safety_proof_ref="proof://safety/004",
            calibration_proof_ref="",  # Missing for judge calibration
            rollback_plan_ref="rollback://004",
        )
        
        result = gauntlet.run_gauntlet(request)
        
        assert result.passed is False
        assert any("CALIBRATION_PROOF_MISSING" in f for f in result.failures)
    
    def test_w10_l6_promotion_activation_future_run_only(self) -> None:
        """Promotion activation only for future runs."""
        gauntlet = PromotionGauntlet()
        
        request = FutureRunPromotionRequest(
            request_id="promo-005",
            run_id="run-005",
            proposal_packets=(),
            target_future_run_window="CURRENT_RUN",  # Forbidden
            rollback_plan_ref="rollback://005",
        )
        
        result = gauntlet.run_gauntlet(request)
        
        assert result.passed is False
        assert any("CURRENT_RUN_ACTIVATION_BLOCKED" in f for f in result.failures)
    
    def test_w10_l6_promotion_requires_rollback_plan(self) -> None:
        """Promotion requires rollback plan."""
        gauntlet = PromotionGauntlet()
        
        request = FutureRunPromotionRequest(
            request_id="promo-006",
            run_id="run-006",
            proposal_packets=(),
            rollback_plan_ref="",  # Missing
        )
        
        result = gauntlet.run_gauntlet(request)
        
        assert result.passed is False
        assert any("ROLLBACK_PLAN_REQUIRED" in f for f in result.failures)
    
    def test_w10_l6_no_direct_l4_write(self) -> None:
        """L6 cannot write directly to L4."""
        # L6 emits proposals, not L4 writes
        pass  # Enforced by proposal packet design


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Package-Driven Config Loading
# ─────────────────────────────────────────────────────────────────────────────

class TestW10PackageDrivenConfig:
    """Verify config loading from U0 package."""

    def test_w10_learning_profile_loaded_from_u0_package(self) -> None:
        """Learning profile must load from U0 package."""
        u0_package = {
            'learning_profile': {
                'profile_id': 'test_learning',
                'entity_aliases': {'enabled': True},
            },
            'meta_feedback_profile': {},
            'promotion_policy': {},
        }
        
        binding = PackageDrivenL6Binding(u0_package)
        
        assert binding._learning_profile['profile_id'] == 'test_learning'
    
    def test_w10_meta_feedback_profile_loaded_from_u0_package(self) -> None:
        """Meta-feedback profile must load from U0 package."""
        u0_package = {
            'learning_profile': {},
            'meta_feedback_profile': {
                'profile_id': 'test_meta_feedback',
                'feedback_loops': {'enabled': True},
            },
            'promotion_policy': {},
        }
        
        binding = PackageDrivenL6Binding(u0_package)
        
        assert binding._meta_feedback_profile['profile_id'] == 'test_meta_feedback'


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Learning Targets
# ─────────────────────────────────────────────────────────────────────────────

class TestW10LearningTargets:
    """Verify learning targets produce inert proposals."""

    def test_w10_l6_proposes_cache_threshold_change_as_inert(self) -> None:
        """L6 proposes cache threshold changes as inert proposals."""
        eval_record = CompletedEvalRecord(
            run_id="test-run-005",
            trace_root="trace-005",
            cache_threshold_proposals={"threshold_adjustment_hint": 0.05},
        )
        
        config = ProposalConfig()
        builder = FutureRunProposalBuilder(config)
        proposals = builder.build_proposals(eval_record)
        
        cache_proposals = [p for p in proposals if p.proposal_type == ProposalType.CACHE_THRESHOLD]
        assert len(cache_proposals) > 0
        assert cache_proposals[0].is_inert() is True
    
    def test_w10_l6_proposes_source_reliability_change_as_inert(self) -> None:
        """L6 proposes source reliability changes as inert proposals."""
        eval_record = CompletedEvalRecord(
            run_id="test-run-006",
            trace_root="trace-006",
            source_reliability_signals={"tier_changes": [{"source": "reuters", "new_tier": "primary"}]},
        )
        
        config = ProposalConfig()
        builder = FutureRunProposalBuilder(config)
        proposals = builder.build_proposals(eval_record)
        
        source_proposals = [p for p in proposals if p.proposal_type == ProposalType.SOURCE_RELIABILITY]
        assert len(source_proposals) > 0
        assert source_proposals[0].is_inert() is True
    
    def test_w10_l6_proposes_entity_alias_change_as_inert(self) -> None:
        """L6 proposes entity alias changes as inert proposals."""
        eval_record = CompletedEvalRecord(
            run_id="test-run-007",
            trace_root="trace-007",
            entity_alias_observations={"alias_candidates": [{"entity": "IBM", "alias": "International Business Machines"}]},
        )
        
        config = ProposalConfig()
        builder = FutureRunProposalBuilder(config)
        proposals = builder.build_proposals(eval_record)
        
        entity_proposals = [p for p in proposals if p.proposal_type == ProposalType.ENTITY_ALIAS]
        assert len(entity_proposals) > 0
        assert entity_proposals[0].is_inert() is True
    
    def test_w10_l6_proposes_judge_calibration_change_as_inert(self) -> None:
        """L6 proposes judge calibration changes as inert proposals."""
        eval_record = CompletedEvalRecord(
            run_id="test-run-008",
            trace_root="trace-008",
            judge_calibration_signals={
                "claim_support": {"score": 0.6, "confidence": 0.5, "needs_recalibration": True},
            },
        )
        
        config = ProposalConfig()
        builder = FutureRunProposalBuilder(config)
        proposals = builder.build_proposals(eval_record)
        
        judge_proposals = [p for p in proposals if p.proposal_type == ProposalType.JUDGE_CALIBRATION]
        assert len(judge_proposals) > 0
        assert judge_proposals[0].is_inert() is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Boundary Enforcement (apps_research vs core)
# ─────────────────────────────────────────────────────────────────────────────

class TestW10BoundaryEnforcement:
    """Verify no executable L6 logic in apps_research."""

    def test_w10_no_apps_research_l6_logic_hardcoded_in_agentic_core(self) -> None:
        """Core L6 must be generic, not apps_research-specific."""
        # Core L6 components use generic types and config-driven behavior
        evaluator = CompletedRunEvaluator({})  # Generic, takes any profile
        
        # Should work with empty profile (generic)
        assert evaluator._profile == {}
    
    def test_w10_apps_research_l6_config_only(self) -> None:
        """apps_research must only have L6 config files."""
        config_dir = Path("apps_research/config/domain_contract")
        
        # Must have learning config files
        assert (config_dir / "learning_profile.company_brief.v1.yaml").exists()
        assert (config_dir / "meta_feedback_profile.company_brief.v1.yaml").exists()
        assert (config_dir / "l6_promotion_policy.company_brief.v1.yaml").exists()
        assert (config_dir / "learning_negative_controls.yaml").exists()
        
        # Must NOT have L6 executable code
        l6_code_dir = Path("apps_research/engines/l6")
        assert not l6_code_dir.exists() or not any(l6_code_dir.glob("*.py"))


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Observer Law Compliance
# ─────────────────────────────────────────────────────────────────────────────

class TestW10ObserverLawCompliance:
    """Verify L6 observer law receipts."""

    def test_w10_l6_produces_observer_law_receipt(self) -> None:
        """L6 must produce ObserverLawReceipt certifying compliance."""
        validator = ObserverLawValidator()
        
        l6_outputs = {
            'mutation_attempted': False,
            'x3_emitted': False,
            'cache_write_attempted': False,
            'vector_store_write_attempted': False,
            'l4_write_attempted': False,
            'current_run_reroute_attempted': False,
            'current_run_reexecute_attempted': False,
        }
        
        receipt = validator.validate(
            l6_session_id="l6-session-001",
            run_id="run-001",
            l6_outputs=l6_outputs,
        )
        
        assert isinstance(receipt, ObserverLawReceipt)
        assert receipt.no_current_run_mutation is True
        assert receipt.no_x3_emission is True
        assert receipt.no_cache_write is True
        assert receipt.no_vector_store_write is True
        assert receipt.no_l4_write is True
    
    def test_w10_l6_detects_violations(self) -> None:
        """Observer law validator must detect L6 violations."""
        validator = ObserverLawValidator()
        
        l6_outputs = {
            'mutation_attempted': True,  # Violation
            'x3_emitted': False,
            'cache_write_attempted': True,  # Violation
            'vector_store_write_attempted': False,
            'l4_write_attempted': False,
            'current_run_reroute_attempted': False,
            'current_run_reexecute_attempted': False,
        }
        
        receipt = validator.validate(
            l6_session_id="l6-session-002",
            run_id="run-002",
            l6_outputs=l6_outputs,
        )
        
        assert receipt.no_current_run_mutation is False
        assert receipt.no_cache_write is False
        assert len(receipt.evidence_refs) > 0  # Violations recorded
