from __future__ import annotations

import zipfile
from html import escape
from pathlib import Path

from apps_rg.runtime.c0 import prior_resume_variant_extractor as extractor
from apps_rg.runtime.c0.constants import (
    CLAIM_ELIGIBLE,
    CONFIDENCE_HIGH,
    CONFIDENCE_PENDING,
    PROOF_ELIGIBLE,
)


def _write_minimal_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p>"
        for text in paragraphs
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", xml)


def test_extract_prior_resume_manifest_rows_matches_ledger_and_pending_atoms(
    tmp_path: Path,
    monkeypatch,
) -> None:
    matched_atom = "Led platform modernization saving 20 percent across cloud operations."
    _write_minimal_docx(
        tmp_path / "Chief AI Officer Resume.docx",
        [
            "Experience",
            matched_atom,
            "- Built unmatched governance playbooks for AI controls.",
        ],
    )
    monkeypatch.setattr(
        extractor,
        "_ledger_claim_index",
        lambda repo_root: {matched_atom.lower(): "fact_platform_001"},
    )

    rows = extractor.extract_prior_resume_manifest_rows(tmp_path, repo_root=tmp_path)

    assert len(rows) == 2
    matched = rows[0]
    assert matched["source_resume_variant"] == "Chief AI Officer Resume.docx"
    assert matched["variant_family"] == "AI/Data/Governance"
    assert matched["matched_existing_fact_id"] == "fact_platform_001"
    assert matched["confidence"] == CONFIDENCE_HIGH
    assert matched["proof_status"] == PROOF_ELIGIBLE
    assert matched["requires_trace_audit"] is False
    assert matched["embed_allowed"] is True

    pending = rows[1]
    assert pending["confidence"] == CONFIDENCE_PENDING
    assert pending["proof_status"] == CLAIM_ELIGIBLE
    assert pending["requires_trace_audit"] is True
    assert pending["embed_allowed"] is False


def test_claim_sized_atoms_skip_section_headers_and_split_long_lines() -> None:
    long_line = (
        "Delivered platform modernization across teams with measurable controls. "
        * 9
    ).strip()

    atoms = extractor._claim_sized_atoms_from_lines(["Skills", "Short", "- Built durable controls.", long_line])

    assert atoms[0] == ("line_2", "Built durable controls.")
    assert all(span.startswith("line_3:sent_") for span, _ in atoms[1:])
    assert all(len(atom) >= 12 for _, atom in atoms)


def test_corrupt_docx_is_ignored(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "Strategic Finance Resume.docx").write_bytes(b"not a zip")
    monkeypatch.setattr(extractor, "_ledger_claim_index", lambda repo_root: {})

    assert extractor.extract_prior_resume_manifest_rows(tmp_path, repo_root=tmp_path) == []
