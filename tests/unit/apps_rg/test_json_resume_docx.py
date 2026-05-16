"""json_resume_docx — stub/minimal payloads render as readable receipts, not JSON dumps."""
from __future__ import annotations

from pathlib import Path

from docx import Document

from apps_rg.runtime.render.json_resume_docx import render_resume_dict_to_docx


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
