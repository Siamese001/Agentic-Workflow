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
