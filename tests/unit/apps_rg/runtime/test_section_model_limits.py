"""Wave 4.2 — apps_rg untested-hotspot coverage.

Covers ``apps_rg/runtime/section_model_limits.py``: the provider-neutral
section-model identity/budget constants and the env-override resolver
``external_claude_generation_model``.
"""
from __future__ import annotations

import importlib

import apps_rg.runtime.section_model_limits as sml
from apps_rg.runtime.section_model_limits import (
    DEFAULT_EXTERNAL_CLAUDE_MODEL,
    SECTION_MODEL_MAX_MODEL_LEN,
    external_claude_generation_model,
)


class TestConstants:
    def test_default_model_identity(self) -> None:
        assert DEFAULT_EXTERNAL_CLAUDE_MODEL == "claude-haiku-4-5"

    def test_max_model_len_is_positive_int(self) -> None:
        assert isinstance(SECTION_MODEL_MAX_MODEL_LEN, int)
        assert SECTION_MODEL_MAX_MODEL_LEN > 0

    def test_exports(self) -> None:
        assert set(sml.__all__) == {
            "DEFAULT_EXTERNAL_CLAUDE_MODEL",
            "SECTION_MODEL_ID",
            "SECTION_MODEL_MAX_MODEL_LEN",
            "external_claude_generation_model",
        }


class TestExternalClaudeGenerationModel:
    def test_default_when_unset(self) -> None:
        assert external_claude_generation_model({}) == DEFAULT_EXTERNAL_CLAUDE_MODEL

    def test_env_override_applied(self) -> None:
        out = external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-opus-4-8"})
        assert out == "claude-opus-4-8"

    def test_blank_override_falls_back_to_default(self) -> None:
        assert external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "   "}) == (
            DEFAULT_EXTERNAL_CLAUDE_MODEL
        )

    def test_whitespace_is_stripped(self) -> None:
        out = external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "  claude-x  "})
        assert out == "claude-x"

    def test_reads_os_environ_when_none(self, monkeypatch) -> None:
        monkeypatch.setenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", "claude-env-model")
        assert external_claude_generation_model() == "claude-env-model"

    def test_section_model_id_tracks_env_at_import(self, monkeypatch) -> None:
        monkeypatch.setenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", "claude-reimport-model")
        reloaded = importlib.reload(sml)
        try:
            assert reloaded.SECTION_MODEL_ID == "claude-reimport-model"
        finally:
            monkeypatch.delenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", raising=False)
            importlib.reload(sml)
