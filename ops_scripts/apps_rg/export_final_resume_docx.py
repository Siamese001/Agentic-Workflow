"""Export an assembled final_resume.json (spine aggregation output) to a polished .docx.

The integrated runtime is JSON-only by design (plan apps-rg-docx-output-removal-4650ff);
this operator tool renders the canonical product artifact on demand. It walks
final_resume.json with the SAME accessors the full-resume judge flattener uses
(apps_rg.runtime.assembly.full_resume_text), so the document matches the judged text
exactly — no content is invented or reordered at export time.

Usage:
    python ops_scripts/apps_rg/export_final_resume_docx.py <run_dir_or_final_resume.json> [out.docx]

The legacy ops_scripts/apps_rg/export_to_docx.py consumes the retired pre-spine
generated_resume_<ts>.json shape and is unrelated.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.assembly.full_resume_text import (  # noqa: E402
    CERTIFICATIONS_AND_CREDENTIALS_HEADING,
    ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
    bullets_from_list,
    contact_line,
    exp_header,
    format_cert,
    format_edu,
)

ACCENT = RGBColor(0x1F, 0x3A, 0x5F)


def _resolve_final_resume(arg: str) -> Path:
    p = Path(arg)
    if p.is_file():
        return p
    candidates = sorted(p.rglob("final_resume.json"))
    if not candidates:
        raise FileNotFoundError(f"No final_resume.json under {p}")
    return candidates[-1]


def _heading(doc: Document, text: str) -> None:
    para = doc.add_paragraph()
    run = para.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = ACCENT
    para.paragraph_format.space_before = Pt(10)
    para.paragraph_format.space_after = Pt(3)


def _para(doc: Document, text: str, *, bold: bool = False, italic: bool = False,
          size: int = 10, center: bool = False, space_after: int = 2) -> None:
    para = doc.add_paragraph()
    if center:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    para.paragraph_format.space_after = Pt(space_after)


def _bullets(doc: Document, snap: dict[str, Any]) -> None:
    for line in bullets_from_list(snap.get("bullets") or []):
        _para(doc, line, size=10)


def _role_block(doc: Document, narr_snap: dict[str, Any], bullet_snap: dict[str, Any],
                header_key: str) -> None:
    hdr = narr_snap.get(header_key) or bullet_snap.get(header_key) or {}
    if not hdr:
        return
    header_lines = exp_header(hdr)
    if header_lines:
        _para(doc, header_lines[0], bold=True, size=11, space_after=0)
        if len(header_lines) > 1:
            _para(doc, header_lines[1], italic=True, size=9, space_after=2)
    narrative = str(narr_snap.get("narrative_sentence") or "").strip()
    if narrative:
        _para(doc, narrative, italic=True, size=10)
    _bullets(doc, bullet_snap)


def export(final_resume_path: Path, out_path: Path | None = None) -> Path:
    blob = json.loads(final_resume_path.read_text(encoding="utf-8"))
    identity = blob.get("candidate_identity") or {}
    sections = [s for s in (blob.get("sections") or []) if isinstance(s, dict)]
    by_id = {s.get("section_id"): s for s in sections}

    def snap(sid: str) -> dict[str, Any]:
        sec = by_id.get(sid) or {}
        s = sec.get("l2_output_snapshot")
        return s if isinstance(s, dict) else {}

    doc = Document()
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Pt(36)
        section.left_margin = section.right_margin = Pt(48)

    name = str(identity.get("candidate_name") or "Candidate").strip()
    _para(doc, name, bold=True, size=18, center=True, space_after=0)
    cl = contact_line(identity.get("header_contact") or {})
    if cl:
        _para(doc, cl, size=9, center=True, space_after=4)

    headline = str(snap("headline").get("headline_line") or "").strip()
    if headline:
        _para(doc, headline, bold=True, size=11, center=True, space_after=6)

    exec_text = str(snap("executive_summary").get("resume_display_text") or "").strip()
    if exec_text:
        _heading(doc, "Executive Summary")
        _para(doc, exec_text, size=10, space_after=4)

    _heading(doc, "Professional Experience")
    _role_block(doc, snap("unify_narrative"), snap("unify_bullets"), "unify_header")
    _role_block(doc, snap("ibm_narrative"), snap("ibm_bullets"), "ibm_header")
    _role_block(doc, snap("insurtech_narrative"), snap("insurtech_bullets"), "insurtech_header")
    _role_block(doc, snap("ey_narrative"), snap("ey_bullets"), "ey_header")

    early = (by_id.get("early_career") or {}).get("copied_text_exact")
    if early:
        obj = json.loads(early)
        hdr_lines = exp_header(
            {k: obj.get(k) for k in ("employer", "title", "location", "start_date", "end_date", "is_current")}
        )
        if hdr_lines:
            _para(doc, hdr_lines[0], bold=True, size=11, space_after=0)
            if len(hdr_lines) > 1:
                _para(doc, hdr_lines[1], italic=True, size=9, space_after=2)
        role_narr = str(obj.get("role_narrative") or "").strip()
        if role_narr:
            _para(doc, role_narr, italic=True, size=10)
        for line in bullets_from_list(obj.get("bullets") or []):
            _para(doc, line, size=10)

    comp_cats = snap("competencies").get("competencies") or []
    if comp_cats:
        _heading(doc, ENGINEERING_PLATFORM_COMPETENCIES_HEADING)
        for cat in comp_cats:
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "Capabilities").strip()
            terms = []
            for t in cat.get("terms") or []:
                txt = str(t.get("text") if isinstance(t, dict) else t).strip()
                if txt:
                    terms.append(txt)
            if terms:
                para = doc.add_paragraph()
                run = para.add_run(f"{label}: ")
                run.bold = True
                run.font.size = Pt(10)
                run2 = para.add_run(", ".join(terms))
                run2.font.size = Pt(10)
                para.paragraph_format.space_after = Pt(2)

    edu_raw = (by_id.get("education") or {}).get("copied_text_exact")
    if edu_raw:
        _heading(doc, "Education")
        for entry in json.loads(edu_raw):
            if isinstance(entry, dict):
                line = format_edu(entry)
                if line:
                    _para(doc, line, size=10)

    cert_raw = (by_id.get("certifications") or {}).get("copied_text_exact")
    if cert_raw:
        _heading(doc, CERTIFICATIONS_AND_CREDENTIALS_HEADING)
        for entry in json.loads(cert_raw):
            if isinstance(entry, dict):
                line = format_cert(entry)
                if line:
                    _para(doc, line, size=10)

    if out_path is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = final_resume_path.parent / f"AmitAyer_AIG_VP_AgenticAI_{stamp}.docx"
    doc.save(str(out_path))
    return out_path


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: export_final_resume_docx.py <run_dir_or_final_resume.json> [out.docx]")
        return 2
    final_path = _resolve_final_resume(argv[0])
    out = Path(argv[1]) if len(argv) > 1 else None
    written = export(final_path, out)
    print(f"DOCX_WRITTEN={written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
