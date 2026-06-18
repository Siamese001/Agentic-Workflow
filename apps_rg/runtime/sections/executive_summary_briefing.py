"""Structured briefing preparation for executive_summary (no silent tail amputation)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.executive_summary_context_limits import (
    resolve_briefing_ranked_selection_max_chars,
)

_SECTION_HEADING_RE = re.compile(r"^(?:#{1,3}\s+|[A-Z][A-Z0-9 /&-]{3,}:)\s*", re.MULTILINE)

_BRIEFING_THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "strategy": (
        "strategy",
        "strategic",
        "mandate",
        "priority",
        "priorities",
        "pressure",
        "business model",
    ),
    "operating_model": (
        "operating model",
        "operating-model",
        "decision rights",
        "governance",
        "cadence",
        "delivery model",
        "operating rhythm",
        "process",
    ),
    "leadership": (
        "leadership",
        "stakeholder",
        "stakeholders",
        "executive",
        "board",
        "organization",
        "org",
        "decision-maker",
        "decision makers",
    ),
    "platform": (
        "platform",
        "architecture",
        "data",
        "cloud",
        "ai",
        "technology",
    ),
    "forward_looking": (
        "forward",
        "future",
        "prospective",
        "roadmap",
        "next 12",
        "next 18",
        "forward-looking",
    ),
    "urgency": (
        "recent",
        "launch",
        "earnings",
        "acquisition",
        "competitive",
        "urgency",
        "pressure",
    ),
}

_BRIEFING_THEME_PRIORITY: tuple[str, ...] = (
    "strategy",
    "operating_model",
    "leadership",
    "platform",
    "forward_looking",
    "urgency",
)

_BRIEFING_THEME_RANK: dict[str, int] = {
    "strategy": 0,
    "operating_model": 0,
    "leadership": 1,
    "platform": 2,
    "forward_looking": 3,
    "urgency": 4,
}


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


def _section_blob(section_id: str, section_body: str) -> str:
    return f"{section_id}\n{section_body}".lower()


def _section_signal_hits(section_body: str, *, section_id: str = "") -> dict[str, int]:
    blob = _section_blob(section_id, section_body)
    hits: dict[str, int] = {}
    for theme, keywords in _BRIEFING_THEME_KEYWORDS.items():
        count = sum(1 for keyword in keywords if keyword in blob)
        if count > 0:
            hits[theme] = count
    return hits


def extract_briefing_signal_packet(
    briefing: str,
    *,
    role_family_key: str | None = None,
) -> dict[str, Any]:
    """Compact thematic packet for downstream briefing-aware graph selection."""

    sections = _split_briefing_sections(briefing)
    section_rows: list[dict[str, Any]] = []
    theme_counts: dict[str, int] = {theme: 0 for theme in _BRIEFING_THEME_PRIORITY}
    for section_id, body in sections:
        hits = _section_signal_hits(body, section_id=section_id)
        themes = [
            theme
            for theme in _BRIEFING_THEME_PRIORITY
            if hits.get(theme, 0) > 0
        ]
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        section_rows.append(
            {
                "section_id": section_id,
                "themes": themes,
                "char_count": len(body),
            }
        )

    dominant_themes = [
        theme
        for theme in sorted(
            theme_counts,
            key=lambda theme: (-theme_counts.get(theme, 0), _BRIEFING_THEME_RANK.get(theme, 99), theme),
        )
        if theme_counts.get(theme, 0) > 0
    ]
    section_rows.sort(
        key=lambda row: (
            min((_BRIEFING_THEME_RANK.get(theme, 99) for theme in row.get("themes") or []), default=99),
            row.get("section_id") or "",
        )
    )
    return {
        "schema": "briefing_signal_packet_v1",
        "role_family_key": str(role_family_key or ""),
        "section_count": len(sections),
        "section_ids": [section_id for section_id, _ in sections],
        "theme_counts": theme_counts,
        "dominant_themes": dominant_themes,
        "section_signals": section_rows,
        "signal_summary": "; ".join(
            f"{theme}={theme_counts.get(theme, 0)}"
            for theme in dominant_themes
        ),
    }


_BRIEFING_SIGNAL_BONUS_WEIGHTS: dict[str, float] = {
    "strategy": 0.40,
    "operating_model": 0.35,
    "leadership": 0.25,
    "platform": 0.20,
    "forward_looking": 0.15,
    "urgency": 0.10,
}


def briefing_signal_bonus(
    packet: dict[str, Any],
    *,
    bundle_blob: str,
    target_blob: str = "",
) -> float:
    """Return a modest score bonus when the briefing packet and bundle align."""

    # Match against the bundle content only; the target briefing already produced
    # the packet, so including it here would self-match every theme and flatten the score.
    blob = bundle_blob.lower()
    theme_counts = dict(packet.get("theme_counts") or {})
    total = 0.0
    for theme, weight in _BRIEFING_SIGNAL_BONUS_WEIGHTS.items():
        if theme_counts.get(theme, 0) <= 0:
            continue
        keywords = _BRIEFING_THEME_KEYWORDS.get(theme, ())
        if not keywords:
            continue
        if any(keyword in blob for keyword in keywords):
            total += min(float(theme_counts.get(theme, 0)), 2.0) * weight
    return min(total, 1.0)


def _rank_section(
    section_id: str,
    *,
    section_body: str = "",
    role_family_key: str | None = None,
) -> tuple[int, int, str]:
    sid = section_id.lower()
    body = str(section_body or "").lower()
    rf = str(role_family_key or "").upper()
    hits = _section_signal_hits(body, section_id=sid)
    if hits:
        theme_rank = min(
            _BRIEFING_THEME_RANK.get(theme, 99)
            for theme in hits
        )
    else:
        theme_rank = 99
    if "INSURANCE_BROKERAGE" in rf and any(k in sid for k in _INSURANCE_BROKERAGE_SECTION_BOOST):
        return (0, 0, sid)
    if any(k in sid for k in ("target", "role", "company", "priority", "must")):
        return (0 if theme_rank >= 99 else theme_rank, 1, sid)
    if any(k in sid for k in ("post_merger", "federated", "integration", "interoperab", "enterprise_architecture")):
        return (min(theme_rank, 1), 1, sid)
    if any(k in sid for k in ("innovation", "ai_engineering", "automation", "pragmatic_process")):
        return (min(theme_rank, 2), 2, sid)
    if any(k in sid for k in ("regulated", "governance", "risk", "compliance", "audit")):
        return (min(theme_rank, 3), 3, sid)
    if any(k in sid for k in ("platform", "agentic", "modern", "delivery")):
        return (min(theme_rank, 4), 4, sid)
    if sid in ("preamble", "body"):
        return (max(theme_rank, 5), 5, sid)
    return (theme_rank if theme_rank < 99 else 6, 6, sid)


def prepare_briefing_for_executive_summary(
    briefing: str,
    *,
    role_family_key: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Select briefing content with an auditable manifest (never silent tail-only drop)."""
    raw = str(briefing or "")
    original_chars = len(raw)
    cap = _max_chars()
    signal_packet = extract_briefing_signal_packet(raw, role_family_key=role_family_key)
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
            "briefing_signal_packet": signal_packet,
        }

    sections = _split_briefing_sections(raw)
    ranked = sorted(
        sections,
        key=lambda pair: (
            _rank_section(pair[0], section_body=pair[1], role_family_key=role_family_key),
            pair[0],
        ),
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
        "briefing_signal_packet": signal_packet,
    }


__all__ = [
    "extract_briefing_signal_packet",
    "briefing_signal_bonus",
    "prepare_briefing_for_executive_summary",
]
