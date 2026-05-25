"""Deterministic targeting-only JD/briefing cap for executive_summary capsule mode.

Compacts jd_requirements block prose only. Never touches proof substrate, schema, or evidence law.
"""
from __future__ import annotations

import os
import re
from typing import Any

from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate

SECTION_ID = "executive_summary"
TARGETING_CAP_STRATEGY = "executive_summary_capsule_mode_targeting_cap_v1"
_CAP_NOTICE = "\n[# APPS_RG_EXEC_SUMMARY_TARGETING_CAP targeting-only; not proof]\n"

_JD_TAG = "jd_requirements"

_BRIEFING_SECTION_PRIORITY: tuple[str, ...] = (
    "STRATEGIC MANDATE",
    "POST-MERGER",
    "POST MERGER",
    "FEDERATED",
    "ENTERPRISE ARCHITECTURE",
    "M&A INTEGRATION",
    "INNOVATION",
    "AI ENGINEERING",
    "INNOVATION & AI AGENDA",
    "ENTERPRISE ARCHITECTURE & DATA",
    "LEADERSHIP & STAKEHOLDERS",
    "M&A INTEGRATION PLAYBOOK",
    "SEGMENTS",
    "MARKET & CULTURE",
    "RESUME / EXECUTIVE SUMMARY POSITIONING",
)

_BRIEFING_SLUG_BOOST: tuple[str, ...] = (
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
)

_JD_LINE_PRIORITY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.I)
    for p in (
        r"^Senior Vice President",
        r"^Requisition:",
        r"^Pay Range:",
        r"^Skills & Experience",
        r"^How You Will Contribute",
        r"^\s*-\s+",
        r"enterprise architecture",
        r"innovation",
        r"\bAI\b",
        r"data platform",
        r"interoperab",
        r"15\+ years",
        r"must|required|responsible",
    )
)

_TARGETING_CONTENT_PRESERVED: tuple[str, ...] = (
    "target_company",
    "target_role",
    "must_have_role_themes",
    "role_specific_responsibilities",
    "constraints",
    "jd_is_targeting_only_rule",
)


def targeting_cap_enabled(runtime_payload: dict[str, Any]) -> bool:
    if not runtime_payload.get("evidence_capsule_active"):
        return False
    if runtime_payload.get("targeting_cap_disabled") is True:
        return False
    env = os.environ.get("APPS_RG_EXEC_SUMMARY_TARGETING_CAP", "1").strip().lower()
    return env not in ("0", "false", "no")


def _resolve_max_chars(kind: str, *, gap_tokens: int = 0) -> int:
    env_key = f"APPS_RG_EXEC_SUMMARY_TARGETING_CAP_{kind.upper()}_CHARS"
    raw = os.environ.get(env_key, "").strip()
    if raw:
        return max(512, int(raw))
    defaults = {"JD": 2000, "BRIEFING": 2600}
    base = defaults.get(kind.upper(), 2000)
    if gap_tokens > 0:
        # Rough chars to shed from targeting region only (~3 chars/token).
        shed = max(0, int(gap_tokens * 3.2))
        if kind.upper() == "BRIEFING":
            return max(768, base - int(shed * 0.65))
        return max(512, base - int(shed * 0.35))
    return base


