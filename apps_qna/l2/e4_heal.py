"""L2 E4 — Heal: formatting repair only, NO fact invention.

W4.1: Healing stage that fixes formatting issues in rendered cards.
Must never invent facts, add content, or modify evidence.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W4.1
"""

from __future__ import annotations

from typing import Any


def heal_cards(
    *,
    cards: dict[str, str],
    manifest: Any,
) -> dict[str, str]:
    """Apply formatting repairs to rendered cards.

    Allowed repairs:
    - Fix trailing whitespace
    - Normalize line endings to LF
    - Ensure cards end with exactly one newline

    Forbidden:
    - Adding or removing content
    - Modifying evidence references
    - Inventing facts

    Args:
        cards: Dict of card_id -> rendered content.
        manifest: The card pack manifest.

    Returns:
        Healed cards dict.
    """
    healed: dict[str, str] = {}
    for card_id, content in cards.items():
        fixed = content.rstrip() + "\n"
        fixed = fixed.replace("\r\n", "\n")
        healed[card_id] = fixed
    return healed


__all__ = ["heal_cards"]
