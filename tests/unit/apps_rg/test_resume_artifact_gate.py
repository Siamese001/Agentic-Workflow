"""W2 resume artifact gate + REAL_RESUME classification (unit)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.l2_recipe.resume_artifact_gate import (
    merge_manifest_after_artifact_gate,
    persist_json_product_outputs,
    verify_full_resume_artifact_bundle,
)
from apps_rg.l2_recipe.resume_output_shape import (
    BLOCKED_PROVIDER_LANE,
    BLOCKED_STUB_PROVIDER,
    FAILED_ARTIFACT_GATE,
    FAILED_PROVIDER,
    REAL_RESUME,
    STUB_RECEIPT,
    ResumeShapeReport,
    classify_resume_payload,
    is_real_resume_shape_report,
)
from apps_rg.l2_recipe.steps import ResumeArtifactGateStep


def _real_resume_dict() -> dict:
    return {
        "headline": "SVP Engineering",
        "executive_summary": "Executive leader.",
        "competencies": ["AI strategy"],
        "professional_experience": [
            {
                "company": "Co",
                "title": "VP",
                "location": "FL",
                "dates": "2020 - Present",
                "summary": "Led teams.",
                "bullets": ["Shipped products."],
            }
        ],
        "education": [],
        "certifications": [],
    }


def _write_bundle(
    tmp: Path,
    *,
    resume: dict | None,
    skip_manifest: bool = False,
) -> None:
    out = tmp / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    jp = out / "generated_resume.json"
    if resume is not None:
        jp.write_text(json.dumps(resume, ensure_ascii=False), encoding="utf-8")
    if skip_manifest:
        return
    man = {
        "schema_version": "apps_rg_output_manifest.v1",
        "generated_resume_json_relpath": "outputs/generated_resume.json",
        "apps_rg_generation_status": REAL_RESUME,
        "full_resume_generated": True,
        "resume_shape": REAL_RESUME,
    }
    (tmp / "apps_rg_output_manifest.json").write_text(
        json.dumps(man, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_missing_generated_resume_json_blocks(tmp_path: Path) -> None:
    (tmp_path / "apps_rg_output_manifest.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE"):
        verify_full_resume_artifact_bundle(tmp_path)


def test_empty_generated_resume_json_blocks(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "generated_resume.json").write_text("   \n", encoding="utf-8")
    (tmp_path / "apps_rg_output_manifest.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE"):
        verify_full_resume_artifact_bundle(tmp_path)


def test_missing_output_manifest_blocks(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "generated_resume.json").write_text(
        json.dumps(_real_resume_dict()), encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE"):
        verify_full_resume_artifact_bundle(tmp_path)


def test_missing_section_blocks_real_resume(tmp_path: Path) -> None:
    bad = {"headline": "x", "executive_summary": "y"}
    _write_bundle(tmp_path, resume=bad)
    with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE"):
        verify_full_resume_artifact_bundle(tmp_path)


def test_all_sections_classifies_real_resume() -> None:
    rep = classify_resume_payload(_real_resume_dict())
    assert rep.generation_status == REAL_RESUME
    assert is_real_resume_shape_report(rep)


def test_stub_receipt_payload_not_real_resume(tmp_path: Path) -> None:
    _write_bundle(tmp_path, resume={"stub_response": True, "hash": "a"})
    with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE"):
        verify_full_resume_artifact_bundle(tmp_path)


def test_stub_receipt_classify_not_real() -> None:
    rep = classify_resume_payload({"stub_response": True})
    assert rep.generation_status == STUB_RECEIPT
    assert not is_real_resume_shape_report(rep)


def test_failed_provider_constant_not_real_resume() -> None:
    assert FAILED_PROVIDER != REAL_RESUME
    rep = ResumeShapeReport(FAILED_PROVIDER, False, "FAILURE")
    assert not is_real_resume_shape_report(rep)


def test_blocked_stub_provider_not_real_resume() -> None:
    assert BLOCKED_STUB_PROVIDER != REAL_RESUME
    rep = ResumeShapeReport(BLOCKED_STUB_PROVIDER, False, "BLOCKED")
    assert not is_real_resume_shape_report(rep)


def test_blocked_provider_lane_not_real_resume() -> None:
    assert BLOCKED_PROVIDER_LANE != REAL_RESUME
    rep = ResumeShapeReport(BLOCKED_PROVIDER_LANE, False, "BLOCKED")
    assert not is_real_resume_shape_report(rep)


def test_failed_artifact_gate_token() -> None:
    assert FAILED_ARTIFACT_GATE != REAL_RESUME


def test_gate_success_merges_manifest(tmp_path: Path) -> None:
    _write_bundle(tmp_path, resume=_real_resume_dict())
    rep = verify_full_resume_artifact_bundle(tmp_path)
    merge_manifest_after_artifact_gate(tmp_path, shape_rep=rep)
    man = json.loads((tmp_path / "apps_rg_output_manifest.json").read_text(encoding="utf-8"))
    assert man.get("apps_rg_generation_status") == REAL_RESUME
    assert man.get("full_resume_generated") is True
    assert man.get("resume_shape") == REAL_RESUME
    ra = man.get("required_artifacts")
    assert isinstance(ra, dict)
    assert ra.get("generated_resume_json") == "verified"
    assert "resume_docx" not in ra


def test_persist_json_product_outputs_writes_files(tmp_path: Path) -> None:
    resume = _real_resume_dict()
    persist_json_product_outputs(tmp_path, generated_resume=resume)
    assert (tmp_path / "outputs" / "generated_resume.json").is_file()
    assert (tmp_path / "apps_rg_output_manifest.json").is_file()


def test_artifact_gate_step_json_only(tmp_path: Path) -> None:
    gate = ResumeArtifactGateStep()
    resume = _real_resume_dict()
    ctx = {"artifact_dir": str(tmp_path), "generated_resume": resume}
    out = gate(ctx)
    assert out["status"] == "ok"
    assert not (tmp_path / "outputs" / "resume.docx").exists()
    assert (tmp_path / "outputs" / "generated_resume.json").is_file()
