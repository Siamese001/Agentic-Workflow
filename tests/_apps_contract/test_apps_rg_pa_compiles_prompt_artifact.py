"""Test: apps_rg PA compiler emits a valid CompiledPromptArtifact.

Verifies that given valid mock JD/resume/brief, the compiler produces
an artifact with all required fields and PA_L2_HANDOFF_READY status.
"""

from __future__ import annotations

import pytest

from apps_rg.prompt_assembly.contracts import (
    AppsRgCompiledPromptArtifact,
    AppsRgPromptRequest,
    PACompileStatus,
)
from apps_rg.prompt_assembly.compiler import compile_prompt


@pytest.fixture
def valid_request() -> AppsRgPromptRequest:
    return AppsRgPromptRequest(
        flow_route="strategic_tailor",
        jd_data="Software Engineer at Acme Corp. Requires Python, AWS.",
        master_resume_data="John Doe. 10 years Python. AWS certified.",
        company_brief_data="Acme Corp is a tech company.",
        user_task="Tailor my resume for this role",
        policy_hash="policy_abc123",
        blueprint_hash="blueprint_def456",
        provider_lane="anthropic_claude",
        symbolic_model_id="claude-3-5-sonnet",
    )


def test_compile_returns_artifact(valid_request):
    artifact = compile_prompt(valid_request)
    assert isinstance(artifact, AppsRgCompiledPromptArtifact)


def test_compile_status_is_ready(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.compile_status == PACompileStatus.PA_L2_HANDOFF_READY.value


def test_artifact_has_prompt_id(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.prompt_id == "apps_rg.resume_generation.strategic_tailor.v1"


def test_artifact_has_prompt_template_hash(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.prompt_template_hash) == 16


def test_artifact_has_prompt_bom_hash(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.prompt_bom_hash) == 16


def test_artifact_has_prompt_hash(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.prompt_hash) == 16


def test_artifact_has_policy_hash(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.policy_hash == "policy_abc123"


def test_artifact_has_blueprint_hash(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.blueprint_hash == "blueprint_def456"


def test_artifact_has_replay_key(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.replay_key) >= 8


def test_artifact_has_provider_lane(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.provider_lane == "anthropic_claude"


def test_artifact_has_output_schema_ref(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.output_schema_ref == "generated_resume.json"


def test_artifact_has_output_schema_hash(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.output_schema_hash) > 0


def test_artifact_has_structured_slots(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.structured_slots_used) >= 5


def test_artifact_has_source_refs(valid_request):
    artifact = compile_prompt(valid_request)
    assert "jd_data_hash" in artifact.source_refs
    assert "master_resume_hash" in artifact.source_refs


def test_artifact_has_provider_messages(valid_request):
    artifact = compile_prompt(valid_request)
    assert len(artifact.provider_specific_messages) >= 2
    roles = [m["role"] for m in artifact.provider_specific_messages]
    assert "system" in roles
    assert "user" in roles


def test_artifact_is_ready_method(valid_request):
    artifact = compile_prompt(valid_request)
    assert artifact.is_ready()


def test_artifact_to_dict(valid_request):
    artifact = compile_prompt(valid_request)
    d = artifact.to_dict()
    assert isinstance(d, dict)
    assert d["prompt_id"] == artifact.prompt_id
    assert d["compile_status"] == PACompileStatus.PA_L2_HANDOFF_READY.value


@pytest.mark.parametrize("flow", [
    "strategic_tailor",
    "tailor_existing",
    "generate_scratch",
    "enhance_current",
])
def test_all_flows_compile(flow):
    req = AppsRgPromptRequest(
        flow_route=flow,
        jd_data="Test JD",
        master_resume_data="Test Resume",
    )
    artifact = compile_prompt(req)
    assert artifact.is_ready()
    assert artifact.prompt_id.startswith("apps_rg.resume_generation.")
