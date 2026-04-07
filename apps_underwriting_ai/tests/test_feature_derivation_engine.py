"""
Test Feature Derivation Engine.
"""
import unittest

from apps_underwriting_ai.engines.feature_derivation_engine import FeatureDerivationEngine
from apps_underwriting_ai.types import (
    BankingPackage,
    BorrowerProfile,
    CollateralPackage,
    CreditPackage,
    FinancialPackage,
    FinancialPeriod,
    OwnerInfo,
    UnderwritingRequest,
)


class TestFeatureDerivation(unittest.TestCase):
    """Test cases for feature derivation."""

    def setUp(self):
        self.engine = FeatureDerivationEngine()

    def _create_test_request(self):
        """Create a test request."""
        return UnderwritingRequest(
            request_id="TEST-001",
            submission_ts="2024-03-15T09:30:00Z",
            product_type="term_loan",
            decision_type="new",
            requested_amount=1000000.00,
            requested_term_months=60,
            requested_structure={},
            borrower=BorrowerProfile(
                legal_name="Test Co",
                entity_type="llc",
                industry_code="541330",
                industry_description="Engineering",
                years_in_business=8.0,
                state_of_incorporation="CA",
                ownership=[
                    OwnerInfo(
                        owner_name="Test",
                        ownership_pct=100.0,
                        role="CEO",
                        fico=720,
                        guarantor=True,
                    ),
                ],
            ),
            financials=FinancialPackage(
                periods=[
                    FinancialPeriod(
                        period_end="2023-12-31",
                        fiscal_type="annual",
                        revenue=5000000.00,
                        ebitda=1000000.00,
                        total_debt=1500000.00,
                        debt_service=300000.00,
                    ),
                ],
                calculated_metrics={
                    "dscr_ttm": 3.33,
                    "debt_to_ebitda_ttm": 1.50,
                },
            ),
            collateral=CollateralPackage(
                collateral_type="ar",
                estimated_value=2000000.00,
                lien_position="first",
            ),
            credit=CreditPackage(
                personal_fico_scores=[720],
                delinquencies_24m=0,
                defaults_ever=0,
                bankruptcies_ever=0,
            ),
            banking=BankingPackage(
                nsf_count_12m=0,
                overdraft_days_12m=0,
                deposit_trend="up",
            ),
            documents={},
            policy_context={},
            external_signals={},
            relationship_context={},
            decision_constraints={},
        )

    def test_dscr_calculation(self):
        """Test DSCR feature derivation."""
        request = self._create_test_request()
        features = self.engine.derive_features(request, None)

        self.assertIsNotNone(features.capacity.dscr_ttm)
        self.assertGreater(features.capacity.dscr_ttm, 0)

    def test_leverage_calculation(self):
        """Test leverage feature derivation."""
        request = self._create_test_request()
        features = self.engine.derive_features(request, None)

        self.assertIsNotNone(features.capacity.debt_to_ebitda_ttm)
        self.assertGreater(features.capacity.debt_to_ebitda_ttm, 0)

    def test_composite_score(self):
        """Test composite risk score derivation."""
        request = self._create_test_request()
        features = self.engine.derive_features(request, None)

        self.assertIsNotNone(features.composite.raw_risk_score)
        self.assertGreaterEqual(features.composite.raw_risk_score, 0)
        self.assertLessEqual(features.composite.raw_risk_score, 1)
        self.assertIn(features.composite.normalized_risk_grade, [str(i) for i in range(1, 10)])


if __name__ == "__main__":
    unittest.main()
