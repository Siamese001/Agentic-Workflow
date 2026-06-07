"""External API provider implementation for apps_rg Wave 10A.

External providers are selectable for parity work, but they are not the default.
This class is deliberately transport-injectable: production wiring can provide a
real HTTP transport later, while tests can prove the profile path works without
network or secrets.
"""
from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from typing import Any, Mapping

from apps_rg.runtime.providers.provider_gateway import ProviderGatewayError, ProviderProfile
from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

ExternalTransport = Callable[[dict[str, Any]], dict[str, Any]]


def _prompt_text(compiled_prompt: Any) -> str:
    blocks = getattr(compiled_prompt, "prompt_blocks", ()) or ()
    if blocks:
        return "\n".join(f"{getattr(b, 'role', '?')}: {getattr(b, 'content', '')}" for b in blocks)
    return "\n".join(
        part
        for part in (
            str(getattr(compiled_prompt, "system_preamble", "") or ""),
            str(getattr(compiled_prompt, "user_instruction", "") or ""),
        )
        if part
    ).strip()


class ExternalProvider:
    """External API provider wrapper; functional when supplied a transport."""

    def __init__(
        self,
        *,
        provider_profile: ProviderProfile = ProviderProfile.EXTERNAL_OPENAI,
        model: str = "",
        api_key_env_var: str | None = None,
        base_url: str | None = None,
        transport: ExternalTransport | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        if provider_profile not in (
            ProviderProfile.EXTERNAL_CLAUDE,
            ProviderProfile.EXTERNAL_OPENAI,
            ProviderProfile.EXTERNAL_DEFAULT,
        ):
            raise ProviderGatewayError(f"ExternalProvider cannot serve profile={provider_profile.value}")
        self.provider_profile = provider_profile
        self.model = model or (
            "claude-sonnet-4-6"
            if provider_profile == ProviderProfile.EXTERNAL_CLAUDE
            else "gpt-5.4"
        )
        self.api_key_env_var = api_key_env_var or (
            "ANTHROPIC_API_KEY"
            if provider_profile == ProviderProfile.EXTERNAL_CLAUDE
            else "OPENAI_API_KEY"
        )
        self.base_url = base_url or ""
        self.transport = transport
        self.environ = os.environ if environ is None else environ

    def generate(
        self,
        compiled_prompt: Any,
        *,
        token_budget: int,
        temperature: float = 0.7,
    ) -> ProviderResult:
        prompt = _prompt_text(compiled_prompt)
        request = {
            "provider_profile": self.provider_profile.value,
            "model": self.model,
            "prompt": prompt,
            "max_tokens": int(token_budget),
            "temperature": float(temperature),
            "base_url": self.base_url,
        }
        if not str(self.environ.get(self.api_key_env_var) or "").strip():
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=False,
                provider_available=False,
                exact_provider_error=f"External provider credential unavailable: {self.api_key_env_var}",
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=None,
            )
        if self.transport is None:
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=False,
                provider_available=False,
                exact_provider_error="External provider transport not configured for Wave 10A",
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=None,
            )
        response = self.transport(request)
        text = str(response.get("text") or response.get("content") or "")
        resolved_model = str(response.get("model") or self.model)
        return ProviderResult(
            provider_requested=self.provider_profile.value,
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model=resolved_model,
            raw_model_output=text,
            provider_response={
                "provider_profile": self.provider_profile.value,
                "model": resolved_model,
                "request_digest": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "transport_response": response,
            },
        )


__all__ = ["ExternalProvider", "ExternalTransport"]
