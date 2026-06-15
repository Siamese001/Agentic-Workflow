"""W2 SSOT parity guard (plan apps-rg-config-ssot-consolidation): provider_profiles.yaml
``judge_models`` is the source-of-record for per-tier proof-judge models, and the code
``profile_defaults[0]`` in section_judge_profile.py are kept EQUAL to it.

Same migration pattern as test_section_model_limits_ssot.py (literal kept == YAML). This guards
drift between the YAML SSOT and the code fallback until W4 repoints the resolver to read the YAML."""
from __future__ import annotations

from pathlib import Path

import yaml

from apps_rg.runtime.judges.section_judge_profile import _ENHANCED_PROFILE, _STANDARD_PROFILE

_YAML = Path(__file__).resolve().parents[3] / "apps_rg" / "config" / "provider_profiles.yaml"


def _judge_models() -> dict:
    data = yaml.safe_load(_YAML.read_text(encoding="utf-8"))
    return (data or {}).get("judge_models") or {}


def test_judge_models_block_present_and_complete():
    jm = _judge_models()
    assert set(jm) >= {"enhanced", "standard"}
    for tier in ("enhanced", "standard"):
        assert set(jm[tier]) >= {"gemini_pro", "openai_chatgpt", "anthropic_claude"}


def test_yaml_enhanced_matches_code_profile_defaults():
    jm = _judge_models()["enhanced"]
    for provider, prof in _ENHANCED_PROFILE.items():
        assert jm[provider] == prof["profile_defaults"][0], f"enhanced/{provider} drift"


def test_yaml_standard_matches_code_profile_defaults():
    jm = _judge_models()["standard"]
    for provider, prof in _STANDARD_PROFILE.items():
        assert jm[provider] == prof["profile_defaults"][0], f"standard/{provider} drift"


def test_resolver_sources_enhanced_gemini_from_yaml_when_env_absent():
    # W3 repoint: with no APPS_RG_*_JUDGE_MODEL_* env overrides, the resolver sources the model
    # from the YAML judge_models SSOT. enhanced/gemini_pro avoids the standard-only google_ai_pro
    # special-case, so the YAML candidate is the first non-forbidden one.
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

    res = resolve_section_proof_judge_model("executive_summary", "gemini_pro", environ={})
    assert res.model_actual == _judge_models()["enhanced"]["gemini_pro"]
    assert res.model_source == "yaml_judge_models"
    assert not res.blocked


def test_resolver_sources_standard_anthropic_from_yaml_when_env_absent():
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

    res = resolve_section_proof_judge_model("unify_narrative", "anthropic_claude", environ={})
    assert res.model_actual == _judge_models()["standard"]["anthropic_claude"]
    assert res.model_source == "yaml_judge_models"
    assert not res.blocked


def test_w4_enhanced_anthropic_judge_migrated_to_sonnet():
    # W4: APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED removed from .env; the SSOT pins the enhanced
    # anthropic judge to claude-sonnet-4-6 (the actual prior runtime value). With env absent, the
    # resolver sources sonnet from the YAML judge_models SSOT (not the opus code aspiration).
    from apps_rg.runtime.judges.section_judge_profile import resolve_section_proof_judge_model

    assert _judge_models()["enhanced"]["anthropic_claude"] == "claude-sonnet-4-6"
    res = resolve_section_proof_judge_model("executive_summary", "anthropic_claude", environ={})
    assert res.model_actual == "claude-sonnet-4-6"
    assert res.model_source == "yaml_judge_models"
    assert not res.blocked
