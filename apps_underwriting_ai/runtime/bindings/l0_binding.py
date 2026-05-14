"""L0 routing binding for apps_underwriting_ai.

Thin pass-through: the underwriting domain uses a fixed route. L0
accepts the UWL1Plan from L1 and returns a minimal UWRoute that
activates both grounding (C0) and model generation (PA→L2) stages
in AppIngressRunner._run_profile_stages.

Pattern: pure function. No state. No I/O. No provider calls.
AppIngressRunner calls: l0_fn(l1_plan) → route

Plan: apps-underwriting-ai-profile-migration (Bundle B).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_underwriting_ai.runtime.bindings.l1_binding import UWL1Plan

UW_L0_CERT_REF: str = "l0-apps-underwriting-ai-underwriting-decision-v1"
UW_ROUTE_ID: str = "apps_underwriting_ai.decision_packet_v1"
UW_ROUTE_FAMILY: str = "R3R4_MANAGED_WORKFLOW"


@dataclass
class UWRoute:
    """Minimal L0 route output for underwriting.

    Sets grounding_required=True and model_generation_required=True so
    AppIngressRunner._run_profile_stages invokes both C0 (deterministic
    pipeline) and PA→L2 (rationale generation).
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str
    tenant_id: str
    route_id: str = UW_ROUTE_ID
    route_family: str = UW_ROUTE_FAMILY
    grounding_required: bool = True
    model_generation_required: bool = True
    l5_certification_ref: str = UW_L0_CERT_REF
    l0_cert_ref: str = UW_L0_CERT_REF
    l1_plan: UWL1Plan | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def l0_route_underwriting(l1_plan: UWL1Plan) -> UWRoute:
    """Fixed-route L0 stage for underwriting.

    Accepts the UWL1Plan from L1 and returns a UWRoute with
    grounding_required=True and model_generation_required=True so both
    the C0 deterministic pipeline and the PA→L2 rationale path fire.
    Called by AppIngressRunner as l0_fn(l1_plan).

    Args:
        l1_plan: L1 plan output carrying the validated request.

    Returns:
        UWRoute with fixed underwriting routing policy.
    """
    validated = l1_plan.validated_request
    return UWRoute(
        request_id=validated.request_id,
        run_id=validated.request_id,
        app_id=validated.app_id,
        trace_id=validated.trace_id,
        tenant_id=validated.app_id,
        l5_certification_ref=l1_plan.l5_certification_ref,
        l1_plan=l1_plan,
    )


__all__ = [
    "UW_L0_CERT_REF",
    "UW_ROUTE_ID",
    "UW_ROUTE_FAMILY",
    "UWRoute",
    "l0_route_underwriting",
]
