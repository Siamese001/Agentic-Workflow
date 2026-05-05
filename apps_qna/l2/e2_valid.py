"""L2 E2 — Valid: validate schema, evidence, routes.

W0 thin-slice: minimal validation that checks required fields.
Full implementation lands in W4.1.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.3
"""

from __future__ import annotations

from typing import Any


def validate_build_inputs(
    workspace: dict[str, Any],
    *,
    evidence_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate build inputs before execution.

    Args:
        workspace: The E1 workspace dict.
        evidence_contract: The evidence contract (C0 or briefing).

    Returns:
        A validation result dict with status and reason codes.
    """
    errors: list[str] = []

    if not workspace.get("interview_slug"):
        errors.append("missing interview_slug")
    if not workspace.get("route_id"):
        errors.append("missing route_id")

    if evidence_contract is None:
        errors.append("missing evidence_contract")

    return {
        "stage": "E2_VALID",
        "valid": len(errors) == 0,
        "errors": tuple(errors),
        "workspace": workspace,
    }


__all__ = ["validate_build_inputs"]
