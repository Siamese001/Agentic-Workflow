"""Release repair policy for ibm_narrative — bounded same-authority theme-overpack repair only."""

from __future__ import annotations

import os

# Bounded same-authority theme-overpack regen (apply_ibm_narrative_theme_overpack_repair).
RELEASE_IBM_NARRATIVE_THEME_REPAIR_ENABLED = True
# Hard cap — absolute ceiling, not operator-raisable (no env knob exists for attempts).
THEME_REPAIR_MAX_ATTEMPTS = 1


def theme_repair_enabled() -> bool:
    raw = os.environ.get("APPS_RG_IBM_NARRATIVE_THEME_REPAIR", "1").strip().lower()
    return RELEASE_IBM_NARRATIVE_THEME_REPAIR_ENABLED and raw not in ("0", "false", "no", "off")


def theme_repair_env_state() -> str:
    raw = os.environ.get("APPS_RG_IBM_NARRATIVE_THEME_REPAIR")
    return raw.strip() if isinstance(raw, str) and raw.strip() else "unset"


__all__ = [
    "RELEASE_IBM_NARRATIVE_THEME_REPAIR_ENABLED",
    "THEME_REPAIR_MAX_ATTEMPTS",
    "theme_repair_enabled",
    "theme_repair_env_state",
]
