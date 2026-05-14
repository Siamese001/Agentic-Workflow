"""L1 binding — adapts AppIngressRunner validated request to apps_qna L1 planner.

AppIngressRunner calls: l1_plan = l1(validated)

Consumes: ValidatedRequest (from agentic_core.L0_routing.intake.validated_request)
Emits:    L1PlanContract (from agentic_core.L1_cognition.types.plan_contract_types)

The L1 result must carry .grounding_required — AppIngressRunner reads it to
decide whether to call c0_fn.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def qna_l1(validated: Any) -> Any:
    """L1 stage binding for apps_qna.

    Extracts interview context from the ValidatedRequest and delegates to
    apps_qna.l1_planner.plan_live_interview().

    Args:
        validated: ValidatedRequest from qna_u0.

    Returns:
        L1PlanContract with .grounding_required populated.
    """
    from apps_qna.l1_planner import plan_live_interview

    request_id = getattr(validated, "request_id", "") or ""

    # ValidatedRequest carries .batch_id as the interview_slug in apps_qna U0
    interview_slug = getattr(validated, "batch_id", "") or ""

    # No briefing on the spine path (briefing path uses separate profile config)
    _LOGGER.debug("qna_l1: request_id=%s slug=%s", request_id, interview_slug)

    return plan_live_interview(
        request_id=request_id,
        has_briefing=False,
        briefing_valid=False,
    )


__all__ = ["qna_l1"]
