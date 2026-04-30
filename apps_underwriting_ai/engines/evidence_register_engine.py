"""
Evidence Register Engine - Collects and manages evidence for underwriting claims.
"""

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from ..types import EvidenceEntry, UnderwritingRequest

@dataclass
class EvidenceRegister:
    """Internal evidence register for the underwriting process."""

    request_id: str
    entries: List[EvidenceEntry] = field(default_factory=list)

    @traces_execute(layer="L4_STATE")
    def add_entry(self, entry: EvidenceEntry) -> None:
        """Add an evidence entry."""
        self.entries.append(entry)

    def add_claim(
        self,
        claim_category: str,
        claim_text: str,
        evidence_source: str,
        evidence_type: str,
        confidence: float = 0.8,
        excerpt: Optional[str] = None,
    ) -> EvidenceEntry:
        """Add a new claim with evidence."""
        entry = EvidenceEntry(
            entry_id=f"EV-{len(self.entries) + 1:04d}",
            claim_category=claim_category,
            claim_text=claim_text,
            evidence_source=evidence_source,
            evidence_type=evidence_type,
            extraction_timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=confidence,
            supporting_excerpt=excerpt,
            contradicting_evidence=[],
        )
        self.entries.append(entry)
        return entry

    def get_completeness_pct(self) -> float:
        """Calculate evidence completeness percentage."""
        if not self.entries:
            return 0.0
        # Count non-zero confidence entries
        valid_entries = sum(1 for e in self.entries if e.confidence > 0)
        return valid_entries / len(self.entries)

    def get_contradiction_count(self) -> int:
        """Count entries with contradicting evidence."""
        return sum(1 for e in self.entries if e.contradicting_evidence)

