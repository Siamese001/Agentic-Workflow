"""Template-free JSON → DOCX export for apps_rg (post-L2 resume payload).

Handles common shapes: legacy ops_scripts JSON, rg_output_schema-ish ``sections``,
and arbitrary dicts (JSON snapshot fallback).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Pt


def _is_provider_stub_payload(data: dict[str, Any]) -> bool:
    """True for LLM stub envelopes and other non-resume dicts we should not json-line-dump."""
    if data.get("stub_response") is True:
        return True
    resume_hint_keys = (
        "sections",
        "experience",
        "contact_info",
        "candidate_name",
        "name",
        "headline",
        "tagline",
        "summary",
        "executive_summary",
        "skills",
        "education",
    )
    if any(k in data for k in resume_hint_keys):
        return False
    # Small opaque dicts (e.g. {hash, note, error}) — treat as metadata-only
    if len(data) <= 6 and not any(isinstance(v, (list, dict)) for v in data.values()):
        return True
    return False


def _render_stub_or_metadata_body(
    doc: Document,
    data: dict[str, Any],
    *,
    target_role: str,
    target_company: str,
    title_line: str,
) -> None:
    """Readable export when there is no structured resume (stub provider, errors, receipts)."""
    _add_heading(doc, title_line)
    if target_company.strip():
        _add_para(doc, f"Target organization: {target_company.strip()}")
    if target_role.strip():
        _add_para(doc, f"Target role: {target_role.strip()}")
    doc.add_paragraph()

    _add_h2(doc, "GENERATION STATUS")
    if data.get("stub_response") is True:
        _add_para(
            doc,
            "This run completed with a provider stub. No LLM-authored résumé sections "
            "were produced; attach a live model profile to generate full content.",
        )
    note = data.get("note")
    if note:
        _add_para(doc, str(note))
    err = data.get("error")
    if err:
        _add_para(doc, f"Error: {err}", bold=True)
    h = data.get("hash")
    if h:
        _add_para(doc, f"Content fingerprint: {h}")

    # Any remaining primitive keys (excluding those already shown)
    shown = {"stub_response", "note", "error", "hash"}
    extras = [
        (k, v)
        for k, v in sorted(data.items())
        if k not in shown and not isinstance(v, (dict, list))
    ]
    if extras:
        doc.add_paragraph()
        _add_h2(doc, "ADDITIONAL FIELDS")
        for k, v in extras:
            _add_para(doc, f"{k}: {v}")


def _add_heading(doc: Document, text: str) -> None:
    p = doc.add_heading(text, level=1)
    for r in p.runs:
        r.font.size = Pt(14)


def _add_h2(doc: Document, text: str) -> None:
    p = doc.add_heading(text, level=2)
    for r in p.runs:
        r.font.size = Pt(11)


def _add_para(doc: Document, text: str, *, bold: bool = False) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(10)


def _normalize_for_render(
    data: dict[str, Any],
    *,
    fallback_name: str,
    fallback_role: str,
    fallback_company: str,
) -> dict[str, Any]:
    if "sections" in data and isinstance(data["sections"], dict):
        sec = data["sections"]
        summary = sec.get("summary") or {}
        summary_text = ""
        if isinstance(summary, dict):
            summary_text = str(summary.get("text", "") or "")
        exp = sec.get("experience") or []
        skills = sec.get("skills") or []
        edu = sec.get("education") or []
        return {
            "name": str(data.get("candidate_name") or fallback_name or "Candidate"),
            "tagline": str(data.get("target_role") or fallback_role or ""),
            "company_line": str(data.get("target_company") or fallback_company or ""),
            "executive_summary": summary_text,
            "experience": exp if isinstance(exp, list) else [],
            "skills": skills if isinstance(skills, list) else [],
            "education": edu if isinstance(edu, list) else [],
            "raw_fallback": False,
        }

    ci = data.get("contact_info") if isinstance(data.get("contact_info"), dict) else {}
    name = str(ci.get("name") or data.get("name") or data.get("candidate_name") or fallback_name or "Candidate")
    headline = str(data.get("headline") or data.get("tagline") or fallback_role or "")
    summary = str(data.get("summary") or data.get("executive_summary") or "")
    if isinstance(data.get("executive_summary"), dict):
        summary = str(data["executive_summary"].get("content", summary))
    contact_bits = [
        str(ci.get("phone") or ""),
        str(ci.get("email") or ""),
        str(ci.get("linkedin") or ""),
    ]
    contact = " | ".join(b for b in contact_bits if b)
    return {
        "name": name,
        "tagline": headline,
        "company_line": contact,
        "executive_summary": summary,
        "experience": data.get("experience") or [],
        "skills": data.get("skills") or [],
        "education": data.get("education") or [],
        "raw_fallback": False,
    }


def render_resume_dict_to_docx(
    data: dict[str, Any],
    output_path: Path,
    *,
    target_role: str = "",
    target_company: str = "",
) -> None:
    """Write ``data`` to ``output_path`` as a .docx (creates parent dirs)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if _is_provider_stub_payload(data):
        doc = Document()
        if target_company.strip():
            title_line = f"Résumé export — {target_company.strip()}"
        elif target_role.strip():
            title_line = f"Résumé export — {target_role.strip()}"
        else:
            title_line = "Résumé export (stub)"
        _render_stub_or_metadata_body(
            doc,
            data,
            target_role=target_role,
            target_company=target_company,
            title_line=title_line,
        )
        doc.save(output_path)
        return

    norm = _normalize_for_render(
        data,
        fallback_name=target_role and f"Candidate — {target_role}" or "Resume export",
        fallback_role=target_role,
        fallback_company=target_company,
    )
    if not any(
        [
            norm.get("executive_summary"),
            norm.get("experience"),
            norm.get("skills"),
            norm.get("education"),
            norm.get("tagline"),
        ]
    ):
        norm["raw_fallback"] = True

    doc = Document()

    _add_heading(doc, str(norm["name"]))
    if norm.get("tagline"):
        _add_para(doc, str(norm["tagline"]))
    if norm.get("company_line"):
        _add_para(doc, str(norm["company_line"]))
    doc.add_paragraph()

    if norm.get("raw_fallback"):
        _add_h2(doc, "GENERATED CONTENT (JSON)")
        for line in json.dumps(data, ensure_ascii=False, indent=2).splitlines():
            _add_para(doc, line)
        doc.save(output_path)
        return

    if norm.get("executive_summary"):
        _add_h2(doc, "EXECUTIVE SUMMARY")
        _add_para(doc, str(norm["executive_summary"]))
        doc.add_paragraph()

    exp = norm.get("experience") or []
    if isinstance(exp, list) and exp:
        _add_h2(doc, "PROFESSIONAL EXPERIENCE")
        for role in exp:
            if not isinstance(role, dict):
                _add_para(doc, str(role))
                continue
            company = str(role.get("company", ""))
            title = str(role.get("title") or role.get("role", ""))
            dates = str(role.get("dates", ""))
            loc = str(role.get("location", ""))
            header = " | ".join(p for p in [company, loc] if p)
            if header:
                _add_para(doc, header, bold=True)
            line = " | ".join(p for p in [title, dates] if p)
            if line:
                _add_para(doc, line)
            bullets = role.get("bullets") or role.get("achievements") or []
            if isinstance(bullets, list):
                for b in bullets:
                    if isinstance(b, dict):
                        txt = str(b.get("description") or b.get("text") or "")
                    else:
                        txt = str(b)
                    if txt:
                        p = doc.add_paragraph(style="List Bullet")
                        r = p.add_run(txt)
                        r.font.size = Pt(10)
            doc.add_paragraph()

    skills = norm.get("skills") or []
    if isinstance(skills, list) and skills:
        _add_h2(doc, "SKILLS")
        parts: list[str] = []
        for s in skills:
            if isinstance(s, dict):
                parts.append(str(s.get("label") or s.get("name") or s))
            else:
                parts.append(str(s))
        _add_para(doc, ", ".join(parts))

    edu = norm.get("education") or []
    if isinstance(edu, list) and edu:
        _add_h2(doc, "EDUCATION")
        for e in edu:
            if isinstance(e, dict):
                line = ", ".join(
                    str(p)
                    for p in [
                        e.get("degree", ""),
                        e.get("institution", ""),
                        e.get("year", e.get("graduation_year", "")),
                    ]
                    if p
                )
                _add_para(doc, line or json.dumps(e, ensure_ascii=False))
            else:
                _add_para(doc, str(e))

    doc.save(output_path)


__all__ = ["render_resume_dict_to_docx"]
