#!/usr/bin/env python3
"""_notion_plans_status_check.py — Plans DB Status value validator.

Pure logic. No I/O at import. Safe to import from any hook, audit, or CI gate.

Constitutional rule: `.windsurf/rules/notion-plans-taxonomy.md` > "CANONICAL
Status option strings" (2026-05-03). Plans DB `Status` Select field has six
canonical options — any other value writes a new duplicate option into the
schema (Notion auto-creates unknown Select names silently).

Contract
--------
    decide(db_id: str, property_name: str, value: str) -> Violation | None
        db_id         — Notion database id OR data-source id from the write
                        payload (normalized to lowercase, dashes preserved).
        property_name — property key from the write payload (e.g. "Status").
        value         — the Select.name string being written.

    Returns a ``Violation`` when the write targets the Plans DB + Status
    property with a non-canonical value; ``None`` otherwise (not-plans-db,
    not-status-property, or canonical value).

Violation fields:
    db_id         — input db_id (normalized)
    property_name — input property_name
    value         — offending value
    suggested     — canonical replacement (or "" when no mapping known)
    message       — human-readable explanation with canonical list

The helper does NOT read the environment or the filesystem; callers honor
``NOTION_PLANS_STATUS_BYPASS=1`` themselves.
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# SSOT — canonical Plans DB identifiers and Status values.
# ---------------------------------------------------------------------------

# Plans database id (used for API-post-page parent.database_id writes).
PLANS_DB_ID: str = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"

# Plans data-source id (used for API-query-data-source reads; sometimes
# appears in write payloads where the caller conflated the two).
PLANS_DATA_SOURCE_ID: str = "ac53d31b-3068-4039-9ebe-856c12caab32"

# Set of id strings that identify the Plans surface — both are treated as
# "plans write target" for validation purposes.
_PLANS_IDS: frozenset[str] = frozenset({
    PLANS_DB_ID.lower(),
    PLANS_DB_ID.replace("-", "").lower(),
    PLANS_DATA_SOURCE_ID.lower(),
    PLANS_DATA_SOURCE_ID.replace("-", "").lower(),
})

# Canonical Plans Status option names. Exact match required (case-sensitive).
# Renamed 2026-05-03: "Live" → "In Progress", "Draft" → "Not Started" (same
# Notion option IDs, display names changed in the Notion UI).
# Added 2026-05-05: "Deprioritized" for paused/deferred plans.
# Renamed 2026-05-10: "Deprioritized" → "Deferred" (UI rename, same option ID).
CANONICAL_STATUSES: frozenset[str] = frozenset({
    "In Progress",
    "Not Started",
    "Deferred",
    "Waiting",
    "Completed",
    "Retired",
    "Archived",
})

# Known stale duplicate strings → canonical replacement.  Matches are
# reported with a concrete suggestion.  Any other non-canonical value
# still violates, but carries no mapping.
STALE_EQUIVALENTS: dict[str, str] = {
    # Old emoji-prefixed forms.
    "🟢Live": "In Progress",
    "🟡Draft": "Not Started",
    "🔵Completed": "Completed",
    "🟣Retired": "Retired",
    "⚪Archived": "Archived",
    "🟢 Live": "In Progress",
    "🟡 Draft": "Not Started",
    "🔵 Completed": "Completed",
    "🟣 Retired": "Retired",
    "⚪ Archived": "Archived",
    # Old plain-word forms superseded by the 2026-05-03 rename.
    "Live": "In Progress",
    "Draft": "Not Started",
    # 2026-05-10: "Deprioritized" renamed to "Deferred".
    "Deprioritized": "Deferred",
}

# Property names that map to the Plans Status field.  Exact match required —
# Notion property names are case-sensitive.
_STATUS_PROPERTY_NAMES: frozenset[str] = frozenset({"Status"})


@dataclass(frozen=True)
class Violation:
    db_id: str
    property_name: str
    value: str
    suggested: str
    message: str


def _normalize_id(raw: str | None) -> str:
    """Lowercase an id and strip dashes for tolerant matching."""
    if not raw:
        return ""
    return str(raw).strip().lower()


def _is_plans_surface(db_id: str) -> bool:
    norm = _normalize_id(db_id)
    if not norm:
        return False
    # Compare both dashed and un-dashed forms.
    return norm in _PLANS_IDS or norm.replace("-", "") in _PLANS_IDS


def decide(
    db_id: str | None,
    property_name: str | None,
    value: str | None,
) -> Violation | None:
    """Return a Violation when the write is a Plans-DB Status with a
    non-canonical value; else None.

    The check is intentionally narrow: only fires for Plans DB + Status
    property.  Writes to any other DB, or any other property on the Plans
    DB, pass through untouched.
    """
    if not _is_plans_surface(db_id or ""):
        return None
    if (property_name or "") not in _STATUS_PROPERTY_NAMES:
        return None
    value_str = "" if value is None else str(value)
    if value_str in CANONICAL_STATUSES:
        return None

    suggested = STALE_EQUIVALENTS.get(value_str, "")
    canonical_list = sorted(CANONICAL_STATUSES)
    if suggested:
        msg = (
            f"Stale Plans-DB Status value {value_str!r} — this is a "
            f"duplicate option left from migrations. Use {suggested!r} "
            f"(the canonical plain-word option) instead. "
            f"Canonical set: {canonical_list}. "
            f"See .windsurf/rules/notion-plans-taxonomy.md."
        )
    else:
        msg = (
            f"Unknown Plans-DB Status value {value_str!r}. "
            f"Notion silently auto-creates new Select options, so "
            f"writing this would pollute the schema with a new duplicate. "
            f"Canonical set: {canonical_list}. "
            f"See .windsurf/rules/notion-plans-taxonomy.md."
        )
    return Violation(
        db_id=_normalize_id(db_id),
        property_name=property_name or "",
        value=value_str,
        suggested=suggested,
        message=msg,
    )


def check(
    db_id: str | None,
    property_name: str | None,
    value: str | None,
) -> tuple[bool, str | None, str | None]:
    """Tuple alias for callers that prefer ``(blocked, message, suggested)``."""
    v = decide(db_id, property_name, value)
    if v is None:
        return (False, None, None)
    return (True, v.message, v.suggested or None)
