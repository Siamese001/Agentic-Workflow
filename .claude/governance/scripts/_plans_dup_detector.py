"""
_plans_dup_detector.py — pure logic for Plans-DB duplicate POST detection.

Imported by both:
  - .claude/governance/scripts/post_agent_plans_dup_audit.py  (advisory hook)
  - ops_scripts/ci/check_notion_plans_no_duplicates.py (fail-closed CI gate)

Pure: no I/O at import. Deterministic. Specific exceptions only.

RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B regression coverage.
Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2c/d).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Plans-DB id strings (mirror of _notion_plans_status_check.py — kept local
# so this module has zero cross-imports).
# ---------------------------------------------------------------------------

PLANS_DB_ID: str = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
PLANS_DATA_SOURCE_ID: str = "ac53d31b-3068-4039-9ebe-856c12caab32"

_PLANS_IDS: frozenset[str] = frozenset({
    PLANS_DB_ID.lower(),
    PLANS_DB_ID.replace("-", "").lower(),
    PLANS_DATA_SOURCE_ID.lower(),
    PLANS_DATA_SOURCE_ID.replace("-", "").lower(),
})


# ---------------------------------------------------------------------------
# Cursor Agent-response invocation parsing
# ---------------------------------------------------------------------------

# Matches <invoke name="API-post-page">...</invoke> (with or without mcpN_ prefix).
_INVOKE_BLOCK_RE = re.compile(
    r'<invoke\s+name="(?:mcp\d+_)?(API-post-page)">(.*?)</invoke>',
    re.DOTALL,
)

# Captures the database_id / data_source_id appearing inside the body.
_DB_ID_RE = re.compile(
    r'["\'](?:database_id|data_source_id)["\']\s*:\s*["\']([0-9a-fA-F\-]+)["\']'
)

# Captures the Slug.title content from the properties payload.
_SLUG_RE = re.compile(
    r'["\']Slug["\']\s*:\s*\{[^}]*?["\']content["\']\s*:\s*["\']([a-z0-9][a-z0-9-]*-[0-9a-f]{6})["\']',
    re.DOTALL,
)


def _is_plans_id(candidate: str) -> bool:
    norm = candidate.replace("-", "").lower()
    return norm in _PLANS_IDS


@dataclass(frozen=True)
class PlansPostInvocation:
    """One Cursor Agent-response invocation that POSTs to the Plans DB."""

    invoke_index: int
    slug: str  # extracted from the payload; "" when not parseable


def extract_plans_post_invocations(response_text: str) -> list[PlansPostInvocation]:
    """Find every Cursor Agent-response API-post-page targeting the Plans DB.

    Returns a list of (invoke_index, slug). Slug may be "" when the payload
    didn't include a parseable Slug.title field.
    """
    if not response_text:
        return []
    out: list[PlansPostInvocation] = []
    for idx, match in enumerate(_INVOKE_BLOCK_RE.finditer(response_text)):
        body = match.group(2)
        candidate_ids = _DB_ID_RE.findall(body)
        if not any(_is_plans_id(cid) for cid in candidate_ids):
            continue
        slug_match = _SLUG_RE.search(body)
        slug = slug_match.group(1) if slug_match else ""
        out.append(PlansPostInvocation(invoke_index=idx, slug=slug))
    return out


# ---------------------------------------------------------------------------
# Duplicate detection over a Plans-cache snapshot
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DuplicateGroup:
    """A slug with multiple active Plans rows."""

    slug: str
    page_ids: tuple[str, ...]
    statuses: tuple[str, ...]


def find_duplicate_groups(
    plans_snapshot: dict[str, list[dict]] | list[dict],
) -> list[DuplicateGroup]:
    """Return every slug with ≥2 active Plans rows.

    Args:
        plans_snapshot: Either:
          - dict mapping slug -> list of row dicts
            (each row dict has at least ``id`` and ``status`` keys), or
          - flat list of row dicts (each with ``slug``, ``id``, ``status``,
            and optional ``in_trash`` / ``archived``). Archived rows are
            EXCLUDED from the duplicate count.

    Returns:
        Sorted list of DuplicateGroup, by slug.
    """
    by_slug: dict[str, list[dict]] = {}
    if isinstance(plans_snapshot, list):
        for row in plans_snapshot:
            if row.get("in_trash") or row.get("archived"):
                continue
            slug = str(row.get("slug") or "")
            if not slug:
                continue
            by_slug.setdefault(slug, []).append(row)
    elif isinstance(plans_snapshot, dict):
        for slug, rows in plans_snapshot.items():
            for row in rows:
                if row.get("in_trash") or row.get("archived"):
                    continue
                by_slug.setdefault(slug, []).append(row)

    groups: list[DuplicateGroup] = []
    for slug, rows in sorted(by_slug.items()):
        if len(rows) < 2:
            continue
        page_ids = tuple(str(r.get("id") or "") for r in rows)
        statuses = tuple(str(r.get("status") or "") for r in rows)
        groups.append(DuplicateGroup(slug=slug, page_ids=page_ids, statuses=statuses))
    return groups


__all__ = [
    "PLANS_DB_ID",
    "PLANS_DATA_SOURCE_ID",
    "PlansPostInvocation",
    "DuplicateGroup",
    "extract_plans_post_invocations",
    "find_duplicate_groups",
]
