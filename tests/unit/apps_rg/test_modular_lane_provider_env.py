"""Env wiring: modular section lanes must not ignore ``APPS_RG_MODULAR_LANE_PROVIDER``."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from unittest import mock

import pytest

from apps_rg.l2_recipe.r4_generation_mode import (
    ENV_APPS_RG_MODULAR_LANE_PROVIDER,
    ENV_APPS_RG_R4_GENERATION_MODE,
    MODE_MODULAR_SECTION_LANES,
    resolve_apps_rg_modular_lane_provider,
)
from apps_rg.l2_recipe.steps import GenerateResumeStep
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


def test_resolve_modular_lane_provider_default_qwen_vllm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_APPS_RG_MODULAR_LANE_PROVIDER, raising=False)
    assert resolve_apps_rg_modular_lane_provider() == "qwen_vllm"


def test_resolve_modular_lane_provider_qwen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_MODULAR_LANE_PROVIDER, "qwen_vllm")
    assert resolve_apps_rg_modular_lane_provider() == "qwen_vllm"


def test_resolve_modular_lane_provider_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_APPS_RG_MODULAR_LANE_PROVIDER, "openai")
    with pytest.raises(RuntimeError, match="INVALID_APPS_RG_MODULAR_LANE_PROVIDER"):
        resolve_apps_rg_modular_lane_provider()


@mock.patch("apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope", autospec=True)
@mock.patch("apps_rg.l2_recipe.modular_resume_generation.run_modular_resume_generation", autospec=True)
def test_generate_resume_step_passes_lane_provider_from_env(
    mock_modular: mock.MagicMock,
    mock_env: mock.MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    from apps_rg.l2_recipe.modular_r4_generation_result import ModularR4GenerationResult

    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_MODULAR_SECTION_LANES)
    monkeypatch.setenv(ENV_APPS_RG_MODULAR_LANE_PROVIDER, "qwen_vllm")
    repo = find_repo_root()
    gr = json.loads(
        (repo / "tests" / "_fixtures" / "rg_output_phase0_min_valid.json").read_text(encoding="utf-8"),
    )
    mock_modular.return_value = ModularR4GenerationResult(
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
    art = repo / "artifacts" / "apps_rg" / "runs" / f"lane_prof_{uuid.uuid4().hex[:10]}"
    art.mkdir(parents=True, exist_ok=True)
    cpa = SimpleNamespace(
        request_id="test-req",
        run_id="test-run",
        trace_id="test-trace",
        compile_status="PA_L2_HANDOFF_READY",
        artifact_id="test",
        prompt_id="apps_rg.resume_generation.strategic_tailor.v1",
        prompt_hash="abcd1234abcd1234abcd1234abcd1234",
        prompt_template_hash="tmpl1234tmpl1234tmpl1234tmpl1234",
        prompt_bom_hash="bom12345bom12345bom12345bom12345",
        replay_key="replay",
        policy_hash="",
        blueprint_hash="",
        provider_lane="default",
        source_refs={},
        output_schema_ref="generated_resume.json",
        output_schema_hash="",
        messages=[],
    )
    ctx = {
        "target_company": "TestCo",
        "target_role": "SVP Engineering",
        "artifact_dir": str(art),
        "resume_artifact_contract_mode": "full",
        "compiled_prompt_artifact": cpa,
    }

    GenerateResumeStep()(ctx)
    assert mock_modular.call_count == 1
    _inp, _art, _tok, prof = mock_modular.call_args[0]
    assert prof.phase1_lane_provider == "qwen_vllm"


def test_collect_lane_mocked_not_latest_successful_real(tmp_path: Path) -> None:
    """MOCKED bundles must not receive ``latest_successful_real_run.json`` rollup tag."""
    repo = tmp_path
    (repo / "apps_rg" / "resume" / "base").mkdir(parents=True)
    lane = "headline"
    base = repo / "modular_r4" / "sections" / lane / "mock" / "run1"
    base.mkdir(parents=True, exist_ok=True)
    l2 = {
        "run_id": "run1",
        "section_id": lane,
        "runtime_generation_status": "MOCKED",
        "headline_line": "Test | Test | Test",
    }
    for name, blob in [
        ("l2_output.json", l2),
        ("x2_gate_outputs.json", {"gates": [], "x2_passed": 1, "x2_failed": 0}),
        ("x1d_llm_judge_outputs.json", {"judges": []}),
        ("x3_disposition.json", {"x3_code": "X3_REVIEW_MOCKED_PLUMBING_ONLY"}),
        ("l6_shadow_eval_package.json", {"offline_only": True}),
    ]:
        (base / name).write_text(json.dumps(blob), encoding="utf-8")
    ptr = {
        "run_id": "run1",
        "run_dir": str(base.relative_to(repo)).replace("\\", "/"),
        "runtime_generation_status": "MOCKED",
    }
    ptr_root = base.parent.parent
    (ptr_root / "latest_successful_real_run.json").write_text(json.dumps(ptr), encoding="utf-8")

    from apps_rg.runtime.reports.generated_lane_rollup import collect_lane_from_run_dir

    row = collect_lane_from_run_dir(lane, base, repo=repo)
    assert row["accepted_real_evidence_resolution"] != "latest_successful_real_run.json"


def test_collect_lane_real_llm_with_pointer_matches_gate(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "apps_rg" / "resume" / "base").mkdir(parents=True)
    lane = "headline"
    base = repo / "modular_r4" / "sections" / lane / "real" / "run1"
    base.mkdir(parents=True, exist_ok=True)
    l2 = {
        "run_id": "run1",
        "section_id": lane,
        "runtime_generation_status": "REAL_LLM",
        "headline_line": "A | B | C",
    }
    for name, blob in [
        ("l2_output.json", l2),
        ("x2_gate_outputs.json", {"gates": [], "x2_passed": 1, "x2_failed": 0}),
        ("x1d_llm_judge_outputs.json", {"judges": []}),
        ("x3_disposition.json", {"x3_code": "X3_ALLOW"}),
        ("l6_shadow_eval_package.json", {"offline_only": True}),
        (
            "provider_request.json",
            {"provider_requested": "qwen_vllm", "provider_attempted": True},
        ),
    ]:
        (base / name).write_text(json.dumps(blob), encoding="utf-8")
    rel = str(base.relative_to(repo)).replace("\\", "/")
    ptr = {"run_dir": rel, "run_id": "run1", "runtime_generation_status": "REAL_LLM"}
    (base.parent.parent / "latest_successful_real_run.json").write_text(
        json.dumps(ptr),
        encoding="utf-8",
    )
    from apps_rg.runtime.reports.generated_lane_rollup import collect_lane_from_run_dir

    row = collect_lane_from_run_dir(lane, base, repo=repo)
    assert row["accepted_real_evidence_resolution"] == "latest_successful_real_run.json"