class EvidenceRegisterEngine:
    """
    Manages evidence collection and registration throughout underwriting.

    Collects:
    - Financial metric evidence
    - Credit bureau evidence
    - Collateral appraisal evidence
    - Policy rule evidence
    """

    def __init__(self):
        self._register: Optional[EvidenceRegister] = None

    def initialize(self, request_id: str) -> EvidenceRegister:
        """Initialize evidence register for a request."""
        self._register = EvidenceRegister(request_id=request_id)
        return self._register

    def collect_financial_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> None:
        """Collect evidence from financial package."""
        metrics = request.financials.calculated_metrics

        if metrics.dscr_ttm:
            register.add_claim(
                claim_category="capacity",
                claim_text=f"Debt Service Coverage Ratio is {metrics.dscr_ttm:.2f}x",
                evidence_source="financial_package.calculated_metrics.dscr_ttm",
                evidence_type="structured_metric",
                confidence=0.9,
            )

        if metrics.debt_to_ebitda_ttm:
            register.add_claim(
                claim_category="capacity",
                claim_text=f"Leverage ratio (Debt/EBITDA) is {metrics.debt_to_ebitda_ttm:.2f}x",
                evidence_source="financial_package.calculated_metrics.debt_to_ebitda_ttm",
                evidence_type="structured_metric",
                confidence=0.9,
            )

        if metrics.ebitda_margin_ttm:
            register.add_claim(
                claim_category="capacity",
                claim_text=f"EBITDA margin is {metrics.ebitda_margin_ttm:.1%}",
                evidence_source="financial_package.calculated_metrics.ebitda_margin_ttm",
                evidence_type="structured_metric",
                confidence=0.9,
            )

        # Add revenue trend evidence
        if request.financials.periods and len(request.financials.periods) >= 2:
            periods = request.financials.periods
            latest_revenue = periods[-1].revenue
            prior_revenue = periods[-2].revenue if len(periods) > 1 else None

            if prior_revenue and prior_revenue > 0:
                growth = (latest_revenue - prior_revenue) / prior_revenue
                register.add_claim(
                    claim_category="capacity",
                    claim_text=f"Revenue growth of {growth:.1%} from prior period",
                    evidence_source="financial_package.periods",
                    evidence_type="structured_metric",
                    confidence=0.85,
                )

    def collect_credit_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> None:
        """Collect evidence from credit package."""
        credit = request.credit

        if credit.business_bureau_score:
            register.add_claim(
                claim_category="credit",
                claim_text=f"Business credit bureau score is {credit.business_bureau_score}",
                evidence_source="credit_package.business_bureau_score",
                evidence_type="structured_metric",
                confidence=0.95,
            )

        if credit.personal_fico_scores:
            min_fico = min(credit.personal_fico_scores)
            register.add_claim(
                claim_category="credit",
                claim_text=f"Minimum personal FICO score is {min_fico}",
                evidence_source="credit_package.personal_fico_scores",
                evidence_type="structured_metric",
                confidence=0.95,
            )

        if credit.delinquencies_24m > 0:
            register.add_claim(
                claim_category="credit",
                claim_text=f"{credit.delinquencies_24m} delinquencies in last 24 months",
                evidence_source="credit_package.delinquencies_24m",
                evidence_type="structured_metric",
                confidence=0.95,
            )

        if credit.bankruptcies_ever > 0:
            register.add_claim(
                claim_category="credit",
                claim_text=f"{credit.bankruptcies_ever} bankruptcy filing(s) on record",
                evidence_source="credit_package.bankruptcies_ever",
                evidence_type="structured_metric",
                confidence=1.0,
            )

    def collect_collateral_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> None:
        """Collect evidence from collateral package."""
        collateral = request.collateral

        if collateral.estimated_value:
            register.add_claim(
                claim_category="collateral",
                claim_text=f"Collateral estimated value is ${collateral.estimated_value:,.0f}",
                evidence_source="collateral_package.estimated_value",
                evidence_type="document",
                confidence=0.8,
            )

        if collateral.borrowing_base_value:
            register.add_claim(
                claim_category="collateral",
                claim_text=f"Borrowing base calculated at ${collateral.borrowing_base_value:,.0f}",
                evidence_source="collateral_package.borrowing_base_value",
                evidence_type="structured_metric",
                confidence=0.85,
            )

        if collateral.appraisal_date:
            register.add_claim(
                claim_category="collateral",
                claim_text=f"Appraisal dated {collateral.appraisal_date}",
                evidence_source="collateral_package.appraisal_date",
                evidence_type="document",
                confidence=0.9,
            )

    def collect_policy_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
        policy_exception_count: int,
    ) -> None:
        """Collect evidence from policy context."""
        policy = request.policy_context

        register.add_claim(
            claim_category="policy",
            claim_text=f"Underwriting policy version {policy.policy_version} applied",
            evidence_source="policy_context.policy_version",
            evidence_type="policy_rule",
            confidence=1.0,
        )

        if policy_exception_count > 0:
            register.add_claim(
                claim_category="policy",
                claim_text=f"{policy_exception_count} policy exception(s) triggered",
                evidence_source="policy_context.threshold_checks",
                evidence_type="policy_rule",
                confidence=0.95,
            )

        if policy.min_dscr:
            register.add_claim(
                claim_category="policy",
                claim_text=f"Minimum DSCR requirement: {policy.min_dscr:.2f}x",
                evidence_source="policy_context.min_dscr",
                evidence_type="policy_rule",
                confidence=1.0,
            )

    def collect_relationship_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> None:
        """Collect evidence from relationship context."""
        rel = request.relationship_context

        if rel.existing_customer:
            tenure_text = f" with {rel.tenure_years:.1f} year tenure" if rel.tenure_years else ""
            register.add_claim(
                claim_category="relationship",
                claim_text=f"Existing customer{tenure_text}",
                evidence_source="relationship_context",
                evidence_type="structured_metric",
                confidence=0.95,
            )

        if rel.deposit_relationship:
            register.add_claim(
                claim_category="relationship",
                claim_text="Active deposit relationship",
                evidence_source="relationship_context.deposit_relationship",
                evidence_type="structured_metric",
                confidence=0.95,
            )

# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.engines.evidence_register_engine', "module_loaded")
