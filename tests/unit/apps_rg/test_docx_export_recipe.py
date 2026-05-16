"""DOCX export step — writes real .docx under artifact_dir and records manifest paths."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.l2_recipe.registry import get_apps_rg_recipe_metadata
from apps_rg.l2_recipe.steps import DocxExportStep, GenerateResumeStep, ResumeArtifactGateStep
from apps_rg.runtime.orchestration.canonical_dispatch import (
    _augment_integrated_manifest_with_apps_rg_docx,
)


def test_recipe_registers_generate_then_docx_then_artifact_gate() -> None:
    meta = get_apps_rg_recipe_metadata()
    assert meta["steps"][0] is GenerateResumeStep
    assert meta["steps"][1] is DocxExportStep
    assert meta["steps"][2] is ResumeArtifactGateStep
    assert len(meta["steps"]) == 3


def test_docx_export_step_writes_docx_and_apps_rg_manifest(tmp_path: Path) -> None:
    step = DocxExportStep()
    resume = {
        "candidate_name": "Taylor Example",
        "target_role": "SVP Example",
        "target_company": "Example Co",
        "sections": {
            "summary": {"text": "Summary for docx export test.", "word_count": 5},
            "experience": [],
            "skills": ["Python"],
            "education": [],
        },
    }
    out = step(
        {
            "artifact_dir": str(tmp_path),
            "generated_resume": resume,
            "target_role": "SVP Example",
            "target_company": "Example Co",
        }
    )
    assert out.get("status") == "ok"
    docx = tmp_path / "outputs" / "resume.docx"
    assert docx.is_file()
    assert docx.stat().st_size > 1_500
    man = json.loads((tmp_path / "apps_rg_output_manifest.json").read_text(encoding="utf-8"))
    assert man.get("resume_docx_relpath") == "outputs/resume.docx"
    assert man.get("docx_verified") is True


def test_augment_integrated_manifest_only_when_docx_exists(tmp_path: Path) -> None:
    integ = tmp_path / "integrated_runtime_artifact_manifest.json"
    integ.write_text(json.dumps({"artifact_filenames": ["agentic_core_how_trace.json"]}), encoding="utf-8")
    _augment_integrated_manifest_with_apps_rg_docx(tmp_path)
    data = json.loads(integ.read_text(encoding="utf-8"))
    assert "apps_rg_resume_docx_relpath" not in data

    outd = tmp_path / "outputs"
    outd.mkdir(parents=True)
    docx = outd / "resume.docx"
    docx.write_bytes(b"PK\x03\x04fake")

    _augment_integrated_manifest_with_apps_rg_docx(tmp_path)
    data = json.loads(integ.read_text(encoding="utf-8"))
    assert data.get("apps_rg_resume_docx_relpath") == "outputs/resume.docx"
    assert data.get("apps_rg_resume_docx_sha256", "").startswith("sha256:")
