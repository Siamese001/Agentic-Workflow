"""
Document Completeness Validator - Verifies required documents are present.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..types import DocumentPackage, UnderwritingRequest


@dataclass
class CompletenessResult:
    """Result of document completeness validation."""
    complete: bool = False
    completeness_pct: float = 0.0
    missing_required: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)
    stale_documents: List[str] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)


class DocumentCompletenessValidator:
    """
    Validates that required documents are present by product and decision type.

    Checks:
    - Required docs by product type
    - Required docs by decision type
    - Stale document detection
    - Document quality flags
    """

    # Document requirements by product type
    PRODUCT_REQUIRED_DOCS = {
        "term_loan": [
            "financial_statements",
            "tax_returns",
            "debt_schedule",
        ],
        "revolver": [
            "financial_statements",
            "tax_returns",
            "debt_schedule",
            "ar_aging",
            "bank_statements",
        ],
        "equipment_finance": [
            "financial_statements",
            "tax_returns",
            "appraisals",
            "insurance_certificates",
        ],
        "sba_like": [
            "financial_statements",
            "tax_returns",
            "bank_statements",
            "entity_docs",
            "debt_schedule",
        ],
    }

    # Additional docs for new vs renewal
    DECISION_TYPE_ADDITIONAL_DOCS = {
        "new": ["entity_docs"],
        "renewal": [],
        "increase": ["updated_financials"],
        "modification": [],
    }

    # Document freshness thresholds (days)
    FRESHNESS_THRESHOLDS = {
        "financial_statements": 365,
        "tax_returns": 180,
        "bank_statements": 90,
        "ar_aging": 60,
        "ap_aging": 60,
        "debt_schedule": 90,
        "appraisals": 365,
    }

    def validate(
        self,
        request: UnderwritingRequest,
    ) -> CompletenessResult:
        """
        Validate document completeness.

        Args:
            request: UnderwritingRequest

        Returns:
            CompletenessResult
        """
        result = CompletenessResult()
        docs = request.documents
        product = request.product_type
        decision_type = request.decision_type

        # Get required documents
        required = self._get_required_documents(product, decision_type)

        # Check each required document
        for doc_type in required:
            present, count = self._check_document_present(docs, doc_type)

            if not present:
                result.missing_required.append(doc_type)
                result.findings.append({
                    "document_type": doc_type,
                    "status": "missing",
                    "severity": "required",
                    "message": f"Required document '{doc_type}' not present",
                })
            else:
                result.findings.append({
                    "document_type": doc_type,
                    "status": "present",
                    "count": count,
                    "severity": "info",
                })

        # Check document freshness
        result.stale_documents = self._check_document_freshness(request)

        # Calculate completeness percentage
        if required:
            present_count = len(required) - len(result.missing_required)
            result.completeness_pct = present_count / len(required)
        else:
            result.completeness_pct = 1.0

        result.complete = len(result.missing_required) == 0

        return result

    def _get_required_documents(
        self,
        product_type: str,
        decision_type: str,
    ) -> List[str]:
        """Get list of required documents for product/decision combination."""
        required = list(self.PRODUCT_REQUIRED_DOCS.get(product_type, []))
        additional = self.DECISION_TYPE_ADDITIONAL_DOCS.get(decision_type, [])

        # Add unique additional docs
        for doc in additional:
            if doc not in required:
                required.append(doc)

        return required

    def _check_document_present(
        self,
        docs: DocumentPackage,
        doc_type: str,
    ) -> tuple[bool, int]:
        """Check if document type is present and return count."""
        doc_lists = {
            "financial_statements": docs.financial_statements,
            "tax_returns": docs.tax_returns,
            "bank_statements": docs.bank_statements,
            "ar_aging": docs.ar_aging,
            "ap_aging": docs.ap_aging,
            "debt_schedule": docs.debt_schedule,
            "entity_docs": docs.entity_docs,
            "insurance_certificates": docs.insurance_certificates,
            "appraisals": docs.appraisals,
            "management_comments": docs.management_comments,
        }

        doc_list = doc_lists.get(doc_type, [])
        return len(doc_list) > 0, len(doc_list)

    def _check_document_freshness(
        self,
        request: UnderwritingRequest,
    ) -> List[str]:
        """Check for stale documents."""
        stale = []
        from datetime import datetime

        # Check collateral appraisal date
        if request.collateral.appraisal_date:
            try:
                appraisal_dt = datetime.fromisoformat(
                    request.collateral.appraisal_date.replace('Z', '+00:00'),
                )
                days_old = (datetime.now() - appraisal_dt).days
                threshold = self.FRESHNESS_THRESHOLDS.get("appraisals", 365)

                if days_old > threshold:
                    stale.append(f"appraisal ({days_old} days old)")
            except Exception:
                pass

        # Check field exam date
        if request.collateral.field_exam_date:
            try:
                exam_dt = datetime.fromisoformat(
                    request.collateral.field_exam_date.replace('Z', '+00:00'),
                )
                days_old = (datetime.now() - exam_dt).days

                if days_old > 180:
                    stale.append(f"field_exam ({days_old} days old)")
            except Exception:
                pass

        return stale
