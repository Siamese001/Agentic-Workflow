"""
Test Document Completeness Validator.
"""

import unittest
from datetime import datetime, timezone

from apps_underwriting_ai.types import (
    BankingPackage,
    BorrowerProfile,
    CollateralPackage,
    CreditPackage,
    DocumentPackage,
    DocumentRef,
    FinancialPackage,
    FinancialPeriod,
    OwnerInfo,
    UnderwritingRequest,
)
from apps_underwriting_ai.validators.document_completeness_validator import DocumentCompletenessValidator


class TestDocumentCompleteness(unittest.TestCase):
    """Test cases for document completeness validation."""

    def setUp(self):
        self.validator = DocumentCompletenessValidator()

    def _make_minimal_request(
        self, product_type="term_loan", decision_type="new", documents=None, collateral_appraisal_date=None
    ):
        """Build a minimal UnderwritingRequest for document completeness tests."""
        return UnderwritingRequest(
            request_id="DOC-TEST-001",
            submission_ts="2024-03-15T09:30:00Z",
            product_type=product_type,
            decision_type=decision_type,
            requested_amount=500000.0,
            requested_term_months=36,
            requested_structure={},
            borrower=BorrowerProfile(
                legal_name="Test Co",
                entity_type="llc",
                industry_code="541330",
                industry_description="Engineering",
                years_in_business=5.0,
                state_of_incorporation="CA",
                ownership=[
                    OwnerInfo(
                        owner_name="Owner",
                        ownership_pct=100.0,
                        role="CEO",
                        fico=700,
                        guarantor=True,
                    )
                ],
            ),
            financials=FinancialPackage(
                periods=[
                    FinancialPeriod(
                        period_end="2023-12-31",
                        fiscal_type="annual",
                        revenue=1000000.0,
                    )
                ],
            ),
            collateral=CollateralPackage(
                collateral_type="unsecured",
                lien_position="none",
                appraisal_date=collateral_appraisal_date,
            ),
            credit=CreditPackage(
                personal_fico_scores=[700],
                delinquencies_24m=0,
                defaults_ever=0,
                bankruptcies_ever=0,
            ),
            banking=BankingPackage(nsf_count_12m=0, overdraft_days_12m=0, deposit_trend="unknown"),
            documents=documents if documents is not None else DocumentPackage(),
            policy_context={},
            external_signals={},
            relationship_context={},
            decision_constraints={},
        )

    def test_complete_document_package(self):
        """Happy path: all required docs present — complete=True, completeness_pct=1.0."""

        def _doc(n):
            return DocumentRef(doc_id=f"DOC-{n:03d}", doc_type="test", source_uri="t.pdf", hash=f"h{n}")

        docs = DocumentPackage(
            financial_statements=[_doc(1)],
            tax_returns=[_doc(2)],
            debt_schedule=[_doc(3)],
            entity_docs=[_doc(4)],
        )
        request = self._make_minimal_request(documents=docs)
        result = self.validator.validate(request)
        self.assertTrue(result.complete)
        self.assertEqual(result.completeness_pct, 1.0)
        self.assertEqual(result.missing_required, [])

    def test_incomplete_package(self):
        """Failure path: empty docs — complete=False, all 4 required docs missing."""
        request = self._make_minimal_request(documents=DocumentPackage())
        result = self.validator.validate(request)
        self.assertFalse(result.complete)
        self.assertEqual(result.completeness_pct, 0.0)
        self.assertEqual(len(result.missing_required), 4)

    def test_stale_appraisal_detected(self):
        """Edge case: now_provider injection (phase-introduced) flags a stale appraisal."""
        frozen_now = datetime(2024, 6, 1, tzinfo=timezone.utc)
        validator = DocumentCompletenessValidator(now_provider=lambda: frozen_now)
        request = self._make_minimal_request(collateral_appraisal_date="2022-01-01")
        result = validator.validate(request)
        self.assertEqual(len(result.stale_documents), 1)
        self.assertIn("appraisal", result.stale_documents[0])


if __name__ == "__main__":
    unittest.main()
