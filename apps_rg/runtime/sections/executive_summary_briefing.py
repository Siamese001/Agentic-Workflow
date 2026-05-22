"""Structured briefing preparation for executive_summary (no silent tail amputation)."""

from __future__ import annotations

import os
import re
from typing import Any

_DEFAULT_MAX_CHARS = 12000
_SECTION_HEADING_RE = re.compile(r"^(?:#{1,3}\s+|[A-Z][A-Z0-9 /&-]{3,}:)\s*", re.MULTILINE)


def _max_chars() -> int:
    cap_s = os.environ.get("APPS_RG_EXEC_SUMMARY_BRIEFING_MAX_CHARS", "").strip()
    if cap_s:
        return max(2048, int(cap_s))
    return _DEFAULT_MAX_CHARS


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


def _rank_section(section_id: str) -> int:
    sid = section_id.lower()
    if any(k in sid for k in ("target", "role", "company", "priority", "must")):
        return 0
    if any(k in sid for k in ("regulated", "governance", "risk", "compliance", "audit")):
        return 1
    if any(k in sid for k in ("platform", "agentic", "modern", "delivery")):
        return 2
    if sid in ("preamble", "body"):
        return 3
    return 4


def prepare_briefing_for_executive_summary(briefing: str) -> tuple[str, dict[str, Any]]:
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

    fail_closed = os.environ.get("APPS_RG_EXEC_SUMMARY_BRIEFING_FAIL_CLOSED", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if fail_closed:
        return raw, {
            "briefing_original_chars": original_chars,
            "briefing_included_chars": 0,
            "briefing_excluded_chars": original_chars,
            "truncation_or_selection_reason": "fail_closed_briefing_exceeds_max_chars",
            "included_section_ids": [],
            "excluded_section_ids": ["full_document"],
            "selection_policy": "fail_closed",
            "briefing_max_chars": cap,
            "fail_closed": True,
        }

    sections = _split_briefing_sections(raw)
    ranked = sorted(sections, key=lambda pair: (_rank_section(pair[0]), pair[0]))
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
            "raise APPS_RG_EXEC_SUMMARY_BRIEFING_MAX_CHARS or enable fail_closed]\n"
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
