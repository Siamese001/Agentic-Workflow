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
import queue
import threading
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any, Mapping

from agentic_core.L0_routing.config.model_catalog import OPENAI_OMIT_TEMPERATURE_MODELS

from apps_rg.runtime.env_bootstrap import bootstrap_process_env_if_needed
from apps_rg.runtime.providers.provider_gateway import ProviderGatewayError, ProviderProfile
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.section_model_limits import (
    external_claude_generation_model,
    external_openai_generation_model,
)

ExternalTransport = Callable[[dict[str, Any]], dict[str, Any]]

DEFAULT_ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS = 90.0


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


def _coerce_timeout_seconds(value: Any) -> float:
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        return DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    if timeout <= 0:
        return DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS
    return timeout


def _format_timeout_seconds(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.3f}".rstrip("0").rstrip(".")


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
        self.environ = os.environ if environ is None else environ
        self._uses_process_environ = self.environ is os.environ
        self.model = model or (
            external_claude_generation_model(self.environ)
            if provider_profile == ProviderProfile.EXTERNAL_CLAUDE
            else external_openai_generation_model(self.environ)
        )
        self.api_key_env_var = api_key_env_var or (
            "ANTHROPIC_API_KEY"
            if provider_profile == ProviderProfile.EXTERNAL_CLAUDE
            else "OPENAI_API_KEY"
        )
        self.base_url = base_url or ""
        self.transport = transport

    def _default_transport(self, request: dict[str, Any]) -> dict[str, Any]:
        if self.provider_profile == ProviderProfile.EXTERNAL_CLAUDE:
            return self._anthropic_messages_transport(request)
        return self._openai_responses_transport(request)

    def _anthropic_messages_transport(self, request: dict[str, Any]) -> dict[str, Any]:
        prompt = str(request.get("prompt") or "")
        timeout_seconds = _coerce_timeout_seconds(request.get("timeout_seconds"))
        # STREAM the Messages API (SSE). Non-streaming holds the connection idle for the whole
        # server-side generation (~30s for a multi-thousand-token output); in the long-lived run
        # process that idle connection is dropped and the read hangs until timeout, while a tiny
        # output (no idle) and a fresh process both succeed. Streaming keeps tokens flowing, so the
        # connection never idles and the read returns normally. (Diagnosed 2026-06-16: in-process
        # probe — non-stream 2800-tok hangs; identical stream=True returns in ~34s/79 chunks.)
        body = {
            "model": str(request.get("model") or self.model),
            "max_tokens": int(request.get("max_tokens") or 900),
            "temperature": float(request.get("temperature") or 0.0),
            "system": "Return compact JSON only.",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        url = str(request.get("base_url") or self.base_url or DEFAULT_ANTHROPIC_MESSAGES_URL)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": str(self.environ.get(self.api_key_env_var) or ""),
            "anthropic-version": "2023-06-01",
        }
        data = json.dumps(body).encode("utf-8")
        # Short per-read timeout + retry. In the long-lived run process a streamed connection can
        # stall mid-stream (no data on an otherwise-open socket); cap each read and reconnect rather
        # than block to the wall-clock. A fresh stream completes in ~34s, so a retry recovers.
        per_read = float(os.environ.get("APPS_RG_STREAM_READ_TIMEOUT_S") or 18.0)
        _attempts = int(os.environ.get("APPS_RG_STREAM_ATTEMPTS") or 8)
        text_parts: list[str] = []
        resolved_model = str(body["model"])
        usage: dict[str, Any] = {}
        last_exc: Exception | None = None
        for _attempt in range(_attempts):
            text_parts = []
            resolved_model = str(body["model"])
            usage = {}
            try:
                http_req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(http_req, timeout=per_read) as resp:
                    for raw_line in resp:
                        line = raw_line.decode("utf-8", errors="replace").strip()
                        if not line.startswith("data:"):
                            continue
                        payload = line[5:].strip()
                        if not payload or payload == "[DONE]":
                            continue
                        try:
                            event = json.loads(payload)
                        except json.JSONDecodeError:
                            continue
                        etype = event.get("type")
                        if etype == "message_start":
                            msg = event.get("message") or {}
                            resolved_model = str(msg.get("model") or resolved_model)
                            if isinstance(msg.get("usage"), dict):
                                usage.update(msg["usage"])
                        elif etype == "content_block_delta":
                            delta = event.get("delta") or {}
                            if delta.get("type") == "text_delta":
                                text_parts.append(str(delta.get("text") or ""))
                        elif etype == "message_delta":
                            if isinstance(event.get("usage"), dict):
                                usage.update(event["usage"])
                        elif etype == "message_stop":
                            break
                        elif etype == "error":
                            err = event.get("error") or {}
                            raise urllib.error.URLError(
                                f"anthropic stream error: {err.get('type')}: {err.get('message')}"
                            )
            except urllib.error.HTTPError:
                raise
            except (TimeoutError, urllib.error.URLError, OSError) as exc:
                last_exc = exc
                if _attempt + 1 < _attempts:
                    continue
                raise
            break
        text = "".join(text_parts).strip()
        return {
            "text": text,
            "model": resolved_model,
            "raw_response": {
                "model": resolved_model,
                "usage": usage,
                "stream": True,
                "content": [{"type": "text", "text": text}],
            },
        }

    def _openai_responses_transport(self, request: dict[str, Any]) -> dict[str, Any]:
        prompt = str(request.get("prompt") or "")
        timeout_seconds = _coerce_timeout_seconds(request.get("timeout_seconds"))
        body = {
            "model": str(request.get("model") or self.model),
            "input": prompt,
            "max_output_tokens": int(request.get("max_tokens") or 900),
        }
        if str(body["model"]).strip() not in OPENAI_OMIT_TEMPERATURE_MODELS:
            body["temperature"] = float(request.get("temperature") or 0.0)
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
        with urllib.request.urlopen(http_req, timeout=timeout_seconds) as resp:
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

    def _transport_with_wall_clock_timeout(
        self,
        transport: ExternalTransport,
        request: dict[str, Any],
        *,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        # Optional global wall-clock floor (env). Workaround for a per-process download throttle
        # seen in the long-lived run where streamed generations trickle far slower than in a fresh
        # process; a larger budget lets them complete. Unset by default (no behavior change).
        _floor = float(os.environ.get("APPS_RG_PROVIDER_WALLCLOCK_FLOOR_S") or 0.0)
        if _floor > float(timeout_seconds):
            timeout_seconds = _floor
        result_queue: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)

        def _runner() -> None:
            try:
                result_queue.put(("ok", transport(request)), block=False)
            except Exception as exc:
                result_queue.put(("error", exc), block=False)

        worker = threading.Thread(
            target=_runner,
            name=f"apps-rg-{self.provider_profile.value}-provider-call",
            daemon=True,
        )
        worker.start()
        worker.join(timeout_seconds)
        if worker.is_alive():
            formatted = _format_timeout_seconds(timeout_seconds)
            raise TimeoutError(f"External provider wall-clock timeout after {formatted}s")
        try:
            kind, payload = result_queue.get_nowait()
        except queue.Empty as exc:
            raise TimeoutError("External provider returned without a transport result") from exc
        if kind == "error":
            raise payload
        return payload

    def generate(
        self,
        compiled_prompt: Any,
        *,
        token_budget: int,
        temperature: float = 0.7,
        timeout_seconds: int | float | None = None,
    ) -> ProviderResult:
        prompt = _prompt_text(compiled_prompt)
        provider_timeout_seconds = _coerce_timeout_seconds(timeout_seconds)
        request = {
            "provider_profile": self.provider_profile.value,
            "model": self.model,
            "prompt": prompt,
            "max_tokens": int(token_budget),
            "temperature": float(temperature),
            "base_url": self.base_url,
            "timeout_seconds": provider_timeout_seconds,
        }
        if self._uses_process_environ:
            bootstrap_process_env_if_needed(self.environ)
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
            response = self._transport_with_wall_clock_timeout(
                transport,
                request,
                timeout_seconds=provider_timeout_seconds,
            )
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
