"""SSOT: the apps_rg per-section generator model resolves from provider_profiles.yaml.

Guards the single-SSOT consolidation: model_by_section (Haiku cost tier) + default_model
(Sonnet high-signal) in apps_rg/config/provider_profiles.yaml, resolved by
section_model_limits.resolve_section_generation_model(section_id). environ={} is passed so the
test is deterministic regardless of any operator APPS_RG_EXTERNAL_CLAUDE_MODEL pin in the
process env.
"""
from __future__ import annotations

from apps_rg.runtime.section_model_limits import resolve_section_generation_model as resolve

_HAIKU = "claude-haiku-4-5"
_SONNET = "claude-sonnet-4-6"


def test_haiku_cost_tier_lanes() -> None:
    for section in ("competencies", "unify_narrative", "ibm_narrative", "insurtech_narrative", "ey_narrative"):
        assert resolve(section, environ={}) == _HAIKU, section


def test_sonnet_high_signal_lanes() -> None:
    for section in ("unify_bullets", "ibm_bullets", "insurtech_bullets", "ey_bullets", "executive_summary", "headline"):
        assert resolve(section, environ={}) == _SONNET, section


def test_default_is_sonnet() -> None:
    assert resolve(None, environ={}) == _SONNET
    assert resolve("some_unmapped_section", environ={}) == _SONNET


def test_operator_env_pin_overrides_all_sections() -> None:
    pin = {"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-opus-4-8"}
    assert resolve("competencies", environ=pin) == "claude-opus-4-8"
    assert resolve("unify_bullets", environ=pin) == "claude-opus-4-8"
