"""W9: the per-section model pin must be WIRED into the section provider call path.

Before this wiring, ``provider_profiles.yaml`` section overrides were ignored and the runtime
used the section-agnostic Claude default. These tests prove the resolver is now threaded
through ``call_section_model_provider`` via the ``_reasoning_section_lane`` tag / explicit
``section_id``, and that the gateway pins the resolved model on the Claude provider.
"""
from __future__ import annotations

import pytest

import apps_rg.runtime.providers.section_provider_call as spc
from apps_rg.runtime.providers.external_provider import ExternalProvider
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import ProviderProfile
from apps_rg.runtime.section_model_limits import resolve_section_generation_model


class _FakeGateway:
    def generate(self, profile, compiled, **kw):
        return ProviderResult(
            provider_requested="external_claude",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="captured-elsewhere",
            raw_model_output="{}",
            provider_response=None,
        )


def _capture_gateway_model(monkeypatch):
    captured: dict = {}

    def fake_build(claude_model=None, openai_model=None):
        captured["claude_model"] = claude_model
        captured["openai_model"] = openai_model
        return _FakeGateway()

    monkeypatch.setattr(spc, "build_section_provider_gateway", fake_build)
    return captured


def test_competencies_resolves_to_pinned_model_via_tag(monkeypatch):
    monkeypatch.delenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", raising=False)
    captured = _capture_gateway_model(monkeypatch)
    spc.call_section_model_provider(
        "external_claude",
        {"_reasoning_section_lane": "competencies", "messages": [{"role": "user", "content": "x"}]},
    )
    assert captured["claude_model"] == resolve_section_generation_model("competencies")
    assert captured["claude_model"] == "claude-sonnet-5"


def test_explicit_section_id_resolves_pin(monkeypatch):
    monkeypatch.delenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", raising=False)
    captured = _capture_gateway_model(monkeypatch)
    spc.call_section_model_provider(
        "external_claude",
        {"messages": [{"role": "user", "content": "x"}]},
        section_id="ibm_bullets",
    )
    assert captured["claude_model"] == "claude-sonnet-5"


def test_untagged_lane_fails_closed(monkeypatch):
    monkeypatch.delenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", raising=False)
    _capture_gateway_model(monkeypatch)
    with pytest.raises(Exception):
        spc.call_section_model_provider(
            "external_claude",
            {"messages": [{"role": "user", "content": "x"}]},
        )


def test_operator_pin_does_not_override_per_section(monkeypatch):
    monkeypatch.setenv("APPS_RG_EXTERNAL_CLAUDE_MODEL", "ignored-operator-override")
    captured = _capture_gateway_model(monkeypatch)
    spc.call_section_model_provider(
        "external_claude",
        {"_reasoning_section_lane": "competencies", "messages": [{"role": "user", "content": "x"}]},
    )
    assert captured["claude_model"] == "claude-sonnet-5"


def test_gateway_pins_model_on_claude_provider():
    gw = spc.build_section_provider_gateway(claude_model="claude-sonnet-5")
    prov = gw._providers[ProviderProfile.EXTERNAL_CLAUDE]
    assert isinstance(prov, ExternalProvider)
    assert prov.model == "claude-sonnet-5"


def test_gateway_empty_model_fails_closed():
    with pytest.raises(ValueError):
        spc.build_section_provider_gateway()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
