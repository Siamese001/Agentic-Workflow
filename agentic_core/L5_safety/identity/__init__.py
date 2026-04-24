"""L5 Identity sub-package — front-door principal resolution (G-04, L5 v4).

Single source of truth for resolving the invoking principal at the
front door of the governance plane. Called by L5 G2 (Authority Context
Resolution) before any capability_token is issued.

Reference: docs/contracts/identity_propagation.md
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from agentic_core.L5_safety.identity.front_door_resolver import (
    FRONT_DOOR_AUTOMATION_ENV_VARS,
    clear_resolver_cache,
    resolve_front_door_principal,
)

__all__ = [
    "FRONT_DOOR_AUTOMATION_ENV_VARS",
    "clear_resolver_cache",
    "resolve_front_door_principal",
]
