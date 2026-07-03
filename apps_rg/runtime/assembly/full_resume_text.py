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

CANONICAL_RENDERED_RESUME_ORDER: tuple[str, ...] = (
    "candidate_header",
    "headline",
    "executive_summary",
    "competencies",
    "professional_experience",
    "education",
    "certifications",
)

BASE_ROLE_HEADER_KEYS: tuple[str, ...] = (
    "unify",
    "ibm",
    "insurtech",
    "ey",
    "early_career",
)


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


def _locked_json(final_resume: dict[str, Any], invariant_id: str) -> Any:
    inv = final_resume.get("locked_copy_invariants") or {}
    if not isinstance(inv, dict):
        return None
    row = inv.get(invariant_id)
    if not isinstance(row, dict):
        return None
    copied = row.get("copied_text_exact")
    if not isinstance(copied, str) or not copied.strip():
        return None
    try:
        return json.loads(copied)
    except json.JSONDecodeError:
        return None


def base_role_headers_from_final_resume(final_resume: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return role headers copied from base-resume locked invariants."""
    employers = _locked_json(final_resume, "company_names")
    titles = _locked_json(final_resume, "titles")
    locations = _locked_json(final_resume, "locations")
    dates = _locked_json(final_resume, "dates")
    if not all(isinstance(v, list) for v in (employers, titles, locations, dates)):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for idx, role_key in enumerate(BASE_ROLE_HEADER_KEYS):
        if idx >= len(employers) or idx >= len(titles) or idx >= len(locations) or idx >= len(dates):
            continue
        date_row = dates[idx]
        if not isinstance(date_row, dict):
            date_row = {}
        out[role_key] = {
            "employer": employers[idx],
            "title": titles[idx],
            "location": locations[idx],
            "start_date": date_row.get("start_date"),
            "end_date": date_row.get("end_date"),
            "is_current": date_row.get("is_current"),
        }
    return out


def base_role_header_lines_from_final_resume(final_resume: dict[str, Any]) -> dict[str, list[str]]:
    return {
        role_key: exp_header(header)
        for role_key, header in base_role_headers_from_final_resume(final_resume).items()
    }


def rendered_resume_section_order() -> tuple[str, ...]:
    return CANONICAL_RENDERED_RESUME_ORDER


def render_locked(copied: str, *, header_override: dict[str, Any] | None = None) -> list[str]:
    obj = json.loads(copied)
    hdr = header_override or {
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


def _not_generated_lines(section_id: str, reason: str) -> list[str]:
    """Explicit generated-content gap marker for whole-resume gates."""
    return [f"[NOT_GENERATED_BY_RUN: {section_id} - {reason}]", ""]


def _append_generated_role(
    *,
    lines: list[str],
    by_id: dict[str, dict[str, Any]],
    narrative_id: str,
    bullets_id: str,
    header_key: str,
    base_header: dict[str, Any] | None = None,
    missing_label: str,
) -> None:
    narr_snap = (by_id.get(narrative_id) or {}).get("l2_output_snapshot") or {}
    bullet_snap = (by_id.get(bullets_id) or {}).get("l2_output_snapshot") or {}
    hdr = base_header or narr_snap.get(header_key) or bullet_snap.get(header_key) or {}
    if hdr:
        lines.extend(exp_header(hdr))
        narr = str(narr_snap.get("narrative_sentence") or "").strip()
        if narr:
            lines.append(narr)
        bullets = bullets_from_list(bullet_snap.get("bullets") or [])
        lines.extend(bullets)
        if not narr and not bullets:
            lines.extend(
                _not_generated_lines(
                    missing_label,
                    "generated narrative and bullets were not produced in this run",
                )
            )
            return
        lines.append("")
    else:
        lines.extend(_not_generated_lines(missing_label, "missing_generated_role_section"))


def _append_competencies(*, lines: list[str], by_id: dict[str, dict[str, Any]]) -> None:
    comp = (by_id.get("competencies") or {}).get("l2_output_snapshot") or {}
    cats = comp.get("competencies") or []
    display_text = str(comp.get("resume_display_text") or "").strip()
    lines.append(ENGINEERING_PLATFORM_COMPETENCIES_HEADING)
    if cats:
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
    elif display_text:
        lines.append(display_text)
        lines.append("")
    else:
        lines.extend(
            _not_generated_lines(
                "competencies",
                "missing_competencies_or_empty_graph_skills_signal",
            )
        )


def flatten_final_resume_to_text(final_resume: dict[str, Any]) -> str:
    identity = final_resume.get("candidate_identity") or {}
    contact = identity.get("header_contact") or {}
    sections = sorted(
        [s for s in (final_resume.get("sections") or []) if isinstance(s, dict)],
        key=lambda s: int(s.get("assemble_order", 999)),
    )
    by_id = {s["section_id"]: s for s in sections if s.get("section_id")}
    base_headers = base_role_headers_from_final_resume(final_resume)

    lines: list[str] = []
    lines.append(str(identity.get("candidate_name") or "Candidate").strip())
    cl = contact_line(contact)
    if cl:
        lines.append(cl)
    lines.append("")

    snap = (by_id.get("headline") or {}).get("l2_output_snapshot") or {}
    hl = str(snap.get("headline_line") or "").strip()
    lines.append("HEADLINE")
    if hl:
        lines.append(hl)
        lines.append("")
    else:
        lines.extend(_not_generated_lines("headline", "missing_or_empty_headline"))

    exec_snap = (by_id.get("executive_summary") or {}).get("l2_output_snapshot") or {}
    es = str(exec_snap.get("resume_display_text") or "").strip()
    lines.append("EXECUTIVE SUMMARY")
    if es:
        lines.append(es)
        lines.append("")
    else:
        lines.extend(_not_generated_lines("executive_summary", "missing_or_empty_executive_summary"))

    _append_competencies(lines=lines, by_id=by_id)

    lines.append("PROFESSIONAL EXPERIENCE")
    lines.append("")

    un_n = (by_id.get("unify_narrative") or {}).get("l2_output_snapshot") or {}
    un_b = (by_id.get("unify_bullets") or {}).get("l2_output_snapshot") or {}
    uh = base_headers.get("unify") or un_n.get("unify_header") or un_b.get("unify_header") or {}
    if uh:
        lines.extend(exp_header(uh))
        narr = str(un_n.get("narrative_sentence") or "").strip()
        if narr:
            lines.append(narr)
        bullets = bullets_from_list(un_b.get("bullets") or [])
        lines.extend(bullets)
        if not narr and not bullets:
            lines.extend(
                _not_generated_lines(
                    "unify",
                    "unify_bullets and unify_narrative did not produce finalized content",
                )
            )
        else:
            lines.append("")
    else:
        lines.extend(_not_generated_lines("unify_narrative", "missing_unify_section"))

    ibm_n = (by_id.get("ibm_narrative") or {}).get("l2_output_snapshot") or {}
    ibm_b = (by_id.get("ibm_bullets") or {}).get("l2_output_snapshot") or {}
    ih = base_headers.get("ibm") or ibm_n.get("ibm_header") or ibm_b.get("ibm_header") or {}
    if ih:
        lines.extend(exp_header(ih))
        narr = str(ibm_n.get("narrative_sentence") or "").strip()
        if narr:
            lines.append(narr)
        bullets = bullets_from_list(ibm_b.get("bullets") or [])
        lines.extend(bullets)
        if not narr and not bullets:
            lines.extend(
                _not_generated_lines(
                    "ibm",
                    "ibm_bullets and ibm_narrative did not produce finalized content",
                )
            )
        else:
            lines.append("")
    else:
        lines.extend(_not_generated_lines("ibm_narrative", "missing_ibm_section"))

    _append_generated_role(
        lines=lines,
        by_id=by_id,
        narrative_id="insurtech_narrative",
        bullets_id="insurtech_bullets",
        header_key="insurtech_header",
        base_header=base_headers.get("insurtech"),
        missing_label="insurtech",
    )
    _append_generated_role(
        lines=lines,
        by_id=by_id,
        narrative_id="ey_narrative",
        bullets_id="ey_bullets",
        header_key="ey_header",
        base_header=base_headers.get("ey"),
        missing_label="ey",
    )

    for sid in ("early_career",):
        copied = (by_id.get(sid) or {}).get("copied_text_exact")
        if copied:
            lines.extend(render_locked(copied, header_override=base_headers.get("early_career")))
            lines.append("")
        else:
            lines.extend(_not_generated_lines(sid, "missing_locked_copy_section"))

    edu_sec = by_id.get("education") or {}
    if edu_sec.get("copied_text_exact"):
        lines.append("EDUCATION")
        for e in json.loads(edu_sec["copied_text_exact"]):
            if isinstance(e, dict):
                line = format_edu(e)
                if line:
                    lines.append(line)
        lines.append("")
    else:
        lines.extend(_not_generated_lines("education", "missing_locked_education"))

    cert_sec = by_id.get("certifications") or {}
    if cert_sec.get("copied_text_exact"):
        lines.append(CERTIFICATIONS_AND_CREDENTIALS_HEADING)
        for c in json.loads(cert_sec["copied_text_exact"]):
            if isinstance(c, dict):
                line = format_cert(c)
                if line:
                    lines.append(line)
        lines.append("")
    else:
        lines.extend(_not_generated_lines("certifications", "missing_locked_certifications"))

    return "\n".join(lines).rstrip() + "\n"
