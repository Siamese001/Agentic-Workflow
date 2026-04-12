"""
Feature Interpreter - Converts numeric features into underwriter-readable prose.
"""

from typing import List

from ..types import RiskFeatures, UnderwritingRequest


class FeatureInterpreter:
    """
    Converts numeric risk features into business language.

    Explains risk in underwriter-friendly terms with specific metrics and policy references.
    """

    def interpret_features(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """
        Generate human-readable interpretations of risk features.

        Args:
            features: Derived RiskFeatures
            request: UnderwritingRequest for context

        Returns:
            List of interpretation strings
        """
        interpretations = []

        # Capacity interpretations
        interpretations.extend(self._interpret_capacity(features, request))

        # Liquidity interpretations
        interpretations.extend(self._interpret_liquidity(features, request))

        # Collateral interpretations
        interpretations.extend(self._interpret_collateral(features, request))

        # Credit interpretations
        interpretations.extend(self._interpret_credit(features, request))

        # Operating risk interpretations
        interpretations.extend(self._interpret_operating_risk(features, request))

        # Relationship interpretations
        interpretations.extend(self._interpret_relationship(features, request))

        return interpretations

    def _interpret_capacity(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Interpret capacity features."""
        interpretations = []
        policy = request.policy_context

        if features.capacity.dscr_ttm:
            dscr = features.capacity.dscr_ttm
            if policy.min_dscr:
                if dscr >= policy.min_dscr * 1.5:
                    interpretations.append(
                        f"DSCR of {dscr:.2f}x provides strong coverage cushion "
                        f"against policy minimum of {policy.min_dscr:.2f}x",
                    )
                elif dscr >= policy.min_dscr:
                    interpretations.append(
                        f"DSCR of {dscr:.2f}x meets policy minimum of {policy.min_dscr:.2f}x",
                    )
                else:
                    interpretations.append(
                        f"DSCR of {dscr:.2f}x falls below policy minimum of {policy.min_dscr:.2f}x - "
                        "exception or structure adjustment required",
                    )
            else:
                interpretations.append(f"Debt service coverage ratio is {dscr:.2f}x")

        if features.capacity.debt_to_ebitda_ttm:
            lev = features.capacity.debt_to_ebitda_ttm
            if policy.max_debt_to_ebitda:
                if lev <= policy.max_debt_to_ebitda * 0.7:
                    interpretations.append(
                        f"Conservative leverage at {lev:.2f}x vs policy maximum {policy.max_debt_to_ebitda:.2f}x",
                    )
                elif lev <= policy.max_debt_to_ebitda:
                    interpretations.append(
                        f"Leverage at {lev:.2f}x is within policy limits",
                    )
                else:
                    interpretations.append(
                        f"Leverage of {lev:.2f}x exceeds policy maximum of {policy.max_debt_to_ebitda:.2f}x",
                    )

        if features.capacity.ebitda_margin_ttm:
            margin = features.capacity.ebitda_margin_ttm
            if margin >= 0.20:
                interpretations.append(f"Strong profitability with EBITDA margin of {margin:.1%}")
            elif margin >= 0.10:
                interpretations.append(f"Adequate profitability with EBITDA margin of {margin:.1%}")
            else:
                interpretations.append(f"Thin margins at {margin:.1%} limit debt service capacity")

        return interpretations

    def _interpret_liquidity(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Interpret liquidity features."""
        interpretations = []

        if features.liquidity.current_ratio:
            ratio = features.liquidity.current_ratio
            if ratio >= 2.0:
                interpretations.append(f"Strong liquidity position with current ratio of {ratio:.2f}x")
            elif ratio >= 1.5:
                interpretations.append(f"Adequate liquidity with current ratio of {ratio:.2f}x")
            elif ratio >= 1.2:
                interpretations.append(
                    f"Tight liquidity with current ratio of {ratio:.2f}x - monitoring recommended"
                )
            else:
                interpretations.append(
                    f"Concerning liquidity at {ratio:.2f}x current ratio - structure accordingly"
                )

        if features.liquidity.deposit_stability_score:
            score = features.liquidity.deposit_stability_score
            if score >= 0.8:
                interpretations.append("Stable deposit relationship supports cash flow assessment")
            elif score <= 0.4:
                interpretations.append("Deposit volatility indicates cash management challenges")

        return interpretations

    def _interpret_collateral(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Interpret collateral features."""
        interpretations = []

        if features.collateral.ltv:
            ltv = features.collateral.ltv
            if ltv <= 0.60:
                interpretations.append(f"Conservative LTV of {ltv:.1%} provides substantial cushion")
            elif ltv <= 0.75:
                interpretations.append(f"Moderate LTV of {ltv:.1%} with adequate coverage")
            elif ltv <= 0.85:
                interpretations.append(f"Higher LTV of {ltv:.1%} requires careful monitoring")
            else:
                interpretations.append(
                    f"Elevated LTV of {ltv:.1%} - consider additional collateral or guaranty"
                )

        if features.collateral.borrowing_base_coverage:
            coverage = features.collateral.borrowing_base_coverage
            if coverage >= 1.5:
                interpretations.append(f"Strong borrowing base coverage at {coverage:.2f}x of request")
            elif coverage >= 1.2:
                interpretations.append(f"Adequate borrowing base coverage at {coverage:.2f}x")
            else:
                interpretations.append(
                    f"Tight borrowing base coverage at {coverage:.2f}x - consider amount reduction"
                )

        return interpretations

    def _interpret_credit(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Interpret credit features."""
        interpretations = []
        policy = request.policy_context

        if features.credit.personal_fico_min:
            fico = features.credit.personal_fico_min
            if policy.min_fico:
                if fico >= policy.min_fico + 50:
                    interpretations.append(f"Strong personal credit with FICO of {fico}, well above minimum")
                elif fico >= policy.min_fico:
                    interpretations.append(
                        f"Personal FICO of {fico} meets policy minimum of {policy.min_fico}"
                    )
                else:
                    interpretations.append(
                        f"Personal FICO of {fico} falls below policy minimum of {policy.min_fico}",
                    )
            else:
                if fico >= 720:
                    interpretations.append(f"Excellent personal credit with FICO of {fico}")
                elif fico >= 680:
                    interpretations.append(f"Adequate personal credit with FICO of {fico}")
                else:
                    interpretations.append(f"Weak personal credit with FICO of {fico}")

        if features.credit.derogatory_event_score > 0.3:
            interpretations.append("Derogatory credit history requires additional scrutiny")

        return interpretations

    def _interpret_operating_risk(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Interpret operating risk features."""
        interpretations = []
        borrower = request.borrower

        if features.operating_risk.industry_risk_score >= 0.7:
            interpretations.append(
                f"{borrower.industry_description} sector carries elevated industry risk - price accordingly",
            )

        if features.operating_risk.years_in_business_score:
            score = features.operating_risk.years_in_business_score
            years = borrower.years_in_business
            if score >= 0.8:
                interpretations.append(
                    f"Established {years:.1f}-year operating history reduces business risk"
                )
            elif score <= 0.4:
                interpretations.append(f"Limited {years:.1f}-year operating history increases business risk")

        return interpretations

    def _interpret_relationship(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Interpret relationship features."""
        interpretations = []
        rel = request.relationship_context

        if rel.existing_customer and rel.tenure_years:
            if rel.tenure_years >= 5:
                interpretations.append(
                    f"Strong {rel.tenure_years:.1f}-year banking relationship supports credit decision",
                )
            else:
                interpretations.append(
                    f"Building {rel.tenure_years:.1f}-year relationship with positive history",
                )

        if rel.deposit_relationship:
            interpretations.append("Active deposit relationship provides additional repayment insight")

        return interpretations
