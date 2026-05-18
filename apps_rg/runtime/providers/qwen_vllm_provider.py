"""Qwen/vLLM provider seam for apps_rg executive summary runtime slice.

No secrets are hardcoded. No silent mock fallback is allowed.

**W3 note:** This module is **shared transport** (HTTP/OpenAI-compatible client). It does not
select governed vs parallel routing — callers classify execution surfaces:

- Section ``*_dispatch`` modules: import ``call_qwen_vllm`` from ``section_qwen_slice`` (centralized temporary slice).
- ``l2_envelope_adapter`` / spine: ``governed_pa_l2_exit`` (via ``ProviderGateway``).

Ownership unchanged: apps_rg-local seam; not FEC and not a pseudo-FEC surface.
"""
from __future__ import annotations

import errno
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any

from apps_rg.runtime.artifact_secret_redaction import redact_sensitive_mapping
from apps_rg.runtime.validators.executive_summary_x2 import ALLOWED_MODELS


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
        return redact_sensitive_mapping(asdict(self))


@dataclass
class ProviderResult:
    provider_requested: str
    provider_attempted: bool
    provider_available: bool
    exact_provider_error: str | None
    runtime_generation_status: str  # REAL_LLM | BLOCKED | MOCKED | STUBBED
    model: str
    raw_model_output: str
    provider_response: dict[str, Any] | None
    reasoning_execution_receipt: dict[str, Any] | None = None
    stub: bool = False
    apps_rg_qwen_preflight_blocked: bool = False
    apps_rg_last_probe_snapshot: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assert_temperature_in_profile(
    temperature: float,
    low: float = 0.0,
    high: float = 0.99,
) -> None:
    if not (low <= temperature <= high):
        raise ValueError(f"temperature {temperature} outside allowed bounds [{low}, {high}]")


def _normalize_model_key(model: str) -> str:
    return re.sub(r"\s+", "", str(model).strip().lower())


def _resolved_model_from_completion(response_data: dict[str, Any], fallback: str) -> str:
    m = response_data.get("model")
    if m is not None and str(m).strip():
        return str(m).strip()
    return str(fallback).strip()


_SYNTHETIC_MODEL_MARKERS = (
    "synthetic",
    "intest",
    "unittest",
    "unit-test",
    "dummy",
    "placeholder",
)


