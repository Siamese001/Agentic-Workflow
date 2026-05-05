"""L2 E5 — Seal: produce CardPackManifest with hashes and source register.

W4.1: Sealing stage that finalizes the manifest with evidence refs,
card hashes, and source register for audit trail.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W4.1
"""

from __future__ import annotations

import hashlib
from typing import Any

from apps_qna.types.spine_contracts import CardPackManifestExtended


def seal_manifest(
    *,
    cards: dict[str, str],
    interview_slug: str,
    route_id: str,
    evidence_contract: dict[str, Any],
    tiering: dict[str, str],
) -> CardPackManifestExtended:
    """Seal the card pack manifest with hashes and evidence refs.

    Args:
        cards: Dict of card_id -> rendered content.
        interview_slug: The interview slug.
        route_id: The selected route id.
        evidence_contract: The evidence contract used.
        tiering: Card tier assignments (tier_1 / tier_2).

    Returns:
        A sealed CardPackManifestExtended.
    """
    card_hashes: dict[str, str] = {}
    for card_id, content in cards.items():
        card_hashes[card_id] = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()[:16]

    evidence_refs = (
        evidence_contract.get("producer", ""),
        evidence_contract.get("briefing_hash", ""),
    )

    return CardPackManifestExtended(
        interview_slug=interview_slug,
        built_at="",
        builder_version="0.1.0",
        template_set_version="v2",
        cards=tuple(cards.keys()),
        routes_covered=(route_id,),
        interviewers=(),
        pasted_cards=tuple(cards.keys()),
        paste_exceeds_chatgpt_limit=len(cards) > 25,
        evidence_refs=tuple(r for r in evidence_refs if r),
        tiering=tiering,
        card_hashes=card_hashes,
        source_register=(),
    )


__all__ = ["seal_manifest"]
