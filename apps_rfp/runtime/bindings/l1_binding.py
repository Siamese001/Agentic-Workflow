"""L1 binding — adapts AppIngressRunner validated request to apps_rfp L1 planning.

AppIngressRunner calls: l1_plan = l1(validated)

Consumes: ValidatedRequest (from rfp_u0)
Emits:    L1PlanContract (from agentic_core.L1_cognition.types.plan_contract_types)

apps_rfp L1 uses the GovernedAppRunner shared substrate's query-decomposition
step: breaks the rfp_document_path / target_company into sub-queries for C0.

The returned L1PlanContract carries .grounding_required — AppIngressRunner reads
it to decide whether to call the c0 binding. For apps_rfp, grounding_required
is always True (rfp_docs retrieval confirmed in W0 Stage-Necessity Table).

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def rfp_l1(validated: Any) -> Any:
    """L1 stage binding for apps_rfp.

    Produces an L1PlanContract from the ValidatedRequest. The plan decomposes
    the rfp query into C0 sub-queries and marks grounding_required=True so
    the c0 retrieval step fires.

    Args:
        validated: ValidatedRequest from rfp_u0.

    Returns:
        L1PlanContract with .grounding_required=True and .sub_queries populated.

    Raises:
        ValueError: If validated carries no usable batch_id / raw_payload.
    """
    import hashlib
    import uuid

    from agentic_core.L1_cognition.types.plan_contract_types import L1PlanContract, ReasoningMode

    batch_id: str = getattr(validated, "batch_id", "") or ""
    request_id: str = getattr(validated, "request_id", "") or ""
    normalized_payload: dict = getattr(validated, "normalized_payload", {}) or {}

    rfp_document_path: str = normalized_payload.get("rfp_document_path", "") or batch_id
    target_company: str = normalized_payload.get("target_company", "") or ""

    if not rfp_document_path and not target_company:
        raise ValueError(
            "rfp_l1: ValidatedRequest carries no rfp_document_path or target_company; "
            "cannot produce L1 plan."
        )

    sub_query = (
        f"RFP proposal assembly for {target_company}: {rfp_document_path}"
        if target_company
        else f"RFP proposal assembly: {rfp_document_path}"
    )

    plan_id = f"rfp-plan-{uuid.uuid4().hex[:12]}"
    policy_hash = hashlib.sha256(
        f"apps_rfp.proposal_assembly:{request_id}".encode()
    ).hexdigest()[:32]

    _LOGGER.debug(
        "rfp_l1: request_id=%s batch_id=%s plan_id=%s sub_query=%s",
        request_id,
        batch_id,
        plan_id,
        sub_query[:80],
    )

    return L1PlanContract(
        plan_id=plan_id,
        request_id=request_id,
        policy_hash=policy_hash,
        reasoning_mode=ReasoningMode.DECOMPOSED,
        grounding_required=True,
        confidence_score=0.90,
        steps=({"step": "rfp_proposal_assembly", "query": sub_query,
                "rfp_document_path": rfp_document_path, "target_company": target_company},),
    )


__all__ = ["rfp_l1"]
