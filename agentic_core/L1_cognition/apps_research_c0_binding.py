"""apps_research C0 grounding binding using generic package-driven grounding.

Consumes app-owned retrieval/freshness/source policies.
Delegates to generic core binding.
"""
from __future__ import annotations

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L1_cognition.package_driven_l1_binding import PackageDrivenL1Plan
from agentic_core.runtime.c0.c0_package_driven_grounding import (
    c0_ground_package_driven,
    FinalEvidenceContract,
)


def c0_ground_apps_research(
    route_contract: RouteContract,
    validated_request: ValidatedRequest,
    l1_plan: PackageDrivenL1Plan,
) -> FinalEvidenceContract:
    """
    apps_research C0 grounding that consumes app-owned profiles.
    
    Delegates to generic package-driven core binding.
    All retrieval/source/freshness policy comes from apps_research/config/.
    """
    return c0_ground_package_driven(route_contract, validated_request, l1_plan)


__all__ = ["c0_ground_apps_research"]
