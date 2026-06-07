"""External API provider implementation for apps_rg Wave 10A.

External providers are selectable for parity work, but they are not the default.
This class is deliberately transport-injectable: production wiring can provide a
real HTTP transport later, while tests can prove the profile path works without
network or secrets.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any, Mapping

from apps_rg.runtime.providers.provider_gateway import ProviderGatewayError, ProviderProfile
from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult

ExternalTransport = Callable[[dict[str, Any]], dict[str, Any]]

DEFAULT_ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


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

    def _default_transport(self, request: dict[str, Any]) -> dict[str, Any]:
        if self.provider_profile == ProviderProfile.EXTERNAL_CLAUDE:
            return self._anthropic_messages_transport(request)
        return self._openai_responses_transport(request)

    def _anthropic_messages_transport(self, request: dict[str, Any]) -> dict[str, Any]:
        prompt = str(request.get("prompt") or "")
        body = {
            "model": str(request.get("model") or self.model),
            "max_tokens": int(request.get("max_tokens") or 900),
            "temperature": float(request.get("temperature") or 0.0),
            "system": "Return compact JSON only.",
            "messages": [{"role": "user", "content": prompt}],
        }
        url = str(request.get("base_url") or self.base_url or DEFAULT_ANTHROPIC_MESSAGES_URL)
        http_req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-key": str(self.environ.get(self.api_key_env_var) or ""),
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(http_req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text_parts: list[str] = []
        for block in data.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(str(block.get("text") or ""))
        return {
            "text": "\n".join(p for p in text_parts if p).strip(),
            "model": data.get("model") or body["model"],
            "raw_response": data,
        }

    def _openai_responses_transport(self, request: dict[str, Any]) -> dict[str, Any]:
        prompt = str(request.get("prompt") or "")
        body = {
            "model": str(request.get("model") or self.model),
            "input": prompt,
            "max_output_tokens": int(request.get("max_tokens") or 900),
            "temperature": float(request.get("temperature") or 0.0),
        }
        url = str(request.get("base_url") or self.base_url or DEFAULT_OPENAI_RESPONSES_URL)
        http_req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.environ.get(self.api_key_env_var) or ''}",
            },
            method="POST",
        )
        with urllib.request.urlopen(http_req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = str(data.get("output_text") or "")
        if not text:
            parts: list[str] = []
            for item in data.get("output") or []:
                if not isinstance(item, dict):
                    continue
                for block in item.get("content") or []:
                    if isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                        parts.append(str(block.get("text") or ""))
            text = "\n".join(p for p in parts if p).strip()
        return {
            "text": text,
            "model": data.get("model") or body["model"],
            "raw_response": data,
        }

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
        transport = self.transport or self._default_transport
        try:
            response = transport(request)
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:1000]
            except OSError:
                detail = ""
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"External provider HTTP {exc.code}: {detail or exc.reason}",
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=None,
            )
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"External provider call failed: {type(exc).__name__}: {exc}",
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=None,
            )
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
