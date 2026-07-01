"""ProviderGateway — provider-native Anthropic payload + usage telemetry.

Covers PR "ProviderGateway structured Anthropic payload":
  - prompt_text back-compat (flat single user message),
  - structured anthropic_payload passthrough (system / messages / cache_control survive),
  - fail-closed rejection of gateway-owned keys (model/max_tokens/temperature),
  - actual usage capture into invocation_meta + receipt token_usage,
  - prompt-cache read/write token capture,
  - beta/extra header support (no beta by default; conflict fails closed),
  - payload immutability,
  - end-to-end flow of a build_messages_payload()-composed request.

A fake ``anthropic`` module is injected via sys.modules so the gateway's in-method
``import anthropic`` picks it up — no network, no real SDK behavior asserted.
"""
from __future__ import annotations

import copy as _copy
import inspect
import sys
import types
from types import SimpleNamespace

import pytest

from agentic_core.runtime.providers.provider_gateway import ProviderGateway
from agentic_core.runtime.providers.provider_types import (
    ProviderGatewayError,
    ProviderKind,
    ProviderMode,
    ProviderProfile,
    ProviderRequest,
)

# --------------------------------------------------------------------------- helpers


def _make_message(*, text="generated text", model="claude-sonnet-5", usage=None, content=None):
    """Build a fake Anthropic Message (duck-typed: .content / .model / .usage)."""
    return SimpleNamespace(
        content=content if content is not None else [SimpleNamespace(type="text", text=text)],
        model=model,
        usage=usage,
    )


def _install_fake_anthropic(monkeypatch, *, message, recorder):
    """Replace the ``anthropic`` module so Anthropic(...).messages.create(**kw) is captured."""

    class _Messages:
        def create(self, **kwargs):
            recorder["create_kwargs"] = kwargs
            return message

    class _Client:
        def __init__(self, **kwargs):
            recorder["client_kwargs"] = kwargs
            self.messages = _Messages()

    fake_mod = types.ModuleType("anthropic")
    fake_mod.Anthropic = _Client
    monkeypatch.setitem(sys.modules, "anthropic", fake_mod)


def _anthropic_profile(**overrides) -> ProviderProfile:
    base = {
        "profile_id": "anthropic_test",
        "provider_kind": ProviderKind.EXTERNAL_API,
        "model_id": "claude-sonnet-5",
        "api_key_env_var": "ANTHROPIC_API_KEY",
        "vendor": "anthropic",
        "max_tokens": 1024,
    }
    base.update(overrides)
    return ProviderProfile(**base)


def _gateway() -> ProviderGateway:
    # registry is unused on the invoke() path; a sentinel avoids loading the real registry.
    return ProviderGateway(registry=object(), provider_mode=ProviderMode.LIVE_ALLOWED)


@pytest.fixture
def anthropic_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    return monkeypatch


# --------------------------------------------------------------------------- tests


def test_cache_usage_telemetry_uses_retrieval_public_surface():
    source = inspect.getsource(ProviderGateway._record_cache_usage)
    assert "agentic_core.knowledge.retrieval.anthropic_cache_telemetry" not in source
    assert "from agentic_core.knowledge.retrieval import" in source


def test_anthropic_prompt_text_backcompat(anthropic_env):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(text="hi"), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(prompt_text="hello", provider_profile=_anthropic_profile())
    )
    assert resp.success
    ck = recorder["create_kwargs"]
    assert ck["messages"] == [{"role": "user", "content": "hello"}]
    # gateway owns model/max_tokens/temperature
    assert ck["model"] == "claude-sonnet-5"
    assert ck["max_tokens"] == 1024
    assert "temperature" in ck
    # no beta header sent by default
    assert "extra_headers" not in ck


