"""SSOT: the apps_rg per-section generator model resolves from provider_profiles.yaml.

Guards the single-SSOT consolidation: model_by_section (Sonnet bullet tier) + default_model
(Sonnet baseline) with headline / executive_summary per-section Opus overrides in
apps_rg/config/provider_profiles.yaml, resolved by
section_model_limits.resolve_section_generation_model(section_id). environ={} is passed so the
test is deterministic; env model pins are ignored by design.
"""
from __future__ import annotations

from apps_rg.runtime.section_model_limits import resolve_section_generation_model as resolve

_SONNET = "claude-sonnet-4-6"
_OPUS = "claude-opus-4-8"


def test_sonnet_bullet_lanes() -> None:
    for section in ("unify_bullets", "ibm_bullets", "insurtech_bullets", "ey_bullets"):
        assert resolve(section, environ={}) == _SONNET, section


def test_opus_high_signal_lanes() -> None:
    for section in ("executive_summary", "headline"):
        assert resolve(section, environ={}) == _OPUS, section


def test_default_is_sonnet() -> None:
    assert resolve(None, environ={}) == _SONNET
    assert resolve("some_unmapped_section", environ={}) == _SONNET


def test_operator_env_pin_is_ignored() -> None:
    pin = {"APPS_RG_EXTERNAL_CLAUDE_MODEL": "claude-opus-4-8"}
    assert resolve("unify_bullets", environ=pin) == _SONNET
    assert resolve("headline", environ=pin) == _OPUS
