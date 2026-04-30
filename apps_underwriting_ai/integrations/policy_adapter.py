"""
Policy Adapter - Reads underwriting policy context and prepares compliance payload.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from ..types import UnderwritingRequest


@dataclass
class PolicyCompliancePayload:
    """Policy compliance payload for governance."""

    policy_version: str = ""
    applicable_rules: Dict[str, Any] = field(default_factory=dict)
    exception_rules: list = field(default_factory=list)
    human_review_triggers: list = field(default_factory=list)
    compliance_flags: list = field(default_factory=list)


class PolicyAdapter:
    """
    Adapter for policy and governance integration.

    Responsibilities:
    - Read underwriting policy context
    - Pass domain policy references to core governance
    - Attach policy_version where available
    - Preserve exception rules and human-review triggers
    - Prepare domain compliance payload
    """

    def prepare_policy_context(
        self,
        request: UnderwritingRequest,
    ) -> PolicyCompliancePayload:
        """
        Prepare policy context for governance.

        Args:
            request: UnderwritingRequest

        Returns:
            PolicyCompliancePayload
        """
        policy = request.policy_context

        payload = PolicyCompliancePayload()
        payload.policy_version = policy.policy_version

        # Build applicable rules
        payload.applicable_rules = {
            "min_dscr": policy.min_dscr,
            "max_debt_to_ebitda": policy.max_debt_to_ebitda,
            "min_fico": policy.min_fico,
            "max_ltv": policy.collateral_rules.max_ltv if policy.collateral_rules else None,
            "eligible_collateral": policy.collateral_rules.eligible_collateral
            if policy.collateral_rules
            else [],
        }

        # Preserve exception rules
        payload.exception_rules = policy.exception_rules

        # Preserve human review triggers
        payload.human_review_triggers = policy.human_review_triggers

        return payload

    def check_policy_exceptions(
        self,
        request: UnderwritingRequest,
        features: Any,
    ) -> Dict[str, Any]:
        """
        Check which policy exceptions apply.

        Args:
            request: UnderwritingRequest
            features: RiskFeatures

        Returns:
            Dictionary of exception details
        """
        exceptions = {
            "count": 0,
            "details": [],
            "requires_approval": False,
        }

        policy = request.policy_context
        metrics = request.financials.calculated_metrics

        # Check DSCR exception
        if policy.min_dscr and metrics.dscr_ttm and metrics.dscr_ttm < policy.min_dscr:
            exceptions["count"] += 1
            exceptions["details"].append(
                {
                    "type": "dscr_below_minimum",
                    "value": metrics.dscr_ttm,
                    "threshold": policy.min_dscr,
                    "severity": "moderate",
                }
            )
            exceptions["requires_approval"] = True

        # Check leverage exception
        if (
            policy.max_debt_to_ebitda
            and metrics.debt_to_ebitda_ttm
            and metrics.debt_to_ebitda_ttm > policy.max_debt_to_ebitda
        ):
            exceptions["count"] += 1
            exceptions["details"].append(
                {
                    "type": "leverage_above_maximum",
                    "value": metrics.debt_to_ebitda_ttm,
                    "threshold": policy.max_debt_to_ebitda,
                    "severity": "moderate",
                }
            )
            exceptions["requires_approval"] = True

        # Check FICO exception
        if policy.min_fico:
            min_fico = (
                min(request.credit.personal_fico_scores) if request.credit.personal_fico_scores else None
            )
            if min_fico and min_fico < policy.min_fico:
                exceptions["count"] += 1
                exceptions["details"].append(
                    {
                        "type": "fico_below_minimum",
                        "value": min_fico,
                        "threshold": policy.min_fico,
                        "severity": "moderate",
                    }
                )
                exceptions["requires_approval"] = True

        return exceptions


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.integrations.policy_adapter', "module_loaded")
