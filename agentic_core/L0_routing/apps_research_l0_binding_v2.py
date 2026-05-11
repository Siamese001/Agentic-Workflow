"""apps_research L0 binding using generic package-driven routing.

Consumes app-owned route profile, delegates to generic core binding.
"""
from __future__ import annotations

from typing import Tuple, Union, List

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L1_cognition.package_driven_l1_binding import PackageDrivenL1Plan
from agentic_core.L0_routing.package_driven_l0_binding import (
    l0_evaluate_routes_package_driven,
    RETTerminalPacket,
    RouteEvaluation,
)


def l0_route_apps_research(
    validated_request: ValidatedRequest,
    l1_plan: PackageDrivenL1Plan,
) -> Tuple[Union[RouteContract, RETTerminalPacket], List[RouteEvaluation]]:
    """
    apps_research L0 routing that consumes app-owned route profile.
    
    Delegates to generic package-driven core binding.
    All route policy comes from apps_research/config/domain_contract/route_profile.*.yaml
    
    Route order (from profile):
        1. R5_PRE_ROUTE_FALLBACK (unroutable check)
        2. R1A_EXACT_CACHE
        3. R1B_SEMANTIC_CACHE
        4. R3_SIMPLE_GROUNDED_READ (default)
    
    Returns:
        Tuple of (selected_route_or_ret_packet, evaluation_log)
    """
    return l0_evaluate_routes_package_driven(validated_request, l1_plan)


__all__ = ["l0_route_apps_research"]
