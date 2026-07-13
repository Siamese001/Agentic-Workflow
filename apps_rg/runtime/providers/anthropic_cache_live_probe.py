"""Minimal live Anthropic prompt-cache hit probe for promotion evidence.

The probe performs two sequential Messages API calls with the exact same stable
prefix. It succeeds only when the second call reports cache-read tokens and the
observable text output is identical. No API key or raw request headers are
written to the receipt.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from agentic_core.knowledge.retrieval import min_cacheable_chars
from apps_rg.runtime.providers.anthropic_prompt_cache import build_cache_receipt_from_usage

DEFAULT_ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
LIVE_PROBE_SCHEMA = "apps_rg_anthropic_cache_live_probe_v1"
Urlopen = Callable[..., Any]


def _stable_prefix(model: str, *, extra_chars: int = 512) -> str:
    floor = min_cacheable_chars(model)
    seed = (
        "APPS_RG LIVE PROMPT-CACHE PROBE. This text is inert test data, not application authority. "
        "Return the fixed response requested by the user message. "
    )
    target = max(floor + max(0, int(extra_chars)), len(seed))
    repeats = (target // len(seed)) + 1
    return (seed * repeats)[:target]


def _response_text(payload: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for block in payload.get("content") or []:
        if isinstance(block, Mapping) and str(block.get("type") or "") == "text":
            parts.append(str(block.get("text") or ""))
    return "".join(parts).strip()


def _post_message(
    *,
    api_key: str,
    model: str,
    stable_prefix: str,
    url: str,
    opener: Urlopen,
    timeout_seconds: float,
) -> dict[str, Any]:
    body = {
        "model": model,
        "max_tokens": 16,
        "system": [
            {
                "type": "text",
                "text": stable_prefix,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly: CACHE_PROBE_OK",
            }
        ],
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with opener(request, timeout=timeout_seconds) as response:
        raw = response.read().decode("utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("Anthropic live probe response root must be an object")
    return payload


def run_live_cache_probe(
    *,
    api_key: str,
    model: str = "claude-sonnet-5",
    url: str = DEFAULT_ANTHROPIC_MESSAGES_URL,
    opener: Urlopen = urllib.request.urlopen,
    timeout_seconds: float = 90.0,
    sleep_seconds: float = 0.0,
    input_usd_per_million: float | None = None,
) -> dict[str, Any]:
    if not str(api_key or "").strip():
        raise ValueError("Anthropic API key is required")
    stable_prefix = _stable_prefix(model)
    started = datetime.now(timezone.utc).isoformat()

    first = _post_message(
        api_key=api_key,
        model=model,
        stable_prefix=stable_prefix,
        url=url,
        opener=opener,
        timeout_seconds=timeout_seconds,
    )
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    second = _post_message(
        api_key=api_key,
        model=model,
        stable_prefix=stable_prefix,
        url=url,
        opener=opener,
        timeout_seconds=timeout_seconds,
    )

    seed: dict[str, Any] = {
        "provider": "anthropic_claude",
        "model": model,
        "section_id": "anthropic_cache_live_probe",
        "cache_enabled": True,
        "cache_strategy": "single_5m_live_probe_v1",
        "cache_marker_count": 1,
        "active_cache_ttls": ["5m"],
        "stable_prefix_chars": len(stable_prefix),
    }
    if input_usd_per_million is not None:
        seed["input_usd_per_million"] = float(input_usd_per_million)

    first_usage = first.get("usage") if isinstance(first.get("usage"), Mapping) else {}
    second_usage = second.get("usage") if isinstance(second.get("usage"), Mapping) else {}
    first_receipt = build_cache_receipt_from_usage(
        seed={**seed, "probe_call": 1},
        provider="anthropic_claude",
        model=model,
        section_id="anthropic_cache_live_probe",
        usage=first_usage,
    )
    second_receipt = build_cache_receipt_from_usage(
        seed={**seed, "probe_call": 2},
        provider="anthropic_claude",
        model=model,
        section_id="anthropic_cache_live_probe",
        usage=second_usage,
    )
    first_text = _response_text(first)
    second_text = _response_text(second)
    read_tokens = int(second_receipt.get("cache_read_input_tokens") or 0)
    outputs_equal = bool(first_text and first_text == second_text)
    expected_text = "CACHE_PROBE_OK"
    output_contract_ok = outputs_equal and first_text == expected_text
    savings_positive = float(second_receipt.get("estimated_input_token_savings") or 0.0) > 0
    pass_ = read_tokens > 0 and output_contract_ok and savings_positive

    return {
        "schema": LIVE_PROBE_SCHEMA,
        "status": "PASS" if pass_ else "BLOCKED",
        "pass": pass_,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "anthropic",
        "model": model,
        "stable_prefix_chars": len(stable_prefix),
        "model_cache_floor_chars": min_cacheable_chars(model),
        "outputs_equal": outputs_equal,
        "output_contract_ok": output_contract_ok,
        "output_sha256": __import__("hashlib").sha256(first_text.encode("utf-8")).hexdigest() if first_text else "",
        "second_call_cache_read_input_tokens": read_tokens,
        "second_call_estimated_input_token_savings": second_receipt.get("estimated_input_token_savings"),
        "second_call_estimated_input_cost_savings_usd": second_receipt.get("estimated_input_cost_savings_usd"),
        "promotion_reasons": [
            reason
            for condition, reason in (
                (read_tokens <= 0, "second_call_has_no_cache_read_tokens"),
                (not output_contract_ok, "two_call_output_contract_mismatch"),
                (not savings_positive, "second_call_has_no_positive_input_token_savings"),
            )
            if condition
        ],
        "calls": [first_receipt, second_receipt],
    }


__all__ = [
    "DEFAULT_ANTHROPIC_MESSAGES_URL",
    "LIVE_PROBE_SCHEMA",
    "run_live_cache_probe",
]
