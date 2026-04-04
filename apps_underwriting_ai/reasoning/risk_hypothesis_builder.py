"""
Risk Hypothesis Builder - Produces structured risk hypothesis from features and evidence.
"""
from typing import List, Optional
from dataclasses import dataclass, field

from ..types import RiskFeatures, UnderwritingRequest, DecisionState


@dataclass
class RiskHypothesis:
    """Structured risk hypothesis output."""
    primary_strengths: List[str] = field(default_factory=list)
    primary_risks: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    initial_recommendation: str = ""
    recommendation_confidence: float = 0.0


class RiskHypothesisBuilder:
    """
    Builds structured risk hypothesis from risk features.

    Identifies:
    - Primary credit strengths
    - Primary credit risks
    - Open questions requiring resolution
    - Initial recommendation
    """

    def build_hypothesis(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures
    ) -> RiskHypothesis:
        """
        Build risk hypothesis from features.

        Args:
            request: UnderwritingRequest
            features: Derived RiskFeatures

        Returns:
            RiskHypothesis with strengths, risks, and recommendation
        """
        hypothesis = RiskHypothesis()

        # Identify strengths
        hypothesis.primary_strengths = self._identify_strengths(features)

        # Identify risks
        hypothesis.primary_risks = self._identify_risks(features)

        # Identify open questions
        hypothesis.open_questions = self._identify_open_questions(features, request)

        # Generate initial recommendation
        hypothesis.initial_recommendation, hypothesis.recommendation_confidence = self._generate_recommendation(features)

        return hypothesis

    def _identify_strengths(self, features: RiskFeatures) -> List[str]:
        """Identify primary credit strengths."""
        strengths = []

        # Capacity strengths
        if features.capacity.dscr_ttm and features.capacity.dscr_ttm >= 2.0:
            strengths.append(f"Strong debt service coverage at {features.capacity.dscr_ttm:.2f}x")
        elif features.capacity.dscr_ttm and features.capacity.dscr_ttm >= 1.5:
            strengths.append(f"Adequate debt service coverage at {features.capacity.dscr_ttm:.2f}x")

        if features.capacity.debt_to_ebitda_ttm and features.capacity.debt_to_ebitda_ttm <= 2.0:
            strengths.append(f"Conservative leverage at {features.capacity.debt_to_ebitda_ttm:.2f}x Debt/EBITDA")

        if features.capacity.revenue_trend_score >= 0.7:
            strengths.append("Positive revenue trend trajectory")

        # Liquidity strengths
        if features.liquidity.current_ratio and features.liquidity.current_ratio >= 1.5:
            strengths.append(f"Healthy liquidity with current ratio of {features.liquidity.current_ratio:.2f}x")

        if features.liquidity.deposit_stability_score >= 0.8:
            strengths.append("Stable deposit relationship with minimal NSF/overdraft activity")

        # Collateral strengths
        if features.collateral.ltv and features.collateral.ltv <= 0.7:
            strengths.append(f"Strong collateral coverage with LTV of {features.collateral.ltv:.1%}")

        if features.collateral.collateral_quality_score >= 0.7:
            strengths.append("High-quality collateral with first lien position")

        # Credit strengths
        if features.credit.personal_fico_min and features.credit.personal_fico_min >= 720:
            strengths.append(f"Strong personal credit with FICO of {features.credit.personal_fico_min}")

        if features.credit.derogatory_event_score <= 0.1:
            strengths.append("Clean credit history with no significant derogatories")

        # Relationship strengths
        if features.relationship.tenure_score >= 0.7:
            strengths.append("Established banking relationship with demonstrated history")

        if features.relationship.historical_performance_score >= 0.9:
            strengths.append("Strong historical payment performance")

        return strengths

    def _identify_risks(self, features: RiskFeatures) -> List[str]:
        """Identify primary credit risks."""
        risks = []

        # Capacity risks
        if features.capacity.dscr_ttm and features.capacity.dscr_ttm < 1.25:
            risks.append(f"Thin debt service coverage at {features.capacity.dscr_ttm:.2f}x, below policy minimum")

        if features.capacity.debt_to_ebitda_ttm and features.capacity.debt_to_ebitda_ttm > 3.5:
            risks.append(f"Elevated leverage at {features.capacity.debt_to_ebitda_ttm:.2f}x Debt/EBITDA")

        if features.capacity.revenue_trend_score <= 0.4:
            risks.append("Declining revenue trend indicates potential business pressure")

        if features.capacity.earnings_stability_score <= 0.4:
            risks.append("Volatile earnings pattern creates repayment uncertainty")

        # Liquidity risks
        if features.liquidity.current_ratio and features.liquidity.current_ratio < 1.2:
            risks.append(f"Tight liquidity with current ratio of {features.liquidity.current_ratio:.2f}x")

        if features.liquidity.deposit_stability_score <= 0.4:
            risks.append("Unstable deposit pattern with NSF/overdraft activity")

        # Collateral risks
        if features.collateral.ltv and features.collateral.ltv > 0.8:
            risks.append(f"High LTV at {features.collateral.ltv:.1%} leaves limited cushion")

        if features.collateral.collateral_quality_score <= 0.4:
            risks.append("Collateral quality concerns or junior lien position")

        # Credit risks
        if features.credit.personal_fico_min and features.credit.personal_fico_min < 650:
            risks.append(f"Weak personal credit with FICO below 650")
        elif features.credit.personal_fico_min and features.credit.personal_fico_min < 680:
            risks.append(f"Marginal personal credit with FICO of {features.credit.personal_fico_min}")

        if features.credit.derogatory_event_score > 0.5:
            risks.append("Significant derogatory credit events in history")

        if features.credit.delinquencies_24m > 2:
            risks.append("Multiple recent delinquencies indicate credit stress")

        # Operating risks
        if features.operating_risk.industry_risk_score >= 0.7:
            risks.append("Operating in higher-risk industry segment")

        if features.operating_risk.years_in_business_score <= 0.4:
            risks.append("Limited operating history increases business risk")

        # Documentation risks
        if features.documentation.document_completeness_score < 0.7:
            risks.append("Incomplete documentation limits full risk assessment")

        if features.documentation.data_consistency_score < 0.7:
            risks.append("Data inconsistencies between sources require reconciliation")

        return risks

    def _identify_open_questions(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest
    ) -> List[str]:
        """Identify open questions requiring resolution."""
        questions = []

        # Check for missing data
        if features.capacity.dscr_ttm is None:
            questions.append("DSCR calculation requires verified debt service figure")

        if features.credit.personal_fico_min is None and request.requested_structure.guarantor_required:
            questions.append("Personal guarantor FICO scores not provided")

        # Check for stale documents
        if features.documentation.staleness_score > 0.3:
            questions.append("Financial documentation may be outdated - verify current position")

        # Check for policy exceptions
        if features.policy.policy_exception_count > 0:
            questions.append("Policy exception justification and approval authority required")

        # Check concentration
        if features.operating_risk.customer_concentration_score is None:
            questions.append("Customer concentration analysis requires AR aging detail")

        return questions

    def _generate_recommendation(self, features: RiskFeatures) -> tuple[str, float]:
        """Generate initial recommendation and confidence."""
        composite = features.composite

        # Based on composite risk grade
        if composite.normalized_risk_grade in ["1", "2", "3"]:
            return "APPROVE", composite.confidence_score
        elif composite.normalized_risk_grade == "4":
            return "APPROVE_WITH_CONDITIONS", composite.confidence_score
        elif composite.normalized_risk_grade == "5":
            if features.policy.policy_exception_count > 0:
                return "PEND_FOR_INFORMATION", composite.confidence_score * 0.8
            return "APPROVE_WITH_CONDITIONS", composite.confidence_score
        elif composite.normalized_risk_grade == "6":
            return "COUNTER_OFFER", composite.confidence_score * 0.9
        elif composite.normalized_risk_grade in ["7", "8"]:
            return "PEND_FOR_INFORMATION", composite.confidence_score * 0.7
        elif composite.normalized_risk_grade == "9":
            if features.policy.mandatory_review_triggered:
                return "ESCALATE_TO_HUMAN", composite.confidence_score * 0.6
            return "DECLINE", composite.confidence_score
        else:
            return "DECLINE", composite.confidence_score * 0.5
