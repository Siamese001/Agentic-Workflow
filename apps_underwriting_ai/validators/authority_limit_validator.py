"""
Authority Limit Validator - Compares request to delegated approval authority.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from ..types import UnderwritingRequest, RiskFeatures


@dataclass
class AuthorityResult:
    """Result of authority limit validation."""
    within_authority: bool = True
    requested_amount: float = 0.0
    max_auto_approval: Optional[float] = None
    excess_amount: Optional[float] = None
    human_review_required: bool = False
    recommended_approver: Optional[str] = None
    findings: list = field(default_factory=list)


class AuthorityLimitValidator:
    """
    Validates that request is within delegated approval authority.

    Checks:
    - Requested amount vs max auto-approval
    - Risk grade impact on authority
    - Exception count impact on authority
    """

    # Authority limits by risk grade
    RISK_ADJUSTED_LIMITS = {
        "1": 1.0,    # 100% of base limit
        "2": 1.0,
        "3": 1.0,
        "4": 0.8,    # 80% of base limit
        "5": 0.6,    # 60% of base limit
        "6": 0.4,    # 40% of base limit
        "7": 0.0,    # No auto-approval
        "8": 0.0,
        "9": 0.0,
    }

    def validate(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures
    ) -> AuthorityResult:
        """
        Validate against authority limits.

        Args:
            request: UnderwritingRequest
            features: Derived RiskFeatures

        Returns:
            AuthorityResult
        """
        result = AuthorityResult()
        result.requested_amount = request.requested_amount

        # Get base authority limit
        base_limit = request.decision_constraints.max_auto_approval_amount
        result.max_auto_approval = base_limit

        if base_limit is None:
            # No auto-approval authority configured
            result.within_authority = False
            result.human_review_required = True
            result.findings.append("No auto-approval authority configured - human review required")
            return result

        # Adjust for risk grade
        risk_grade = features.composite.normalized_risk_grade
        risk_adjustment = self.RISK_ADJUSTED_LIMITS.get(risk_grade, 0.0)
        adjusted_limit = base_limit * risk_adjustment

        # Further reduce for exceptions
        if features.policy.policy_exception_count > 0:
            adjusted_limit *= 0.5  # 50% reduction with exceptions
            result.findings.append(
                f"Authority reduced 50% due to {features.policy.policy_exception_count} policy exception(s)"
            )

        # Check if within authority
        if request.requested_amount > adjusted_limit:
            result.within_authority = False
            result.excess_amount = request.requested_amount - adjusted_limit
            result.human_review_required = True
            result.findings.append(
                f"Requested amount ${request.requested_amount:,.0f} exceeds "
                f"adjusted authority of ${adjusted_limit:,.0f}"
            )

        # Recommend approver
        result.recommended_approver = self._recommend_approver(
            request.requested_amount,
            risk_grade,
            features.policy.policy_exception_count
        )

        return result

    def _recommend_approver(
        self,
        amount: float,
        risk_grade: str,
        exception_count: int
    ) -> Optional[str]:
        """Recommend approval authority level."""
        amount_millions = amount / 1_000_000
        risk = int(risk_grade)

        if amount_millions >= 10 or risk >= 8 or exception_count >= 3:
            return "Credit Committee"
        elif amount_millions >= 5 or risk >= 6 or exception_count >= 2:
            return "Regional Credit Officer"
        elif amount_millions >= 1 or risk >= 5 or exception_count >= 1:
            return "Senior Underwriter"
        else:
            return "Underwriter"
