"""Contract: ``GenerateResumeStep`` modular-only (``APPS_RG_R4_GENERATION_MODE``).

Default when env is **unset** is ``modular_section_lanes``. ``legacy_full_resume`` is retired.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.r4_generation_mode import (
    ENV_APPS_RG_R4_GENERATION_MODE,
    MODE_MODULAR_SECTION_LANES,
    RETIRED_MODE_LEGACY_FULL_RESUME,
    resolve_apps_rg_r4_generation_mode,
)
from apps_rg.l2_recipe.r4_generation_route import R4_RECIPE_GENERATION_EXECUTION_STYLE
from apps_rg.l2_recipe.steps import GenerateResumeStep
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


def _pa_context(*, artifact_dir: str) -> dict:
    cpa = SimpleNamespace(
        request_id="test-req-wiring",
        run_id="test-run-wiring",
        trace_id="test-trace-wiring",
        compile_status="PA_L2_HANDOFF_READY",
        artifact_id="test_wiring",
        prompt_id="apps_rg.resume_generation.strategic_tailor.v1",
        prompt_hash="abcd1234abcd1234abcd1234abcd1234",
        prompt_template_hash="tmpl1234tmpl1234tmpl1234tmpl1234",
        prompt_bom_hash="bom12345bom12345bom12345bom12345",
        replay_key="replay_wiring",
        policy_hash="",
        blueprint_hash="",
        provider_lane="default",
        source_refs={},
        output_schema_ref="generated_resume.json",
        output_schema_hash="",
        messages=[],
    )
    return {
        "target_company": "TestCo",
        "target_role": "SVP Engineering",
        "artifact_dir": artifact_dir,
        "resume_artifact_contract_mode": "full",
        "compiled_prompt_artifact": cpa,
    }


def _valid_rg_output(repo: Path) -> dict:
    p = repo / "tests" / "_fixtures" / "rg_output_phase0_min_valid.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _successful_modular_result(repo: Path) -> ModularR4GenerationResult:
    gr = _valid_rg_output(repo)
    return ModularR4GenerationResult(
        generated_resume=gr,
        section_provider_calls_ref="modular_r4/section_provider_calls.json",
        section_output_refs={"headline": "m/h/l2.json"},
        merge_receipt_ref="modular_r4/final_resume_assembly/final_resume_receipt.json",
        schema_validation_receipt_ref="modular_r4/rg_output_schema_validation_receipt.json",
        final_schema_valid=True,
        decisive_status="PASS",
        failure_reason="",
        provider_call_count=7,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
        rg_output_merge_receipt_ref="modular_r4/outputs/rg_output_merge_receipt.json",
    )


def test_resolve_mode_default_is_modular_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_APPS_RG_R4_GENERATION_MODE, raising=False)
    assert resolve_apps_rg_r4_generation_mode() == MODE_MODULAR_SECTION_LANES


def test_resolve_modular_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_MODULAR_SECTION_LANES)
    assert resolve_apps_rg_r4_generation_mode() == MODE_MODULAR_SECTION_LANES


def test_resolve_invalid_mode_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, "nope")
    with pytest.raises(RuntimeError, match="INVALID_APPS_RG_R4_GENERATION_MODE"):
        resolve_apps_rg_r4_generation_mode()


def test_r4_generation_route_declares_modular_canonical() -> None:
    assert R4_RECIPE_GENERATION_EXECUTION_STYLE == "modular_section_lanes"


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_default_mode_calls_modular_not_envelope(mock_modular, mock_env, tmp_path, monkeypatch) -> None:
    monkeypatch.delenv(ENV_APPS_RG_R4_GENERATION_MODE, raising=False)
    mock_env.return_value = SimpleNamespace(
        proposed_state_diff={"generated_resume": _valid_rg_output(find_repo_root())},
        execution_status="completed",
    )
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"wiring_default_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    mock_modular.return_value = _successful_modular_result(repo)
    step = GenerateResumeStep()
    out = step(_pa_context(artifact_dir=str(art)))
    mock_modular.assert_called_once()
    mock_env.assert_not_called()
    assert out.get("apps_rg_r4_generation_mode") == MODE_MODULAR_SECTION_LANES
    assert "generated_resume" in out


def test_legacy_env_raises_before_step(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, RETIRED_MODE_LEGACY_FULL_RESUME)
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="RETIRED_APPS_RG_R4_GENERATION_MODE"):
        step(_pa_context(artifact_dir=str(find_repo_root())))


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_modular_mode_calls_modular_not_envelope(mock_modular, mock_env, monkeypatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_MODULAR_SECTION_LANES)
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"wiring_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    mock_modular.return_value = _successful_modular_result(repo)
    step = GenerateResumeStep()
    out = step(_pa_context(artifact_dir=str(art)))
    mock_modular.assert_called_once()
    mock_env.assert_not_called()
    assert out.get("apps_rg_r4_generation_mode") == MODE_MODULAR_SECTION_LANES
    assert out.get("generated_resume") == mock_modular.return_value.generated_resume
    receipt = art / "modular_r4" / "generate_resume_step_receipt.json"
    assert receipt.is_file()


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_modular_failure_does_not_fallback_to_envelope(mock_modular, mock_env, monkeypatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_MODULAR_SECTION_LANES)
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"wiring_fail_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    mock_modular.return_value = ModularR4GenerationResult(
        generated_resume=None,
        section_provider_calls_ref="modular_r4/section_provider_calls.json",
        section_output_refs={},
        merge_receipt_ref=None,
        schema_validation_receipt_ref="modular_r4/rg_output_schema_validation_receipt.json",
        final_schema_valid=False,
        decisive_status="PARTIAL",
        failure_reason="mocked_lane_rejected:headline",
        provider_call_count=0,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
        rg_output_merge_receipt_ref=None,
    )
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="FAILED_MODULAR_R4"):
        step(_pa_context(artifact_dir=str(art)))
    mock_modular.assert_called_once()
    mock_env.assert_not_called()


def test_modular_stub_contract_mode_rejects_without_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_MODULAR_SECTION_LANES)
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"wiring_stub_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    ctx = _pa_context(artifact_dir=str(art))
    ctx["resume_artifact_contract_mode"] = "stub_receipt"
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="MODULAR_MODE_INCOMPATIBLE"):
        step(ctx)


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_docx_skipped_when_generate_step_fails(mock_modular, mock_env, monkeypatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_MODULAR_SECTION_LANES)
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"wiring_docx_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    mock_modular.return_value = ModularR4GenerationResult(
        generated_resume=None,
        section_provider_calls_ref="m",
        section_output_refs={},
        merge_receipt_ref=None,
        schema_validation_receipt_ref="m",
        final_schema_valid=False,
        decisive_status="FAIL",
        failure_reason="test",
        provider_call_count=0,
        locked_sections_provider_calls_detected=False,
        lanes_executed=0,
        lane_outputs_valid=False,
        final_merge_attempted=True,
        rg_output_merge_receipt_ref=None,
    )
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="FAILED_MODULAR_R4"):
        step(_pa_context(artifact_dir=str(art)))

    mock_env.assert_not_called()
