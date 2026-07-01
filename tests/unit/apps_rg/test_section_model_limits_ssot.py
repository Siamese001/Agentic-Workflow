"""SSOT parity + resolution tests for apps_rg section model identity."""

from __future__ import annotations

import pytest

import apps_rg.runtime.section_model_limits as sml


def _yaml_data() -> dict:
    import yaml

    return yaml.safe_load(sml._PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))


def _yaml_openai_section_model(section_id: str) -> str:
    return _yaml_data()["profiles"]["external_openai_generator"]["model_by_section"][section_id]


def _yaml_claude_section_model(section_id: str) -> str:
    return _yaml_data()["profiles"]["external_claude_generator"]["model_by_section"][section_id]


def test_generation_profiles_have_no_default_model() -> None:
    profiles = _yaml_data()["profiles"]
    assert "default_model" not in profiles["external_claude_generator"]
    assert "default_model" not in profiles["external_openai_generator"]


def test_explicit_claude_section_pins() -> None:
    for section_id in (
        "competencies",
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
        "headline",
        "executive_summary",
    ):
        assert (
            sml.resolve_section_generation_model(section_id)
            == _yaml_claude_section_model(section_id)
            == "claude-sonnet-5"
        )


def test_explicit_openai_section_pins() -> None:
    for section_id in ("unify_narrative", "ibm_narrative", "insurtech_narrative", "ey_narrative"):
        assert (
            sml.external_openai_generation_model(section_id=section_id)
            == _yaml_openai_section_model(section_id)
            == "gpt-5.4-mini-2026-03-17"
        )


def test_missing_section_id_fails_closed() -> None:
    with pytest.raises(sml.SectionModelSSOTError):
        sml.resolve_section_generation_model(None)
    with pytest.raises(sml.SectionModelSSOTError):
        sml.external_claude_generation_model({})
    with pytest.raises(sml.SectionModelSSOTError):
        sml.external_openai_generation_model(section_id="headline")


def test_env_override_is_ignored_for_explicit_section() -> None:
    env = {"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-zzz-9"}
    assert sml.resolve_section_generation_model("competencies", env) == "claude-sonnet-5"


def test_openai_model_source_reports_only_configured_section() -> None:
    assert (
        sml.external_openai_generation_model_source("unify_narrative")
        == "apps_rg/config/provider_profiles.yaml:profiles.external_openai_generator.model_by_section.unify_narrative"
    )
    with pytest.raises(sml.SectionModelSSOTError):
        sml.external_openai_generation_model_source("headline")


def test_selector_models_are_explicit_and_advisory() -> None:
    assert sml.resolve_selector_provider_model("competencies_graph_pool_selector") == (
        "anthropic_claude",
        "claude-sonnet-5",
        "apps_rg/config/provider_profiles.yaml:selector_models.competencies_graph_pool_selector.model",
    )
    assert sml.resolve_selector_provider_model("employment_bullet_pool_selector") == (
        "anthropic_claude",
        "claude-sonnet-5",
        "apps_rg/config/provider_profiles.yaml:selector_models.employment_bullet_pool_selector.model",
    )


def test_missing_yaml_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(sml, "_PROVIDER_PROFILES_PATH", tmp_path / "nope.yaml")
    with pytest.raises(sml.SectionModelSSOTError):
        sml.resolve_section_generation_model("competencies")


def test_malformed_yaml_fails_closed(monkeypatch, tmp_path) -> None:
    bad = tmp_path / "provider_profiles.yaml"
    bad.write_text("{ not: : valid yaml", encoding="utf-8")
    monkeypatch.setattr(sml, "_PROVIDER_PROFILES_PATH", bad)
    with pytest.raises(sml.SectionModelSSOTError):
        sml.resolve_section_generation_model("competencies")
