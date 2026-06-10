"""Release repair policy for headline — bounded same-authority content-signal repair only."""

from __future__ import annotations

import os

# Bounded same-authority content-signal regen (retry_headline_content_signal).
RELEASE_HEADLINE_CONTENT_SIGNAL_REPAIR_ENABLED = True
# Hard cap — absolute ceiling, not operator-raisable (no env knob exists for attempts).
CONTENT_SIGNAL_REPAIR_MAX_ATTEMPTS = 1


def content_signal_repair_enabled() -> bool:
    raw = os.environ.get("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR", "1").strip().lower()
    return RELEASE_HEADLINE_CONTENT_SIGNAL_REPAIR_ENABLED and raw not in ("0", "false", "no", "off")


def content_signal_repair_env_state() -> str:
    raw = os.environ.get("APPS_RG_HEADLINE_CONTENT_SIGNAL_REPAIR")
    return raw.strip() if isinstance(raw, str) and raw.strip() else "unset"


__all__ = [
    "CONTENT_SIGNAL_REPAIR_MAX_ATTEMPTS",
    "RELEASE_HEADLINE_CONTENT_SIGNAL_REPAIR_ENABLED",
    "content_signal_repair_enabled",
    "content_signal_repair_env_state",
]
