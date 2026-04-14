"""
Authority Limit Validator - Compares request to delegated approval authority.
"""

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from ..types import RiskFeatures, UnderwritingRequest


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
        "1": 1.0,  # 100% of base limit
        "2": 1.0,
        "3": 1.0,
        "4": 0.8,  # 80% of base limit
        "5": 0.6,  # 60% of base limit
        "6": 0.4,  # 40% of base limit
        "7": 0.0,  # No auto-approval
        "8": 0.0,
        "9": 0.0,
    }

    def validate(
        self,
        request: UnderwritingRequest | Mapping[str, Any],
        features: Optional[RiskFeatures] = None,
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
        request_amount = self._get_request_amount(request)
        base_limit = self._get_base_limit(request)
        risk_grade = self._get_risk_grade(features)
        exception_count = self._get_policy_exception_count(features)

        result.requested_amount = request_amount
        result.max_auto_approval = base_limit

        if base_limit is None:
            # No auto-approval authority configured
            result.within_authority = False
            result.human_review_required = True
            result.findings.append("No auto-approval authority configured - human review required")
            return result

        # Adjust for risk grade
        risk_adjustment = self.RISK_ADJUSTED_LIMITS.get(risk_grade, 0.0)
        adjusted_limit = base_limit * risk_adjustment

        # Further reduce for exceptions
        if exception_count > 0:
            adjusted_limit *= 0.5  # 50% reduction with exceptions
            result.findings.append(
                f"Authority reduced 50% due to {exception_count} policy exception(s)",
            )

        # Check if within authority
        if request_amount > adjusted_limit:
            result.within_authority = False
            result.excess_amount = request_amount - adjusted_limit
            result.human_review_required = True
            result.findings.append(
                f"Requested amount ${request_amount:,.0f} exceeds "
                f"adjusted authority of ${adjusted_limit:,.0f}",
            )

        # Recommend approver
        result.recommended_approver = self._recommend_approver(
            request_amount,
            risk_grade,
            exception_count,
        )

        return result

    def _get_request_amount(self, request: UnderwritingRequest | Mapping[str, Any]) -> float:
        """Extract requested amount from model or smoke-test mapping."""
        if isinstance(request, Mapping):
            raw_amount = request.get("requested_amount", request.get("amount", 0.0))
        else:
            raw_amount = getattr(request, "requested_amount", 0.0)
        return self._safe_float(raw_amount)

    def _get_base_limit(self, request: UnderwritingRequest | Mapping[str, Any]) -> Optional[float]:
        """Extract base approval limit from model or smoke-test mapping."""
        if isinstance(request, Mapping):
            raw_limit = request.get("max_auto_approval_amount", request.get("limit"))
        else:
            constraints = getattr(request, "decision_constraints", None)
            raw_limit = getattr(constraints, "max_auto_approval_amount", None)
        if raw_limit is None:
            return None
        return self._safe_float(raw_limit)

    def _get_risk_grade(self, features: Optional[RiskFeatures]) -> str:
        """Default to safest risk grade when features are unavailable."""
        if not features:
            return "1"
        composite = getattr(features, "composite", None)
        risk_grade = getattr(composite, "normalized_risk_grade", "1")
        return str(risk_grade)

    def _get_policy_exception_count(self, features: Optional[RiskFeatures]) -> int:
        """Extract exception count safely from optional derived features."""
        if not features:
            return 0
        policy = getattr(features, "policy", None)
        raw_count = getattr(policy, "policy_exception_count", 0)
        return int(raw_count or 0)

    @staticmethod
    def _safe_float(value: Any) -> float:
        """Best-effort numeric coercion for permissive validator entry points."""
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _recommend_approver(
        self,
        amount: float,
        risk_grade: str,
        exception_count: int,
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
