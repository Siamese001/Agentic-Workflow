"""LINT-7 — token (word) budget per card.

Enforces a sanity cap on per-card word count so packs do not balloon and the
runtime context budget rule in card 00 stays achievable.

Cap is intentionally generous (default 1500 words) — this is a guardrail
against runaway templates, not a stylistic constraint.
"""

from __future__ import annotations

import re

from apps_qna.config.route_registry import RouteRegistry
from apps_qna.router.pack_loader import LoadedPack
from apps_qna.validators.types import LintError, LintResult

_DEFAULT_WORD_CAP = 1500

# Approximate words/token = 0.75 (English prose). 1500 words ≈ 2000 tokens —
# well under the GPT-5.5 8k working-context window for one card.

_WORD_RE = re.compile(r"\b\w+\b")


def _count_words(text: str) -> int:
    """Cheap word counter — splits on word boundaries, ignores markdown/markup."""
    return len(_WORD_RE.findall(text))


def check_token_budget(
    pack: LoadedPack,
    registry: RouteRegistry,
    word_cap: int = _DEFAULT_WORD_CAP,
) -> LintResult:
    """LINT-7 — every card stays under the per-card word cap.

    Args:
        pack: Loaded card pack.
        registry: Unused; kept for validator-signature compatibility.
        word_cap: Maximum allowed words per card. Default 1500.

    Returns:
        LintResult with one LINT-7 error per over-budget card.
    """
    errors: list[LintError] = []
    for card in pack.cards:
        words = _count_words(card.content)
        if words > word_cap:
            errors.append(
                LintError(
                    code="LINT-7",
                    message=(
                        f"Card {card.filename} has {words} words "
                        f"(cap is {word_cap}). Tighten the template or split "
                        "the content across two cards."
                    ),
                    where=card.filename,
                )
            )
    return LintResult(errors=errors)
