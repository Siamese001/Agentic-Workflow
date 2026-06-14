"""SSOT parity + resolution tests for apps_rg section model identity.

The single source of truth for the apps_rg external Claude generation model is
``apps_rg/config/provider_profiles.yaml`` (``external_claude_generator.default_model``).
``section_model_limits.py`` resolves from it with the precedence:
env ``APPS_RG_EXTERNAL_CLAUDE_MODEL`` -> YAML SSOT -> literal fallback (fail-soft).

Plan: config-drift wave 2 (model-ID SSOT). Guards against the prior latent drift
where ``DEFAULT_EXTERNAL_CLAUDE_MODEL`` duplicated the YAML value as a hardcoded
literal that the docstring merely *claimed* to match.
"""

from __future__ import annotations

import apps_rg.runtime.section_model_limits as sml


def _yaml_default_model() -> str:
    import yaml

    data = yaml.safe_load(sml._PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
    return data["profiles"]["external_claude_generator"]["default_model"]


def test_fallback_literal_matches_yaml_ssot() -> None:
    """The fail-soft literal must equal the YAML SSOT so they cannot diverge."""
    assert sml.DEFAULT_EXTERNAL_CLAUDE_MODEL == _yaml_default_model()


def test_resolves_from_yaml_when_no_env() -> None:
    # Explicit empty environ -> no operator override -> YAML SSOT value wins.
    assert sml.external_claude_generation_model({}) == _yaml_default_model()


def test_ssot_reader_returns_yaml_value() -> None:
    assert sml._ssot_default_model() == _yaml_default_model()


def test_env_override_wins() -> None:
    assert (
        sml.external_claude_generation_model({"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-zzz-9"})
        == "claude-zzz-9"
    )


def test_failsoft_to_literal_when_yaml_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(sml, "_PROVIDER_PROFILES_PATH", tmp_path / "nope.yaml")
    assert sml._ssot_default_model() is None
    assert sml.external_claude_generation_model({}) == sml.DEFAULT_EXTERNAL_CLAUDE_MODEL


def test_failsoft_on_malformed_yaml(monkeypatch, tmp_path) -> None:
    bad = tmp_path / "provider_profiles.yaml"
    bad.write_text("{ not: : valid yaml", encoding="utf-8")
    monkeypatch.setattr(sml, "_PROVIDER_PROFILES_PATH", bad)
    assert sml._ssot_default_model() is None
    assert sml.external_claude_generation_model({}) == sml.DEFAULT_EXTERNAL_CLAUDE_MODEL
