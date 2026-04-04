"""
Compliance Validator - Validates product vs policy fit.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from ..types import UnderwritingRequest, RiskFeatures


@dataclass
class ComplianceResult:
    """Result of compliance validation."""
    passed: bool = True
    violations: List[Dict[str, Any]] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    exception_required: bool = False


class ComplianceValidator:
    """
    Validates underwriting request against policy constraints.

    Checks:
    - Restricted industries
    - Prohibited jurisdictions
    - Minimum DSCR
    - Maximum leverage
    - Minimum FICO
    - Collateral eligibility
    """

    def validate(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures
    ) -> ComplianceResult:
        """
        Perform full compliance validation.

        Args:
            request: UnderwritingRequest
            features: Derived RiskFeatures

        Returns:
            ComplianceResult
        """
        result = ComplianceResult()

        # Check restricted industries
        self._check_industry(request, result)

        # Check prohibited jurisdictions
        self._check_jurisdiction(request, result)

        # Check DSCR minimum
        self._check_dscr(request, features, result)

        # Check leverage maximum
        self._check_leverage(request, features, result)

        # Check FICO minimum
        self._check_fico(request, features, result)

        # Check collateral eligibility
        self._check_collateral(request, features, result)

        # Determine overall pass/fail
        result.passed = len(result.violations) == 0 or not any(
            v.get("severity") == "blocking" for v in result.violations
        )

        result.exception_required = len(result.violations) > 0

        return result

    def _check_industry(
        self,
        request: UnderwritingRequest,
        result: ComplianceResult
    ) -> None:
        """Check for restricted industries."""
        policy = request.policy_context
        industry_code = request.borrower.industry_code

        if not policy.restricted_industries:
            return

        for restricted in policy.restricted_industries:
            if industry_code.startswith(restricted):
                result.violations.append({
                    "type": "restricted_industry",
                    "field": "borrower.industry_code",
                    "value": industry_code,
                    "threshold": restricted,
                    "severity": "blocking",
                    "message": f"Industry code {industry_code} matches restricted category {restricted}"
                })
                result.required_actions.append(
                    "Policy exception required for restricted industry"
                )

    def _check_jurisdiction(
        self,
        request: UnderwritingRequest,
        result: ComplianceResult
    ) -> None:
        """Check for prohibited jurisdictions."""
        policy = request.policy_context
        operating_states = request.borrower.operating_states

        if not policy.prohibited_jurisdictions:
            return

        for state in operating_states:
            if state in policy.prohibited_jurisdictions:
                result.violations.append({
                    "type": "prohibited_jurisdiction",
                    "field": "borrower.operating_states",
                    "value": state,
                    "threshold": None,
                    "severity": "blocking",
                    "message": f"Operating state {state} is in prohibited jurisdictions list"
                })

    def _check_dscr(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures,
        result: ComplianceResult
    ) -> None:
        """Check minimum DSCR requirement."""
        policy = request.policy_context

        if policy.min_dscr is None or features.capacity.dscr_ttm is None:
            return

        if features.capacity.dscr_ttm < policy.min_dscr:
            result.violations.append({
                "type": "dscr_below_minimum",
                "field": "capacity.dscr_ttm",
                "value": features.capacity.dscr_ttm,
                "threshold": policy.min_dscr,
                "severity": "exception",
                "message": f"DSCR of {features.capacity.dscr_ttm:.2f}x below policy minimum of {policy.min_dscr:.2f}x"
            })
            result.required_actions.append(
                f"Exception required: DSCR below {policy.min_dscr:.2f}x minimum"
            )

    def _check_leverage(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures,
        result: ComplianceResult
    ) -> None:
        """Check maximum leverage requirement."""
        policy = request.policy_context

        if policy.max_debt_to_ebitda is None or features.capacity.debt_to_ebitda_ttm is None:
            return

        if features.capacity.debt_to_ebitda_ttm > policy.max_debt_to_ebitda:
            result.violations.append({
                "type": "leverage_above_maximum",
                "field": "capacity.debt_to_ebitda_ttm",
                "value": features.capacity.debt_to_ebitda_ttm,
                "threshold": policy.max_debt_to_ebitda,
                "severity": "exception",
                "message": f"Leverage of {features.capacity.debt_to_ebitda_ttm:.2f}x exceeds policy maximum of {policy.max_debt_to_ebitda:.2f}x"
            })
            result.required_actions.append(
                f"Exception required: Leverage above {policy.max_debt_to_ebitda:.2f}x maximum"
            )

    def _check_fico(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures,
        result: ComplianceResult
    ) -> None:
        """Check minimum FICO requirement."""
        policy = request.policy_context

        if policy.min_fico is None or features.credit.personal_fico_min is None:
            return

        if features.credit.personal_fico_min < policy.min_fico:
            result.violations.append({
                "type": "fico_below_minimum",
                "field": "credit.personal_fico_min",
                "value": features.credit.personal_fico_min,
                "threshold": policy.min_fico,
                "severity": "exception",
                "message": f"FICO of {features.credit.personal_fico_min} below policy minimum of {policy.min_fico}"
            })
            result.required_actions.append(
                f"Exception required: FICO below {policy.min_fico} minimum"
            )

    def _check_collateral(
        self,
        request: UnderwritingRequest,
        features: RiskFeatures,
        result: ComplianceResult
    ) -> None:
        """Check collateral eligibility."""
        policy = request.policy_context
        collateral = request.collateral

        if not policy.collateral_rules.eligible_collateral:
            return

        if collateral.collateral_type not in policy.collateral_rules.eligible_collateral:
            result.violations.append({
                "type": "ineligible_collateral",
                "field": "collateral.collateral_type",
                "value": collateral.collateral_type,
                "threshold": policy.collateral_rules.eligible_collateral,
                "severity": "blocking",
                "message": f"Collateral type '{collateral.collateral_type}' not in eligible list"
            })

        # Check max LTV
        if policy.collateral_rules.max_ltv and features.collateral.ltv:
            if features.collateral.ltv > policy.collateral_rules.max_ltv:
                result.violations.append({
                    "type": "ltv_above_maximum",
                    "field": "collateral.ltv",
                    "value": features.collateral.ltv,
                    "threshold": policy.collateral_rules.max_ltv,
                    "severity": "exception",
                    "message": f"LTV of {features.collateral.ltv:.1%} exceeds policy maximum of {policy.collateral_rules.max_ltv:.1%}"
                })
