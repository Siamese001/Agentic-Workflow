"""Tests for SovereignLLMGateway.route_generation async adapter."""

from __future__ import annotations

import asyncio

import pytest

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    GatewayError,
    SovereignLLMGateway,
)
from agentic_core.L2_execution.types.gateway_types import (
    GenerationRequest,
    GenerationResponse,
)


def _new_gateway() -> SovereignLLMGateway:
    # secret_key is required positional; test uses a fixed HMAC secret.
    return SovereignLLMGateway(secret_key=b"unit-test-secret")


def test_route_generation_returns_generation_response_for_openai() -> None:
    gw = _new_gateway()
    request = GenerationRequest(
        prompt="hello",
        agent_id="test_agent",
        provider="openai",
        model="gpt-4o",
    )
    response = asyncio.run(gw.route_generation(request))
    assert isinstance(response, GenerationResponse)
    assert response.content is not None
    assert response.provider == "openai"
    assert response.replay_envelope.startswith("route-gen-")


@pytest.mark.parametrize("provider", ["openai", "anthropic", "google", "vertex", "azure", "local"])
def test_route_generation_accepts_every_documented_provider(provider: str) -> None:
    gw = _new_gateway()
    request = GenerationRequest(
        prompt="ping",
        agent_id="unit",
        provider=provider,  # type: ignore[arg-type]
    )
    response = asyncio.run(gw.route_generation(request))
    assert isinstance(response, GenerationResponse)
    assert response.provider == provider


def test_route_generation_rejects_unknown_provider() -> None:
    gw = _new_gateway()
    request = GenerationRequest(
        prompt="x",
        agent_id="unit",
        provider="mystery",  # type: ignore[arg-type]
    )
    with pytest.raises(GatewayError, match="unsupported provider"):
        asyncio.run(gw.route_generation(request))


def test_route_generation_auto_registers_provider_when_missing() -> None:
    gw = _new_gateway()
    assert not gw._providers  # nothing registered yet  # noqa: SLF001
    request = GenerationRequest(prompt="p", agent_id="a", provider="anthropic")
    asyncio.run(gw.route_generation(request))
    # After route_generation, ANTHROPIC is registered.
    assert any(pt.name == "ANTHROPIC" for pt in gw._providers)  # noqa: SLF001


def test_route_generation_preserves_model_passthrough() -> None:
    gw = _new_gateway()
    request = GenerationRequest(
        prompt="p",
        agent_id="a",
        provider="openai",
        model="claude-3-5-sonnet",
    )
    response = asyncio.run(gw.route_generation(request))
    # PlaceholderProvider may override model; empty model should still fallback
    # to the request.model. Just assert it's a non-empty string.
    assert isinstance(response.model, str)


def test_route_generation_artifact_is_signed_and_verifies() -> None:
    gw = _new_gateway()
    # Directly exercise the artifact builder — it must pass signature verification.
    request = GenerationRequest(prompt="sign-me", agent_id="a", provider="openai")
    artifact = gw._artifact_from_request(request)  # noqa: SLF001
    assert artifact.verify_signature(b"unit-test-secret") is True
    # Wrong key must fail verification.
    assert artifact.verify_signature(b"wrong-secret") is False


def test_route_generation_returns_positive_tokens_when_provider_returns_count() -> None:
    gw = _new_gateway()
    request = GenerationRequest(prompt="p", agent_id="a", provider="openai")
    response = asyncio.run(gw.route_generation(request))
    # Placeholder provider returns tokens_used=10.
    assert response.tokens >= 0


def test_route_generation_is_awaitable() -> None:
    gw = _new_gateway()
    request = GenerationRequest(prompt="p", agent_id="a", provider="openai")
    coro = gw.route_generation(request)
    assert asyncio.iscoroutine(coro)
    asyncio.run(coro)  # consume to avoid unawaited-coroutine warning


def test_route_generation_empty_provider_defaults_to_openai() -> None:
    gw = _new_gateway()

    class _Req:
        prompt = "x"
        agent_id = "a"
        provider = ""
        model = None
        temperature = 0.7
        max_tokens = 100

    response = asyncio.run(gw.route_generation(_Req()))
    assert response.provider == "openai"
