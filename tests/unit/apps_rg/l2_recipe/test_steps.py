from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.l2_recipe import steps
from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.resume_output_shape import (
    INCOMPLETE_STRUCTURE,
    REAL_RESUME,
    ResumeShapeReport,
)


def test_write_stub_or_diagnostic_snapshot_ignores_missing_artifact_dir(
    tmp_path: Path,
) -> None:
    steps._write_stub_or_diagnostic_snapshot(
        {},
        gr={"headline": "Ignored"},
        shape_rep=ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        ),
        mode="diagnostic",
    )

    assert not (tmp_path / "outputs" / "stub_receipt_diagnostic.json").exists()


def test_write_stub_or_diagnostic_snapshot_records_bounded_shape_fields(
    tmp_path: Path,
) -> None:
    steps._write_stub_or_diagnostic_snapshot(
        {"artifact_dir": str(tmp_path)},
        gr={"headline": "Generated"},
        shape_rep=ResumeShapeReport(
            generation_status=INCOMPLETE_STRUCTURE,
            full_resume_generated=False,
            resume_shape=INCOMPLETE_STRUCTURE,
        ),
        mode="diagnostic",
    )

    payload = json.loads((tmp_path / "outputs" / "stub_receipt_diagnostic.json").read_text())
    assert payload == {
        "schema_version": "apps_rg.stub_receipt_diagnostic.v1",
        "resume_artifact_contract_mode": "diagnostic",
        "classified_generation_status": INCOMPLETE_STRUCTURE,
        "full_resume_generated": False,
        "resume_shape": INCOMPLETE_STRUCTURE,
        "had_generated_resume_dict": True,
    }


def test_write_modular_generate_step_receipt_preserves_result_refs_and_policy(
    tmp_path: Path,
) -> None:
    result = ModularR4GenerationResult(
        generated_resume={"headline": "Generated"},
        section_provider_calls_ref="modular_r4/section_provider_calls.json",
        section_output_refs={"headline": "modular_r4/headline.json"},
        merge_receipt_ref="modular_r4/final_resume_assembly/final_resume_receipt.json",
        schema_validation_receipt_ref="modular_r4/schema_validation.json",
        final_schema_valid=True,
        decisive_status="PASS",
        failure_reason="",
        provider_call_count=7,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
        rg_output_merge_receipt_ref="modular_r4/outputs/rg_output_merge_receipt.json",
        extras={"recipe_lane_policy": {"fatal_lane_failures": []}},
    )

    out = steps.write_modular_generate_step_receipt(tmp_path, modular_result=result)

    assert out == tmp_path / "modular_r4" / "generate_resume_step_receipt.json"
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "apps_rg.modular_generate_step_receipt.v1"
    assert payload["section_provider_calls_ref"] == result.section_provider_calls_ref
    assert payload["section_output_refs"] == result.section_output_refs
    assert payload["rg_output_merge_receipt_ref"] == result.rg_output_merge_receipt_ref
    assert payload["final_schema_valid"] is True
    assert payload["decisive_status"] == "PASS"
    assert payload["recipe_lane_policy"] == {"fatal_lane_failures": []}


@pytest.mark.parametrize(
    "key",
    [
        "compiled_prompt_artifact",
        "pa_artifact",
        "prompt_artifact",
        "governed_context",
    ],
)
def test_pa_guard_accepts_every_current_artifact_key(key: str) -> None:
    step = steps.GenerateResumeStep()
    step._check_pa_guard({key: object()})


def test_pa_guard_error_names_current_step() -> None:
    step = steps.GenerateResumeStep()

    with pytest.raises(steps.PAGuardError, match="Step 'generate_resume'"):
        step._check_pa_guard({})


def test_generate_resume_compile_error_preempts_compile_and_modular_path() -> None:
    step = steps.GenerateResumeStep()

    with pytest.raises(RuntimeError, match="PA_COMPILE_FAILED: compiler unavailable"):
        step({"pa_compile_error": "compiler unavailable"})


def test_modular_generation_requires_artifact_dir_before_dispatch() -> None:
    step = steps.GenerateResumeStep()

    with pytest.raises(RuntimeError, match="artifact_dir is required"):
        step._modular_section_lanes_generation(
            {"compiled_prompt_artifact": SimpleNamespace(run_id="run-1")}
        )


def test_resume_artifact_gate_persists_generated_resume_then_merges_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, object]] = []
    report = ResumeShapeReport(
        generation_status=REAL_RESUME,
        full_resume_generated=True,
        resume_shape=REAL_RESUME,
    )

    def _persist(base: Path, *, generated_resume: dict) -> None:
        calls.append(("persist", base, generated_resume))

    def _verify(base: Path) -> ResumeShapeReport:
        calls.append(("verify", base))
        return report

    def _merge(base: Path, *, shape_rep: ResumeShapeReport) -> None:
        calls.append(("merge", base, shape_rep))

    monkeypatch.setattr(steps, "persist_json_product_outputs", _persist)
    monkeypatch.setattr(steps, "verify_full_resume_artifact_bundle", _verify)
    monkeypatch.setattr(steps, "merge_manifest_after_artifact_gate", _merge)

    out = steps.ResumeArtifactGateStep()(
        {"artifact_dir": str(tmp_path), "generated_resume": {"headline": "Generated"}}
    )

    assert calls == [
        ("persist", tmp_path, {"headline": "Generated"}),
        ("verify", tmp_path),
        ("merge", tmp_path, report),
    ]
    assert out == {
        "status": "ok",
        "step": "resume_artifact_gate",
        "generation_status": REAL_RESUME,
        "full_resume_generated": True,
        "resume_shape": REAL_RESUME,
    }


def test_resume_artifact_gate_fails_closed_without_artifact_dir() -> None:
    with pytest.raises(RuntimeError, match="FAILED_ARTIFACT_GATE: no artifact_dir"):
        steps.ResumeArtifactGateStep()({})
