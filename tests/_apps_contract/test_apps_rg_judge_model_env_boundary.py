"""W3 — apps_rg proof judges: APPS_RG_*_JUDGE_MODEL_* primary; spine vars classified."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.judges.section_judge_profile import (
    resolve_section_proof_judge_model,
)


def test_google_standard_tier_uses_apps_rg_env_not_spine_when_set() -> None:
    env = {
        "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD": "gemini-2.5-pro",
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
        "GOOGLE_AI_MODEL": "gemini-2.0-flash",
    }
    r = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert r.model_actual == "gemini-2.5-pro"
    assert r.model_source == "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD"
    assert r.model_source != "GOOGLE_AI_PRO_MODEL"


def test_google_standard_falls_back_to_google_ai_pro_model_when_apps_rg_unset() -> None:
    """LIMITED_FALLBACK — GOOGLE_AI_PRO_MODEL env_tier before profile_default (NEEDS_DECISION)."""
    env = {
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-pro",
    }
    r = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert r.model_actual == "gemini-2.5-pro"
    assert r.model_source == "GOOGLE_AI_PRO_MODEL"
    assert "APPS_RG" not in (r.model_source or "")


def test_google_standard_spine_flash_env_is_forbidden_then_profile_default() -> None:
    """Flash-tier spine var is classified advisory-only; profile_default wins (NEEDS_DECISION)."""
    env = {
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
    }
    r = resolve_section_proof_judge_model("headline", "gemini_pro", env)
    assert r.model_actual == "gemini-2.5-pro"
    assert r.model_source == "profile_default"


def test_openai_standard_does_not_use_openai_model_env_when_apps_rg_set() -> None:
    env = {
        "APPS_RG_OPENAI_JUDGE_MODEL_STANDARD": "gpt-5.5",
        "OPENAI_MODEL": "gpt-5.1",
    }
    r = resolve_section_proof_judge_model("headline", "openai_chatgpt", env)
    assert r.model_actual == "gpt-5.5"
    assert r.model_source == "APPS_RG_OPENAI_JUDGE_MODEL_STANDARD"


def test_anthropic_standard_does_not_use_anthropic_model_env_when_apps_rg_set() -> None:
    env = {
        "APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD": "claude-sonnet-4-6",
        "ANTHROPIC_MODEL": "claude-haiku-4-5",
    }
    r = resolve_section_proof_judge_model("headline", "anthropic_claude", env)
    assert r.model_actual == "claude-sonnet-4-6"
    assert r.model_source == "APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD"


def test_enhanced_google_never_reads_googe_ai_pro_model_tier_env() -> None:
    env = {
        "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED": "gemini-3.1-pro-preview",
        "GOOGLE_AI_PRO_MODEL": "gemini-2.5-flash",
    }
    r = resolve_section_proof_judge_model("executive_summary", "gemini_pro", env)
    assert r.model_source == "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED"


def test_executive_summary_x1d_documents_spine_fallback_metadata() -> None:
    """Static: legacy x1d module lists spine fallbacks; proof path uses section_judge_profile."""
    from apps_rg.runtime.judges import executive_summary_x1d as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "GOOGLE_AI_PRO_MODEL" in src
    assert "OPENAI_MODEL" in src
    assert "APPS_RG_GOOGLE_JUDGE_MODEL" in src or "APPS_RG_GEMINI_JUDGE_MODEL" in src
