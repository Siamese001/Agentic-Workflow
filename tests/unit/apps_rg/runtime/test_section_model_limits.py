"""Wave 4.2 — apps_rg untested-hotspot coverage.

Covers ``apps_rg/runtime/section_model_limits.py``: the provider-neutral
section-model identity/budget constants and the SSOT-backed resolver.
"""
from __future__ import annotations

import apps_rg.runtime.section_model_limits as sml
from apps_rg.runtime.section_model_limits import (
    DEFAULT_EXTERNAL_CLAUDE_MODEL,
    SECTION_MODEL_MAX_MODEL_LEN,
    external_claude_generation_model,
)


class TestConstants:
    def test_default_model_identity(self) -> None:
        # SSOT-derived from provider_profiles.yaml. Default tier is sonnet, NOT haiku;
        # haiku is applied per-section via model_by_section, never as the default.
        assert DEFAULT_EXTERNAL_CLAUDE_MODEL == external_claude_generation_model({})
        assert "haiku" not in DEFAULT_EXTERNAL_CLAUDE_MODEL

    def test_max_model_len_is_positive_int(self) -> None:
        assert isinstance(SECTION_MODEL_MAX_MODEL_LEN, int)
        assert SECTION_MODEL_MAX_MODEL_LEN > 0

    def test_exports(self) -> None:
        assert set(sml.__all__) == {
            "DEFAULT_EXTERNAL_CLAUDE_MODEL",
            "DEFAULT_EXTERNAL_OPENAI_MODEL",
            "SECTION_MODEL_ID",
            "SECTION_MODEL_MAX_MODEL_LEN",
            "SectionModelSSOTError",
            "external_claude_generation_model",
            "external_openai_generation_model",
            "external_openai_generation_model_source",
            "resolve_section_generation_model",
            "runtime_limit_float",
            "runtime_limit_mapping",
            "runtime_limit_int",
            "runtime_limit_str",
        }


class TestExternalClaudeGenerationModel:
    def test_default_when_unset(self) -> None:
        assert external_claude_generation_model({}) == DEFAULT_EXTERNAL_CLAUDE_MODEL

    def test_env_override_ignored(self) -> None:
        out = external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-opus-4-8"})
        assert out == DEFAULT_EXTERNAL_CLAUDE_MODEL

    def test_blank_override_still_returns_default(self) -> None:
        assert external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "   "}) == (
            DEFAULT_EXTERNAL_CLAUDE_MODEL
        )

    def test_non_blank_override_still_ignored(self) -> None:
        out = external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "  claude-x  "})
        assert out == DEFAULT_EXTERNAL_CLAUDE_MODEL

    def test_does_not_read_os_environ_when_none(self, monkeypatch) -> None:
        monkeypatch.setenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", "claude-env-model")
        assert external_claude_generation_model() == DEFAULT_EXTERNAL_CLAUDE_MODEL
