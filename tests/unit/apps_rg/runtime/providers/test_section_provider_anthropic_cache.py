from __future__ import annotations

import hashlib
from types import SimpleNamespace

import pytest

import apps_rg.runtime.providers.section_provider_call as section_provider_call
from apps_rg.prompt_assembly.contracts import (
    CompiledPromptArtifact,
    PromptSlotPayload,
    SlotAuthority,
)
from apps_rg.runtime.providers.external_provider import (
    ExternalProvider,
    _anthropic_body_from_native_request,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.providers.provider_gateway import ProviderGatewayError, ProviderProfile

_LONG_STABLE = "NO FABRICATION truth oath\n" + ("stable-instruction " * 600)


class _CapturingGateway:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        profile,
        compiled_prompt,
        *,
        token_budget: int,
        temperature: float = 0.7,
        timeout_seconds: int | float | None = None,
    ) -> ProviderResult:
        self.calls.append(
            {
                "profile": profile,
                "compiled_prompt": compiled_prompt,
                "token_budget": token_budget,
                "temperature": temperature,
                "timeout_seconds": timeout_seconds,
            }
        )
        return ProviderResult(
            provider_requested=str(getattr(profile, "value", profile)),
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="claude-sonnet-5",
            raw_model_output='{"ok":true}',
            provider_response={
                "transport_response": {
                    "raw_response": {
                        "usage": {
                            "input_tokens": 10,
                            "output_tokens": 2,
                            "cache_creation_input_tokens": 40,
                            "cache_read_input_tokens": 80,
                        }
                    }
                }
            },
        )


def _slot(slot_id: str, content: str) -> PromptSlotPayload:
    return PromptSlotPayload(
        slot_id=slot_id,
        slot_name=slot_id,
        authority_class=SlotAuthority.SYSTEM_AUTHORITY,
        content=content,
        content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
    )


def _artifact() -> CompiledPromptArtifact:
    slots = [
        ("S0", _LONG_STABLE),
        ("D0", "origin fence"),
        ("I0", "instructions"),
        ("C0", "proof pool"),
        ("U0", "volatile targeting"),
    ]
    system = "\n\n".join(f"<!-- SLOT: {slot_id} -->\n{content}" for slot_id, content in slots)
    return CompiledPromptArtifact(
        slot_payloads=[_slot(slot_id, content) for slot_id, content in slots],
        messages=[{"role": "system", "content": system}],
        system_prompt=system,
        prompt_hash="prompt-hash",
    )


def test_cache_enabled_external_claude_threads_native_payload_and_receipt(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setenv("APPS_RG_ANTHROPIC_PROMPT_CACHE", "1")
    gateway = _CapturingGateway()
    monkeypatch.setattr(
        section_provider_call,
        "build_section_provider_gateway",
        lambda claude_model=None, openai_model=None: gateway,
    )
    artifact = _artifact()

    result = section_provider_call.call_section_model_provider(
        ProviderProfile.EXTERNAL_CLAUDE,
        {
            "messages": [*artifact.messages, {"role": "user", "content": "path_index=0"}],
            "compiled_prompt_artifact": artifact,
            "anthropic_workload_kind": "SELF_CONSISTENCY",
            "_reasoning_section_lane": "competencies",
            "max_tokens": 77,
        },
        artifact_dir=tmp_path,
        run_id="run-1",
    )

    compiled = gateway.calls[0]["compiled_prompt"]
    assert compiled.anthropic_payload is not None
    assert "cache_control" in str(compiled.anthropic_payload["system"])
    assert "cache_control" not in str(compiled.anthropic_payload["messages"])
    assert result.prompt_cache_receipt is not None
    assert result.prompt_cache_receipt["cache_enabled"] is True
    assert result.prompt_cache_receipt["cache_read_input_tokens"] == 80
    assert result.prompt_cache_receipt["cache_hit_ratio"] == pytest.approx(0.666667)
    assert result.prompt_cache_receipt["effective_cached_prefix_hash"]
    assert result.prompt_cache_receipt["prompt_semantics_preserved"] is True
    assert (tmp_path / "provider_cache_receipt.json").is_file()


def test_cache_disabled_does_not_attach_native_anthropic_payload(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_ANTHROPIC_PROMPT_CACHE", raising=False)
    gateway = _CapturingGateway()
    monkeypatch.setattr(
        section_provider_call,
        "build_section_provider_gateway",
        lambda claude_model=None, openai_model=None: gateway,
    )

    section_provider_call.call_section_model_provider(
        ProviderProfile.EXTERNAL_CLAUDE,
        {
            "messages": [{"role": "user", "content": "Write JSON."}],
            "compiled_prompt_artifact": _artifact(),
            "_reasoning_section_lane": "headline",
        },
    )

    compiled = gateway.calls[0]["compiled_prompt"]
    assert compiled.anthropic_payload is None
    assert compiled.anthropic_cache_receipt_seed is None


def test_external_openai_generate_ignores_anthropic_only_payload(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    captured: dict[str, object] = {}

    def _transport(request):
        captured.update(request)
        return {"text": "ok", "model": "gpt-test"}

    provider = ExternalProvider(
        provider_profile=ProviderProfile.EXTERNAL_OPENAI,
        model="gpt-test",
        transport=_transport,
    )
    compiled = SimpleNamespace(
        prompt_blocks=(),
        system_preamble="system",
        user_instruction="user",
        anthropic_payload={
            "system": [{"type": "text", "text": "cached", "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": "volatile"}],
        },
    )

    result = provider.generate(compiled, token_budget=20)

    assert result.runtime_generation_status == "REAL_LLM"
    assert "anthropic_payload" not in captured
    assert "anthropic_cache_receipt_seed" not in captured


def test_native_anthropic_payload_rejects_gateway_owned_key_conflicts() -> None:
    with pytest.raises(ProviderGatewayError, match="gateway-owned"):
        _anthropic_body_from_native_request(
            {
                "model": "claude-sonnet-5",
                "max_tokens": 99,
                "temperature": 0.2,
                "anthropic_payload": {
                    "model": "attacker-controlled-model",
                    "system": "system",
                    "messages": [{"role": "user", "content": "hello"}],
                },
            },
            "claude-sonnet-5",
        )


def test_native_anthropic_payload_keeps_cache_control_and_gateway_model() -> None:
    body = _anthropic_body_from_native_request(
        {
            "model": "claude-sonnet-5",
            "max_tokens": 99,
            "temperature": 0.2,
            "anthropic_payload": {
                "system": [
                    {
                        "type": "text",
                        "text": "stable selector rules",
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                "messages": [{"role": "user", "content": "candidate pool"}],
            },
        },
        "claude-sonnet-5",
    )

    assert body["model"] == "claude-sonnet-5"
    assert body["max_tokens"] == 99
    assert body["temperature"] == 0.2
    assert body["stream"] is True
    assert body["system"][0]["cache_control"] == {"type": "ephemeral"}
