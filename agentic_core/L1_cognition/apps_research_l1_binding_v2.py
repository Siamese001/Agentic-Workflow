"""apps_research L1 binding using generic package-driven planning.

Consumes app-owned L1 planning profile, delegates to generic core binding.
"""
from __future__ import annotations

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.L1_cognition.package_driven_l1_binding import (
    l1_plan_package_driven,
    l1_plan_to_contract,
)
from agentic_core.runtime.contracts.route_contract import L1PlanContract


# Default L1 planning profile ref for apps_research
DEFAULT_L1_PROFILE_REF = "apps_research/config/domain_contract/l1_planning_profile.company_brief.v1.yaml"


def l1_plan_apps_research(validated_request: ValidatedRequest) -> L1PlanContract:
    """
    apps_research L1 planning that consumes app-owned profile.
    
    Delegates to generic package-driven core binding.
    All app-specific values come from apps_research/config/.
    """
    # Use package-driven planning with app-owned profile
    package_plan = l1_plan_package_driven(
        validated_request,
        l1_planning_profile_ref=DEFAULT_L1_PROFILE_REF,
    )
    
    # Convert to standard contract
    return l1_plan_to_contract(package_plan)


__all__ = ["l1_plan_apps_research"]
