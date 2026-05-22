"""W3 — apps_rg full-résumé product eligibility for package X3 (unit)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.l2_recipe.resume_output_shape import (
    BLOCKED_PROVIDER_LANE,
    BLOCKED_STUB_PROVIDER,
    FAILED_ARTIFACT_GATE,
    FAILED_PROVIDER,
    REAL_RESUME,
    STUB_RECEIPT,
)
from apps_rg.runtime.package.apps_rg_full_resume_x3_eligibility import (
    evaluate_apps_rg_full_success_eligibility,
)
from apps_rg.runtime.internal.resume_package_disposition import (
    X3_ALLOW_CODE,
    X3_BLOCKED_DETERMINISTIC,
    evaluate_resume_package,
)
from tests._apps_contract.test_resume_package_x3 import _write_minimal_fixture_tree


def _run_root_with_artifacts(tmp: Path) -> Path:
    """Manifest lives under .../docx/; JSON under docx/outputs/."""
    docx_root = tmp / "artifacts" / "apps_rg" / "runtime_proofs" / "docx"
    out = docx_root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "generated_resume.json").write_text(
        json.dumps({"headline": "SVP", "executive_summary": "x", "k": 1}),
        encoding="utf-8",
    )
    return docx_root


def _manifest(**overrides: object) -> dict:
    m: dict = {
        "apps_rg_generation_status": REAL_RESUME,
        "resume_shape": REAL_RESUME,
        "full_resume_generated": True,
        "generated_resume_json_relpath": "outputs/generated_resume.json",
        "docx_output_required": False,
    }
    m.update(overrides)
    return m


def test_eligible_real_resume_artifact_gate_passes(tmp_path: Path) -> None:
    root = _run_root_with_artifacts(tmp_path)
    man = _manifest()
    ok, reasons = evaluate_apps_rg_full_success_eligibility(manifest=man, run_root=root)
    assert ok is True
    assert reasons == []


@pytest.mark.parametrize(
    "status",
    [
        STUB_RECEIPT,
        FAILED_PROVIDER,
        BLOCKED_STUB_PROVIDER,
        BLOCKED_PROVIDER_LANE,
        FAILED_ARTIFACT_GATE,
    ],
)
def test_blocked_generation_status_not_eligible(tmp_path: Path, status: str) -> None:
    root = _run_root_with_artifacts(tmp_path)
    ok, reasons = evaluate_apps_rg_full_success_eligibility(
        manifest=_manifest(apps_rg_generation_status=status),
        run_root=root,
    )
    assert ok is False
    assert any("blocked_generation_status" in r for r in reasons)


def test_missing_generation_status_not_eligible(tmp_path: Path) -> None:
    root = _run_root_with_artifacts(tmp_path)
    m = _manifest()
    del m["apps_rg_generation_status"]
    ok, reasons = evaluate_apps_rg_full_success_eligibility(manifest=m, run_root=root)
    assert ok is False
    assert any(r == "missing_generation_status" for r in reasons)


def test_missing_resume_shape_not_eligible(tmp_path: Path) -> None:
    root = _run_root_with_artifacts(tmp_path)
    m = _manifest()
    del m["resume_shape"]
    ok, reasons = evaluate_apps_rg_full_success_eligibility(manifest=m, run_root=root)
    assert ok is False
    assert any(r == "missing_resume_shape" for r in reasons)


def test_docx_verified_false_not_eligible_when_docx_required(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPS_RG_DOCX_OUTPUT_REQUIRED", "1")
    root = _run_root_with_artifacts(tmp_path)
    (root / "outputs" / "resume.docx").write_bytes(b"DOCX")
    ok, reasons = evaluate_apps_rg_full_success_eligibility(
        manifest=_manifest(docx_verified=False, docx_output_required=True),
        run_root=root,
    )
    assert ok is False
    assert any("docx_verified_not_true" in r for r in reasons)


def test_full_resume_generated_false_not_eligible(tmp_path: Path) -> None:
    root = _run_root_with_artifacts(tmp_path)
    ok, reasons = evaluate_apps_rg_full_success_eligibility(
        manifest=_manifest(full_resume_generated=False),
        run_root=root,
    )
    assert ok is False
    assert any(r == "full_resume_generated_not_true" for r in reasons)


def test_w3_manifest_good_package_allow(tmp_path: Path) -> None:
    paths = _write_minimal_fixture_tree(tmp_path)
    docx_root = paths.apps_rg_output_manifest_json.parent
    out = docx_root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "generated_resume.json").write_text(json.dumps({"r": 1}), encoding="utf-8")
    paths.apps_rg_output_manifest_json.write_text(
        json.dumps(_manifest()),
        encoding="utf-8",
    )
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["final_x3_code"] == X3_ALLOW_CODE
    assert dsp["apps_rg_full_resume_product_gate"]["w3_enforced"] is True
    assert dsp["apps_rg_full_resume_product_gate"]["eligible_for_package_x3_allow"] is True
    assert dsp["apps_rg_full_resume_outcome_authorized"] is True
    assert dsp["apps_rg_product_terminal_class"] == "SUCCESS"


def test_w3_manifest_stub_blocks_package_allow(tmp_path: Path) -> None:
    paths = _write_minimal_fixture_tree(tmp_path)
    docx_root = paths.apps_rg_output_manifest_json.parent
    out = docx_root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "generated_resume.json").write_text(json.dumps({"r": 1}), encoding="utf-8")
    paths.apps_rg_output_manifest_json.write_text(
        json.dumps(_manifest(apps_rg_generation_status=STUB_RECEIPT, resume_shape=STUB_RECEIPT)),
        encoding="utf-8",
    )
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["final_x3_code"] == X3_BLOCKED_DETERMINISTIC
    assert dsp["deterministic_blocked"] is True
    assert dsp["apps_rg_full_resume_outcome_authorized"] is False
    assert dsp["apps_rg_product_terminal_class"] == "BLOCKED"
    assert dsp["apps_rg_full_resume_decisive_reason"]

