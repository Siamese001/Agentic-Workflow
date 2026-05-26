"""Deterministic bullet line-discipline X2 helpers (shared sentence splitting)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

# One resume bullet thought — executive employment lanes.
DEFAULT_BULLET_MAX_CHARS = 320

_IBM_NARRATIVE_BLEED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bthis role (?:positioned|established|demonstrated)\b", re.I),
    re.compile(r"\bcapstone\b", re.I),
    re.compile(r"\bin summary\b", re.I),
    re.compile(r"\bthe role mattered\b", re.I),
)


def check_bullet_no_embedded_newline(bullet_text: str) -> tuple[bool, str, str | None]:
    text = str(bullet_text or "")
    if "\n" in text or "\r" in text:
        return False, "embedded_newline", "bullet must be a single line (no newline characters)"
    return True, "single_line", None


def check_bullet_single_thought(bullet_text: str) -> tuple[bool, int, str | None]:
    text = str(bullet_text or "").strip()
    if not text:
        return False, 0, "empty bullet text"
    sentences = split_sentences(text)
    count = len(sentences)
    if count != 1:
        return False, count, f"expected exactly 1 sentence, found {count}"
    return True, count, None


def check_bullet_no_paragraph_block(
    bullet_text: str,
    *,
    max_chars: int = DEFAULT_BULLET_MAX_CHARS,
) -> tuple[bool, int, str | None]:
    text = str(bullet_text or "").strip()
    length = len(text)
    if length > max_chars:
        return False, length, f"bullet exceeds {max_chars} characters (paragraph block)"
    return True, length, None


def check_ibm_narrative_slot_reservation(bullet_text: str) -> tuple[bool, list[str], str | None]:
    """IBM bullets must not read as the one-sentence narrative capstone."""
    text = str(bullet_text or "").strip()
    hits: list[str] = []
    for pat in _IBM_NARRATIVE_BLEED_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    if len(text.split()) > 55:
        hits.append("word_count>55")
    if hits:
        return False, hits, "bullet consumes narrative capstone slot"
    return True, [], None


def register_bullet_line_discipline_x2_gates(
    add: Any,
    bullets: list[dict[str, Any]],
    *,
    lane_prefix: str,
    section_id: str,
    max_chars: int = DEFAULT_BULLET_MAX_CHARS,
) -> None:
    """Register per-lane line-discipline gates (call after bullet-count gate)."""
    newline_fails: list[str] = []
    single_thought_fails: list[str] = []
    para_fails: list[str] = []
    narr_fails: list[str] = []
    for bullet in bullets:
        if not isinstance(bullet, dict):
            continue
        bid = str(bullet.get("bullet_id") or "?")
        text = str(bullet.get("bullet_text") or "")
        nl_ok, _, _ = check_bullet_no_embedded_newline(text)
        if not nl_ok:
            newline_fails.append(bid)
        st_ok, st_n, _ = check_bullet_single_thought(text)
        if not st_ok:
            single_thought_fails.append(f"{bid}:{st_n}")
        para_ok, ln, _ = check_bullet_no_paragraph_block(text, max_chars=max_chars)
        if not para_ok:
            para_fails.append(f"{bid}:{ln}")
        if section_id == "ibm_bullets":
            narr_ok, hits, _ = check_ibm_narrative_slot_reservation(text)
            if not narr_ok:
                narr_fails.append(f"{bid}:{','.join(hits)}")
    add(
        f"x2_{lane_prefix}_bullet_no_embedded_newline",
        not newline_fails,
        newline_fails or "none",
        "single-line bullets",
        f"Embedded newline in: {', '.join(newline_fails)}" if newline_fails else None,
    )
    add(
        f"x2_{lane_prefix}_bullet_single_thought",
        not single_thought_fails,
        single_thought_fails or "1 sentence each",
        "len(split_sentences(bullet_text)) == 1",
        f"Multi-sentence bullets: {', '.join(single_thought_fails)}" if single_thought_fails else None,
    )
    add(
        f"x2_{lane_prefix}_bullet_no_paragraph_block",
        not para_fails,
        para_fails or f"<={max_chars} chars",
        f"max {max_chars} chars per bullet",
        f"Paragraph blocks: {', '.join(para_fails)}" if para_fails else None,
    )
    if section_id == "ibm_bullets":
        add(
            "x2_ibm_narrative_slot_reservation",
            not narr_fails,
            narr_fails or "none",
            "no capstone/narrative bleed",
            f"Narrative slot bleed: {', '.join(narr_fails)}" if narr_fails else None,
        )


def audit_bullets_line_discipline(
    bullets: list[dict[str, Any]],
    *,
    section_id: str,
    max_chars: int = DEFAULT_BULLET_MAX_CHARS,
) -> dict[str, Any]:
    """Return per-bullet audit rows for receipts/tests."""
    rows: list[dict[str, Any]] = []
    for bullet in bullets:
        if not isinstance(bullet, dict):
            continue
        bid = str(bullet.get("bullet_id") or "")
        text = str(bullet.get("bullet_text") or "")
        nl_ok, _, nl_fail = check_bullet_no_embedded_newline(text)
        st_ok, st_n, st_fail = check_bullet_single_thought(text)
        para_ok, para_n, para_fail = check_bullet_no_paragraph_block(text, max_chars=max_chars)
        narr_ok, narr_hits, narr_fail = (True, [], None)
        if section_id == "ibm_bullets":
            narr_ok, narr_hits, narr_fail = check_ibm_narrative_slot_reservation(text)
        rows.append(
            {
                "bullet_id": bid,
                "pass": nl_ok and st_ok and para_ok and narr_ok,
                "newline_ok": nl_ok,
                "single_thought_ok": st_ok,
                "sentence_count": st_n,
                "paragraph_ok": para_ok,
                "char_count": para_n,
                "narrative_slot_ok": narr_ok,
                "failures": [x for x in (nl_fail, st_fail, para_fail, narr_fail) if x],
                "narrative_hits": narr_hits,
            },
        )
    overall = all(r.get("pass") for r in rows) if rows else True
    return {"section_id": section_id, "pass": overall, "bullets": rows}


__all__ = [
    "DEFAULT_BULLET_MAX_CHARS",
    "register_bullet_line_discipline_x2_gates",
    "audit_bullets_line_discipline",
    "check_bullet_no_embedded_newline",
    "check_bullet_no_paragraph_block",
    "check_bullet_single_thought",
    "check_ibm_narrative_slot_reservation",
]
