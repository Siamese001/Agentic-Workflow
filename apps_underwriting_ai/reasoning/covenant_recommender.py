"""
Covenant Recommender - Generates covenants when needed.
"""
from typing import List

from ..types import RiskFeatures, UnderwritingRequest


class CovenantRecommender:
    """
    Recommends ongoing financial covenants based on risk profile.

    Generates covenants to monitor credit quality post-close.
    """

    def recommend_covenants(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """
        Recommend ongoing covenants.

        Args:
            features: Derived RiskFeatures
            request: UnderwritingRequest

        Returns:
            List of recommended covenants
        """
        covenants = []
        policy = request.policy_context

        # DSCR covenant
        if features.capacity.dscr_ttm:
            min_dscr = max(1.10, (features.capacity.dscr_ttm * 0.8))  # 80% of current
            if policy.min_dscr:
                min_dscr = max(min_dscr, policy.min_dscr)
            covenants.append(f"Minimum quarterly DSCR of {min_dscr:.2f}x tested quarterly")

        # Leverage covenant
        if features.capacity.debt_to_ebitda_ttm:
            max_lev = features.capacity.debt_to_ebitda_ttm * 1.2  # 20% cushion
            if policy.max_debt_to_ebitda:
                max_lev = min(max_lev, policy.max_debt_to_ebitda * 1.1)
            covenants.append(f"Maximum Debt/EBITDA of {max_lev:.2f}x tested quarterly")

        # Liquidity covenant
        if features.liquidity.current_ratio:
            min_ratio = min(1.25, features.liquidity.current_ratio * 0.8)
            covenants.append(f"Minimum current ratio of {min_ratio:.2f}x")

        # Collateral coverage
        if features.collateral.ltv:
            max_ltv = min(0.85, features.collateral.ltv * 1.15)
            covenants.append(f"Maximum LTV of {max_ltv:.1%} based on annual appraisal")

        # Minimum liquidity
        if features.liquidity.cash_buffer_months:
            min_cash = max(1.0, features.liquidity.cash_buffer_months * 0.5)
            covenants.append(f"Minimum cash balance of {min_cash:.1f} months debt service")

        # Additional covenants for higher risk
        if features.composite.normalized_risk_grade in ["5", "6"]:
            covenants.append("Annual financial statements reviewed by CPA within 90 days of year-end")
            covenants.append("No material adverse change in business condition without immediate notice")

        if features.operating_risk.customer_concentration_score and features.operating_risk.customer_concentration_score > 0.3:
            covenants.append("Top customer concentration not to exceed 35% of AR without approval")

        return covenants
