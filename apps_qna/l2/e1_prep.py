"""L2 E1 — Prep: freeze refs, bind policy_hash, create workspace.

W0 thin-slice: minimal prep that returns a workspace dict.
Full implementation lands in W4.1.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.3
"""

from __future__ import annotations

from typing import Any


def prep_workspace(
    *,
    interview_slug: str,
    route_id: str,
    policy_hash: str = "apps_qna.v1",
) -> dict[str, Any]:
    """Prepare the L2 workspace with frozen references.

    Args:
        interview_slug: The interview slug.
        route_id: The selected route id.
        policy_hash: Policy snapshot hash.

    Returns:
        A workspace dict ready for validation.
    """
    return {
        "interview_slug": interview_slug,
        "route_id": route_id,
        "policy_hash": policy_hash,
        "stage": "E1_PREP",
        "frozen_at": "",
    }


__all__ = ["prep_workspace"]
