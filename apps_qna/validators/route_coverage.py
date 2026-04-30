"""LINT-5 — orphan card check.

Every emitted card (other than the always-on cards 00, 01, 02, the
interviewer-lens family 03*, and the company overlay 04) must be referenced
by some route's load list.
"""

from __future__ import annotations

from apps_qna.config.route_registry import RouteRegistry
from apps_qna.router.pack_loader import LoadedPack
from apps_qna.validators.types import LintError, LintResult

# Cards that are always loaded, not route-specific.
# 00–04 are the original always-on family.
# 18–22 are the Wave 0–5 always-on additions:
#   18 ethics & disclosure, 19 source register, 20 glossary,
#   21 likely questions, 22 learnings (post-rehearsal).
_ALWAYS_ON_PREFIXES = (
    "00_", "01_", "02_", "04_",
    "18_", "19_", "20_", "21_", "22_",
)


def _is_lens_card(filename: str) -> bool:
    """Card 03 (single-mode) or 03A_/03B_/... (panel-mode)."""
    return filename.startswith("03_") or (
        len(filename) >= 4
        and filename[:2] == "03"
        and filename[2].isalpha()
        and filename[2:3].isupper()
    )


def check_no_orphan_cards(
    pack: LoadedPack, registry: RouteRegistry
) -> LintResult:
    """LINT-5 — every emitted card is referenced or is always-on."""
    errors: list[LintError] = []
    referenced: set[str] = set()
    for route in registry.routes:
        referenced.add(route.primary_card)
        referenced.update(route.optional_specialists)

    for card in pack.cards:
        fn = card.filename
        if any(fn.startswith(p) for p in _ALWAYS_ON_PREFIXES):
            continue
        if _is_lens_card(fn):
            continue
        if fn in referenced:
            continue
        errors.append(
            LintError(
                code="LINT-5",
                message=(
                    f"Card {fn} is in the pack but no route's load list "
                    "references it. Either add it to a route in "
                    "route_registry.yaml or remove the template."
                ),
                where=fn,
            )
        )
    return LintResult(errors=errors)
