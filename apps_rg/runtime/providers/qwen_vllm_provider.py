"""Qwen/vLLM provider seam for apps_rg executive summary runtime slice.

No secrets are hardcoded. No silent mock fallback is allowed.

**W3 note:** This module is **shared transport** (HTTP/OpenAI-compatible client). It does not
select governed vs parallel routing — callers classify execution surfaces:

- Section ``*_dispatch`` modules: import ``call_qwen_vllm`` from ``section_qwen_slice`` (centralized temporary slice).
- ``l2_envelope_adapter`` / spine: ``governed_pa_l2_exit`` (via ``ProviderGateway``).

Ownership unchanged: apps_rg-local seam; not FEC and not a pseudo-FEC surface.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any


DEFAULT_QWEN_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
DEFAULT_QWEN_MODEL = os.environ.get("QWEN_VLLM_MODEL", "Qwen/Qwen2.5-32B-Instruct-AWQ")
DEFAULT_QWEN_TIMEOUT_SECONDS = int(os.environ.get("APPS_RG_QWEN_TIMEOUT_SECONDS", "60"))


@dataclass
class ProviderRequest:
    provider_requested: str
    provider_attempted: bool
    provider_url: str
    model: str
    temperature: float
    max_tokens: int
    timeout_seconds: int
    prompt_hash: str
    input_payload_hash: str
    mock_fallback_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProviderResult:
    provider_requested: str
    provider_attempted: bool
    provider_available: bool
    exact_provider_error: str | None
    runtime_generation_status: str  # REAL_LLM | BLOCKED | MOCKED
    model: str
    raw_model_output: str
    provider_response: dict[str, Any] | None
    reasoning_execution_receipt: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assert_temperature_in_profile(
    temperature: float,
    low: float = 0.0,
    high: float = 0.99,
) -> None:
    if not (low <= temperature <= high):
        raise ValueError(f"temperature {temperature} outside allowed bounds [{low}, {high}]")


def build_qwen_request(
    *,
    messages: list[dict[str, str]],
    prompt_hash: str,
    input_payload_hash: str,
    temperature: float = 0.45,
    max_tokens: int = 700,
    timeout_seconds: int = DEFAULT_QWEN_TIMEOUT_SECONDS,
    base_url: str = DEFAULT_QWEN_BASE_URL,
    model: str = DEFAULT_QWEN_MODEL,
    temperature_bounds: tuple[float, float] = (0.0, 0.99),
) -> tuple[ProviderRequest, dict[str, Any]]:
    """Build an OpenAI-compatible vLLM chat request."""
    t_low, t_high = temperature_bounds
    bounded = float(min(max(float(temperature), t_low), t_high))
    assert_temperature_in_profile(bounded, low=t_low, high=t_high)
    provider_request = ProviderRequest(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_url=base_url,
        model=model,
        temperature=bounded,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        mock_fallback_allowed=False,
    )
    payload = {
        "model": model,
        "messages": messages,
        "temperature": bounded,
        "max_tokens": max_tokens,
        "timeout_seconds": timeout_seconds,
        "response_format": {"type": "json_object"},
    }
    return provider_request, payload


def call_qwen_vllm(
    payload: dict[str, Any],
    *,
    base_url: str = DEFAULT_QWEN_BASE_URL,
    timeout: int | None = None,
) -> ProviderResult:
    """Call Qwen/vLLM using an OpenAI-compatible endpoint.

    If unavailable, returns BLOCKED. It never silently falls back to mock.
    Timeout defaults to payload['timeout_seconds'] or DEFAULT_QWEN_TIMEOUT_SECONDS.
    """
    if timeout is None:
        timeout = payload.get("timeout_seconds", DEFAULT_QWEN_TIMEOUT_SECONDS)
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response_data = json.loads(response.read().decode("utf-8"))
        choices = response_data.get("choices") or []
        if not choices:
            return ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error="Qwen/vLLM returned no choices",
                runtime_generation_status="BLOCKED",
                model=str(payload.get("model", DEFAULT_QWEN_MODEL)),
                raw_model_output="",
                provider_response=response_data,
            )
        text = choices[0].get("message", {}).get("content", "")
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model=str(payload.get("model", DEFAULT_QWEN_MODEL)),
            raw_model_output=text,
            provider_response=response_data,
        )
    except urllib.error.URLError as exc:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error=f"Cannot reach Qwen/vLLM at {base_url}: {getattr(exc, 'reason', exc)}",
            runtime_generation_status="BLOCKED",
            model=str(payload.get("model", DEFAULT_QWEN_MODEL)),
            raw_model_output="",
            provider_response=None,
        )
    except Exception as exc:  # noqa: BLE001
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error=f"Qwen/vLLM call failed: {type(exc).__name__}: {exc}",
            runtime_generation_status="BLOCKED",
            model=str(payload.get("model", DEFAULT_QWEN_MODEL)),
            raw_model_output="",
            provider_response=None,
        )
