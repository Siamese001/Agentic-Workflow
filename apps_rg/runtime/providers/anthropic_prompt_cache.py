"""Anthropic prompt-cache flags, usage normalization, and cost receipts.

Cache telemetry is observational. It never changes runtime gates, X3 outcomes, or
write authority. Cost estimates use Anthropic's documented token multipliers and
optionally convert to USD when a base input-token price is supplied by environment.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Mapping


ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE = "APPS_RG_ANTHROPIC_PROMPT_CACHE"
ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY = "APPS_RG_ANTHROPIC_PROMPT_CACHE_TELEMETRY"
ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM = "APPS_RG_ANTHROPIC_PROMPT_CACHE_PREWARM"
ENV_APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT = "APPS_RG_ANTHROPIC_PROMPT_CACHE_FANOUT"
ENV_APPS_RG_ANTHROPIC_INPUT_USD_PER_MILLION = "APPS_RG_ANTHROPIC_INPUT_USD_PER_MILLION"

CACHE_READ_INPUT_MULTIPLIER = 0.10
CACHE_WRITE_5M_INPUT_MULTIPLIER = 1.25
CACHE_WRITE_1H_INPUT_MULTIPLIER = 2.00
CACHE_HIT_RATIO_DEFINITION = "cache_read_input_tokens/(cache_creation_input_tokens+cache_read_input_tokens)"


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


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _active_cache_ttls(seed: Mapping[str, Any] | None) -> list[str]:
    raw = (seed or {}).get("active_cache_ttls")
    if not isinstance(raw, (list, tuple)):
        return []
    return [str(item).strip().lower() for item in raw if str(item).strip()]


def _cache_creation_breakdown(
    usage_map: Mapping[str, Any],
    *,
    creation_tokens: int,
    seed: Mapping[str, Any] | None,
) -> tuple[int, int, int, str]:
    detail = usage_map.get("cache_creation")
    detail_map = detail if isinstance(detail, Mapping) else {}
    creation_5m = _coerce_int(detail_map.get("ephemeral_5m_input_tokens")) or 0
    creation_1h = _coerce_int(detail_map.get("ephemeral_1h_input_tokens")) or 0
    attributed = creation_5m + creation_1h
    unattributed = max(0, int(creation_tokens) - attributed)
    if attributed:
        basis = "anthropic_usage_cache_creation_breakdown"
    elif creation_tokens:
        ttls = _active_cache_ttls(seed)
        if ttls == ["1h"]:
            creation_1h = int(creation_tokens)
            unattributed = 0
            basis = "single_active_1h_marker"
        elif ttls == ["5m"]:
            creation_5m = int(creation_tokens)
            unattributed = 0
            basis = "single_active_5m_marker"
        else:
            basis = "aggregate_creation_conservative_multiplier"
    else:
        basis = "no_cache_creation"
    return creation_5m, creation_1h, unattributed, basis


def _fallback_creation_multiplier(seed: Mapping[str, Any] | None) -> float:
    ttls = _active_cache_ttls(seed)
    return CACHE_WRITE_1H_INPUT_MULTIPLIER if "1h" in ttls else CACHE_WRITE_5M_INPUT_MULTIPLIER


def _input_price_usd_per_million(seed: Mapping[str, Any] | None) -> float | None:
    seeded = _coerce_float((seed or {}).get("input_usd_per_million"))
    if seeded is not None:
        return seeded
    return _coerce_float(os.environ.get(ENV_APPS_RG_ANTHROPIC_INPUT_USD_PER_MILLION))


def build_cache_receipt_from_usage(
    *,
    seed: Mapping[str, Any] | None,
    provider: str,
    model: str,
    section_id: str | None = None,
    usage: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge Anthropic usage counters into a provider-neutral cache receipt.

    The uncached estimate treats every cache-created/read token as normal input.
    The cached estimate applies 1.25x for 5-minute writes, 2.0x for 1-hour
    writes, and 0.10x for reads. When Anthropic omits the creation-TTL
    breakdown, the estimate uses the active marker TTLs and otherwise applies a
    conservative multiplier.
    """
    usage_map = usage if isinstance(usage, Mapping) else {}
    input_tokens = _coerce_int(usage_map.get("input_tokens"))
    output_tokens = _coerce_int(usage_map.get("output_tokens"))
    creation_tokens = _coerce_int(usage_map.get("cache_creation_input_tokens"))
    read_tokens = _coerce_int(usage_map.get("cache_read_input_tokens"))

    normal_input = input_tokens or 0
    creation_total = creation_tokens or 0
    read_total = read_tokens or 0
    creation_5m, creation_1h, unattributed_creation, creation_basis = _cache_creation_breakdown(
        usage_map,
        creation_tokens=creation_total,
        seed=seed,
    )
    fallback_multiplier = _fallback_creation_multiplier(seed)

    uncached_equivalent = float(normal_input + creation_total + read_total)
    cached_equivalent = (
        float(normal_input)
        + float(creation_5m) * CACHE_WRITE_5M_INPUT_MULTIPLIER
        + float(creation_1h) * CACHE_WRITE_1H_INPUT_MULTIPLIER
        + float(unattributed_creation) * fallback_multiplier
        + float(read_total) * CACHE_READ_INPUT_MULTIPLIER
    )
    savings_equivalent = uncached_equivalent - cached_equivalent
    denom = creation_total + read_total
    hit_ratio = round(float(read_total) / float(denom), 6) if denom > 0 else None

    price = _input_price_usd_per_million(seed)
    uncached_cost = (uncached_equivalent * price / 1_000_000.0) if price is not None else None
    cached_cost = (cached_equivalent * price / 1_000_000.0) if price is not None else None
    cost_savings = (uncached_cost - cached_cost) if uncached_cost is not None and cached_cost is not None else None

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
            "cache_creation_5m_input_tokens": creation_5m or None,
            "cache_creation_1h_input_tokens": creation_1h or None,
            "cache_creation_unattributed_input_tokens": unattributed_creation or None,
            "cache_creation_cost_basis": creation_basis,
            "cache_read_input_tokens": read_tokens,
            "cache_hit_ratio": hit_ratio,
            "cache_hit_ratio_definition": CACHE_HIT_RATIO_DEFINITION,
            "estimated_uncached_input_tokens": round(uncached_equivalent) if uncached_equivalent else None,
            "estimated_cached_input_tokens": round(cached_equivalent) if cached_equivalent else None,
            "estimated_input_token_savings": round(savings_equivalent, 3),
            "input_usd_per_million": price,
            "estimated_input_cost_without_cache_usd": round(uncached_cost, 8) if uncached_cost is not None else None,
            "estimated_input_cost_with_cache_usd": round(cached_cost, 8) if cached_cost is not None else None,
            "estimated_input_cost_savings_usd": round(cost_savings, 8) if cost_savings is not None else None,
            "cache_savings_estimate_source": (
                "anthropic_usage_multipliers_v1"
                if any(v is not None for v in (input_tokens, creation_tokens, read_tokens))
                else "usage_absent"
            ),
        }
    )
    return merged


__all__ = [
    "CACHE_HIT_RATIO_DEFINITION",
    "CACHE_READ_INPUT_MULTIPLIER",
    "CACHE_WRITE_1H_INPUT_MULTIPLIER",
    "CACHE_WRITE_5M_INPUT_MULTIPLIER",
    "ENV_APPS_RG_ANTHROPIC_INPUT_USD_PER_MILLION",
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
