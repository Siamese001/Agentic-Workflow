"""Contract: full résumé generation fail-closed unless STRUCTURED_RESUME_OK (modular path)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult
from apps_rg.l2_recipe.resume_output_shape import (
    MALFORMED_MODEL_OUTPUT,
    STRUCTURED_RESUME_OK,
)
from apps_rg.l2_recipe.steps import GenerateResumeStep
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


def _valid_structured_resume() -> dict:
    return {
        "headline": "SVP Engineering",
        "executive_summary": "Engineering executive.",
        "competencies": ["AI platform strategy"],
        "professional_experience": [
            {
                "company": "Unify Consulting",
                "title": "SVP Engineering",
                "location": "Boca Raton, FL",
                "dates": "2023 - Present",
                "summary": "Led platforms.",
                "bullets": ["Shipped governed agentic workflows."],
            }
        ],
        "education": [],
        "certifications": [],
    }


def _pa_context(artifact_dir: str) -> dict:
    cpa = SimpleNamespace(
        request_id="test-req-contract",
        run_id="test-run-contract",
        trace_id="test-trace-contract",
        compile_status="PA_L2_HANDOFF_READY",
        artifact_id="test_123",
        prompt_id="apps_rg.resume_generation.strategic_tailor.v1",
        prompt_hash="abcd1234abcd1234abcd1234abcd1234",
        prompt_template_hash="tmpl1234tmpl1234tmpl1234tmpl1234",
        prompt_bom_hash="bom12345bom12345bom12345bom12345",
        replay_key="replay_test",
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
        "target_role": "Engineer",
        "artifact_dir": artifact_dir,
        "resume_artifact_contract_mode": "full",
        "compiled_prompt_artifact": cpa,
    }


def _modular_result(gr: dict, *, schema_ok: bool = True) -> ModularR4GenerationResult:
    return ModularR4GenerationResult(
        generated_resume=gr,
        section_provider_calls_ref="modular_r4/section_provider_calls.json",
        section_output_refs={"headline": "m/h/l2.json"},
        merge_receipt_ref="modular_r4/final_resume_assembly/final_resume_receipt.json",
        schema_validation_receipt_ref="modular_r4/rg_output_schema_validation_receipt.json",
        final_schema_valid=schema_ok,
        decisive_status="PASS" if schema_ok else "FAIL",
        failure_reason="" if schema_ok else "schema_invalid",
        provider_call_count=7,
        locked_sections_provider_calls_detected=False,
        lanes_executed=7,
        lane_outputs_valid=True,
        final_merge_attempted=True,
        rg_output_merge_receipt_ref="modular_r4/outputs/rg_output_merge_receipt.json",
    )


def _artifact_dir() -> str:
    repo = find_repo_root()
    art = repo / "artifacts" / "apps_rg" / "runs" / f"contract_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    return str(art)


@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_full_mode_raw_text_only_blocks(mock_modular) -> None:
    mock_modular.return_value = _modular_result({"raw_text": "# prose only\n"})
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match=MALFORMED_MODEL_OUTPUT):
        step(_pa_context(_artifact_dir()))


@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_full_mode_incomplete_structure_blocks(mock_modular) -> None:
    mock_modular.return_value = _modular_result({"headline": "Only a headline"})
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="INCOMPLETE_STRUCTURE"):
        step(_pa_context(_artifact_dir()))


@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_full_mode_missing_required_section_blocks(mock_modular) -> None:
    payload = _valid_structured_resume()
    del payload["competencies"]
    mock_modular.return_value = _modular_result(payload)
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="INCOMPLETE_STRUCTURE"):
        step(_pa_context(_artifact_dir()))


@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_full_mode_modular_failure_blocks(mock_modular) -> None:
    mock_modular.return_value = _modular_result(_valid_structured_resume(), schema_ok=False)
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="FAILED_MODULAR_R4"):
        step(_pa_context(_artifact_dir()))


@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_full_mode_structured_ok_passes(mock_modular) -> None:
    gr = _valid_structured_resume()
    mock_modular.return_value = _modular_result(gr)
    step = GenerateResumeStep()
    out = step(_pa_context(_artifact_dir()))
    assert out["status"] == "ok"
    assert out["generation_status"] == STRUCTURED_RESUME_OK
    assert out["full_resume_generated"] is True
    assert out["generated_resume"] == gr


@mock.patch(
    "apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation",
    autospec=True,
)
def test_stub_mode_raises_modular_incompatible(mock_modular) -> None:
    ctx = _pa_context(_artifact_dir())
    ctx["resume_artifact_contract_mode"] = "stub_receipt"
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="MODULAR_MODE_INCOMPATIBLE"):
        step(ctx)
    mock_modular.assert_not_called()
