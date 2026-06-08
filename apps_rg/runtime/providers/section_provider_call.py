"""Provider-neutral section-lane model calls.

Older apps_rg lanes still build OpenAI-compatible ``messages`` payloads for the
local qwen slice. This helper keeps that qwen path intact while letting the same
payloads route through ``ProviderGateway`` for external profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.providers.external_provider import ExternalProvider
from apps_rg.runtime.providers.provider_gateway import ProviderGateway, ProviderProfile, normalize_provider_profile
from apps_rg.runtime.providers.provider_contract import ProviderResult


@dataclass(frozen=True)
class _PromptBlock:
    role: str
    content: str


@dataclass(frozen=True)
class _CompiledMessagesPrompt:
    prompt_blocks: tuple[_PromptBlock, ...]
    compilation_hash: str
    request_id: str
    run_id: str


def build_section_provider_gateway() -> ProviderGateway:
    return ProviderGateway(
        {
            ProviderProfile.EXTERNAL_CLAUDE: ExternalProvider(
                provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
            ),
            ProviderProfile.EXTERNAL_OPENAI: ExternalProvider(
                provider_profile=ProviderProfile.EXTERNAL_OPENAI,
            ),
        }
    )


def _compiled_prompt_from_payload(provider_payload: dict[str, Any], *, run_id: str | None) -> _CompiledMessagesPrompt:
    messages = provider_payload.get("messages") or []
    blocks: list[_PromptBlock] = []
    if isinstance(messages, list):
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            role = str(msg.get("role") or "user")
            content = str(msg.get("content") or "")
            if content:
                blocks.append(_PromptBlock(role=role, content=content))
    if not blocks:
        blocks.append(_PromptBlock(role="user", content=str(provider_payload.get("prompt") or "")))
    return _CompiledMessagesPrompt(
        prompt_blocks=tuple(blocks),
        compilation_hash=str(provider_payload.get("prompt_hash") or ""),
        request_id=str(provider_payload.get("request_id") or ""),
        run_id=str(run_id or provider_payload.get("run_id") or ""),
    )


def call_section_model_provider(
    provider_profile: str | ProviderProfile | None,
    provider_payload: dict[str, Any],
    *,
    artifact_dir: Path | None = None,
    run_id: str | None = None,
    temperature_override: float | None = None,
    token_budget: int | None = None,
) -> ProviderResult:
    profile = normalize_provider_profile(provider_profile)
    compiled = _compiled_prompt_from_payload(provider_payload, run_id=run_id)
    budget = int(token_budget or provider_payload.get("max_tokens") or provider_payload.get("max_output_tokens") or 900)
    temperature = float(
        temperature_override
        if temperature_override is not None
        else provider_payload.get("temperature", 0.45)
    )
    return build_section_provider_gateway().generate(
        profile,
        compiled,
        token_budget=budget,
        temperature=temperature,
    )


__all__ = [
    "build_section_provider_gateway",
    "call_section_model_provider",
]
