"""Test: sealed L2 output references compiled prompt artifact.

Verifies that a successful simulated generation includes all required
prompt artifact references in the sealed step output.
"""

from __future__ import annotations

from unittest import mock

import pytest

from apps_rg.l2_recipe.steps import GenerateResumeStep
from apps_rg.prompt_assembly.contracts import PACompileStatus


@pytest.fixture
def sealed_result() -> dict:
    step = GenerateResumeStep()
    ctx = {
        "jd_data": "Software Engineer role requiring Python",
        "master_resume_data": "Experienced Python developer resume",
        "flow_route": "strategic_tailor",
        "company_brief_data": "Tech startup brief",
    }
    with mock.patch("apps_rg.l2_recipe.steps.Path") as mock_path:
        mock_path.return_value.exists.return_value = False
        with mock.patch("apps_rg.scripts.generate_resume.main", return_value=None):
            with mock.patch("asyncio.run", return_value=None):
                return step(ctx)


def test_result_has_compiled_prompt_artifact(sealed_result):
    assert "compiled_prompt_artifact" in sealed_result


def test_artifact_has_prompt_hash(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert len(cpa["prompt_hash"]) == 16


def test_artifact_has_template_hash(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert len(cpa["prompt_template_hash"]) == 16


def test_artifact_has_bom_hash(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert len(cpa["prompt_bom_hash"]) == 16


def test_artifact_has_replay_key(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert len(cpa["replay_key"]) >= 8


def test_artifact_has_policy_hash(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert "policy_hash" in cpa


def test_artifact_has_blueprint_hash(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert "blueprint_hash" in cpa


def test_artifact_has_provider_lane(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert "provider_lane" in cpa


def test_artifact_has_compile_status_ready(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert cpa["compile_status"] == PACompileStatus.PA_L2_HANDOFF_READY.value


def test_artifact_has_source_refs(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert "source_refs" in cpa
    assert isinstance(cpa["source_refs"], dict)


def test_artifact_has_prompt_id(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert cpa["prompt_id"].startswith("apps_rg.resume_generation.")


def test_artifact_has_output_schema(sealed_result):
    cpa = sealed_result["compiled_prompt_artifact"]
    assert cpa["output_schema_ref"] == "generated_resume.json"
