"""LINT-1 + LINT-4 — route purity and route coverage.

LINT-1: Each route in the registry has exactly one primary card on disk.
LINT-4: Every route in the registry has a primary card present in the pack.
"""

from __future__ import annotations

from apps_qna.config.route_registry import RouteRegistry
from apps_qna.router.pack_loader import LoadedPack
from apps_qna.validators.types import LintError, LintResult


def check_route_purity(
    pack: LoadedPack, registry: RouteRegistry
) -> LintResult:
    """LINT-1 — no card is the primary for two routes."""
    errors: list[LintError] = []
    seen: dict[str, str] = {}  # filename -> route_id
    for route in registry.routes:
        prior = seen.get(route.primary_card)
        if prior is not None:
            errors.append(
                LintError(
                    code="LINT-1",
                    message=(
                        f"Card {route.primary_card} is declared primary for "
                        f"two routes: {prior} and {route.id}. Each route "
                        "must have a unique primary card."
                    ),
                    where=route.primary_card,
                )
            )
        seen[route.primary_card] = route.id
    return LintResult(errors=errors)


def check_route_coverage(
    pack: LoadedPack, registry: RouteRegistry
) -> LintResult:
    """LINT-4 — every route's primary card is on disk in the pack."""
    errors: list[LintError] = []
    on_disk = pack.card_filenames
    for route in registry.routes:
        if route.primary_card not in on_disk:
            errors.append(
                LintError(
                    code="LINT-4",
                    message=(
                        f"Route {route.id} ({route.name}) declares primary "
                        f"card {route.primary_card} but it is missing from "
                        "the emitted pack."
                    ),
                    where=route.id,
                )
            )
    return LintResult(errors=errors)
