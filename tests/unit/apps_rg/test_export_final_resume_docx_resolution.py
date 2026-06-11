"""Regression tests for export_final_resume_docx resolution + hollow-output guard.

Incident (2026-06-11): a run-dir was passed to ``export_final_resume_docx.py``;
``_resolve_final_resume`` used ``sorted(rglob(...))[-1]`` which picked the flat
``outputs/final_resume.json`` export sibling (alphabetically after
``final_resume_assembly/``). That flat schema is not what the builder parses, so
it silently emitted a hollow DOCX containing only "Candidate" +
"Professional Experience". These tests lock in:
  1. run-dir resolution prefers the spine-shaped ``final_resume_assembly`` file;
  2. ``export`` refuses to emit a hollow DOCX from a flat/non-spine blob.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from ops_scripts.apps_rg.export_final_resume_docx import (
    _is_spine_shaped,
    _resolve_final_resume,
    export,
)

SPINE_BLOB = {
    "candidate_identity": {"candidate_name": "Test User", "header_contact": {}},
    "sections": [
        {"section_id": "headline", "l2_output_snapshot": {"headline_line": "Test Headline Line"}},
    ],
}

# Flat ``outputs/`` export shape: candidate_name top-level, sections as a dict.
FLAT_BLOB = {"candidate_name": "Test User", "sections": {"headline": {}}}


def _write(path: Path, blob: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob), encoding="utf-8")
    return path


def test_is_spine_shaped_discriminates(tmp_path: Path) -> None:
    spine = _write(tmp_path / "spine.json", SPINE_BLOB)
    flat = _write(tmp_path / "flat.json", FLAT_BLOB)
    assert _is_spine_shaped(spine) is True
    assert _is_spine_shaped(flat) is False


def test_resolve_prefers_spine_over_flat_sibling(tmp_path: Path) -> None:
    run = tmp_path / "modular_r4"
    _write(run / "final_resume_assembly" / "final_resume.json", SPINE_BLOB)
    _write(run / "outputs" / "final_resume.json", FLAT_BLOB)
    resolved = _resolve_final_resume(str(run))
    assert resolved.parent.name == "final_resume_assembly"
    assert _is_spine_shaped(resolved)


def test_resolve_raises_when_only_flat_present(tmp_path: Path) -> None:
    run = tmp_path / "modular_r4"
    _write(run / "outputs" / "final_resume.json", FLAT_BLOB)
    with pytest.raises(ValueError, match="No spine-shaped final_resume.json"):
        _resolve_final_resume(str(run))


def test_export_refuses_hollow_from_flat_blob(tmp_path: Path) -> None:
    flat = _write(tmp_path / "final_resume.json", FLAT_BLOB)
    with pytest.raises(ValueError, match="refusing to emit a hollow DOCX"):
        export(flat, tmp_path / "out.docx")


def test_export_populates_from_spine_blob(tmp_path: Path) -> None:
    spine = _write(tmp_path / "final_resume.json", SPINE_BLOB)
    out = export(spine, tmp_path / "out.docx")
    assert out.is_file()
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    assert "Test User" in xml
    assert "Test Headline Line" in xml
