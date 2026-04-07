"""
Underwriting Engine - Main orchestrator for the underwriting workflow.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..engines.decision_packet_assembler import AssemblerInput, DecisionPacketAssembler
from ..engines.document_reconciliation_engine import DocumentReconciliationEngine, ReconciliationResult
from ..engines.evidence_register_engine import EvidenceRegister, EvidenceRegisterEngine
from ..engines.feature_derivation_engine import FeatureDerivationEngine
from ..reasoning.condition_recommender import ConditionRecommender
from ..reasoning.counter_offer_recommender import CounterOfferRecommender
from ..reasoning.covenant_recommender import CovenantRecommender
from ..reasoning.exception_summarizer import ExceptionSummarizer
from ..reasoning.feature_interpreter import FeatureInterpreter
from ..reasoning.human_escalation_selector import HumanEscalationSelector
from ..reasoning.risk_hypothesis_builder import RiskHypothesis, RiskHypothesisBuilder
from ..types import (
    AuditTrace,
    DecisionMemo,
    DecisionPacket,
    DecisionState,
    RiskFeatures,
    UnderwritingRequest,
)
from ..validators.authority_limit_validator import AuthorityLimitValidator
from ..validators.compliance_validator import ComplianceValidator
from ..validators.contradiction_validator import ContradictionValidator
from ..validators.document_completeness_validator import DocumentCompletenessValidator
from ..validators.forbidden_feature_checker import ForbiddenFeatureChecker
from ..validators.stale_data_validator import StaleDataValidator


@dataclass
class UnderwritingResult:
    """Complete result of underwriting workflow."""
    success: bool = True
    request_id: str = ""
    decision: DecisionState = "PEND_FOR_INFORMATION"
    decision_memo: Optional[DecisionMemo] = None
    decision_packet: Optional[DecisionPacket] = None
    audit_trace: Optional[AuditTrace] = None
    risk_features: Optional[RiskFeatures] = None
    confidence_score: float = 0.0
    human_review_required: bool = False
    human_review_reason: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


class UnderwritingEngine:
    """
    Main orchestrator for the underwriting workflow.

    Sequences:
    1. Intake + schema validation
    2. Document reconciliation
    3. Feature derivation
    4. Hypothesis building
    5. Feature interpretation
    6. Validator execution
    7. Recommendation refinement
    8. Packet assembly
    9. Artifact rendering
    """

    def __init__(self):
        # Engines
        self.reconciliation_engine = DocumentReconciliationEngine()
        self.feature_engine = FeatureDerivationEngine()
        self.evidence_engine = EvidenceRegisterEngine()
        self.packet_assembler = DecisionPacketAssembler()

        # Reasoning
        self.hypothesis_builder = RiskHypothesisBuilder()
        self.feature_interpreter = FeatureInterpreter()
        self.condition_recommender = ConditionRecommender()
        self.covenant_recommender = CovenantRecommender()
        self.exception_summarizer = ExceptionSummarizer()
        self.counter_offer_recommender = CounterOfferRecommender()
        self.escalation_selector = HumanEscalationSelector()

        # Validators
        self.compliance_validator = ComplianceValidator()
        self.forbidden_checker = ForbiddenFeatureChecker()
        self.completeness_validator = DocumentCompletenessValidator()
        self.authority_validator = AuthorityLimitValidator()
        self.contradiction_validator = ContradictionValidator()
        self.stale_validator = StaleDataValidator()

    def run(self, request: UnderwritingRequest) -> UnderwritingResult:
        """
        Execute complete underwriting workflow.

        Args:
            request: UnderwritingRequest

        Returns:
            UnderwritingResult with decision and artifacts
        """
        result = UnderwritingResult()
        result.request_id = request.request_id
        start_time = datetime.now()

        try:
            # Step 1: Initialize evidence register
            evidence_register = self.evidence_engine.initialize(request.request_id)

            # Step 2: Document reconciliation
            reconciliation = self.reconciliation_engine.reconcile(request)

            # Step 3: Feature derivation
            features = self.feature_engine.derive_features(request, reconciliation)
            result.risk_features = features

            # Step 4: Collect evidence
            self._collect_evidence(evidence_register, request, features)

            # Step 5: Build hypothesis
            hypothesis = self.hypothesis_builder.build_hypothesis(request, features)

            # Step 6: Interpret features
            interpretations = self.feature_interpreter.interpret_features(features, request)

            # Step 7: Run validators
            validator_results = self._run_validators(request, features, reconciliation)

            # Step 8: Determine if escalation needed
            should_escalate, escalation_reasons = self.escalation_selector.should_escalate(
                features, request, validator_results,
            )

            # Step 9: Determine recommendation
            decision, confidence, conditions, covenants, missing_info = self._determine_decision(
                request, features, hypothesis, validator_results, should_escalate, escalation_reasons,
            )

            # Step 10: Build exception summary
            exception_summary = self.exception_summarizer.summarize(
                features, request, decision, validator_results,
            )

            # Step 11: Check for counter-offer
            counter_offer = None
            if decision == "COUNTER_OFFER":
                counter_offer = self.counter_offer_recommender.recommend_counter_offer(
                    features, request,
                )

            # Step 12: Assemble decision outputs
            assembler_input = AssemblerInput(
                request=request,
                features=features,
                recommended_decision=decision,
                conditions=conditions,
                covenants=covenants,
                key_strengths=hypothesis.primary_strengths,
                key_risks=hypothesis.primary_risks,
                policy_exceptions=[e.get("message", "") for e in exception_summary.exception_details],
                missing_info=missing_info,
                evidence_register=evidence_register,
                human_review_reason="; ".join(escalation_reasons) if should_escalate else None,
                confidence_score=confidence,
            )

            memo, packet, trace = self.packet_assembler.assemble(assembler_input)

            # Populate result
            result.decision = decision
            result.decision_memo = memo
            result.decision_packet = packet
            result.audit_trace = trace
            result.confidence_score = confidence
            result.human_review_required = should_escalate
            result.human_review_reason = "; ".join(escalation_reasons) if should_escalate else None

            # Add warnings
            result.warnings.extend(hypothesis.open_questions)

            # Processing metadata
            result.processing_metadata = {
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "reconciliation_pass_rate": reconciliation.pass_rate,
                "validator_results": list(validator_results.keys()),
                "exception_count": exception_summary.exception_count,
            }

        except Exception as e:
            result.success = False
            result.errors.append(f"Underwriting processing error: {str(e)}")
            result.decision = "ESCALATE_TO_HUMAN"

        return result

    def _collect_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
        features: RiskFeatures,
    ) -> None:
        """Collect evidence from all sources."""
        self.evidence_engine.collect_financial_evidence(register, request)
        self.evidence_engine.collect_credit_evidence(register, request)
        self.evidence_engine.collect_collateral_evidence(register, request)
        self.evidence_engine.collect_relationship_evidence(register, request)
        self.evidence_engine.collect_policy_evidence(
            register, request, features.policy.policy_exception_count,
        )

    def _run_validators(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures,
        reconciliation: ReconciliationResult,
    ) -> Dict[str, Any]:
        """Run all validators and return results."""
        results = {}

        # Compliance validation
        results["compliance"] = self.compliance_validator.validate(request, features)

        # Forbidden feature check
        results["forbidden_features"] = self.forbidden_checker.check_request(request)

        # Document completeness
        results["document_completeness"] = self.completeness_validator.validate(request)

        # Authority limit
        results["authority_limit"] = self.authority_validator.validate(request, features)

        # Contradiction validation
        results["contradictions"] = self.contradiction_validator.validate(reconciliation)

        # Stale data validation
        results["stale_data"] = self.stale_validator.validate(request)

        return results

    def _determine_decision(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures,
        hypothesis: RiskHypothesis,
        validator_results: Dict[str, Any],
        should_escalate: bool,
        escalation_reasons: List[str],
    ):
        """Determine final decision and associated terms."""

        # Check for blocking issues first
        compliance = validator_results.get("compliance")
        forbidden = validator_results.get("forbidden_features")
        completeness = validator_results.get("document_completeness")
        contradictions = validator_results.get("contradictions")
        stale_data = validator_results.get("stale_data")

        missing_info = []
        conditions = []
        covenants = []

        # Forbidden features - immediate decline
        if forbidden and not forbidden.passed:
            return "DECLINE", 0.9, [], [], ["Use of prohibited attributes in decisioning"]

        # Escalation path
        if should_escalate:
            # Determine if it's a pend or escalate
            if completeness and not completeness.complete:
                missing_info.extend(completeness.missing_required)
                return "PEND_FOR_INFORMATION", features.composite.confidence_score * 0.7, [], [], missing_info

            if stale_data and stale_data.requires_update:
                return "PEND_FOR_INFORMATION", features.composite.confidence_score * 0.6, [], [], stale_data.stale_items

            if contradictions and contradictions.escalation_recommended:
                return "ESCALATE_TO_HUMAN", features.composite.confidence_score * 0.5, [], [], escalation_reasons

            return "ESCALATE_TO_HUMAN", features.composite.confidence_score, [], [], escalation_reasons

        # Check for blocking compliance issues
        if compliance and not compliance.passed:
            blocking = [v for v in compliance.violations if v.get("severity") == "blocking"]
            if blocking:
                return "DECLINE", 0.8, [], [], [b.get("message", "") for b in blocking]

        # Check for missing documents
        if completeness and not completeness.complete:
            missing_info.extend(completeness.missing_required)
            # If critical docs missing, pend
            if missing_info:
                return "PEND_FOR_INFORMATION", features.composite.confidence_score * 0.7, [], [], missing_info

        # Check for stale data
        if stale_data and stale_data.requires_update:
            return "PEND_FOR_INFORMATION", features.composite.confidence_score * 0.6, [], [], ["Stale documentation requires update"]

        # Check for contradictions requiring pend
        if contradictions and contradictions.pend_recommended:
            return "PEND_FOR_INFORMATION", features.composite.confidence_score * 0.6, [], [], ["Data contradictions require reconciliation"]

        # Use hypothesis recommendation as base
        decision = hypothesis.initial_recommendation
        confidence = hypothesis.recommendation_confidence

        # Apply conditions and covenants based on decision
        if decision in ["APPROVE_WITH_CONDITIONS", "APPROVE"]:
            conditions = self.condition_recommender.recommend_conditions(features, request, decision)
            covenants = self.covenant_recommender.recommend_covenants(features, request)

        # Check for counter-offer opportunity
        if decision in ["APPROVE_WITH_CONDITIONS"] and features.composite.normalized_risk_grade in ["5", "6"]:
            # Could suggest counter-offer instead
            if features.policy.policy_exception_count > 0:
                decision = "COUNTER_OFFER"

        # Final decline check for high risk
        if features.composite.normalized_risk_grade == "9":
            if not (features.capacity.dscr_ttm and features.capacity.dscr_ttm >= 1.0):
                decision = "DECLINE"
                confidence *= 0.8

        return decision, confidence, conditions, covenants, missing_info
