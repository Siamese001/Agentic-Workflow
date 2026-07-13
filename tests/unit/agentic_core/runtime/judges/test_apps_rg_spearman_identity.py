from pathlib import Path

import pytest

from agentic_core.runtime.judges.judge_registry import JudgeRegistry
from agentic_core.runtime.judges.llm_judge_gateway import LLMJudgeGateway, LLMJudgeRequest
from agentic_core.runtime.judges.resume_judges.executive_positioning import (
    ExecutivePositioningJudge,
)
from agentic_core.runtime.providers.provider_registry import ProviderRegistry
from apps_shared.judge_registry import resolve_judge

JUDGE_ID = "rg::executive_positioning_judge::v1"
CORE_MODULE = "agentic_core.runtime.judges.resume_judges.executive_positioning"


def test_active_apps_rg_judge_has_single_canonical_identity():
    shared = resolve_judge("apps_rg", "executive_positioning")
    assert shared.import_path == CORE_MODULE
    assert shared.importable is True
    assert shared.is_stub is False

    registry = JudgeRegistry()
    registry.load_from_grader_roster(Path("apps_rg/config/domain_contract/grader_roster.yaml"))
    profile = registry.get_profile(JUDGE_ID)
    assert profile.judge_implementation_ref == (f"{CORE_MODULE}:ExecutivePositioningJudge")
    assert profile.informational_only is True
    assert profile.required_for_exit is False

    providers = ProviderRegistry()
    providers.load_from_yaml(Path("apps_rg/config/provider_profiles.yaml"))
    provider = providers.get_profile(profile.provider_profile_ref)
    assert provider.profile_id == "apps_rg::provider::local_qwen_generator::v1"

    assert ExecutivePositioningJudge.GRADER_REF == JUDGE_ID
    runtime_prompt = ExecutivePositioningJudge().build_prompt(
        candidate_text="identity probe",
        context_metadata={},
    )
    assert "RUBRIC — executive_positioning" in runtime_prompt.user_prompt


def test_runtime_gateway_builds_prompt_through_core_judge():
    registry = JudgeRegistry()
    registry.load_from_grader_roster(Path("apps_rg/config/domain_contract/grader_roster.yaml"))
    profile = registry.get_profile(JUDGE_ID)
    gateway = LLMJudgeGateway(registry=registry)
    prompt = gateway._build_judge_prompt(  # noqa: SLF001 - identity contract test
        LLMJudgeRequest(
            judge_profile_ref=JUDGE_ID,
            candidate_text="Led a global organization and delivered measurable savings.",
            context_metadata={"target_role": "VP", "target_level": "executive"},
        ),
        profile,
    )
    assert "RUBRIC — executive_positioning" in prompt
    assert "Target" not in prompt or "TARGET CONTEXT" in prompt


def test_runtime_gateway_rejects_malformed_core_judge_response():
    registry = JudgeRegistry()
    registry.load_from_grader_roster(Path("apps_rg/config/domain_contract/grader_roster.yaml"))
    profile = registry.get_profile(JUDGE_ID)
    gateway = LLMJudgeGateway(registry=registry)
    with pytest.raises(ValueError, match="judge response parse failed"):
        gateway._parse_judge_response("not-json", profile)  # noqa: SLF001
