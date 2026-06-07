"""Model pricing table — USD per token, configurable.

Pricing is intentionally a separate module so it can be swapped (test pricing
vs prod pricing, year-over-year tariff changes, etc.) without touching the
aggregator. The table is read-mostly; mutate via a fresh instance.

Default pricing reflects mid-2026 list rates (rounded conservatively). Adjust
in :func:`default_pricing_table` when contracts change. For per-environment
overrides, construct your own ``PricingTable`` and pass it to
``aggregate_by_app(pricing_table=...)``.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (W4.3)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class ModelPricing:
    """Per-model rates. Both rates are USD per single token (NOT per 1k)."""

    input_usd_per_token: float
    output_usd_per_token: float


# Conservative fallback for unknown models — high enough to surface
# missing-pricing-config as a visible cost, low enough not to bankrupt
# a single test run.
_UNKNOWN_FALLBACK = ModelPricing(
    input_usd_per_token=0.000_010,   # $10 / 1M input tokens
    output_usd_per_token=0.000_030,  # $30 / 1M output tokens
)


@dataclass(frozen=True)
class PricingTable:
    """Lookup table from model_id → ModelPricing.

    ``unknown_model`` is the fallback used when a model_id is not in the
    table — set via the constructor; the default is conservative.
    """

    by_model: Mapping[str, ModelPricing] = field(default_factory=dict)
    unknown_model: ModelPricing = _UNKNOWN_FALLBACK

    def lookup(self, model_id: str) -> ModelPricing:
        return self.by_model.get(model_id, self.unknown_model)


def default_pricing_table() -> PricingTable:
    """Return the default model pricing table.

    All rates are USD per single token. Hosted-inference rates are list
    prices for 2026 mid-year; self-hosted models (e.g. local Qwen) get a
    nominal compute-cost estimate based on amortised GPU-hour ÷ throughput.
    """
    return PricingTable(
        by_model={
            # Hosted Anthropic
            "claude-sonnet-4.5": ModelPricing(
                input_usd_per_token=0.000_003,
                output_usd_per_token=0.000_015,
            ),
            "claude-opus-4.7": ModelPricing(
                input_usd_per_token=0.000_015,
                output_usd_per_token=0.000_075,
            ),
            "claude-haiku-4.5": ModelPricing(
                input_usd_per_token=0.000_001,
                output_usd_per_token=0.000_005,
            ),
            # Hosted Google
            "gemini-2.5-flash": ModelPricing(
                input_usd_per_token=0.000_000_30,
                output_usd_per_token=0.000_002_50,
            ),
            "gemini-2.5-pro": ModelPricing(
                input_usd_per_token=0.000_001_25,
                output_usd_per_token=0.000_010_00,
            ),
            # Self-hosted Qwen (compute-cost amortised; tune as actuals land)
            "qwen-32b": ModelPricing(
                input_usd_per_token=0.000_000_50,
                output_usd_per_token=0.000_001_00,
            ),
            "qwen-7b": ModelPricing(
                input_usd_per_token=0.000_000_10,
                output_usd_per_token=0.000_000_20,
            ),
        },
    )


__all__ = [
    "ModelPricing",
    "PricingTable",
    "default_pricing_table",
]
