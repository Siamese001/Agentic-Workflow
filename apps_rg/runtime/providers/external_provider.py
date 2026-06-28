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
import time
import urllib.request
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.error import HTTPError

from agentic_core.L0_routing.config.model_catalog import OPENAI_OMIT_TEMPERATURE_MODELS

from apps_rg.runtime.env_bootstrap import bootstrap_process_env_if_needed
from apps_rg.runtime.providers.provider_gateway import ProviderGatewayError, ProviderProfile
from apps_rg.runtime.providers.provider_attempt_spans import (
    build_provider_attempt_span,
    summarize_provider_attempt_spans,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.section_model_limits import (
    external_claude_generation_model,
    external_openai_generation_model,
)

ExternalTransport = Callable[[dict[str, Any]], dict[str, Any]]

DEFAULT_ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS = 90.0
# Shared upper safety bound for ANY external section provider wall-clock budget.
# The competencies lane may opt into a longer-than-default budget, but it should
# fail closed in minutes, not sit on an API call for an evaluation-era 1000s.
DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS = 300.0


def external_provider_timeout_max_s() -> float:
    """Shared ceiling (seconds) for external section provider wall-clock budgets.

    Defaults to ``DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS`` (300s); a
    malformed/empty env value falls back to that default rather than failing the
    run. Hard-bounded to [30, 300]s so neither a typo nor a hostile value can
    turn a section call into an extended hang.
    """
    raw = os.environ.get("APPS_RG_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS", "").strip()
    if not raw:
        return DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS
    if val <= 0:
        return DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_MAX_SECONDS
    return max(30.0, min(val, 300.0))


def resolve_external_section_timeout_s(
    requested: Any,
    *,
    default: float = DEFAULT_EXTERNAL_PROVIDER_TIMEOUT_SECONDS,
) -> float:
    """Resolve an external section provider call's effective wall-clock budget (seconds).

    Centralized policy: an operator-set budget is honored up to the shared
    ``external_provider_timeout_max_s`` bound. Invalid / non-positive requests
    fall back to ``default``. Replaces the prior per-call
    ``_coerce_timeout_seconds`` that defaulted-but-never-bounded.
    """
    ceiling = external_provider_timeout_max_s()
    try:
        val = float(requested)
    except (TypeError, ValueError):
        val = float(default)
    if val <= 0:
        val = float(default)
    # Small positive budgets are honored verbatim; zero/negative already fell
    # back to ``default`` above.
    return min(val, ceiling)


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
        # W2 transport-progress instrumentation: a slow-but-active streamed response must be
        # observable as PROGRESSING, not indistinguishable from a stall. ``progress_sink`` (an
        # optional dict the caller owns) is mutated IN PLACE as chunks arrive, so even when the
        # wall-clock wrapper abandons this thread on timeout the caller can still read how far the
        # stream got (last_progress_at / chars received). All times: monotonic deltas from t0.
        progress = request.get("progress_sink")
        progress = progress if isinstance(progress, dict) else None
        started_wall = datetime.now(timezone.utc).isoformat()
        t0 = time.monotonic()
        if progress is not None:
            progress.update(
                {
                    "started_at": started_wall,
                    "first_byte_after_s": None,
                    "last_progress_after_s": None,
                    "chunk_count": 0,
                    "raw_output_chars": 0,
                    "completed": False,
                }
            )
        text_parts: list[str] = []
        resolved_model = str(body["model"])
        usage: dict[str, Any] = {}
        first_byte_after_s: float | None = None
        chunk_count = 0
        last_progress_after_s: float | None = None
        for _attempt in range(_attempts):
            text_parts = []
            resolved_model = str(body["model"])
            usage = {}
            chunk_count = 0
            first_byte_after_s = None
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
                        now_after = time.monotonic() - t0
                        if first_byte_after_s is None:
                            first_byte_after_s = now_after
                            if progress is not None:
                                progress["first_byte_after_s"] = round(now_after, 4)
                        chunk_count += 1
                        last_progress_after_s = now_after
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
                            raise ProviderGatewayError(
                                f"anthropic stream error: {err.get('type')}: {err.get('message')}"
                            )
                        if progress is not None:
                            progress["chunk_count"] = chunk_count
                            progress["last_progress_after_s"] = round(now_after, 4)
                            progress["raw_output_chars"] = sum(len(p) for p in text_parts)
            except HTTPError:
                raise
            except (
                TimeoutError,
                OSError,
                json.JSONDecodeError,
                ValueError,
                TypeError,
                RuntimeError,
                LookupError,
                AttributeError,
                KeyError,
                ConnectionError,
                ProviderGatewayError,
            ):
                if _attempt + 1 < _attempts:
                    time.sleep(min(0.25 * (2 ** _attempt), 2.0))
                    continue
                raise
            break
        text = "".join(text_parts).strip()
        completed_after_s = time.monotonic() - t0
        timing = {
            "started_at": started_wall,
            "first_byte_after_s": round(first_byte_after_s, 4) if first_byte_after_s is not None else None,
            "last_progress_after_s": (
                round(last_progress_after_s, 4) if last_progress_after_s is not None else None
            ),
            "completed_after_s": round(completed_after_s, 4),
            "chunk_count": chunk_count,
            "read_iterations": chunk_count,
            "raw_output_chars": len(text),
            "stream": True,
        }
        if progress is not None:
            progress.update(
                {
                    "completed": True,
                    "completed_after_s": round(completed_after_s, 4),
                    "chunk_count": chunk_count,
                    "raw_output_chars": len(text),
                }
            )
        return {
            "text": text,
            "model": resolved_model,
            "transport_timing": timing,
            "raw_response": {
                "model": resolved_model,
                "usage": usage,
                "stream": True,
                "transport_timing": timing,
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
            except HTTPError as exc:
                result_queue.put(("http_error", exc), block=False)
            except (
                TimeoutError,
                OSError,
                json.JSONDecodeError,
                ValueError,
                TypeError,
                RuntimeError,
                LookupError,
                AttributeError,
                KeyError,
                ConnectionError,
                ProviderGatewayError,
            ) as exc:
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
        if kind == "http_error":
            raise payload
        if kind == "error":
            raise ProviderGatewayError(f"{type(payload).__name__}: {payload}") from payload
        return payload

    def generate(
        self,
        compiled_prompt: Any,
        *,
        token_budget: int,
        temperature: float = 0.7,
        timeout_seconds: int | float | None = None,
    ) -> ProviderResult:
        attempt_started_at_utc = datetime.now(timezone.utc).isoformat()

        def _provider_response_with_attempt(
            payload: dict[str, Any] | None,
            *,
            provider_attempted: bool,
            provider_available: bool,
            runtime_generation_status: str,
            exact_provider_error: str | None,
            model: str | None = None,
        ) -> dict[str, Any]:
            response = dict(payload or {})
            response.setdefault("attempt_started_at_utc", attempt_started_at_utc)
            response["attempt_completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            transport_response = response.get("transport_response")
            nested_timing = (
                transport_response.get("transport_timing")
                if isinstance(transport_response, Mapping)
                else None
            )
            span = build_provider_attempt_span(
                attempt_kind="requested",
                attempt_index=0,
                provider=self.provider_profile.value,
                model=str(model or self.model),
                provider_attempted=provider_attempted,
                provider_available=provider_available,
                runtime_generation_status=runtime_generation_status,
                started_at_utc=str(response.get("attempt_started_at_utc") or ""),
                completed_at_utc=str(response.get("attempt_completed_at_utc") or ""),
                exact_provider_error=exact_provider_error,
                timeout_seconds=provider_timeout_seconds,
                token_budget=int(token_budget),
                temperature=float(temperature),
                request_digest=str(response.get("request_digest") or ""),
                transport_progress=response.get("transport_progress")
                if isinstance(response.get("transport_progress"), Mapping)
                else None,
                transport_timing=response.get("transport_timing")
                if isinstance(response.get("transport_timing"), Mapping)
                else nested_timing,
            )
            response["provider_attempt_spans"] = [span]
            response["provider_attempt_timing_summary"] = summarize_provider_attempt_spans([span])
            return response

        prompt = _prompt_text(compiled_prompt)
        # W1: resolve the effective wall-clock budget through the shared policy.
        provider_timeout_seconds = resolve_external_section_timeout_s(timeout_seconds)
        # W2: a caller-owned progress sink the streamed transport mutates in place, so a timeout
        # error can report how far the (now-abandoned) stream actually got.
        progress_sink: dict[str, Any] = {}
        request = {
            "provider_profile": self.provider_profile.value,
            "model": self.model,
            "prompt": prompt,
            "max_tokens": int(token_budget),
            "temperature": float(temperature),
            "base_url": self.base_url,
            "timeout_seconds": provider_timeout_seconds,
            "progress_sink": progress_sink,
        }
        if self._uses_process_environ:
            bootstrap_process_env_if_needed(self.environ)
        if not str(self.environ.get(self.api_key_env_var) or "").strip():
            error = f"External provider credential unavailable: {self.api_key_env_var}"
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=False,
                provider_available=False,
                exact_provider_error=error,
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=_provider_response_with_attempt(
                    {"provider_profile": self.provider_profile.value},
                    provider_attempted=False,
                    provider_available=False,
                    runtime_generation_status="BLOCKED",
                    exact_provider_error=error,
                ),
            )
        transport = self.transport or self._default_transport
        try:
            response = self._transport_with_wall_clock_timeout(
                transport,
                request,
                timeout_seconds=provider_timeout_seconds,
            )
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            error = f"External provider HTTP {exc.code}: {detail or exc.reason}"
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=error,
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=_provider_response_with_attempt(
                    {"transport_progress": dict(progress_sink)} if progress_sink else {},
                    provider_attempted=True,
                    provider_available=False,
                    runtime_generation_status="BLOCKED",
                    exact_provider_error=error,
                ),
            )
        except (ProviderGatewayError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            # Surface last-observed progress so a timeout reads as "slow, got N chars at +Ms",
            # not an opaque stall. progress_sink is populated in place by the streamed transport.
            prog = dict(progress_sink)
            progress_note = ""
            if prog:
                progress_note = (
                    f" [last_progress_after_s={prog.get('last_progress_after_s')}"
                    f", chars_received={prog.get('raw_output_chars')}"
                    f", chunk_count={prog.get('chunk_count')}]"
                )
            error = f"External provider call failed: {type(exc).__name__}: {exc}{progress_note}"
            return ProviderResult(
                provider_requested=self.provider_profile.value,
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=error,
                runtime_generation_status="BLOCKED",
                model=self.model,
                raw_model_output="",
                provider_response=_provider_response_with_attempt(
                    {"transport_progress": prog} if prog else {},
                    provider_attempted=True,
                    provider_available=False,
                    runtime_generation_status="BLOCKED",
                    exact_provider_error=error,
                ),
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
            provider_response=_provider_response_with_attempt(
                {
                    "provider_profile": self.provider_profile.value,
                    "model": resolved_model,
                    "request_digest": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "effective_timeout_seconds": provider_timeout_seconds,
                    "transport_timing": response.get("transport_timing"),
                    "transport_response": response,
                },
                provider_attempted=True,
                provider_available=True,
                runtime_generation_status="REAL_LLM",
                exact_provider_error=None,
                model=resolved_model,
            ),
        )


__all__ = [
    "ExternalProvider",
    "ExternalTransport",
    "external_provider_timeout_max_s",
    "resolve_external_section_timeout_s",
]
