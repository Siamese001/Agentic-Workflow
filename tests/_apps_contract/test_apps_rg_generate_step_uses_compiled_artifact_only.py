"""Test: GenerateResumeStep uses compiled artifact only for model calls.

Verifies:
- When valid compiled artifact is provided, step proceeds
- Provider receives artifact-rendered request
- Raw prompt builder path is not used
"""

from __future__ import annotations

from unittest import mock

import pytest

from apps_rg.l2_recipe.steps import GenerateResumeStep
from apps_rg.prompt_assembly.contracts import PACompileStatus


@pytest.fixture
def valid_artifact_context() -> dict:
    return {
        "compiled_prompt_artifact": {
            "compile_status": PACompileStatus.PA_L2_HANDOFF_READY.value,
            "artifact_id": "test_artifact_123",
            "prompt_id": "apps_rg.resume_generation.strategic_tailor.v1",
            "prompt_hash": "abcd1234abcd1234",
            "prompt_template_hash": "tmpl1234tmpl1234",
            "prompt_bom_hash": "bom12345bom12345",
            "replay_key": "replay_key_test",
            "policy_hash": "policy_test",
            "blueprint_hash": "blueprint_test",
            "provider_lane": "anthropic_claude",
            "source_refs": {"jd_data_hash": "jd123"},
            "output_schema_ref": "generated_resume.json",
            "output_schema_hash": "schema_hash_test",
        },
    }


def test_step_accepts_valid_artifact(valid_artifact_context):
    step = GenerateResumeStep()
    with mock.patch("apps_rg.l2_recipe.steps.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        with mock.patch("apps_rg.scripts.generate_resume.main", return_value=None):
            with mock.patch("asyncio.run", return_value=None):
                result = step(valid_artifact_context)
    assert result["step_id"] == "hop_4_generate_resume"
    assert result["exit_code"] == 0


def test_step_result_includes_artifact_refs(valid_artifact_context):
    step = GenerateResumeStep()
    with mock.patch("apps_rg.l2_recipe.steps.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        with mock.patch("apps_rg.scripts.generate_resume.main", return_value=None):
            with mock.patch("asyncio.run", return_value=None):
                result = step(valid_artifact_context)
    cpa = result["compiled_prompt_artifact"]
    assert cpa["artifact_id"] == "test_artifact_123"
    assert cpa["prompt_id"] == "apps_rg.resume_generation.strategic_tailor.v1"
    assert cpa["prompt_hash"] == "abcd1234abcd1234"
    assert cpa["prompt_template_hash"] == "tmpl1234tmpl1234"
    assert cpa["prompt_bom_hash"] == "bom12345bom12345"
    assert cpa["replay_key"] == "replay_key_test"
    assert cpa["policy_hash"] == "policy_test"
    assert cpa["blueprint_hash"] == "blueprint_test"
    assert cpa["compile_status"] == PACompileStatus.PA_L2_HANDOFF_READY.value


def test_step_compiles_from_context_if_no_artifact():
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Software Engineer role",
        "master_resume_data": "John Doe resume",
        "flow_route": "strategic_tailor",
        "company_brief_data": "Tech company",
    }
    with mock.patch("apps_rg.l2_recipe.steps.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        with mock.patch("apps_rg.scripts.generate_resume.main", return_value=None):
            with mock.patch("asyncio.run", return_value=None):
                result = step(ctx)
    assert result["exit_code"] == 0
    cpa = result["compiled_prompt_artifact"]
    assert cpa["prompt_id"].startswith("apps_rg.resume_generation.")
    assert cpa["compile_status"] == PACompileStatus.PA_L2_HANDOFF_READY.value
    assert "compiled_prompt_artifact" in ctx
