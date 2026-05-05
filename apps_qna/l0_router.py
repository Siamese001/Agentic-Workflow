"""L0 Router — selects exactly one R4_SINGLE_ACTION route.

W0 thin-slice: minimal router that selects between grounded and
briefing-based routes. Full implementation lands in W3.1 with
two-tier router and precedence rules.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.2
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RouteSelection:
    """A single selected route with its grounding contract."""

    route_id: str
    grounding_required: bool
    c0_required: bool
    uploaded_briefing_required: bool
    evidence_source: str


_ROUTE_GROUNDED = RouteSelection(
    route_id="apps_qna.live_interview_runtime_pack_v1",
    grounding_required=True,
    c0_required=True,
    uploaded_briefing_required=False,
    evidence_source="canonical_c0",
)

_ROUTE_BRIEFING = RouteSelection(
    route_id="apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1",
    grounding_required=False,
    c0_required=False,
    uploaded_briefing_required=True,
    evidence_source="uploaded_briefing",
)


def select_route(
    *,
    grounding_required: bool,
    has_valid_briefing: bool = False,
) -> RouteSelection:
    """Select exactly one R4_SINGLE_ACTION route.

    Args:
        grounding_required: Whether the L1 plan requires C0 grounding.
        has_valid_briefing: Whether a valid uploaded briefing is available.

    Returns:
        Exactly one RouteSelection.

    Raises:
        ValueError: If no valid route can be selected (fail-closed).
    """
    if has_valid_briefing and not grounding_required:
        return _ROUTE_BRIEFING
    if grounding_required:
        return _ROUTE_GROUNDED
    raise ValueError(
        "No valid route: grounding_required=False but no valid briefing available. "
        "Route resolution must fail closed."
    )


__all__ = ["RouteSelection", "select_route"]
