"""SSOT parity + resolution tests for apps_rg section model identity.

The single source of truth for the apps_rg external Claude generation model is
``apps_rg/config/provider_profiles.yaml`` (``external_claude_generator.default_model``).
``section_model_limits.py`` resolves from it directly. Environment variables do
not override apps_rg generator model identity.

Plan: config-drift wave 2 (model-ID SSOT). Guards against the prior latent drift
where code duplicated the YAML value as a hardcoded literal that the docstring
merely *claimed* to match.
"""

from __future__ import annotations

import apps_rg.runtime.section_model_limits as sml


def _yaml_default_model() -> str:
    import yaml

    data = yaml.safe_load(sml._PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
    return data["profiles"]["external_claude_generator"]["default_model"]


def _yaml_openai_default_model() -> str:
    import yaml

    data = yaml.safe_load(sml._PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
    return data["profiles"]["external_openai_generator"]["default_model"]


def test_exported_default_matches_yaml_ssot() -> None:
    """The exported default is resolved from YAML, not duplicated in code."""
    assert sml.DEFAULT_EXTERNAL_CLAUDE_MODEL == _yaml_default_model()
    assert sml.DEFAULT_EXTERNAL_OPENAI_MODEL == _yaml_openai_default_model()


def test_resolves_from_yaml_when_no_env() -> None:
    # Explicit empty environ -> no operator override -> YAML SSOT value wins.
    assert sml.external_claude_generation_model({}) == _yaml_default_model()


def test_ssot_reader_returns_yaml_value() -> None:
    assert sml._ssot_default_model() == _yaml_default_model()
    assert sml._ssot_default_model("external_openai_generator") == _yaml_openai_default_model()


def test_env_override_is_ignored() -> None:
    assert (
        sml.external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-zzz-9"})
        == _yaml_default_model()
    )


def test_openai_env_override_is_ignored() -> None:
    assert (
        sml.external_openai_generation_model({"APPS_RG_EXTERNAL_OPENAI_MODEL": "gpt-custom"})
        == _yaml_openai_default_model()
    )


def test_missing_yaml_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(sml, "_PROVIDER_PROFILES_PATH", tmp_path / "nope.yaml")
    import pytest

    with pytest.raises(sml.SectionModelSSOTError):
        sml._ssot_default_model()
    with pytest.raises(sml.SectionModelSSOTError):
        sml.external_claude_generation_model({})


def test_malformed_yaml_fails_closed(monkeypatch, tmp_path) -> None:
    bad = tmp_path / "provider_profiles.yaml"
    bad.write_text("{ not: : valid yaml", encoding="utf-8")
    monkeypatch.setattr(sml, "_PROVIDER_PROFILES_PATH", bad)
    import pytest

    with pytest.raises(sml.SectionModelSSOTError):
        sml._ssot_default_model()
