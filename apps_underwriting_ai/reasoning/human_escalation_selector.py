"""
Human Escalation Selector - Determines when to escalate to human underwriter.
"""
from typing import List

from ..types import RiskFeatures, UnderwritingRequest


class HumanEscalationSelector:
    """
    Determines when recommendation should be ESCALATE_TO_HUMAN.

    Triggers:
    - Policy exceptions
    - Contradictory evidence
    - Authority limits
    - Watchlist/sanctions
    - Low confidence
    - Borderline risk
    - Unusual structure
    - Missing critical docs
    """

    ESCALATION_TRIGGERS = {
        "policy_exception": "Policy exception requires human judgment",
        "contradictory_evidence": "Contradictory evidence between sources",
        "authority_limit": "Request amount exceeds delegated authority",
        "watchlist_hit": "Sanctions or watchlist match detected",
        "low_confidence": "Low confidence in automated assessment",
        "borderline_risk": "Borderline risk grade requires review",
        "unusual_structure": "Unusual loan structure or collateral",
        "missing_docs": "Missing critical documentation",
        "fraud_signal": "Fraud or identity signal detected",
    }

    def should_escalate(
        self,
        features: RiskFeatures,
        request: UnderwritingRequest,
        validator_results: dict
    ) -> tuple[bool, List[str]]:
        """
        Determine if case should escalate to human.

        Args:
            features: Derived RiskFeatures
            request: UnderwritingRequest
            validator_results: Results from validators

        Returns:
            Tuple of (should_escalate, reasons)
        """
        reasons = []

        # Check policy exceptions
        if features.policy.policy_exception_count > 0:
            reasons.append(self.ESCALATION_TRIGGERS["policy_exception"])

        # Check contradictory evidence
        if features.documentation.data_consistency_score < 0.5:
            reasons.append(self.ESCALATION_TRIGGERS["contradictory_evidence"])

        # Check authority limit
        if request.decision_constraints.max_auto_approval_amount:
            if request.requested_amount > request.decision_constraints.max_auto_approval_amount:
                reasons.append(self.ESCALATION_TRIGGERS["authority_limit"])

        # Check watchlist/sanctions
        if request.borrower.sanctions_or_watchlist_hits:
            reasons.append(self.ESCALATION_TRIGGERS["watchlist_hit"])

        # Check confidence
        if features.composite.confidence_score < 0.6:
            reasons.append(self.ESCALATION_TRIGGERS["low_confidence"])

        # Check borderline risk
        if features.composite.normalized_risk_grade in ["6", "7"]:
            reasons.append(self.ESCALATION_TRIGGERS["borderline_risk"])

        # Check unusual structure
        if self._is_unusual_structure(request, features):
            reasons.append(self.ESCALATION_TRIGGERS["unusual_structure"])

        # Check missing docs
        if features.documentation.document_completeness_score < 0.5:
            reasons.append(self.ESCALATION_TRIGGERS["missing_docs"])

        # Check fraud signals
        if request.external_signals.fraud_or_identity_signals:
            reasons.append(self.ESCALATION_TRIGGERS["fraud_signal"])

        # Check manual review triggers from policy
        if self._check_manual_review_triggers(request, features):
            reasons.append("Manual review trigger in policy hit")

        return len(reasons) > 0, reasons

    def _is_unusual_structure(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures
    ) -> bool:
        """Check if loan structure is unusual."""
        unusual = False

        # SBA structures
        if request.product_type == "sba_like":
            unusual = True

        # Junior lien with high advance
        if request.collateral.lien_position == "junior" and request.collateral.ltv and request.collateral.ltv > 0.5:
            unusual = True

        # Unsecured for larger amounts
        if request.collateral.collateral_type == "unsecured" and request.requested_amount > 1000000:
            unusual = True

        return unusual

    def _check_manual_review_triggers(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures
    ) -> bool:
        """Check if any manual review triggers from policy are hit."""
        triggers = request.policy_context.human_review_triggers

        if not triggers:
            return False

        for trigger in triggers:
            if trigger == "dscr_below_1.25":
                if features.capacity.dscr_ttm and features.capacity.dscr_ttm < 1.25:
                    return True
            elif trigger == "debt_to_ebitda_above_3.5":
                if features.capacity.debt_to_ebitda_ttm and features.capacity.debt_to_ebitda_ttm > 3.5:
                    return True
            elif trigger == "fico_below_680":
                if features.credit.personal_fico_min and features.credit.personal_fico_min < 680:
                    return True

        return False
