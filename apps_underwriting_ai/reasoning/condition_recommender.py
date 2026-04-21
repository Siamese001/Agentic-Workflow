"""
Condition Recommender - Generates conditions for APPROVE_WITH_CONDITIONS decisions.
"""

from typing import List

from ..types import DecisionState, RiskFeatures, UnderwritingRequest


class ConditionRecommender:
    """
    Recommends conditions precedent and ongoing requirements.

    Generates conditions based on risk profile gaps and mitigants needed.
    """

    def recommend_conditions(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
        proposed_decision: DecisionState,
    ) -> List[str]:
        """
        Recommend conditions based on risk assessment.

        Args:
            features: Derived RiskFeatures
            request: UnderwritingRequest
            proposed_decision: Proposed decision state

        Returns:
            List of recommended conditions
        """
        conditions = []

        if proposed_decision not in ["APPROVE_WITH_CONDITIONS", "PEND_FOR_INFORMATION"]:
            return conditions

        # Document conditions
        conditions.extend(self._document_conditions(features, request))

        # Collateral conditions
        conditions.extend(self._collateral_conditions(features, request))

        # Structural conditions
        conditions.extend(self._structural_conditions(features, request))

        # Reporting conditions
        conditions.extend(self._reporting_conditions(features, request))

        return conditions

    def _document_conditions(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Recommend document-related conditions."""
        conditions = []
        docs = request.documents

        # Missing financial documents
        if not docs.debt_schedule:
            conditions.append("Complete debt schedule required prior to closing")

        # Stale documents
        if features.documentation.staleness_score > 0.3:
            conditions.append("Updated financial statements required if more than 120 days old at closing")

        # AR aging
        if not docs.ar_aging and request.collateral.collateral_type in ["ar", "mixed"]:
            conditions.append("Current AR aging schedule required for borrowing base certification")

        # Insurance
        if not docs.insurance_certificates:
            conditions.append("Evidence of insurance naming Lender as loss payee required")

        return conditions

    def _collateral_conditions(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Recommend collateral-related conditions."""
        conditions = []

        # Lien perfection
        if request.collateral.collateral_type in ["ar", "mixed"]:
            conditions.append("First lien UCC filing on accounts receivable required")

        if request.collateral.collateral_type in ["equipment", "real_estate"]:
            conditions.append("Mortgage/deed of trust and UCC filing required on equipment")

        # Field exam
        if features.collateral.collateral_quality_score <= 0.5:
            conditions.append("Field examination of collateral required within 30 days of closing")

        # Appraisal
        if request.collateral.appraisal_date:
            from datetime import datetime

            try:
                appraisal_dt = datetime.fromisoformat(
                    request.collateral.appraisal_date.replace("Z", "+00:00")
                )
                days_old = (datetime.now() - appraisal_dt).days
                if days_old > 180:
                    conditions.append("Updated appraisal required if transaction not closed within 60 days")
            except (ValueError, TypeError, AttributeError):  # guardian: allow-silent-swallow -- appraisal-date parse failure skips the optional 180-day check; underwriting continues
                pass

        return conditions

    def _structural_conditions(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Recommend structural conditions."""
        conditions = []

        # Personal guaranty
        if request.requested_structure.guarantor_required:
            conditions.append("Unlimited personal guaranty from all 20%+ owners required")

        # Reduced advance rate for higher risk
        if features.composite.normalized_risk_grade in ["5", "6"]:
            conditions.append("Advance rate capped at 75% of eligible AR pending 6-month performance")

        # Springing dominion
        if features.liquidity.deposit_stability_score <= 0.5:
            conditions.append("Springing cash dominion triggered if DSCR falls below 1.20x")

        return conditions

    def _reporting_conditions(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Recommend reporting conditions."""
        conditions = []

        # Monthly reporting for higher risk
        if features.composite.normalized_risk_grade in ["5", "6", "7"]:
            conditions.append("Monthly borrowing base certificate and financial reporting required")

        # Quarterly for lower risk
        elif features.composite.normalized_risk_grade in ["3", "4"]:
            conditions.append("Quarterly financial reporting and annual CPA-reviewed financials required")

        # Exception tracking
        if features.policy.policy_exception_count > 0:
            conditions.append("Monthly tracking of policy exception compliance required")

        return conditions
