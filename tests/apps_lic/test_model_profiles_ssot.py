"""W1.1 model-profile SSOT resolution tests.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (DoD-1).
"""

from __future__ import annotations

import pytest

from apps_lic.config import model_profiles as mp
from apps_lic.config.model_profiles import (
    GPT_X1D_PROVIDER_PROFILE,
    ModelProfileSSOTError,
    resolve_generator_base_url,
    resolve_generator_model,
    resolve_generator_provider,
    resolve_generator_transport_model_id,
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
    assert resolve_generator_model() == "Claude Sonnet 5"
    assert resolve_generator_provider() == "claude"
    assert resolve_generator_transport_model_id() == "claude-sonnet-5"
    assert resolve_generator_base_url() == ""


def test_generator_model_env_override_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_LIC_GENERATOR_MODEL", "Claude Opus test")
    assert resolve_generator_model() == "Claude Opus test"


def test_x1d_judge_resolves_to_independent_gpt() -> None:
    assert resolve_x1d_judge_provider() == "openai"
    assert resolve_x1d_judge_model() == "GPT-5.5"
    assert resolve_x1d_judge_transport_model_id() == "gpt-5.5"
    assert resolve_x1d_judge_provider_profile() == GPT_X1D_PROVIDER_PROFILE


def test_reasoning_policy_x1d_provider_is_gpt_ssot() -> None:
    assert default_reasoning_policy()["x1d_provider_profile"] == GPT_X1D_PROVIDER_PROFILE
    assert compact_policy({})["x1d_provider_profile"] == GPT_X1D_PROVIDER_PROFILE
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
    assert strict["x1d_provider_profile"] == GPT_X1D_PROVIDER_PROFILE


def test_model_profile_ssot_missing_file_fails_closed(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mp.load_model_profiles.cache_clear()
    monkeypatch.setattr(mp, "_MODEL_PROFILES_PATH", tmp_path / "missing.yaml")
    with pytest.raises(ModelProfileSSOTError):
        mp.load_model_profiles()
    mp.load_model_profiles.cache_clear()
