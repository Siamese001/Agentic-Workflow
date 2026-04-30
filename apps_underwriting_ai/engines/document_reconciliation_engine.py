"""
Document Reconciliation Engine - Compares structured values vs parsed document values.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional

from ..parsers import (
    ARAgingParser,
    CollateralSummaryParser,
    DebtScheduleParser,
    FinancialStatementParser,
)
from ..types import UnderwritingRequest

# L4 retrieval wiring (Turn 3, Wave 36): Import creates ADG edge to L4_state


class ContradictionSeverity(Enum):
    """Severity levels for contradictions."""

    MINOR = "minor"  # Small variance, likely rounding
    MODERATE = "moderate"  # Noticeable difference, may need clarification
    MAJOR = "major"  # Significant variance, requires reconciliation
    CRITICAL = "critical"  # Material difference, blocks decision


@dataclass
class Contradiction:
    """Single identified contradiction."""

    field_name: str
    structured_value: Any
    document_value: Any
    variance_pct: Optional[float] = None
    severity: ContradictionSeverity = ContradictionSeverity.MODERATE
    source_doc_id: Optional[str] = None
    explanation: str = ""


@dataclass
class ReconciliationResult:
    """Result of document reconciliation."""

    contradictions: List[Contradiction] = field(default_factory=list)
    total_checked: int = 0
    match_count: int = 0
    mismatch_count: int = 0
    pass_rate: float = 0.0
    has_critical_issues: bool = False


class DocumentReconciliationEngine:
    """
    Compares structured values vs parsed document values.

    Identifies:
    - Revenue discrepancies
    - Debt amount mismatches
    - Collateral value differences
    - AR/AR aging mismatches
    """

    # Variance thresholds
    VARIANCE_THRESHOLDS = {
        "revenue": 0.05,  # 5% variance allowed
        "ebitda": 0.10,  # 10% variance allowed
        "total_debt": 0.03,  # 3% variance allowed
        "collateral_value": 0.05,  # 5% variance allowed
        "ar": 0.05,  # 5% variance allowed
        "ap": 0.05,  # 5% variance allowed
    }

    def __init__(self):
        self.fs_parser = FinancialStatementParser()
        self.debt_parser = DebtScheduleParser()
        self.collateral_parser = CollateralSummaryParser()
        self.ar_parser = ARAgingParser()

    def reconcile(self, request: UnderwritingRequest) -> ReconciliationResult:
        """
        Perform full document reconciliation.

        Args:
            request: UnderwritingRequest with documents

        Returns:
            ReconciliationResult with contradictions
        """
        result = ReconciliationResult()

        # Reconcile financial statements
        for doc in request.documents.financial_statements:
            if doc.extracted_text_available:
                parsed = self.fs_parser.parse(doc.source_uri)
                self._reconcile_financials(result, request, parsed, doc.doc_id)

        # Reconcile debt schedule
        for doc in request.documents.debt_schedule:
            if doc.extracted_text_available:
                parsed = self.debt_parser.parse(doc.source_uri)
                self._reconcile_debt(result, request, parsed, doc.doc_id)

        # Reconcile collateral
        for doc in request.documents.appraisals:
            if doc.extracted_text_available:
                parsed = self.collateral_parser.parse(doc.source_uri)
                self._reconcile_collateral(result, request, parsed, doc.doc_id)

        # Calculate metrics
        result.total_checked = len(result.contradictions) + result.match_count
        if result.total_checked > 0:
            result.pass_rate = result.match_count / result.total_checked

        result.has_critical_issues = any(
            c.severity == ContradictionSeverity.CRITICAL for c in result.contradictions
        )

        return result

    def _reconcile_financials(
        self,
        result: ReconciliationResult,
        request: UnderwritingRequest,
        parsed: Any,
        doc_id: str,
    ) -> None:
        """Reconcile financial statement values."""
        fields_to_check = [
            (
                "revenue",
                request.financials.periods[0].revenue if request.financials.periods else None,
                parsed.revenue,
            ),
            (
                "ebitda",
                request.financials.periods[0].ebitda if request.financials.periods else None,
                parsed.ebitda,
            ),
            (
                "total_debt",
                request.financials.periods[0].total_debt if request.financials.periods else None,
                parsed.total_debt,
            ),
            ("cash", request.financials.periods[0].cash if request.financials.periods else None, parsed.cash),
            ("ar", request.financials.periods[0].ar if request.financials.periods else None, parsed.ar),
            ("ap", request.financials.periods[0].ap if request.financials.periods else None, parsed.ap),
        ]

        for field_name, structured_val, parsed_val in fields_to_check:
            if structured_val is not None and parsed_val is not None:
                self._check_field(result, field_name, structured_val, parsed_val, doc_id)

    def _reconcile_debt(
        self,
        result: ReconciliationResult,
        request: UnderwritingRequest,
        parsed: Any,
        doc_id: str,
    ) -> None:
        """Reconcile debt schedule values."""
        if parsed.total_current_debt and request.financials.periods:
            structured_debt = request.financials.periods[0].total_debt
            if structured_debt:
                self._check_field(result, "total_debt", structured_debt, parsed.total_current_debt, doc_id)

    def _reconcile_collateral(
        self,
        result: ReconciliationResult,
        request: UnderwritingRequest,
        parsed: Any,
        doc_id: str,
    ) -> None:
        """Reconcile collateral values."""
        if parsed.appraised_value and request.collateral.estimated_value:
            self._check_field(
                result,
                "collateral_value",
                request.collateral.estimated_value,
                parsed.appraised_value,
                doc_id,
            )

    def _check_field(
        self,
        result: ReconciliationResult,
        field_name: str,
        structured_val: float,
        parsed_val: float,
        doc_id: str,
    ) -> None:
        """Check a single field for contradictions."""
        if structured_val == 0:
            variance_pct = abs(parsed_val - structured_val) * 100
        else:
            variance_pct = abs(parsed_val - structured_val) / abs(structured_val)

        threshold = self.VARIANCE_THRESHOLDS.get(field_name, 0.10)

        if variance_pct > threshold:
            # Determine severity
            if variance_pct > 0.50:  # 50% variance
                severity = ContradictionSeverity.CRITICAL
            elif variance_pct > 0.20:  # 20% variance
                severity = ContradictionSeverity.MAJOR
            elif variance_pct > threshold:
                severity = ContradictionSeverity.MODERATE
            else:
                severity = ContradictionSeverity.MINOR

            contradiction = Contradiction(
                field_name=field_name,
                structured_value=structured_val,
                document_value=parsed_val,
                variance_pct=variance_pct,
                severity=severity,
                source_doc_id=doc_id,
                explanation=f"Variance of {variance_pct:.1%} exceeds threshold of {threshold:.1%}",
            )
            result.contradictions.append(contradiction)
            result.mismatch_count += 1
        else:
            result.match_count += 1


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.engines.document_reconciliation_engine', "module_loaded")
