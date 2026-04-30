"""LINT-2 + LINT-3 — context-menu sanity caps.

The routing manifest's "max 2 specialists" rule is a *runtime* load cap (the
runtime picks ≤2 specialists from the menu when answering one q). The
*menu* itself can list more specialists as candidates — the Drew Clements
Architecture route, for example, lists 3 optional specialists for the
runtime to choose from.

These two static checks therefore enforce *menu sanity*, not the runtime
cap (which a static linter cannot enforce without simulating routing).

LINT-2: No route lists more than 4 menu specialists.
LINT-3: No route's total menu (1 primary + N menu specialists) exceeds 5.
"""

from __future__ import annotations

from apps_qna.config.route_registry import RouteRegistry
from apps_qna.router.pack_loader import LoadedPack
from apps_qna.validators.types import LintError, LintResult

# Menu-sanity caps. Runtime cap is "2 specialists per answer" — see
# routing-manifest §"Max context rule" — and is enforced by card 01 at
# question time, not by the static linter.
_MAX_SPECIALIST_MENU = 4
_MAX_TOTAL_MENU = 5


def check_specialist_count(
    pack: LoadedPack, registry: RouteRegistry
) -> LintResult:
    """LINT-2 — each route lists at most 4 menu specialists.

    Menu-sanity check, not the runtime ≤2 cap.
    """
    errors: list[LintError] = []
    for route in registry.routes:
        if len(route.optional_specialists) > _MAX_SPECIALIST_MENU:
            errors.append(
                LintError(
                    code="LINT-2",
                    message=(
                        f"Route {route.id} lists "
                        f"{len(route.optional_specialists)} specialist cards "
                        f"in its menu. Menu-sanity cap is "
                        f"{_MAX_SPECIALIST_MENU}; the runtime independently "
                        "caps loads at 2 per answer."
                    ),
                    where=route.id,
                )
            )
    return LintResult(errors=errors)


def check_max_context(
    pack: LoadedPack, registry: RouteRegistry
) -> LintResult:
    """LINT-3 — total menu (primary + specialists) never exceeds 5.

    Menu-sanity check, not the runtime ≤3 total-load cap.
    """
    errors: list[LintError] = []
    for route in registry.routes:
        total = 1 + len(route.optional_specialists)
        if total > _MAX_TOTAL_MENU:
            errors.append(
                LintError(
                    code="LINT-3",
                    message=(
                        f"Route {route.id} menu has {total} cards "
                        f"(1 primary + {len(route.optional_specialists)} "
                        f"specialists). Menu-sanity cap is "
                        f"{_MAX_TOTAL_MENU}; the runtime independently "
                        "caps loads at 3 per answer."
                    ),
                    where=route.id,
                )
            )
    return LintResult(errors=errors)
