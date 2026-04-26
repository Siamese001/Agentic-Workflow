"""Unit tests for PA.6 provider-aware rendering (5 lanes)."""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.prompt_assembly.input_contracts import (
    upstream_bundle_from_dicts,
)
from agentic_core.prompt_governance.prompt_assembly.pa1_bom_resolver import resolve_bom
from agentic_core.prompt_governance.prompt_assembly.pa2_slot_composition import compose_slots
from agentic_core.prompt_governance.prompt_assembly.pa6_provider_rendering import (
    PROVIDER_LANES,
    render_anthropic,
    render_for_provider,
    render_gemini,
    render_local,
    render_openai_chat,
    render_openai_reasoning,
)


def _bom_comp(model_id="m1", provider="anthropic", thinking_level="", with_tools=False, with_schema=True):
    bundle = upstream_bundle_from_dicts(
        plan_contract={"plan_id": "p1", "policy_hash": "ph"},
        route_contract={
            "route_id": "R3",
            "execution_form": "SINGLE_STEP",
            "policy_hash": "ph",
            "model_id": model_id,
            "provider_lane": provider,
            "thinking_level": thinking_level,
            "temperature": 0.5,
        },
        evidence_contract={"status": "PASS", "support_score": 0.9, "policy_hash": "ph"},
        governance={
            "system_version_hash": "sv",
            "policy_hash": "ph",
            "role_fences": ("MUST",),
            "response_schema_contract": ({"type": "object", "version": "v1"} if with_schema else {}),
            "capability_token": "tok-1" if with_tools else "",
        },
        execution_metadata={"replay_key": "rk", "policy_hash": "ph", "raw_user_task": "Hello?"},
    )
    src = {
        "s0_content": "System.",
        "d0_fences": ("MUST",),
        "i0_content": "Be brief.",
        "budget_ceiling": 1024,
    }
    if with_tools:
        src["tools"] = [{"name": "search", "description": "search"}]
        src["tool_registry"] = ("search",)
        src["tools_allowed_by_token"] = ("search",)
    bom = resolve_bom(bundle, src)
    comp = compose_slots(bom)
    return bom, comp


def test_anthropic_payload_shape():
    bom, comp = _bom_comp(provider="anthropic")
    out = render_anthropic(bom, comp)
    assert out.provider_lane == "anthropic"
    assert "system" in out.payload
    assert isinstance(out.payload["messages"], list)
    assert out.payload["messages"][0]["role"] == "user"
    assert "max_tokens" in out.payload
    assert out.schema_bound is True


def test_openai_chat_has_system_message_role():
    bom, comp = _bom_comp(provider="openai_chat")
    out = render_openai_chat(bom, comp)
    roles = [m["role"] for m in out.payload["messages"]]
    assert "system" in roles
    assert "user" in roles
    assert "response_format" in out.payload


def test_openai_reasoning_drops_temperature_adds_effort():
    bom, comp = _bom_comp(provider="openai_reasoning", thinking_level="high")
    out = render_openai_reasoning(bom, comp)
    assert "temperature" not in out.payload
    assert out.payload["reasoning_effort"] == "high"


def test_gemini_uses_system_instruction_and_contents():
    bom, comp = _bom_comp(provider="gemini")
    out = render_gemini(bom, comp)
    assert "system_instruction" in out.payload
    assert "contents" in out.payload
    assert "generation_config" in out.payload


def test_local_uses_flat_prompt_string():
    bom, comp = _bom_comp(provider="local")
    out = render_local(bom, comp)
    assert "prompt" in out.payload
    assert "[SYSTEM]" in out.payload["prompt"]
    assert "[USER]" in out.payload["prompt"]
    assert "[ASSISTANT]" in out.payload["prompt"]
    assert out.tools_bound is False  # local lane never binds tools


def test_render_for_provider_dispatches_correctly():
    bom, comp = _bom_comp()
    for lane in PROVIDER_LANES:
        out = render_for_provider(bom, comp, lane)
        assert out.provider_lane == lane


def test_render_for_provider_unknown_lane_raises():
    bom, comp = _bom_comp()
    with pytest.raises(ValueError):
        render_for_provider(bom, comp, "nonexistent_lane")


def test_tools_round_trip_when_bound():
    bom, comp = _bom_comp(provider="anthropic", with_tools=True)
    out = render_anthropic(bom, comp)
    assert out.tools_bound is True
    assert any(t.get("name") == "search" for t in out.payload["tools"])
