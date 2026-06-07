"""L0 binding — adapts AppIngressRunner L1 plan to apps_qna L0 router.

AppIngressRunner calls: route = l0(l1_plan)

The route result MUST carry:
  .grounding_required       — whether c0_fn should be called
  .model_generation_required — whether pa_fn/l2_fn should be called

apps_qna always requires model generation (the card pack build IS the
generation step). grounding_required comes from L1.

Consumes: L1PlanContract (from qna_l1)
Emits:    QnaRouteContract — a thin wrapper around RouteSelection that adds
          .model_generation_required = True and the attributes AppIngressRunner
          expects (.request_id, .run_id, .app_id, .trace_id).

Plan: docs/archive/windsurf/legacy-tree/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class QnaRouteContract:
    """Thin wrapper adapting RouteSelection to the AppIngressRunner contract.

    Carries the RouteSelection for downstream stages plus the fields that
    AppIngressRunner._run_profile_stages reads from the route object.
    """

    route_id: str
    grounding_required: bool
    model_generation_required: bool = True  # apps_qna always generates
    c0_required: bool = False
    evidence_source: str = ""

    # Spine identity fields (set by qna_l0 from l1_plan context)
    request_id: str = ""
    run_id: str = ""
    app_id: str = "apps_qna"
    trace_id: str = ""
    tenant_id: str = "apps_qna"

    # Forwarded for downstream stages
    interview_slug: str = ""


def qna_l0(l1_plan: Any) -> QnaRouteContract:
    """L0 stage binding for apps_qna.

    Reads .grounding_required from the L1 plan and calls select_route().
    Wraps the RouteSelection in a QnaRouteContract so AppIngressRunner
    sees the expected attributes.

    Args:
        l1_plan: L1PlanContract from qna_l1.

    Returns:
        QnaRouteContract with grounding_required and model_generation_required.
    """
    from apps_qna.l0_router import select_route

    grounding_required: bool = getattr(l1_plan, "grounding_required", True)
    request_id: str = getattr(l1_plan, "request_id", "") or ""

    _LOGGER.debug("qna_l0: grounding_required=%s request_id=%s", grounding_required, request_id)

    route_sel = select_route(
        grounding_required=grounding_required,
        has_valid_briefing=False,
    )

    return QnaRouteContract(
        route_id=route_sel.route_id,
        grounding_required=route_sel.grounding_required,
        model_generation_required=True,
        c0_required=route_sel.c0_required,
        evidence_source=route_sel.evidence_source,
        request_id=request_id,
        run_id=f"qna-run-{uuid.uuid4().hex[:12]}",
        app_id="apps_qna",
        trace_id=f"qna-trace-{uuid.uuid4().hex[:16]}",
        tenant_id="apps_qna",
    )


__all__ = ["QnaRouteContract", "qna_l0"]
