"""L1 Planner — produces an L1PlanContract declaring C0 vs briefing path.

W0 thin-slice: minimal planner that decides whether C0 grounding is
required or an uploaded briefing is sufficient. Full implementation
lands in W1.2 with registry integration.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W0.1
"""

from __future__ import annotations

import uuid

from agentic_core.L1_cognition.types.plan_contract_types import (
    L1PlanContract,
    ReasoningMode,
)


def plan_live_interview(
    *,
    request_id: str,
    has_briefing: bool = False,
    briefing_valid: bool = False,
) -> L1PlanContract:
    """Produce an L1PlanContract for a live interview runtime invocation.

    Args:
        request_id: The upstream request id this plan serves.
        has_briefing: Whether an uploaded briefing was provided.
        briefing_valid: Whether the uploaded briefing passed validation.

    Returns:
        An L1PlanContract declaring the grounding path.
    """
    plan_id = uuid.uuid4().hex
    grounding_required = not (has_briefing and briefing_valid)

    steps: list[dict] = [
        {"step_id": "intake", "description": "Validate interview request"},
        {"step_id": "route", "description": "Select R4_SINGLE_ACTION route"},
    ]
    if grounding_required:
        steps.append({"step_id": "c0_ground", "description": "Retrieve evidence via C0"})
    else:
        steps.append({"step_id": "briefing_consume", "description": "Consume validated briefing"})
    steps.extend([
        {"step_id": "assemble_context", "description": "Assemble domain card context"},
        {"step_id": "render_cards", "description": "Render Tier 1 + Tier 2 cards"},
        {"step_id": "seal", "description": "Seal output manifest"},
    ])

    return L1PlanContract(
        plan_id=plan_id,
        request_id=request_id,
        policy_hash="apps_qna.v1.live_interview",
        reasoning_mode=ReasoningMode.DIRECT,
        grounding_required=grounding_required,
        confidence_score=0.90,
        steps=tuple(steps),
    )


__all__ = ["plan_live_interview"]
