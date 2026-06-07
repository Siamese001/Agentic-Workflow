"""Context Budget — enforces token/context budget for card assembly.

W3.4: Budget enforcement for domain card context assembly.
Ensures card context stays within model context window limits.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W3.4
"""

from __future__ import annotations

DEFAULT_MAX_TOKENS = 8000
DEFAULT_MAX_CARDS = 25


def check_budget(
    *,
    card_count: int,
    estimated_tokens: int = 0,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_cards: int = DEFAULT_MAX_CARDS,
) -> dict:
    """Check if card context fits within budget.

    Args:
        card_count: Number of cards to render.
        estimated_tokens: Estimated token count.
        max_tokens: Maximum allowed tokens.
        max_cards: Maximum allowed cards.

    Returns:
        A budget check result dict.
    """
    within_budget = True
    warnings: list[str] = []

    if card_count > max_cards:
        within_budget = False
        warnings.append(f"Card count {card_count} exceeds max {max_cards}")

    if estimated_tokens > max_tokens:
        within_budget = False
        warnings.append(f"Estimated tokens {estimated_tokens} exceeds max {max_tokens}")

    return {
        "within_budget": within_budget,
        "card_count": card_count,
        "estimated_tokens": estimated_tokens,
        "max_tokens": max_tokens,
        "max_cards": max_cards,
        "warnings": tuple(warnings),
    }


__all__ = ["DEFAULT_MAX_CARDS", "DEFAULT_MAX_TOKENS", "check_budget"]
