"""Two-Tier Router — selects exactly one primary route with precedence rules.

W3.1: Core router that selects between Tier 1 always-on and Tier 2
specialist cards based on interview context and evidence.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W3.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoutePrecedence(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class TierSelection:
    """Result of two-tier route selection."""

    tier1_cards: tuple[str, ...] = ()
    tier2_cards: tuple[str, ...] = ()
    primary_route: str = ""
    precedence: RoutePrecedence = RoutePrecedence.PRIMARY
    reason: str = ""


_TIER1_ALWAYS_ON = (
    "00_START_HERE_RUNTIME_ROOT",
    "00A_SOURCE_SET_AND_EGRESS_VERIFIER",
    "01_CARD_SELECTION_MANIFEST",
    "03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE",
)

_TIER2_SPECIALISTS: dict[str, tuple[str, ...]] = {
    "star_proof": ("STAR_PROOF",),
    "star_failure": ("STAR_FAILURE_LEARNING",),
    "rag_context": ("RAG_CONTEXT",),
    "governance": ("GOVERNANCE_HITL",),
    "tools_mcp": ("TOOLS_MCP_GATEWAY",),
    "agentic_arch": ("AGENTIC_ARCHITECTURE",),
    "ds_platform": ("DS_TO_PLATFORM",),
    "productization": ("PLATFORM_PRODUCTIZATION",),
    "client_roi": ("CLIENT_ADVISORY_ROI",),
    "role_scope": ("ROLE_SCOPE_MANDATE",),
    "exec_fit": ("EXEC_TRANSLATION_FIT",),
    "cross_exam": ("CROSS_EXAM_DEPTH",),
    "genai_story": ("HARDEST_GENAI_DEFAULT_STORY",),
    "routing_evals": ("ROUTING_EVALS_AND_EDGE_CASES",),
}

_ROUTE_TO_TIER2: dict[str, tuple[str, ...]] = {
    "apps_qna.live_interview_runtime_pack_v1": (
        "star_proof", "rag_context", "governance", "agentic_arch",
        "ds_platform", "productization", "exec_fit", "cross_exam",
    ),
    "apps_qna.live_interview_runtime_pack_from_uploaded_brief_v1": (
        "star_proof", "star_failure", "rag_context", "governance",
        "tools_mcp", "agentic_arch", "ds_platform", "productization",
        "client_roi", "role_scope", "exec_fit", "cross_exam",
        "genai_story", "routing_evals",
    ),
}


def select_tier_cards(
    *,
    route_id: str,
    evidence_contract: dict[str, Any] | None = None,
    tier2_triggers: tuple[str, ...] = (),
) -> TierSelection:
    """Select Tier 1 always-on + Tier 2 specialist cards.

    Args:
        route_id: The selected route id.
        evidence_contract: The evidence contract driving selection.
        tier2_triggers: Explicit Tier 2 triggers (overrides route defaults).

    Returns:
        A TierSelection with exactly one primary route.
    """
    tier1 = _TIER1_ALWAYS_ON

    if tier2_triggers:
        tier2_keys = list(tier2_triggers)
    else:
        tier2_keys = list(_ROUTE_TO_TIER2.get(route_id, ()))

    tier2: list[str] = []
    for key in tier2_keys:
        cards = _TIER2_SPECIALISTS.get(key, ())
        tier2.extend(cards)

    return TierSelection(
        tier1_cards=tier1,
        tier2_cards=tuple(tier2),
        primary_route=route_id,
        precedence=RoutePrecedence.PRIMARY,
        reason=f"Route {route_id} selected {len(tier2)} Tier 2 cards",
    )


def resolve_ambiguity(
    selections: list[TierSelection],
) -> TierSelection:
    """Resolve ambiguity when multiple routes could apply.

    Returns the highest-precedence selection. PRIMARY > SECONDARY > FALLBACK.
    """
    if not selections:
        return TierSelection(reason="No valid route")

    for sel in selections:
        if sel.precedence == RoutePrecedence.PRIMARY:
            return sel
    for sel in selections:
        if sel.precedence == RoutePrecedence.SECONDARY:
            return sel
    return selections[0]


__all__ = [
    "RoutePrecedence",
    "TierSelection",
    "resolve_ambiguity",
    "select_tier_cards",
]
