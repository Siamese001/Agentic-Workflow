"""Canonical ADG output semantics for severity vs enforcement.

Impact severity describes how serious a finding is. Enforcement describes
whether the current run must stop. P0 is reserved for open blockers only.
"""

from __future__ import annotations

from typing import Any

IMPACT_BY_BAND: dict[str, str] = {
    "P0": "critical",
    "P1": "high",
    "P2": "medium",
    "P3": "low",
}

WORK_PRIORITY_BLOCKER = "P0"
WORK_PRIORITY_TRIAGE = "triage"
WORK_PRIORITY_TRACKED = "tracked"
WORK_PRIORITY_WATCH = "watch"
WORK_PRIORITY_NONE = "none"


def impact_severity_from_band(band: Any) -> str:
    """Map the legacy P-band carrier to impact severity language."""
    return IMPACT_BY_BAND.get(str(band or "").upper(), "low")


def queue_section_for_action(action: dict[str, Any]) -> str:
    cluster = str(action.get("verdict_cluster") or "").upper()
    if cluster == "FIX":
        return "open_blockers"
    if cluster == "CANDIDATE_BLOCKER_TRIAGE":
        return "candidate_blockers"
    if cluster == "GRAPHDB":
        return "watchlist"
    return "tracked_debt"


def action_semantics(action: dict[str, Any]) -> dict[str, str]:
    """Return canonical semantic fields for an emitted action-queue row."""
    cluster = str(action.get("verdict_cluster") or "").upper()
    section = queue_section_for_action(action)
    if cluster == "FIX":
        effect = "blocker"
        priority = WORK_PRIORITY_BLOCKER
    elif cluster == "CANDIDATE_BLOCKER_TRIAGE":
        effect = "inventory"
        priority = WORK_PRIORITY_TRIAGE
    elif cluster == "GRAPHDB":
        effect = "watchlist"
        priority = WORK_PRIORITY_WATCH
    else:
        effect = "inventory"
        priority = WORK_PRIORITY_TRACKED
    return {
        "impact_severity": impact_severity_from_band(action.get("sort_band")),
        "enforcement_effect": effect,
        "disposition": "open",
        "work_priority": priority,
        "queue_section": section,
    }