def test_anthropic_structured_payload_preserved(anthropic_env):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    payload = {
        "system": [
            {"type": "text", "text": "S" * 16, "cache_control": {"type": "ephemeral"}}
        ],
        "messages": [{"role": "user", "content": [{"type": "text", "text": "x"}]}],
    }
    resp = _gateway().invoke(
        ProviderRequest(
            prompt_text="ignored",
            provider_profile=_anthropic_profile(),
            anthropic_payload=payload,
        )
    )
    assert resp.success
    ck = recorder["create_kwargs"]
    assert ck["system"] == payload["system"]
    assert ck["system"][0]["cache_control"] == {"type": "ephemeral"}  # marker not dropped
    assert ck["messages"] == payload["messages"]
    assert isinstance(ck["messages"][0]["content"], list)  # not flattened to a string


@pytest.mark.parametrize("bad_key", ["model", "max_tokens", "temperature"])
def test_anthropic_payload_rejects_gateway_owned_conflicts(anthropic_env, bad_key):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    payload = {"messages": [{"role": "user", "content": "x"}], bad_key: "conflict"}
    resp = _gateway().invoke(
        ProviderRequest(
            prompt_text="x",
            provider_profile=_anthropic_profile(),
            anthropic_payload=payload,
        )
    )
    assert not resp.success
    assert bad_key in (resp.error_message or "")
    # fail closed BEFORE any SDK interaction
    assert recorder == {}


def test_validate_anthropic_payload_raises_directly():
    with pytest.raises(ProviderGatewayError):
        ProviderGateway._validate_anthropic_payload(
            {"messages": [{"role": "user", "content": "x"}], "model": "m"}
        )
    with pytest.raises(ProviderGatewayError):
        ProviderGateway._validate_anthropic_payload({"system": "no messages here"})
    with pytest.raises(ProviderGatewayError):
        ProviderGateway._validate_anthropic_payload(["not", "a", "dict"])


def test_anthropic_usage_populates_invocation_meta(anthropic_env):
    recorder: dict = {}
    usage = SimpleNamespace(
        input_tokens=1000,
        output_tokens=50,
        cache_creation_input_tokens=700,
        cache_read_input_tokens=0,
    )
    _install_fake_anthropic(anthropic_env, message=_make_message(usage=usage), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(prompt_text="hello", provider_profile=_anthropic_profile())
    )
    assert resp.success
    meta = resp.invocation_meta
    assert meta["input_tokens"] == 1000
    assert meta["output_tokens"] == 50
    assert meta["cache_creation_input_tokens"] == 700
    assert meta["cache_read_input_tokens"] == 0
    assert meta["anthropic_usage"]["input_tokens"] == 1000
    assert meta["cache_hit_ratio"] == 0.0  # 0 / (0 + 700 + 1000)


def test_receipt_uses_actual_anthropic_usage_when_available(anthropic_env):
    recorder: dict = {}
    usage = SimpleNamespace(
        input_tokens=1000,
        output_tokens=50,
        cache_creation_input_tokens=700,
        cache_read_input_tokens=0,
    )
    _install_fake_anthropic(anthropic_env, message=_make_message(usage=usage), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(prompt_text="hello", provider_profile=_anthropic_profile())
    )
    tu = resp.receipt.token_usage
    # actual numbers, not the word-count heuristic (which would give prompt_tokens == 2)
    assert tu.prompt_tokens == 1700  # 1000 fresh + 700 cache-write + 0 cache-read
    assert tu.completion_tokens == 50
    assert tu.total_tokens == 1750


def test_cache_read_tokens_recorded(anthropic_env):
    recorder: dict = {}
    usage = SimpleNamespace(
        input_tokens=100,
        output_tokens=20,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=900,
    )
    _install_fake_anthropic(anthropic_env, message=_make_message(usage=usage), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(prompt_text="second call", provider_profile=_anthropic_profile())
    )
    meta = resp.invocation_meta
    assert meta["cache_read_input_tokens"] == 900
    assert meta["cache_hit_ratio"] == round(900 / (900 + 0 + 100), 4)  # 0.9
    assert resp.receipt.token_usage.prompt_tokens == 1000  # 100 + 900 + 0


