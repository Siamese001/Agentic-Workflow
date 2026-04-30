"""Cost telemetry — per-app and portfolio rollup over LLM inference samples.

Public API:
    CostSample         — input record (one LLM call's tokens + latency)
    aggregate_by_app() — produces per-app + portfolio rollup
    AppCostRollup      — per-app result with $/call, p50/p95 latency
    PortfolioCostRollup — portfolio rollup with .summary() for RUNBOOKs
    ModelPricing       — single model's USD/token rates
    PricingTable       — lookup table; default_pricing_table() returns 2026 list rates

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.3)
"""
from __future__ import annotations

from tools.cost_telemetry.aggregator import (
    AppCostRollup,
    CostSample,
    PortfolioCostRollup,
    aggregate_by_app,
)
from tools.cost_telemetry.pricing import (
    ModelPricing,
    PricingTable,
    default_pricing_table,
)

__all__ = [
    "AppCostRollup",
    "CostSample",
    "ModelPricing",
    "PortfolioCostRollup",
    "PricingTable",
    "aggregate_by_app",
    "default_pricing_table",
]
