"""apps_rg L0 binding — route constants and routing function for apps_rg.

All L0 route constants are defined here (app-owned).
agentic_core.L0_routing.apps_rg_l0_binding re-exports from this module
(legacy shim direction). Do NOT import from agentic_core here to avoid
a circular import.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "APPS_RG_L0_CERT_REF",
    "APPS_RG_ROUTE_FAMILY",
    "APPS_RG_ROUTE_ID",
    "APPS_RG_CACHE_ELIGIBILITY",
    "APPS_RG_HITL_POSTURE",
    "APPS_RG_FALLBACK_ROUTE_ID",
    "l0_route_apps_rg",
]

APPS_RG_L0_CERT_REF: str = "l0-apps-rg-resume-generation-w3"
APPS_RG_ROUTE_FAMILY: str = "resume_generation"
APPS_RG_ROUTE_ID: str = "R4_MANAGED_DRAFT"
APPS_RG_CACHE_ELIGIBILITY: str = "eligible"
APPS_RG_HITL_POSTURE: str = "advisory"
APPS_RG_FALLBACK_ROUTE_ID: str = "R0_PASSTHROUGH"


def l0_route_apps_rg(request: Any) -> dict[str, Any]:
    """Determine the L0 route for an apps_rg ingress request.

    Returns a routing decision dict with route_id and metadata.
    """
    generation_mode = ""
    if isinstance(request, dict):
        generation_mode = request.get("generation_mode", "")
    else:
        generation_mode = getattr(request, "generation_mode", "")

    route_id = APPS_RG_ROUTE_ID
    if generation_mode == "generate_scratch":
        route_id = "R3_GENERATIVE"
    elif generation_mode == "keyword_match":
        route_id = "R2_KEYWORD_ALIGN"

    return {
        "route_id": route_id,
        "route_family": APPS_RG_ROUTE_FAMILY,
        "cache_eligibility": APPS_RG_CACHE_ELIGIBILITY,
        "hitl_posture": APPS_RG_HITL_POSTURE,
        "cert_ref": APPS_RG_L0_CERT_REF,
    }
