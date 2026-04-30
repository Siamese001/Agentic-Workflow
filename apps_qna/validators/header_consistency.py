"""LINT-6 — always-on header consistency.

Cards 00–17 must all contain the canonical LIVE VERBAL-FIRST OVERWRITE
block. The block is the contract anchor for the runtime — drift here means
the runtime won't behave consistently across cards.
"""

from __future__ import annotations

from apps_qna.config.route_registry import RouteRegistry
from apps_qna.router.pack_loader import LoadedPack
from apps_qna.validators.types import LintError, LintResult

_HEADER_SIGNATURES = (
    "## LIVE VERBAL-FIRST OVERWRITE",
    "### Always-on output rules",
    "### First-person credibility",
    "### Tight routing rule",
    "### Preferred reliability-chain phrasing",
)


def check_header_consistency(
    pack: LoadedPack, registry: RouteRegistry
) -> LintResult:
    """LINT-6 — every card carries the always-on header sub-blocks."""
    errors: list[LintError] = []
    for card in pack.cards:
        for sig in _HEADER_SIGNATURES:
            if sig not in card.content:
                errors.append(
                    LintError(
                        code="LINT-6",
                        message=(
                            f"Card {card.filename} is missing always-on "
                            f"header signature: '{sig}'. Every card must "
                            "include the LIVE VERBAL-FIRST OVERWRITE block "
                            "for the runtime to behave consistently."
                        ),
                        where=card.filename,
                    )
                )
                break  # one error per card is enough
    return LintResult(errors=errors)
