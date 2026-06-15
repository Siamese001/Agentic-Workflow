"""W2 SSOT guard (plan apps-rg-config-ssot-consolidation): per-section reasoning intensity
resolves from provider_profiles.yaml via section_model_limits.resolve_section_reasoning_intensity.

Mirrors test_section_model_limits_ssot.py — proves the resolver mechanics + fail-soft fallback.
The resolver is not yet threaded into live generation (W3); these tests are its consumer."""
from __future__ import annotations

from apps_rg.runtime.section_model_limits import (
    DEFAULT_SECTION_REASONING,
    resolve_section_reasoning_intensity,
)


def test_default_reasoning_has_required_keys():
    r = resolve_section_reasoning_intensity(None)
    assert "temperature" in r
    assert "max_output_tokens" in r


def test_unknown_section_falls_back_to_default():
    unknown = resolve_section_reasoning_intensity("section_that_does_not_exist")
    base = resolve_section_reasoning_intensity(None)
    assert unknown == base


def test_per_lane_override_resolves_from_yaml():
    # executive_summary carries a per-lane override in reasoning_by_section.
    es = resolve_section_reasoning_intensity("executive_summary")
    assert isinstance(es["temperature"], (int, float))
    assert int(es["max_output_tokens"]) >= 1


def test_returns_fresh_dict_not_shared_state():
    a = resolve_section_reasoning_intensity(None)
    a["temperature"] = 999
    b = resolve_section_reasoning_intensity(None)
    assert b["temperature"] != 999


def test_literal_fallback_shape_matches_contract():
    assert set(DEFAULT_SECTION_REASONING) >= {"temperature", "max_output_tokens"}
