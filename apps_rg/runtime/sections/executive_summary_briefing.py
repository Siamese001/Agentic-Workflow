"""Structured briefing preparation for executive_summary (no silent tail amputation)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.executive_summary_context_limits import (
    resolve_briefing_ranked_selection_max_chars,
)

_SECTION_HEADING_RE = re.compile(r"^(?:#{1,3}\s+|[A-Z][A-Z0-9 /&-]{3,}:)\s*", re.MULTILINE)


def _max_chars() -> int:
    return resolve_briefing_ranked_selection_max_chars()


def _split_briefing_sections(briefing: str) -> list[tuple[str, str]]:
    """Return (section_id, body) pairs in document order."""
    raw = str(briefing or "")
    if not raw.strip():
        return [("body", "")]
    lines = raw.splitlines()
    sections: list[tuple[str, str]] = []
    current_id = "preamble"
    buf: list[str] = []
    for line in lines:
        if _SECTION_HEADING_RE.match(line.strip()):
            if buf or current_id == "preamble":
                sections.append((current_id, "\n".join(buf).strip()))
            slug = re.sub(r"[^a-z0-9]+", "_", line.strip().lower())[:48].strip("_") or "section"
            current_id = slug
            buf = [line]
        else:
            buf.append(line)
    sections.append((current_id, "\n".join(buf).strip()))
    return [(sid, body) for sid, body in sections if body]


_INSURANCE_BROKERAGE_SECTION_BOOST = (
    "post_merger",
    "federated",
    "integration",
    "interoperab",
    "enterprise_architecture",
    "innovation",
    "ai_engineering",
    "submission",
    "merger",
    "acquisition",
    "distribution",
)


def _rank_section(section_id: str, *, role_family_key: str | None = None) -> int:
    sid = section_id.lower()
    rf = str(role_family_key or "").upper()
    if "INSURANCE_BROKERAGE" in rf and any(k in sid for k in _INSURANCE_BROKERAGE_SECTION_BOOST):
        return 0
    if any(k in sid for k in ("target", "role", "company", "priority", "must")):
        return 0
    if any(k in sid for k in ("post_merger", "federated", "integration", "interoperab", "enterprise_architecture")):
        return 1
    if any(k in sid for k in ("innovation", "ai_engineering", "automation", "pragmatic_process")):
        return 1
    if any(k in sid for k in ("regulated", "governance", "risk", "compliance", "audit")):
        return 2
    if any(k in sid for k in ("platform", "agentic", "modern", "delivery")):
        return 3
    if sid in ("preamble", "body"):
        return 4
    return 5


def prepare_briefing_for_executive_summary(
    briefing: str,
    *,
    role_family_key: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Select briefing content with an auditable manifest (never silent tail-only drop)."""
    raw = str(briefing or "")
    original_chars = len(raw)
    cap = _max_chars()
    if original_chars <= cap:
        return raw, {
            "briefing_original_chars": original_chars,
            "briefing_included_chars": original_chars,
            "briefing_excluded_chars": 0,
            "truncation_or_selection_reason": "within_budget_no_selection",
            "included_section_ids": ["full_document"],
            "excluded_section_ids": [],
            "selection_policy": "full_include",
            "briefing_max_chars": cap,
        }

    sections = _split_briefing_sections(raw)
    ranked = sorted(
        sections,
        key=lambda pair: (_rank_section(pair[0], role_family_key=role_family_key), pair[0]),
    )
    included_ids: list[str] = []
    excluded_ids: list[str] = []
    parts: list[str] = []
    used = 0
    separator = "\n\n"
    for sid, body in ranked:
        chunk = body if not parts else f"{separator}{body}"
        if used + len(chunk) <= cap or not parts:
            if used + len(chunk) <= cap:
                parts.append(body)
                included_ids.append(sid)
                used += len(chunk)
            else:
                excluded_ids.append(sid)
        else:
            excluded_ids.extend([x[0] for x in ranked if x[0] not in included_ids])
            break
    for sid, _ in sections:
        if sid not in included_ids and sid not in excluded_ids:
            excluded_ids.append(sid)

    selected = separator.join(parts).strip()
    if not selected:
        head = raw[: max(0, cap - 120)].rstrip()
        marker = (
            "\n\n[BRIEFING_SELECTION: no ranked section fit budget; head preserved — "
            "token budget will fail closed if full prompt still exceeds window]\n"
        )
        keep = max(0, cap - len(marker))
        selected = raw[:keep].rstrip() + marker
        included_ids = ["head_fallback"]
        excluded_ids = [s[0] for s in sections if s[0] != "head_fallback"] or ["tail"]

    included_chars = len(selected)
    return selected, {
        "briefing_original_chars": original_chars,
        "briefing_included_chars": included_chars,
        "briefing_excluded_chars": max(0, original_chars - included_chars),
        "truncation_or_selection_reason": "ranked_section_selection",
        "included_section_ids": included_ids,
        "excluded_section_ids": sorted(set(excluded_ids)),
        "selection_policy": "ranked_sections",
        "briefing_max_chars": cap,
    }
