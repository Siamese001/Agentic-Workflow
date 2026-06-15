"""W1.1 model-profile SSOT resolution tests.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (DoD-1).
"""

from __future__ import annotations

import pytest

from apps_lic.config.model_profiles import (
    CLAUDE_X1D_PROVIDER_PROFILE,
    resolve_generator_base_url,
    resolve_generator_model,
    resolve_generator_provider,
    resolve_x1d_judge_model,
    resolve_x1d_judge_provider,
    resolve_x1d_judge_provider_profile,
    resolve_x1d_judge_transport_model_id,
)
from apps_lic.policy.reasoning_intensity import (
    compact_policy,
    default_reasoning_policy,
    select_reasoning_policy,
)


def test_generator_model_resolves_from_yaml_ssot() -> None:
    assert resolve_generator_model() == "Qwen/Qwen2.5-32B-Instruct-AWQ"
    assert resolve_generator_provider() == "vllm"
    assert resolve_generator_base_url().startswith("http")


def test_generator_model_env_override_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_LIC_QWEN_MODEL", "Qwen/Qwen2.5-7B-Instruct-AWQ")
    assert resolve_generator_model() == "Qwen/Qwen2.5-7B-Instruct-AWQ"


def test_x1d_judge_resolves_to_independent_claude_not_qwen() -> None:
    assert resolve_x1d_judge_provider() == "claude"
    assert resolve_x1d_judge_model() == "Claude Sonnet 4.6"
    assert resolve_x1d_judge_transport_model_id() == "claude-sonnet-4-6"
    assert resolve_x1d_judge_provider_profile() == CLAUDE_X1D_PROVIDER_PROFILE
    assert "qwen" not in CLAUDE_X1D_PROVIDER_PROFILE.lower()


def test_reasoning_policy_x1d_provider_is_claude_ssot() -> None:
    # No live policy projection may declare the retired qwen_vllm_x1d provider.
    assert default_reasoning_policy()["x1d_provider_profile"] == CLAUDE_X1D_PROVIDER_PROFILE
    assert compact_policy({})["x1d_provider_profile"] == CLAUDE_X1D_PROVIDER_PROFILE
    strict = select_reasoning_policy(
        {
            "entity_refs": {
                "lead_profile": {
                    "verified_name": "Scott Hallworth",
                    "title": "Chief Digital Officer",
                    "company_name": "AIG",
                }
            }
        }
    )
    assert strict["x1d_provider_profile"] == CLAUDE_X1D_PROVIDER_PROFILE
    assert "qwen_vllm_x1d" != strict["x1d_provider_profile"]