def test_beta_headers_supported_without_defaulting(anthropic_env):
    # With a beta header -> anthropic-beta sent
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(
            prompt_text="hi",
            provider_profile=_anthropic_profile(),
            anthropic_beta_headers=("mid-conversation-system-2026-04-07",),
        )
    )
    assert resp.success
    assert (
        recorder["create_kwargs"]["extra_headers"]["anthropic-beta"]
        == "mid-conversation-system-2026-04-07"
    )

    # Without a beta header -> no anthropic-beta sent
    recorder2: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder2)
    resp2 = _gateway().invoke(
        ProviderRequest(prompt_text="hi", provider_profile=_anthropic_profile())
    )
    assert resp2.success
    assert "extra_headers" not in recorder2["create_kwargs"]


def test_multiple_beta_headers_joined(anthropic_env):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    _gateway().invoke(
        ProviderRequest(
            prompt_text="hi",
            provider_profile=_anthropic_profile(),
            anthropic_beta_headers=("beta-a", "beta-b"),
        )
    )
    assert recorder["create_kwargs"]["extra_headers"]["anthropic-beta"] == "beta-a,beta-b"


def test_extra_headers_passed_through(anthropic_env):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    _gateway().invoke(
        ProviderRequest(
            prompt_text="hi",
            provider_profile=_anthropic_profile(),
            anthropic_extra_headers={"x-custom": "v1"},
        )
    )
    assert recorder["create_kwargs"]["extra_headers"]["x-custom"] == "v1"


def test_conflicting_anthropic_beta_headers_fail_closed(anthropic_env):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(
            prompt_text="hi",
            provider_profile=_anthropic_profile(),
            anthropic_beta_headers=("beta-a",),
            anthropic_extra_headers={"anthropic-beta": "beta-x"},
        )
    )
    assert not resp.success
    assert "conflicting anthropic-beta" in (resp.error_message or "")
    assert recorder == {}


def test_structured_payload_not_mutated(anthropic_env):
    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    payload = {
        "system": [
            {"type": "text", "text": "S" * 16, "cache_control": {"type": "ephemeral"}}
        ],
        "messages": [{"role": "user", "content": [{"type": "text", "text": "nested"}]}],
    }
    snapshot = _copy.deepcopy(payload)
    resp = _gateway().invoke(
        ProviderRequest(
            prompt_text="x",
            provider_profile=_anthropic_profile(),
            anthropic_payload=payload,
        )
    )
    assert resp.success
    assert payload == snapshot  # caller's object untouched


def test_build_messages_payload_flows_through_gateway(anthropic_env):
    from agentic_core.knowledge.retrieval.anthropic_cache_control import (
        build_messages_payload,
        count_cache_markers,
    )

    long_system = "You are an expert assistant. " * 200  # > 3500 chars -> cacheable
    long_user = "Question: " + ("context " * 100)
    payload = build_messages_payload(
        user_prompt=long_user,
        system_prompt=long_system,
        cache_boundary_hint=-1,
    )

    recorder: dict = {}
    _install_fake_anthropic(anthropic_env, message=_make_message(), recorder=recorder)
    resp = _gateway().invoke(
        ProviderRequest(
            prompt_text="[structured anthropic payload]",
            provider_profile=_anthropic_profile(),
            anthropic_payload=payload,
        )
    )
    assert resp.success
    ck = recorder["create_kwargs"]
    assert "system" in ck
    assert "messages" in ck
    # at least one cache_control marker survived to the SDK call
    assert count_cache_markers(ck) >= 1
    # not flattened to a single user string
    assert isinstance(ck["messages"][0]["content"], list)
    # invocation_meta reflects the structured payload's cache markers + prefix fingerprint
    assert resp.invocation_meta["cache_marker_count"] >= 1
    assert resp.invocation_meta["cache_fingerprint"].startswith("system:")
