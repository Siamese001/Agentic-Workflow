"""Provider-neutral section-lane model calls.

Older apps_rg lanes still build OpenAI-compatible ``messages`` payloads for the
local qwen slice. This helper keeps the payload shape intact while letting the
same requests route through ``ProviderGateway`` for external profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.providers.availability_fallback import maybe_fallback_to_openai_for_claude_availability
from apps_rg.runtime.providers.external_provider import ExternalProvider
from apps_rg.runtime.providers.provider_gateway import ProviderGateway, ProviderProfile, normalize_provider_profile
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.section_model_limits import (
    external_openai_generation_model,
    resolve_section_generation_model,
)


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


def build_section_provider_gateway(
    claude_model: str | None = None,
    openai_model: str | None = None,
) -> ProviderGateway:
    """Section provider gateway.

    ``claude_model`` (when set) pins the EXTERNAL_CLAUDE provider's generation model for this
    call — the per-section tier resolved via ``resolve_section_generation_model``. Empty/None
    falls back to ``ExternalProvider``'s SSOT ``default_model`` for each provider profile.
    ``openai_model`` mirrors that for section-specific OpenAI generation overrides.
    """
    return ProviderGateway(
        {
            ProviderProfile.EXTERNAL_CLAUDE: ExternalProvider(
                provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
                model=str(claude_model or ""),
            ),
            ProviderProfile.EXTERNAL_OPENAI: ExternalProvider(
                provider_profile=ProviderProfile.EXTERNAL_OPENAI,
                model=str(openai_model or ""),
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
    section_id: str | None = None,
) -> ProviderResult:
    profile = normalize_provider_profile(provider_profile)
    compiled = _compiled_prompt_from_payload(provider_payload, run_id=run_id)
    budget = int(token_budget or provider_payload.get("max_tokens") or provider_payload.get("max_output_tokens") or 900)
    timeout_seconds = provider_payload.get("timeout_seconds")
    temperature = float(
        temperature_override
        if temperature_override is not None
        else provider_payload.get("temperature", 0.45)
    )
    # Per-section model pin (SSOT): resolve the section from an explicit arg or the
    # ``_reasoning_section_lane`` tag the lane stamped on the payload (``tag_reasoning_lane``),
    # so Claude-backed lanes can use section-specific model overrides (headline/executive_summary
    # -> Opus) instead of every Claude lane silently using the section-agnostic default. Only
    # applied for the external Claude profile; an unknown/missing section resolves to the default.
    # The SSOT resolver is authoritative here: section-specific table entries must win over
    # ambient environment pins so an end-to-end run cannot accidentally force every lane onto one
    # model.
    sid = str(section_id or provider_payload.get("_reasoning_section_lane") or "").strip()
    claude_model: str | None = None
    openai_model: str | None = None
    if profile == ProviderProfile.EXTERNAL_CLAUDE:
        claude_model = resolve_section_generation_model(sid or None)
    elif profile == ProviderProfile.EXTERNAL_OPENAI:
        openai_model = external_openai_generation_model(section_id=sid or None)
    result = build_section_provider_gateway(
        claude_model=claude_model,
        openai_model=openai_model,
    ).generate(
        profile,
        compiled,
        token_budget=budget,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )
    return maybe_fallback_to_openai_for_claude_availability(
        result,
        compiled,
        token_budget=budget,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
        section_id=sid or None,
    )


__all__ = [
    "build_section_provider_gateway",
    "call_section_model_provider",
]