def classify_exec_summary_qwen_generation(
    *,
    requested_model: str,
    response_data: dict[str, Any] | None,
) -> tuple[str, str]:
    """Classify generation proof for executive_summary Qwen slice.

    Returns (runtime_generation_status, resolved_model_to_record).
    STUBBED: test harness / synthetic identity / allowlist mismatch / explicit stub flag.
    """
    req = str(requested_model).strip()
    body = response_data if isinstance(response_data, dict) else {}
    resolved = _resolved_model_from_completion(body, req)

    if body.get("stub") is True:
        return "STUBBED", resolved

    low = resolved.lower()
    for mk in _SYNTHETIC_MODEL_MARKERS:
        if mk in low:
            return "STUBBED", resolved

    allow = set(ALLOWED_MODELS)
    if resolved not in allow:
        return "STUBBED", resolved

    if _normalize_model_key(req) != _normalize_model_key(resolved):
        return "STUBBED", resolved

    return "REAL_LLM", resolved


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

    Bounded W3 retries apply **only** to transient transport failures on chat/completions
    (timeouts, narrow 5xx, connection refused/reset). Semantic failures (empty choices,
    JSON parse, STUBBED model classification, 4xx auth/not-found) are not retried.

    If unavailable after retries, returns BLOCKED. It never silently falls back to mock.
    """
    from apps_rg.runtime import qwen_transport_diag as qtd

    if timeout is None:
        timeout = payload.get("timeout_seconds", DEFAULT_QWEN_TIMEOUT_SECONDS)
    req_model = str(payload.get("model", DEFAULT_QWEN_MODEL))
    max_att = qtd.max_transport_attempts()
    attempts_trace: list[dict[str, Any]] = []
    retry_reasons: list[str] = []

    def _trace(
        *,
        attempt_num: int,
        error_category: str,
        http_status: int | None,
        exception: BaseException | None,
        body_fragment: str,
        note: str | None = None,
    ) -> None:
        attempts_trace.append(
            {
                "attempt_index": attempt_num,
                "phase": "chat_completions",
                "error_category": error_category,
                "http_status": http_status,
                "exception_type": None if exception is None else type(exception).__name__,
                "redacted_message": qtd.redacted_exception_message(exception, body_fragment)[:500],
                "note": note,
            }
        )

    for attempt_idx in range(max_att):
        attempt_num = attempt_idx + 1
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
                out = ProviderResult(
                    provider_requested="qwen_vllm",
                    provider_attempted=True,
                    provider_available=False,
                    exact_provider_error="Qwen/vLLM returned no choices",
                    runtime_generation_status="BLOCKED",
                    model=req_model,
                    raw_model_output="",
                    provider_response=response_data,
                )
                _trace(
                    attempt_num=attempt_num,
                    error_category=qtd.ERR_MALFORMED_RESPONSE,
                    http_status=None,
                    exception=None,
                    body_fragment="",
                    note="empty_choices",
                )
                qtd.persist_failure_for_provider_result(
                    result=out,
                    base_url=base_url,
                    timeout_seconds=int(timeout),
                    exception=None,
                    http_status=None,
                    body_fragment="",
                    error_category=qtd.ERR_MALFORMED_RESPONSE,
                    probe_snapshot=None,
                    attempt_count=attempt_num,
                    retry_reasons=retry_reasons,
                    attempts=attempts_trace,
                    final_error_category=qtd.ERR_MALFORMED_RESPONSE,
                    retried=len(retry_reasons) > 0,
                    model=req_model,
                )
                return out
            text = choices[0].get("message", {}).get("content", "")
            gen_status, resolved_model = classify_exec_summary_qwen_generation(
                requested_model=req_model,
                response_data=response_data,
            )
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=True,
                exact_provider_error=None,
                runtime_generation_status=gen_status,
                model=resolved_model,
                raw_model_output=text,
                provider_response=response_data,
                stub=gen_status == "STUBBED",
            )
            if gen_status == "REAL_LLM" and retry_reasons:
                qtd.persist_success_after_transport_retries(
                    base_url=base_url,
                    timeout_seconds=int(timeout),
                    attempt_count=attempt_num,
                    retry_reasons=retry_reasons,
                    attempts=attempts_trace,
                    model=resolved_model,
                )
            return out
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
            except OSError:
                detail = ""
            code_i = int(exc.code)
            cat = qtd.classify_http_error(code=code_i) or qtd.ERR_UNKNOWN
            _trace(
                attempt_num=attempt_num,
                error_category=cat,
                http_status=code_i,
                exception=exc,
                body_fragment=detail,
            )
            transient = qtd.is_transient_chat_http_status(code_i)
            if transient and attempt_idx < max_att - 1:
                retry_reasons.append(f"transient_http_{code_i}")
                time.sleep(qtd.transport_retry_backoff_seconds(attempt_idx))
                continue
            tail = f" {detail}" if detail else ""
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=(
                    f"Cannot reach Qwen/vLLM at {base_url}: HTTP {exc.code} {exc.reason}{tail}"
                ),
                runtime_generation_status="BLOCKED",
                model=req_model,
                raw_model_output="",
                provider_response=None,
            )
            qtd.persist_failure_for_provider_result(
                result=out,
                base_url=base_url,
                timeout_seconds=int(timeout),
                exception=exc,
                http_status=code_i,
                body_fragment=detail,
                error_category=cat,
                probe_snapshot=None,
                attempt_count=attempt_num,
                retry_reasons=retry_reasons,
                attempts=attempts_trace,
                final_error_category=cat,
                retried=len(retry_reasons) > 0,
                model=req_model,
            )
            return out
        except urllib.error.URLError as exc:
            cat = qtd.ERR_TCP_CONNECT
            transient = qtd.is_transient_url_error(exc)
            _trace(attempt_num=attempt_num, error_category=cat, http_status=None, exception=exc, body_fragment="")
            if transient and attempt_idx < max_att - 1:
                retry_reasons.append("transient_url_error")
                time.sleep(qtd.transport_retry_backoff_seconds(attempt_idx))
                continue
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"Cannot reach Qwen/vLLM at {base_url}: {getattr(exc, 'reason', exc)}",
                runtime_generation_status="BLOCKED",
                model=req_model,
                raw_model_output="",
                provider_response=None,
            )
            qtd.persist_failure_for_provider_result(
                result=out,
                base_url=base_url,
                timeout_seconds=int(timeout),
                exception=exc,
                http_status=None,
                body_fragment="",
                error_category=cat,
                probe_snapshot=None,
                attempt_count=attempt_num,
                retry_reasons=retry_reasons,
                attempts=attempts_trace,
                final_error_category=cat,
                retried=len(retry_reasons) > 0,
                model=req_model,
            )
            return out
        except TimeoutError as exc:
            cat = qtd.ERR_CHAT_TIMEOUT
            _trace(attempt_num=attempt_num, error_category=cat, http_status=None, exception=exc, body_fragment="")
            if attempt_idx < max_att - 1:
                retry_reasons.append("timeout")
                time.sleep(qtd.transport_retry_backoff_seconds(attempt_idx))
                continue
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"Qwen/vLLM call failed: {type(exc).__name__}: {exc}",
                runtime_generation_status="BLOCKED",
                model=req_model,
                raw_model_output="",
                provider_response=None,
            )
            qtd.persist_failure_for_provider_result(
                result=out,
                base_url=base_url,
                timeout_seconds=int(timeout),
                exception=exc,
                http_status=None,
                body_fragment="",
                error_category=cat,
                probe_snapshot=None,
                attempt_count=attempt_num,
                retry_reasons=retry_reasons,
                attempts=attempts_trace,
                final_error_category=cat,
                retried=len(retry_reasons) > 0,
                model=req_model,
            )
            return out
        except json.JSONDecodeError as exc:
            cat = qtd.ERR_MALFORMED_RESPONSE
            _trace(attempt_num=attempt_num, error_category=cat, http_status=None, exception=exc, body_fragment="")
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"Qwen/vLLM call failed: {type(exc).__name__}: {exc}",
                runtime_generation_status="BLOCKED",
                model=req_model,
                raw_model_output="",
                provider_response=None,
            )
            qtd.persist_failure_for_provider_result(
                result=out,
                base_url=base_url,
                timeout_seconds=int(timeout),
                exception=exc,
                http_status=None,
                body_fragment="",
                error_category=cat,
                probe_snapshot=None,
                attempt_count=attempt_num,
                retry_reasons=retry_reasons,
                attempts=attempts_trace,
                final_error_category=cat,
                retried=len(retry_reasons) > 0,
                model=req_model,
            )
            return out
        except OSError as exc:
            cat = qtd.ERR_TCP_CONNECT
            _wsa_reset = getattr(errno, "WSAECONNRESET", None)
            _retryable_errno = (errno.ECONNRESET, errno.ECONNREFUSED, errno.ETIMEDOUT)
            if _wsa_reset is not None:
                _retryable_errno = _retryable_errno + (_wsa_reset,)
            _en = getattr(exc, "errno", None)
            transient = isinstance(exc, (ConnectionResetError, BrokenPipeError)) or _en in _retryable_errno
            _trace(attempt_num=attempt_num, error_category=cat, http_status=None, exception=exc, body_fragment="")
            if transient and attempt_idx < max_att - 1:
                retry_reasons.append("transient_os_error")
                time.sleep(qtd.transport_retry_backoff_seconds(attempt_idx))
                continue
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"Qwen/vLLM call failed: {type(exc).__name__}: {exc}",
                runtime_generation_status="BLOCKED",
                model=req_model,
                raw_model_output="",
                provider_response=None,
            )
            qtd.persist_failure_for_provider_result(
                result=out,
                base_url=base_url,
                timeout_seconds=int(timeout),
                exception=exc,
                http_status=None,
                body_fragment="",
                error_category=cat,
                probe_snapshot=None,
                attempt_count=attempt_num,
                retry_reasons=retry_reasons,
                attempts=attempts_trace,
                final_error_category=cat,
                retried=len(retry_reasons) > 0,
                model=req_model,
            )
            return out
        except Exception as exc:  # noqa: BLE001
            cat = qtd.ERR_UNKNOWN
            _trace(attempt_num=attempt_num, error_category=cat, http_status=None, exception=exc, body_fragment="")
            out = ProviderResult(
                provider_requested="qwen_vllm",
                provider_attempted=True,
                provider_available=False,
                exact_provider_error=f"Qwen/vLLM call failed: {type(exc).__name__}: {exc}",
                runtime_generation_status="BLOCKED",
                model=req_model,
                raw_model_output="",
                provider_response=None,
            )
            qtd.persist_failure_for_provider_result(
                result=out,
                base_url=base_url,
                timeout_seconds=int(timeout),
                exception=exc,
                http_status=None,
                body_fragment="",
                error_category=cat,
                probe_snapshot=None,
                attempt_count=attempt_num,
                retry_reasons=retry_reasons,
                attempts=attempts_trace,
                final_error_category=cat,
                retried=len(retry_reasons) > 0,
                model=req_model,
            )
            return out

    # Exhausted (defensive — loop always returns)
    return ProviderResult(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_available=False,
        exact_provider_error="Qwen/vLLM transport retry budget exhausted",
        runtime_generation_status="BLOCKED",
        model=req_model,
        raw_model_output="",
        provider_response=None,
    )
