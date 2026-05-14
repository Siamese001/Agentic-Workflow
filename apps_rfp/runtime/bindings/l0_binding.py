"""L0 binding — adapts AppIngressRunner L1 plan to apps_rfp route selection.

AppIngressRunner calls: route = l0(l1_plan)

Consumes: L1PlanContract (from rfp_l1)
Emits:    RfpRouteContract — app-local thin wrapper AppIngressRunner can read

apps_rfp routes deterministically to 'rfp_proposal_assembly' capability.
The L0 binding resolves the route from task_class and emits an RfpRouteContract
pointing the C0 retrieval at the 'rfp_docs' collection.

AppIngressRunner reads .grounding_required and .model_generation_required from
the route result to decide whether to call c0_fn and pa_fn.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)

_RFP_ROUTING_TARGET = "rfp_proposal_assembly"
_RFP_COLLECTION = "rfp_docs"
_RFP_CAPABILITY = "apps_rfp.proposal_assembly_v1"


@dataclass(frozen=True)
class RfpRouteContract:
    """Thin wrapper adapting apps_rfp route selection to AppIngressRunner contract.

    Carries the deterministic route for downstream stages plus the fields that
    AppIngressRunner._run_profile_stages reads from the route object.
    """

    route_id: str
    grounding_required: bool
    model_generation_required: bool = True  # apps_rfp always generates proposal
    collection: str = "rfp_docs"
    capability_token: str = _RFP_CAPABILITY

    # Spine identity fields
    request_id: str = ""
    run_id: str = ""
    app_id: str = "apps_rfp"
    trace_id: str = ""
    tenant_id: str = "apps_rfp"

    # Forwarded for downstream stages
    rfp_document_path: str = ""
    target_company: str = ""
    sub_queries: tuple = ()
    metadata: dict = field(default_factory=dict)


def rfp_l0(l1_plan: Any) -> RfpRouteContract:
    """L0 stage binding for apps_rfp.

    Produces an RfpRouteContract from the L1PlanContract. Routes deterministically
    to rfp_proposal_assembly capability with rfp_docs C0 collection.

    Args:
        l1_plan: L1PlanContract from rfp_l1.

    Returns:
        RfpRouteContract with grounding_required=True and model_generation_required=True.

    Raises:
        ValueError: If l1_plan carries no request_id.
    """
    request_id: str = getattr(l1_plan, "request_id", "") or ""
    grounding_required: bool = bool(getattr(l1_plan, "grounding_required", True))
    steps = getattr(l1_plan, "steps", ()) or ()

    # Extract rfp_document_path / target_company from the first plan step
    rfp_document_path: str = ""
    target_company: str = ""
    sub_queries: list = []
    if steps:
        first_step = steps[0] if isinstance(steps, (list, tuple)) else {}
        if isinstance(first_step, dict):
            rfp_document_path = first_step.get("rfp_document_path", "") or ""
            target_company = first_step.get("target_company", "") or ""
            query = first_step.get("query", "") or ""
            if query:
                sub_queries = [query]
    metadata: dict = {}

    if not request_id:
        raise ValueError("rfp_l0: L1PlanContract carries no request_id.")

    _LOGGER.debug(
        "rfp_l0: request_id=%s grounding=%s rfp_document_path=%s",
        request_id,
        grounding_required,
        rfp_document_path,
    )

    return RfpRouteContract(
        route_id=_RFP_ROUTING_TARGET,
        grounding_required=grounding_required,
        model_generation_required=True,
        collection=_RFP_COLLECTION,
        capability_token=_RFP_CAPABILITY,
        request_id=request_id,
        run_id=f"rfp-run-{uuid.uuid4().hex[:12]}",
        app_id="apps_rfp",
        trace_id=f"rfp-trace-{uuid.uuid4().hex[:16]}",
        tenant_id="apps_rfp",
        rfp_document_path=rfp_document_path,
        target_company=target_company,
        sub_queries=tuple(sub_queries),
        metadata=metadata,
    )


__all__ = ["RfpRouteContract", "rfp_l0"]
