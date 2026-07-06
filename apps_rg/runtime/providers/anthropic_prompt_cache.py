"""Anthropic prompt-cache flags and provider-neutral receipts.

Wave 0 keeps prompt caching observational: no native Anthropic payloads and no
``cache_control`` markers are emitted here. The receipt shape is shared early so
later waves can add cacheable payload rendering without changing proof verdicts.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Mapping


ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE = "APPS_RG_ANTHROPIC_PROMPT_CACHE"
ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY = "APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY"
ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM = "APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM"
ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT = "APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT"


@dataclass(frozen=True)
class ProviderCacheReceipt:
    provider: str
    model: str
    section_id: str
    cache_enabled: bool
    cache_strategy: str
    stable_prefix_hash: str
    c0_prefix_hash: str
    volatile_tail_hash: str
    cache_marker_count: int
    input_tokens: int | None
    output_tokens: int | None
    cache_creation_input_tokens: int | None
    cache_read_input_tokens: int | None
    cache_hit_ratio: float | None
    estimated_uncached_input_tokens: int | None
    estimated_cached_input_tokens: int | None
    cache_savings_estimate_source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def env_flag_enabled(name: str, environ: Mapping[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    return str(env.get(name) or "").strip() == "1"


def anthropic_prompt_cache_enabled(environ: Mapping[str, str] | None = None) -> bool:
    return env_flag_enabled(ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE, environ)


def anthropic_prompt_cache_telemetry_enabled(environ: Mapping[str, str] | None = None) -> bool:
    return env_flag_enabled(ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY, environ)


def anthropic_prompt_cache_prewarm_enabled(environ: Mapping[str, str] | None = None) -> bool:
    return env_flag_enabled(ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM, environ)


def anthropic_prompt_cache_fanout_enabled(environ: Mapping[str, str] | None = None) -> bool:
    return env_flag_enabled(ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT, environ)


def build_disabled_cache_receipt(
    *,
    provider: str,
    model: str,
    section_id: str | None = None,
) -> dict[str, Any]:
    return ProviderCacheReceipt(
        provider=str(provider or ""),
        model=str(model or ""),
        section_id=str(section_id or ""),
        cache_enabled=False,
        cache_strategy="disabled",
        stable_prefix_hash="",
        c0_prefix_hash="",
        volatile_tail_hash="",
        cache_marker_count=0,
        input_tokens=None,
        output_tokens=None,
        cache_creation_input_tokens=None,
        cache_read_input_tokens=None,
        cache_hit_ratio=None,
        estimated_uncached_input_tokens=None,
        estimated_cached_input_tokens=None,
        cache_savings_estimate_source="not_estimated_cache_disabled",
    ).to_dict()


def _coerce_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def build_cache_receipt_from_usage(
    *,
    seed: Mapping[str, Any] | None,
    provider: str,
    model: str,
    section_id: str | None = None,
    usage: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge Anthropic usage counters into a provider-neutral cache receipt."""
    usage_map = usage if isinstance(usage, Mapping) else {}
    input_tokens = _coerce_int(usage_map.get("input_tokens"))
    output_tokens = _coerce_int(usage_map.get("output_tokens"))
    creation_tokens = _coerce_int(usage_map.get("cache_creation_input_tokens"))
    read_tokens = _coerce_int(usage_map.get("cache_read_input_tokens"))
    cached_input = (input_tokens or 0) + (creation_tokens or 0) + (read_tokens or 0)
    uncached_input = cached_input
    denom = (creation_tokens or 0) + (read_tokens or 0)
    hit_ratio = round(float(read_tokens or 0) / float(denom), 6) if denom > 0 else None
    merged = dict(seed or {})
    merged.update(
        {
            "provider": str(merged.get("provider") or provider or ""),
            "model": str(merged.get("model") or model or ""),
            "section_id": str(merged.get("section_id") or section_id or ""),
            "cache_enabled": bool(merged.get("cache_enabled", False)),
            "cache_strategy": str(merged.get("cache_strategy") or "unknown"),
            "stable_prefix_hash": str(merged.get("stable_prefix_hash") or ""),
            "c0_prefix_hash": str(merged.get("c0_prefix_hash") or ""),
            "volatile_tail_hash": str(merged.get("volatile_tail_hash") or ""),
            "cache_marker_count": int(merged.get("cache_marker_count") or 0),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_creation_input_tokens": creation_tokens,
            "cache_read_input_tokens": read_tokens,
            "cache_hit_ratio": hit_ratio,
            "estimated_uncached_input_tokens": uncached_input if uncached_input else None,
            "estimated_cached_input_tokens": cached_input if cached_input else None,
            "cache_savings_estimate_source": (
                "anthropic_usage"
                if any(v is not None for v in (input_tokens, creation_tokens, read_tokens))
                else "usage_absent"
            ),
        }
    )
    return merged


__all__ = [
    "ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE",
    "ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT",
    "ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM",
    "ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY",
    "ProviderCacheReceipt",
    "anthropic_prompt_cache_enabled",
    "anthropic_prompt_cache_fanout_enabled",
    "anthropic_prompt_cache_prewarm_enabled",
    "anthropic_prompt_cache_telemetry_enabled",
    "build_disabled_cache_receipt",
    "build_cache_receipt_from_usage",
    "env_flag_enabled",
]
