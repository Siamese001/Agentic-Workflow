"""L2 E3 — Exec: render Tier 1 always-on + Tier 2 via router.

W0 thin-slice: minimal execution that returns a two-tier card list.
Full implementation lands in W3.2-W3.4 with real template rendering.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W0.3
"""

from __future__ import annotations

from typing import Any

from apps_qna.types.spine_contracts import CardPackManifestExtended

_TIER1_CARDS = (
    "00_START_HERE_RUNTIME_ROOT.md",
    "00A_SOURCE_SET_AND_EGRESS_VERIFIER.md",
    "01_CARD_SELECTION_MANIFEST.md",
    "03_INTERVIEWER_LENS_AND_COMPANY_BRIDGE.md",
)

_TIER2_CARDS = (
    "STAR_PROOF.md",
    "STAR_FAILURE_LEARNING.md",
    "RAG_CONTEXT.md",
    "GOVERNANCE_HITL.md",
    "TOOLS_MCP_GATEWAY.md",
    "AGENTIC_ARCHITECTURE.md",
    "DS_TO_PLATFORM.md",
    "PLATFORM_PRODUCTIZATION.md",
    "CLIENT_ADVISORY_ROI.md",
    "ROLE_SCOPE_MANDATE.md",
    "EXEC_TRANSLATION_FIT.md",
    "CROSS_EXAM_DEPTH.md",
    "HARDEST_GENAI_DEFAULT_STORY.md",
    "ROUTING_EVALS_AND_EDGE_CASES.md",
)


def execute_build(
    workspace: dict[str, Any],
    *,
    evidence_contract: dict[str, Any],
    tier2_triggers: tuple[str, ...] = (),
) -> CardPackManifestExtended:
    """Execute the two-tier card build.

    Args:
        workspace: The validated workspace dict.
        evidence_contract: The evidence contract driving card content.
        tier2_triggers: Which Tier 2 specialist cards to include.

    Returns:
        A CardPackManifestExtended with rendered card metadata.
    """
    all_cards: list[str] = list(_TIER1_CARDS)
    tiering: dict[str, str] = {}

    for card in _TIER1_CARDS:
        tiering[card] = "tier_1"

    for card in _TIER2_CARDS:
        if card in tier2_triggers or not tier2_triggers:
            all_cards.append(card)
            tiering[card] = "tier_2"

    card_hashes = {card: f"hash:{card}" for card in all_cards}

    return CardPackManifestExtended(
        interview_slug=workspace.get("interview_slug", ""),
        built_at="",
        builder_version="0.1.0",
        template_set_version="v2",
        cards=tuple(all_cards),
        routes_covered=(workspace.get("route_id", ""),),
        interviewers=(),
        pasted_cards=tuple(all_cards),
        paste_exceeds_chatgpt_limit=len(all_cards) > 25,
        evidence_refs=(evidence_contract.get("producer", ""),),
        tiering=tiering,
        card_hashes=card_hashes,
        source_register=(),
    )


__all__ = ["execute_build"]
