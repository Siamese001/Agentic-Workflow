"""json_resume_docx — stub/minimal payloads render as readable receipts, not JSON dumps."""
from __future__ import annotations

from pathlib import Path

from docx import Document

from apps_rg.runtime.render.json_resume_docx import render_resume_dict_to_docx
from apps_rg.runtime.section_display_labels import (
    CERTIFICATIONS_AND_CREDENTIALS_HEADING,
    ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
)


def _docx_plaintext(path: Path) -> str:
    d = Document(str(path))
    return "\n".join(p.text for p in d.paragraphs if p.text.strip())


def test_stub_payload_docx_is_readable_receipt(tmp_path: Path) -> None:
    stub = {
        "stub_response": True,
        "hash": "dfc6e0fdeaf4521c",
        "note": "Provider stub response for profile apps_rg_envelope_stub",
    }
    out = tmp_path / "stub_resume.docx"
    render_resume_dict_to_docx(
        stub,
        out,
        target_role="Senior Vice President, IT Strategy & Innovation",
        target_company="Brown & Brown",
    )
    assert out.is_file()
    text = _docx_plaintext(out)
    assert "GENERATED CONTENT (JSON)" not in text
    assert "GENERATION STATUS" in text
    assert "provider stub" in text.lower()
    assert "Brown & Brown" in text
    assert "Senior Vice President" in text
    assert "Provider stub response" in text
    assert "dfc6e0fdeaf4521c" in text


def test_rg_output_sections_docx_renders_headline_contact_skills_certs_narrative(tmp_path: Path) -> None:
    summary = (
        "Executive leader delivering agentic AI platforms, retrieval systems, and governed "
        "runtime controls for regulated enterprises with measurable outcomes today."
    )
    bullet = (
        "Delivered measurable platform outcomes including reliability, cost reductions, "
        "and revenue-facing modernization aligned to enterprise controls."
    )
    payload = {
        "candidate_name": "Jane Doe",
        "headline_line": "SVP Engineering | AI platforms and governed delivery",
        "target_role": "Senior Vice President",
        "target_company": "Acme Corp",
        "contact_info": {
            "phone": "+1-555-0100",
            "email": "jane@example.com",
            "linkedin": "https://linkedin.com/in/janedoe",
            "github": "https://github.com/janedoe",
        },
        "sections": {
            "summary": {"text": summary, "word_count": 22},
            "experience": [
                {
                    "title": "VP Engineering",
                    "company": "Example Co",
                    "location": "Remote",
                    "dates": "Jan 2020 – Present",
                    "role_narrative": (
                        "Led platform modernization with strong governance and measurable "
                        "customer outcomes across enterprise accounts."
                    ),
                    "bullets": [
                        {"text": bullet},
                        {"text": bullet},
                        {"text": bullet},
                    ],
                },
            ],
            "skills": {"categories": [{"name": "Platforms", "items": ["GraphRAG", "Policy gates"]}]},
            "education": [{"degree": "MS Example", "institution": "State U", "year": "2010"}],
            "certifications": [{"name": "Certified Example", "issuer": "Board", "date": "2024"}],
        },
    }
    out = tmp_path / "rg_sections.docx"
    render_resume_dict_to_docx(payload, out)
    assert out.is_file()
    text = _docx_plaintext(out)
    assert "SVP Engineering | AI platforms" in text
    assert "jane@example.com" in text
    assert "linkedin.com/in/janedoe" in text
    assert "Tailored for:" in text
    assert "Acme Corp" in text
    # Section order matches base resume / rg_output ``sections``: competencies before education before certs
    assert text.index(ENGINEERING_PLATFORM_COMPETENCIES_HEADING) < text.index("EDUCATION")
    assert text.index("EDUCATION") < text.index(CERTIFICATIONS_AND_CREDENTIALS_HEADING)
    assert "Platforms" in text
    assert "GraphRAG" in text
    assert "Policy gates" in text
    assert CERTIFICATIONS_AND_CREDENTIALS_HEADING in text
    assert "Certified Example" in text
    assert "Led platform modernization" in text


def test_sections_docx_uses_header_name_and_contact_line_includes_location(tmp_path: Path) -> None:
    payload = {
        "header": {"name": "Pat HeaderName", "email": "pat@example.com"},
        "headline_line": "Engineer",
        "contact_info": {"phone": "+1-111", "location": "Remote, USA"},
        "sections": {
            "summary": {"text": "Summary text for docx path minimum length ten.", "word_count": 10},
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Co",
                    "location": "On-site",
                    "dates": "Jan 2020 – Present",
                    "bullets": [{"text": "a" * 25}, {"text": "b" * 25}, {"text": "c" * 25}],
                }
            ],
            "skills": {"categories": [{"name": "X", "items": ["Y"]}]},
            "education": [],
            "certifications": [],
        },
    }
    out = tmp_path / "hdr.docx"
    render_resume_dict_to_docx(payload, out)
    text = _docx_plaintext(out)
    assert "Pat HeaderName" in text
    assert "+1-111 | pat@example.com | Remote, USA" in text.replace("\n", " ")

def test_education_renders_honors_in_single_paragraph(tmp_path: Path) -> None:
    payload = {
        "candidate_name": "Test User",
        "headline_line": "Engineer",
        "sections": {
            "summary": {"text": "Summary text for docx path minimum length ten.", "word_count": 10},
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Co",
                    "location": "Remote",
                    "dates": "Jan 2020 – Present",
                    "bullets": [{"text": "a" * 25}, {"text": "b" * 25}, {"text": "c" * 25}],
                }
            ],
            "skills": {"categories": [{"name": "X", "items": ["Y"]}]},
            "education": [
                {
                    "degree": "Master of Science in Biostatistics",
                    "institution": "Columbia University",
                    "honors": "Graduated with Distinction",
                },
                {
                    "degree": "Bachelor of Arts in Biology",
                    "institution": "Brown University",
                    "honors": "Graduated Cum Laude",
                },
            ],
            "certifications": [],
        },
    }
    out = tmp_path / "edu.docx"
    render_resume_dict_to_docx(payload, out)
    text = _docx_plaintext(out)
    assert "EDUCATION" in text
    assert (
        "Master of Science in Biostatistics, Columbia University (Graduated with Distinction)"
        " Bachelor of Arts in Biology, Brown University (Graduated Cum Laude)"
    ) in text.replace("\n", " ")
