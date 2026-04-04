"""
Counter Offer Recommender - Recommends revised terms when original request is too aggressive.
"""
from typing import List, Optional
from dataclasses import dataclass

from ..types import RiskFeatures, UnderwritingRequest


@dataclass
class CounterOfferTerms:
    """Recommended counter-offer terms."""
    recommended_amount: float
    recommended_term_months: int
    pricing_adjustment_bps: int
    additional_collateral_required: bool
    additional_guarantor_required: bool
    rationale: List[str]


class CounterOfferRecommender:
    """
    Recommends revised terms when original request is too aggressive.

    Suggests:
    - Reduced amounts
    - Shorter terms
    - Additional collateral/guaranties
    - Pricing adjustments
    """

    def recommend_counter_offer(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest
    ) -> Optional[CounterOfferTerms]:
        """
        Recommend counter-offer terms.

        Args:
            features: Derived RiskFeatures
            request: UnderwritingRequest

        Returns:
            CounterOfferTerms or None if no counter-offer needed
        """
        # Only recommend if risk is borderline
        risk_grade = int(features.composite.normalized_risk_grade)
        if risk_grade < 5 or risk_grade > 7:
            return None

        original_amount = request.requested_amount
        original_term = request.requested_term_months

        # Calculate adjustments
        amount_reduction = self._calculate_amount_reduction(features, request)
        term_reduction = self._calculate_term_reduction(features, request)
        pricing_adj = self._calculate_pricing_adjustment(features, request)

        # Build rationale
        rationale = self._build_rationale(features, request, amount_reduction, term_reduction)

        if not rationale:
            return None

        return CounterOfferTerms(
            recommended_amount=original_amount * (1 - amount_reduction),
            recommended_term_months=int(original_term * (1 - term_reduction)),
            pricing_adjustment_bps=pricing_adj,
            additional_collateral_required=features.collateral.collateral_quality_score < 0.5,
            additional_guarantor_required=features.credit.personal_fico_min and features.credit.personal_fico_min < 680,
            rationale=rationale
        )

    def _calculate_amount_reduction(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest
    ) -> float:
        """Calculate recommended amount reduction percentage."""
        reduction = 0.0

        # DSCR-driven reduction
        if features.capacity.dscr_ttm and features.capacity.dscr_ttm < 1.5:
            reduction = max(reduction, 0.15)

        # Leverage-driven reduction
        if features.capacity.debt_to_ebitda_ttm and features.capacity.debt_to_ebitda_ttm > 3.0:
            reduction = max(reduction, 0.10)

        # LTV-driven reduction
        if features.collateral.ltv and features.collateral.ltv > 0.75:
            reduction = max(reduction, 0.10)

        # Cap at 30%
        return min(reduction, 0.30)

    def _calculate_term_reduction(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest
    ) -> float:
        """Calculate recommended term reduction percentage."""
        reduction = 0.0

        # Shorten term for higher risk
        risk_grade = int(features.composite.normalized_risk_grade)
        if risk_grade >= 6:
            reduction = max(reduction, 0.20)

        # Shorten for lower tenure
        if features.relationship.tenure_score < 0.5:
            reduction = max(reduction, 0.15)

        return min(reduction, 0.33)  # Cap at 1/3 reduction

    def _calculate_pricing_adjustment(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest
    ) -> int:
        """Calculate pricing adjustment in basis points."""
        bps = 0

        # Base adjustment by risk grade
        risk_grade = int(features.composite.normalized_risk_grade)
        if risk_grade == 6:
            bps += 50
        elif risk_grade == 7:
            bps += 100

        # Additional for policy exceptions
        bps += features.policy.policy_exception_count * 25

        # Additional for weak credit
        if features.credit.personal_fico_min and features.credit.personal_fico_min < 680:
            bps += 50

        # Additional for industry risk
        if features.operating_risk.industry_risk_score > 0.6:
            bps += 25

        return min(bps, 250)  # Cap at 250 bps

    def _build_rationale(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
        amount_reduction: float,
        term_reduction: float
    ) -> List[str]:
        """Build rationale for counter-offer."""
        rationale = []

        if amount_reduction > 0:
            if features.capacity.dscr_ttm and features.capacity.dscr_ttm < 1.5:
                rationale.append(
                    f"DSCR of {features.capacity.dscr_ttm:.2f}x supports lower facility amount"
                )

            if features.collateral.ltv and features.collateral.ltv > 0.75:
                rationale.append(
                    f"LTV of {features.collateral.ltv:.1%} limits advance against collateral"
                )

        if term_reduction > 0:
            rationale.append(
                "Shorter term aligns with business track record and reduces long-term risk"
            )

        if features.policy.policy_exception_count > 0:
            rationale.append(
                f"Tighter structure mitigates {features.policy.policy_exception_count} policy exception(s)"
            )

        return rationale
