"""Contract: full résumé generation fail-closed unless STRUCTURED_RESUME_OK.

``resume_artifact_contract_mode=full`` (default) requires a complete structured
payload; ``stub_receipt`` / ``diagnostic`` emit ``stub_receipt_diagnostic.json``
then raise ``STUB_RECEIPT`` so the spine never treats the run as fully
authorized generation.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest import mock

import pytest

from apps_rg.l2_recipe.resume_output_shape import (
    MALFORMED_MODEL_OUTPUT,
    STRUCTURED_RESUME_OK,
)
from apps_rg.l2_recipe.steps import GenerateResumeStep


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


def _sealed(*, diff: dict, execution_status: str = "completed") -> SimpleNamespace:
    return SimpleNamespace(
        proposed_state_diff=diff,
        generated_content="",
        execution_status=execution_status,
    )


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_full_mode_raw_text_only_blocks(mock_env, tmp_path) -> None:
    mock_env.return_value = _sealed(
        diff={"generated_resume": {"raw_text": "# prose only\n"}}
    )
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match=MALFORMED_MODEL_OUTPUT):
        step(_pa_context(str(tmp_path)))
    mock_env.assert_called_once()


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_full_mode_incomplete_structure_blocks(mock_env, tmp_path) -> None:
    mock_env.return_value = _sealed(
        diff={"generated_resume": {"headline": "Only a headline"}}
    )
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="INCOMPLETE_STRUCTURE"):
        step(_pa_context(str(tmp_path)))


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_full_mode_missing_required_section_blocks(mock_env, tmp_path) -> None:
    payload = _valid_structured_resume()
    del payload["competencies"]
    mock_env.return_value = _sealed(diff={"generated_resume": payload})
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="INCOMPLETE_STRUCTURE"):
        step(_pa_context(str(tmp_path)))


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_full_mode_failed_provider_blocks(mock_env, tmp_path) -> None:
    mock_env.return_value = _sealed(
        diff={"generated_resume": _valid_structured_resume()},
        execution_status="failed",
    )
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="FAILED_PROVIDER"):
        step(_pa_context(str(tmp_path)))


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_full_mode_structured_ok_passes(mock_env, tmp_path) -> None:
    mock_env.return_value = _sealed(
        diff={"generated_resume": _valid_structured_resume()}
    )
    step = GenerateResumeStep()
    out = step(_pa_context(str(tmp_path)))
    assert out["status"] == "ok"
    assert out["generation_status"] == STRUCTURED_RESUME_OK
    assert out["full_resume_generated"] is True
    assert out["generated_resume"] == _valid_structured_resume()


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_stub_mode_emits_diagnostic_and_raises_stub_receipt(
    mock_env, tmp_path
) -> None:
    mock_env.return_value = _sealed(
        diff={"generated_resume": {"headline": "partial only"}}
    )
    ctx = _pa_context(str(tmp_path))
    ctx["resume_artifact_contract_mode"] = "stub_receipt"
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="STUB_RECEIPT"):
        step(ctx)
    diag = tmp_path / "outputs" / "stub_receipt_diagnostic.json"
    assert diag.is_file()
    snap = json.loads(diag.read_text(encoding="utf-8"))
    assert snap["full_resume_generated"] is False
    assert snap["classified_generation_status"] == "INCOMPLETE_STRUCTURE"


@mock.patch(
    "apps_rg.runtime.bindings.l2_envelope_adapter.run_apps_rg_l2_envelope",
    autospec=True,
)
def test_stub_mode_structured_ok_still_never_claims_full_resume_generated(
    mock_env, tmp_path
) -> None:
    mock_env.return_value = _sealed(
        diff={"generated_resume": _valid_structured_resume()}
    )
    ctx = _pa_context(str(tmp_path))
    ctx["resume_artifact_contract_mode"] = "stub_receipt"
    step = GenerateResumeStep()
    with pytest.raises(RuntimeError, match="STUB_RECEIPT"):
        step(ctx)
    snap = json.loads(
        (tmp_path / "outputs" / "stub_receipt_diagnostic.json").read_text(
            encoding="utf-8"
        )
    )
    assert snap["full_resume_generated"] is False
    assert snap["classified_generation_status"] == STRUCTURED_RESUME_OK
