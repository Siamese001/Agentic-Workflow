"""
Exception Summarizer - Summarizes policy exceptions and escalations.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import DecisionState, RiskFeatures, UnderwritingRequest


@dataclass
class ExceptionSummary:
    """Summary of exceptions and escalations."""
    has_exceptions: bool = False
    exception_count: int = 0
    exception_details: List[Dict[str, Any]] = field(default_factory=list)
    escalation_required: bool = False
    escalation_reasons: List[str] = field(default_factory=list)
    recommended_approver: Optional[str] = None


class ExceptionSummarizer:
    """
    Summarizes policy exceptions and human escalation requirements.

    Provides:
    - Exception categorization
    - Escalation rationale
    - Recommended approval authority
    """

    def summarize(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
        decision: DecisionState,
        validator_results: Optional[Dict[str, Any]] = None,
    ) -> ExceptionSummary:
        """
        Generate exception and escalation summary.

        Args:
            features: Derived RiskFeatures
            request: UnderwritingRequest
            decision: Proposed decision
            validator_results: Optional validator results

        Returns:
            ExceptionSummary
        """
        summary = ExceptionSummary()

        # Count policy exceptions
        summary.exception_count = features.policy.policy_exception_count
        summary.has_exceptions = summary.exception_count > 0

        # Build exception details
        if summary.has_exceptions:
            summary.exception_details = self._build_exception_details(features, request)

        # Determine escalation
        summary.escalation_required = decision == "ESCALATE_TO_HUMAN"
        if summary.escalation_required:
            summary.escalation_reasons = self._identify_escalation_reasons(features, request, decision)

        # Recommend approval authority
        summary.recommended_approver = self._recommend_approver(features, request, decision)

        return summary

    def _build_exception_details(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
    ) -> List[Dict[str, Any]]:
        """Build detailed exception list."""
        details = []
        policy = request.policy_context
        metrics = request.financials.calculated_metrics

        # Check DSCR exception
        if policy.min_dscr and metrics.dscr_ttm and metrics.dscr_ttm < policy.min_dscr:
            details.append({
                "type": "dscr_below_minimum",
                "description": f"DSCR of {metrics.dscr_ttm:.2f}x below policy minimum of {policy.min_dscr:.2f}x",
                "severity": "moderate" if metrics.dscr_ttm >= 1.0 else "high",
                "mitigants": ["strong_collateral", "guarantor_strength"] if features.collateral.collateral_quality_score >= 0.6 else [],
            })

        # Check leverage exception
        if policy.max_debt_to_ebitda and metrics.debt_to_ebitda_ttm and metrics.debt_to_ebitda_ttm > policy.max_debt_to_ebitda:
            details.append({
                "type": "leverage_above_maximum",
                "description": f"Debt/EBITDA of {metrics.debt_to_ebitda_ttm:.2f}x exceeds policy maximum of {policy.max_debt_to_ebitda:.2f}x",
                "severity": "moderate" if metrics.debt_to_ebitda_ttm < 4.0 else "high",
                "mitigants": [],
            })

        # Check FICO exception
        if policy.min_fico and features.credit.personal_fico_min and features.credit.personal_fico_min < policy.min_fico:
            details.append({
                "type": "fico_below_minimum",
                "description": f"FICO of {features.credit.personal_fico_min} below policy minimum of {policy.min_fico}",
                "severity": "moderate",
                "mitigants": ["strong_business_cash_flow"] if features.capacity.dscr_ttm and features.capacity.dscr_ttm >= 2.0 else [],
            })

        # Check industry restriction
        if policy.restricted_industries:
            for restricted in policy.restricted_industries:
                if request.borrower.industry_code.startswith(restricted):
                    details.append({
                        "type": "restricted_industry",
                        "description": f"Industry code {request.borrower.industry_code} matches restricted category {restricted}",
                        "severity": "high",
                        "mitigants": [],
                    })

        return details

    def _identify_escalation_reasons(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
        decision: DecisionState,
    ) -> List[str]:
        """Identify reasons for human escalation."""
        reasons = []

        # Policy exceptions
        if features.policy.policy_exception_count > 0:
            reasons.append(f"{features.policy.policy_exception_count} policy exception(s) requiring human judgment")

        # Authority limit
        if request.decision_constraints.max_auto_approval_amount:
            if request.requested_amount > request.decision_constraints.max_auto_approval_amount:
                reasons.append(f"Request amount exceeds auto-approval authority of ${request.decision_constraints.max_auto_approval_amount:,.0f}")

        # Low confidence
        if features.composite.confidence_score < 0.6:
            reasons.append(f"Low confidence score ({features.composite.confidence_score:.0%}) in automated assessment")

        # Borderline risk
        if features.composite.normalized_risk_grade in ["6", "7"]:
            reasons.append(f"Borderline risk grade ({features.composite.normalized_risk_grade}) requires human review")

        # Watchlist/sanctions
        if request.borrower.sanctions_or_watchlist_hits:
            reasons.append("Sanctions or watchlist hits require compliance review")

        # Contradictory data
        if features.documentation.data_consistency_score < 0.5:
            reasons.append("Significant data inconsistencies require manual reconciliation")

        # Complex structure
        if request.product_type == "sba_like":
            reasons.append("SBA-guaranteed structure requires specialized underwriting review")

        return reasons

    def _recommend_approver(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
        decision: DecisionState,
    ) -> Optional[str]:
        """Recommend approval authority level."""
        # Determine based on amount and risk
        amount = request.requested_amount
        risk_grade = int(features.composite.normalized_risk_grade)
        exception_count = features.policy.policy_exception_count

        if amount >= 10000000 or risk_grade >= 8 or exception_count >= 3:
            return "Senior Credit Committee"
        elif amount >= 5000000 or risk_grade >= 6 or exception_count >= 2:
            return "Regional Credit Officer"
        elif amount >= 1000000 or risk_grade >= 5 or exception_count >= 1:
            return "Senior Underwriter"
        elif decision == "ESCALATE_TO_HUMAN":
            return "Underwriting Manager"

        return None
