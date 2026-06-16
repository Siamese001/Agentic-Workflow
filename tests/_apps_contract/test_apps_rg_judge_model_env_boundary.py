"""apps_rg proof judges: model selection is YAML SSOT-only."""

from __future__ import annotations

from pathlib import Path

import yaml

from apps_rg.runtime.judges.section_judge_profile import (
    resolve_section_proof_judge_model,
)

_SSOT = Path(__file__).resolve().parents[2] / "apps_rg" / "config" / "provider_profiles.yaml"


def _yaml_judge_model(tier: str, provider_key: str) -> str:
    data = yaml.safe_load(_SSOT.read_text(encoding="utf-8"))
    return str(data["judge_models"][tier][provider_key])


def test_google_standard_uses_yaml_not_env() -> None:
    env = {
        "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD": "gemini-2.5-flash",
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
        "GOOGLE_AI_MODEL": "gemini-2.0-flash",
    }
    r = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert r.model_actual == _yaml_judge_model("standard", "gemini_pro")
    assert r.model_source == "yaml_judge_models"


def test_google_standard_no_spine_model_fallback() -> None:
    env = {
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-pro",
    }
    r = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert r.model_actual == _yaml_judge_model("standard", "gemini_pro")
    assert r.model_source == "yaml_judge_models"


def test_openai_standard_uses_yaml_not_env() -> None:
    env = {
        "APPS_RG_OPENAI_JUDGE_MODEL_STANDARD": "gpt-5.5-pro",
        "OPENAI_MODEL": "gpt-5.1",
    }
    r = resolve_section_proof_judge_model("headline", "openai_chatgpt", env)
    assert r.model_actual == _yaml_judge_model("standard", "openai_chatgpt")
    assert r.model_source == "yaml_judge_models"


def test_anthropic_standard_uses_yaml_not_env() -> None:
    env = {
        "APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD": "claude-haiku-4-5",
        "ANTHROPIC_MODEL": "claude-haiku-4-5",
    }
    r = resolve_section_proof_judge_model("headline", "anthropic_claude", env)
    assert r.model_actual == _yaml_judge_model("standard", "anthropic_claude")
    assert r.model_source == "yaml_judge_models"


def test_enhanced_google_uses_yaml_not_env() -> None:
    env = {
        "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED": "gemini-2.5-flash",
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
    }
    r = resolve_section_proof_judge_model("executive_summary", "gemini_pro", env)
    assert r.model_actual == _yaml_judge_model("enhanced", "gemini_pro")
    assert r.model_source == "yaml_judge_models"


def test_executive_summary_x1d_has_no_model_env_fallback_metadata() -> None:
    from apps_rg.runtime.judges import executive_summary_x1d as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert '"model_env"' not in src
    assert '"fallback_env"' not in src
    assert "APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK" not in src