def _normalize_line_key(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def _score_jd_line(line: str) -> int:
    s = line.strip()
    if not s:
        return -10
    score = len(s) // 80
    for pat in _JD_LINE_PRIORITY_PATTERNS:
        if pat.search(s):
            score += 12
    if s.startswith("- "):
        score += 8
    if "proven track record" in s.lower() and "skills" not in s.lower():
        score -= 3
    if s.lower().startswith("built on meritocracy"):
        score -= 5
    return score


def compress_targeting_jd_body(jd_text: str, max_chars: int) -> str:
    """Dedupe and keep high-signal JD lines deterministically."""
    lines = jd_text.replace("\r\n", "\n").split("\n")
    seen: set[str] = set()
    ranked: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        key = _normalize_line_key(line)
        if not key or key in seen:
            continue
        seen.add(key)
        ranked.append((_score_jd_line(line), idx, line.rstrip()))
    ranked.sort(key=lambda t: (-t[0], t[1]))
    out: list[str] = []
    used = 0
    for _score, _idx, line in ranked:
        add = line if not out else "\n" + line
        if used + len(add) > max_chars:
            continue
        out.append(line)
        used += len(add)
    if not out:
        body = jd_text[:max_chars]
    else:
        body = "\n".join(out)
        if len(body) > max_chars:
            body = body[:max_chars]
    if _CAP_NOTICE.strip() not in body:
        body = body.rstrip() + _CAP_NOTICE
    return body


def _parse_briefing_sections(briefing: str) -> tuple[list[str], dict[str, list[str]]]:
    """Return (preamble lines, section_id -> body lines). Supports === and markdown ## headings."""
    from apps_rg.runtime.sections.executive_summary_briefing import _split_briefing_sections

    preamble: list[str] = []
    sections: dict[str, list[str]] = {}
    for section_id, body in _split_briefing_sections(briefing):
        lines = [ln.rstrip() for ln in body.split("\n") if ln.strip()]
        if not lines:
            continue
        if section_id == "preamble":
            preamble.extend(lines)
            continue
        title = section_id
        if lines[0].lstrip().startswith("#"):
            title = re.sub(r"^#+\s*", "", lines[0]).strip() or section_id
        sections[title] = lines
    if not sections and preamble:
        sections["preamble"] = preamble
        preamble = []
    return preamble, sections


def _score_briefing_section_title(title: str) -> int:
    t = title.lower()
    for idx, pat in enumerate(_BRIEFING_SECTION_PRIORITY):
        if pat.lower() in t:
            return idx
    if any(k in t for k in _BRIEFING_SLUG_BOOST):
        return 0
    if any(k in t for k in ("cultural", "narrative", "performance_mapping")):
        return len(_BRIEFING_SECTION_PRIORITY) + 2
    return len(_BRIEFING_SECTION_PRIORITY) + 1


def compress_targeting_briefing_body(briefing: str, max_chars: int) -> str:
    """Section-priority briefing cap; keeps high-signal sections (markdown ## or === headers)."""
    preamble, sections = _parse_briefing_sections(briefing)
    out: list[str] = []
    used = 0

    def _append(chunk: str) -> bool:
        nonlocal used
        if not chunk:
            return True
        add = chunk if not out else "\n" + chunk
        if used + len(add) > max_chars:
            return False
        out.append(chunk)
        used += len(add)
        return True

    ordered_titles = sorted(
        sections.keys(),
        key=lambda t: (_score_briefing_section_title(t), t.lower()),
    )

    for title in ordered_titles:
        bullets = sections.get(title) or []
        if not bullets:
            continue
        header_line = bullets[0]
        if header_line.lstrip().startswith("#"):
            header = header_line.strip()
        else:
            header = f"=== {title} ==="
        if not _append(header):
            break
        seen_b: set[str] = set()
        start_idx = 1 if header_line.lstrip().startswith("#") else 0
        for b in bullets[start_idx:]:
            if b.strip().startswith("- "):
                bk = _normalize_line_key(b)
                if bk in seen_b:
                    continue
                seen_b.add(bk)
            if not _append(b):
                break

    if not out and preamble:
        for pl in preamble[:2]:
            if not _append(pl):
                break

    if not out:
        body = briefing[:max_chars]
    else:
        body = "\n".join(out)
        if len(body) > max_chars:
            body = body[:max_chars]
    if _CAP_NOTICE.strip() not in body:
        body = body.rstrip() + _CAP_NOTICE
    return body


def _extract_tagged_block(content: str, tag: str) -> tuple[int, int, str] | None:
    start = content.find(f"<{tag}")
    if start < 0:
        return None
    open_end = content.find(">", start)
    if open_end < 0:
        return None
    close = content.find(f"</{tag}>", open_end)
    if close < 0:
        return None
    inner_start = open_end + 1
    return start, close + len(f"</{tag}>"), content[inner_start:close]


def _replace_tagged_inner(content: str, tag: str, new_inner: str) -> tuple[str, bool]:
    span = _extract_tagged_block(content, tag)
    if span is None:
        return content, False
    start, end, _old = span
    open_end = content.find(">", start)
    close = content.find(f"</{tag}>", open_end)
    return content[: open_end + 1] + "\n" + new_inner.strip() + "\n" + content[close:], True


def _field_stop_markers() -> dict[str, tuple[str, ...]]:
    return {
        "JD_TEXT (targeting only": ("BRIEFING (targeting only",),
        "BRIEFING (targeting only": (
            "Use TARGET_TITLE and TARGET_COMPANY",
            "Do not mirror JD",
            "SelectedRoleFactSet mode:",
            "Every substantive claim must trace",
        ),
    }


def _extract_multiline_field(
    inner: str, prefix: str
) -> tuple[str, str, int, int] | None:
    """Return (label_head, body, start, end_exclusive) for multiline targeting fields."""
    pos = inner.find(prefix)
    if pos < 0:
        return None
    label_end = inner.find("): ", pos)
    if label_end < 0:
        return None
    body_start = label_end + 3
    stops = _field_stop_markers().get(prefix, ())
    body_end = len(inner)
    for marker in stops:
        mpos = inner.find(marker, body_start)
        if mpos >= 0:
            body_end = min(body_end, mpos)
    head = inner[pos : label_end + 3]
    body = inner[body_start:body_end].strip("\n")
    return head, body, pos, body_end


def _replace_multiline_field(
    inner: str, prefix: str, new_body: str
) -> tuple[str, bool]:
    parsed = _extract_multiline_field(inner, prefix)
    if parsed is None:
        return inner, False
    head, _old, start, end = parsed
    replacement = f"{head}{new_body.strip()}\n"
    return inner[:start] + replacement + inner[end:], True


def cap_jd_requirements_inner(
    inner: str,
    *,
    max_jd_chars: int,
    max_briefing_chars: int,
) -> tuple[str, list[dict[str, Any]]]:
    components: list[dict[str, Any]] = []
    out = inner

    jd_parsed = _extract_multiline_field(out, "JD_TEXT (targeting only")
    if jd_parsed and jd_parsed[1]:
        _head, jd_body, _pos, _end = jd_parsed
        before = estimate_tokens_approximate(jd_body)
        new_jd = compress_targeting_jd_body(jd_body, max_jd_chars)
        if new_jd != jd_body:
            out, did = _replace_multiline_field(out, "JD_TEXT (targeting only", new_jd)
            if did:
                after = estimate_tokens_approximate(new_jd)
                components.append(
                    {
                        "component": "jd",
                        "tokens_before": before,
                        "tokens_after": after,
                        "reason": "targeting_only_budget_cap",
                    }
                )

    br_parsed = _extract_multiline_field(out, "BRIEFING (targeting only")
    if br_parsed and br_parsed[1]:
        _head, br_body, _pos, _end = br_parsed
        before = estimate_tokens_approximate(br_body)
        new_br = compress_targeting_briefing_body(br_body, max_briefing_chars)
        if new_br != br_body:
            out, did = _replace_multiline_field(out, "BRIEFING (targeting only", new_br)
            if did:
                after = estimate_tokens_approximate(new_br)
                components.append(
                    {
                        "component": "manual_briefing",
                        "tokens_before": before,
                        "tokens_after": after,
                        "reason": "targeting_only_budget_cap",
                    }
                )

    return out, components


def estimate_targeting_region_tokens(content: str) -> int:
    span = _extract_tagged_block(content, _JD_TAG)
    if span is None:
        return 0
    return estimate_tokens_approximate(span[2])


def apply_executive_summary_targeting_cap(
    content: str,
    *,
    runtime_payload: dict[str, Any],
    available_input_tokens: int,
) -> tuple[str, dict[str, Any]]:
    """Cap jd_requirements targeting prose when evidence capsule mode is active."""
    meta: dict[str, Any] = {
        "targeting_cap_applied": False,
        "targeting_cap_strategy": TARGETING_CAP_STRATEGY,
        "targeting_tokens_before_cap": 0,
        "targeting_tokens_after_cap": 0,
        "targeting_cap_reason": None,
        "targeting_components_capped": [],
        "targeting_content_preserved": list(_TARGETING_CONTENT_PRESERVED),
        "protected_components_preserved": [],
    }
    if not targeting_cap_enabled(runtime_payload):
        meta["targeting_cap_reason"] = "not_capsule_mode_or_disabled"
        return content, meta

    if runtime_payload.get("targeting_context_frozen") is True:
        meta["targeting_cap_reason"] = "targeting_context_frozen_author_judge_parity"
        meta["targeting_tokens_after_cap"] = estimate_targeting_region_tokens(content)
        return content, meta

    span = _extract_tagged_block(content, _JD_TAG)
    if span is None:
        meta["targeting_cap_reason"] = "jd_requirements_block_missing"
        return content, meta

    before_targeting = estimate_targeting_region_tokens(content)
    meta["targeting_tokens_before_cap"] = before_targeting
    prompt_tokens = estimate_tokens_approximate(content)
    gap = max(0, prompt_tokens - available_input_tokens)

    max_jd = _resolve_max_chars("JD", gap_tokens=gap)
    max_brief = _resolve_max_chars("BRIEFING", gap_tokens=gap)

    inner_new, components = cap_jd_requirements_inner(
        span[2],
        max_jd_chars=max_jd,
        max_briefing_chars=max_brief,
    )
    if not components:
        meta["targeting_cap_reason"] = "already_within_targeting_budget"
        meta["targeting_tokens_after_cap"] = before_targeting
        return content, meta

    new_content, did = _replace_tagged_inner(content, _JD_TAG, inner_new)
    if not did:
        meta["targeting_cap_reason"] = "replace_failed"
        return content, meta

    after_targeting = estimate_targeting_region_tokens(new_content)
    meta.update(
        {
            "targeting_cap_applied": True,
            "targeting_tokens_after_cap": after_targeting,
            "targeting_cap_reason": "targeting_only_budget_cap",
            "targeting_components_capped": components,
        }
    )
    return new_content, meta


__all__ = [
    "TARGETING_CAP_STRATEGY",
    "apply_executive_summary_targeting_cap",
    "compress_targeting_briefing_body",
    "compress_targeting_jd_body",
    "estimate_targeting_region_tokens",
    "targeting_cap_enabled",
]
