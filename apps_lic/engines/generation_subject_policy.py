"""Subject and channel policy helpers for apps_lic generation."""

from __future__ import annotations

from typing import Any, Mapping

from apps_lic.types.linkedin_route_envelope import (
    CHANNEL_LINKEDIN_CHAT,
    CHANNEL_LINKEDIN_INMAIL,
    CONNECTION_REQUEST_CHAR_CAP,
    INMAIL_BODY_CHAR_CAP,
)


def subject_required(length_budget: Mapping[str, Any] | None) -> bool:
    if not isinstance(length_budget, Mapping):
        return False
    if "subject_required" in length_budget:
        return bool(length_budget.get("subject_required"))
    budget_key = str(length_budget.get("budget_key") or "").lower()
    try:
        hard_cap = int(length_budget.get("hard_cap_chars") or 0)
    except (TypeError, ValueError):
        hard_cap = 0
    return "inmail" in budget_key or hard_cap >= INMAIL_BODY_CHAR_CAP


def channel_from_length_budget(length_budget: Mapping[str, Any] | None) -> str:
    if isinstance(length_budget, Mapping):
        channel = str(length_budget.get("channel") or "").strip().lower()
        if channel:
            return channel
    if subject_required(length_budget):
        return CHANNEL_LINKEDIN_INMAIL
    if isinstance(length_budget, Mapping):
        try:
            hard_cap = int(length_budget.get("hard_cap_chars") or 0)
        except (TypeError, ValueError):
            hard_cap = 0
        if hard_cap and hard_cap <= CONNECTION_REQUEST_CHAR_CAP:
            return CHANNEL_LINKEDIN_CHAT
    return "linkedin"
