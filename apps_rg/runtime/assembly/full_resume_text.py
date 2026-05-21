"""Flatten assembled final_resume.json to plain text for full-resume judges."""
from __future__ import annotations

import json
import re
from typing import Any

from apps_rg.runtime.section_display_labels import (
    CERTIFICATIONS_AND_CREDENTIALS_HEADING,
    ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
)

_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def format_dates(start: str, end: str, is_current: bool) -> str:
    def part(raw: str, *, end_side: bool) -> str:
        s = (raw or "").strip()
        if end_side and (is_current or s.lower() in {"present", "current", ""}):
            return "Present"
        m = re.match(r"^(\d{4})-(\d{2})$", s)
        if m:
            y, mo = int(m.group(1)), int(m.group(2))
            if 1 <= mo <= 12:
                return f"{_MONTHS[mo - 1]} {y}"
        return s or ("Present" if end_side else "")

    sp = part(start, end_side=False)
    ep = part(end, end_side=True)
    return f"{sp} – {ep}"


def contact_line(contact: dict[str, Any]) -> str:
    order = ("phone", "email", "linkedin", "github", "location")
    return " | ".join(str(contact[k]).strip() for k in order if contact.get(k))


def format_edu(entry: dict[str, Any]) -> str:
    degree = str(entry.get("degree") or "").strip()
    inst = str(entry.get("institution") or "").strip()
    honors = str(entry.get("honors") or "").strip()
    year = entry.get("year")
    yr = str(year).strip() if year not in (None, "") else ""
    parts = [p for p in (degree, inst) if p]
    if yr:
        parts.append(yr)
    line = ", ".join(parts)
    if honors:
        line = f"{line} ({honors})"
    return line


def format_cert(entry: dict[str, Any]) -> str:
    name = str(entry.get("name") or "").strip()
    issuer = str(entry.get("issuer") or entry.get("issuing_organization") or "").strip()
    yr = entry.get("date") or entry.get("year")
    yr_s = str(yr).strip() if yr not in (None, "") else ""
    parts = [name] if name else []
    if issuer:
        parts.append(issuer)
    if yr_s:
        parts.append(yr_s)
    return ", ".join(parts)


def exp_header(hdr: dict[str, Any]) -> list[str]:
    employer = str(hdr.get("employer") or "").strip()
    title = str(hdr.get("title") or "").strip()
    location = str(hdr.get("location") or "").strip()
    dates = format_dates(
        str(hdr.get("start_date") or ""),
        str(hdr.get("end_date") or ""),
        bool(hdr.get("is_current")),
    )
    line1 = f"{employer} — {title}" if employer and title else (employer or title)
    line2_bits = [b for b in (location, dates) if b]
    out = [line1] if line1 else []
    if line2_bits:
        out.append(" | ".join(line2_bits))
    return out


def bullets_from_list(bullets: list[Any]) -> list[str]:
    rows: list[str] = []
    for b in bullets or []:
        if not isinstance(b, dict):
            continue
        t = str(b.get("bullet_text") or b.get("text") or "").strip()
        if t:
            rows.append(f"• {t}")
    return rows


def render_locked(copied: str) -> list[str]:
    obj = json.loads(copied)
    hdr = {
        "employer": obj.get("employer"),
        "title": obj.get("title"),
        "location": obj.get("location"),
        "start_date": obj.get("start_date"),
        "end_date": obj.get("end_date"),
        "is_current": obj.get("is_current"),
    }
    block = exp_header(hdr)
    narr = str(obj.get("role_narrative") or "").strip()
    if narr:
        block.append(narr)
    block.extend(bullets_from_list(obj.get("bullets") or []))
    return block


def flatten_final_resume_to_text(final_resume: dict[str, Any]) -> str:
    identity = final_resume.get("candidate_identity") or {}
    contact = identity.get("header_contact") or {}
    sections = sorted(
        [s for s in (final_resume.get("sections") or []) if isinstance(s, dict)],
        key=lambda s: int(s.get("assemble_order", 999)),
    )
    by_id = {s["section_id"]: s for s in sections if s.get("section_id")}

    lines: list[str] = []
    lines.append(str(identity.get("candidate_name") or "Candidate").strip())
    cl = contact_line(contact)
    if cl:
        lines.append(cl)
    lines.append("")

    snap = (by_id.get("headline") or {}).get("l2_output_snapshot") or {}
    hl = str(snap.get("headline_line") or "").strip()
    if hl:
        lines.append(hl)
        lines.append("")

    exec_snap = (by_id.get("executive_summary") or {}).get("l2_output_snapshot") or {}
    es = str(exec_snap.get("resume_display_text") or "").strip()
    if es:
        lines.append("EXECUTIVE SUMMARY")
        lines.append(es)
        lines.append("")

    lines.append("PROFESSIONAL EXPERIENCE")
    lines.append("")

    un_n = (by_id.get("unify_narrative") or {}).get("l2_output_snapshot") or {}
    un_b = (by_id.get("unify_bullets") or {}).get("l2_output_snapshot") or {}
    uh = un_n.get("unify_header") or un_b.get("unify_header") or {}
    if uh:
        lines.extend(exp_header(uh))
        narr = str(un_n.get("narrative_sentence") or "").strip()
        if narr:
            lines.append(narr)
        lines.extend(bullets_from_list(un_b.get("bullets") or []))
        lines.append("")

    ibm_n = (by_id.get("ibm_narrative") or {}).get("l2_output_snapshot") or {}
    ibm_b = (by_id.get("ibm_bullets") or {}).get("l2_output_snapshot") or {}
    ih = ibm_n.get("ibm_header") or ibm_b.get("ibm_header") or {}
    if ih:
        lines.extend(exp_header(ih))
        narr = str(ibm_n.get("narrative_sentence") or "").strip()
        if narr:
            lines.append(narr)
        lines.extend(bullets_from_list(ibm_b.get("bullets") or []))
        lines.append("")

    for sid in ("insurtech", "ey", "early_career"):
        copied = (by_id.get(sid) or {}).get("copied_text_exact")
        if copied:
            lines.extend(render_locked(copied))
            lines.append("")

    comp = (by_id.get("competencies") or {}).get("l2_output_snapshot") or {}
    cats = comp.get("competencies") or []
    if cats:
        lines.append(ENGINEERING_PLATFORM_COMPETENCIES_HEADING)
        for cat in cats:
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "Capabilities").strip()
            terms: list[str] = []
            for t in cat.get("terms") or []:
                if isinstance(t, dict):
                    txt = str(t.get("text") or "").strip()
                else:
                    txt = str(t).strip()
                if txt:
                    terms.append(txt)
            if terms:
                lines.append(f"{label}: {', '.join(terms)}")
        lines.append("")

    edu_sec = by_id.get("education") or {}
    if edu_sec.get("copied_text_exact"):
        lines.append("EDUCATION")
        for e in json.loads(edu_sec["copied_text_exact"]):
            if isinstance(e, dict):
                line = format_edu(e)
                if line:
                    lines.append(line)
        lines.append("")

    cert_sec = by_id.get("certifications") or {}
    if cert_sec.get("copied_text_exact"):
        lines.append(CERTIFICATIONS_AND_CREDENTIALS_HEADING)
        for c in json.loads(cert_sec["copied_text_exact"]):
            if isinstance(c, dict):
                line = format_cert(c)
                if line:
                    lines.append(line)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
