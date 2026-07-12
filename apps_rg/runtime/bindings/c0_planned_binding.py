"""Verified L1-plan boundary for apps_rg C0 retrieval.

Canonical product callers use this wrapper rather than calling the compatibility
C0 binding without an L1 plan. C0 remains the evidence authority; this module
only verifies and threads the planning support intent.
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError, c0_retrieve_apps_rg
from apps_rg.runtime.bindings.l1_planning_capsule import (
    extract_verified_planning_capsule,
)


def c0_retrieve_apps_rg_planned(
    route: Any,
    validated_request: ValidatedRequest,
    *,
    l1_plan: L1PlanContract,
    **kwargs: Any,
) -> FinalEvidenceContract:
    """Verify L1 integrity, execute C0, and require capsule lineage on the FEC."""

    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            "c0_retrieve_apps_rg_planned requires an L1PlanContract; "
            f"got {type(l1_plan).__name__}"
        )
    capsule, _verification = extract_verified_planning_capsule(l1_plan, required=True)
    fec = c0_retrieve_apps_rg(
        route,
        validated_request,
        l1_plan=l1_plan,
        **kwargs,
    )
    capsule_digest = str(capsule.get("capsule_digest") or "")
    retrieval_plan_ref = str(getattr(fec, "retrieval_plan_ref", "") or "")
    audit_refs = tuple(str(ref) for ref in (getattr(fec, "audit_refs", None) or ()))
    if not retrieval_plan_ref or capsule_digest[:24] not in retrieval_plan_ref:
        raise C0EvidenceGapError(
            "C0 completed without binding FinalEvidenceContract.retrieval_plan_ref "
            "to the verified L1 planning capsule"
        )
    if not any(
        ref.startswith("l1_capsule_digest:") and capsule_digest[:24] in ref
        for ref in audit_refs
    ):
        raise C0EvidenceGapError(
            "C0 completed without an L1 capsule audit reference on FinalEvidenceContract"
        )
    return fec


__all__ = ["c0_retrieve_apps_rg_planned"]
