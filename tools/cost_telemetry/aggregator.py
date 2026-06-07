"""Cost-telemetry rollup — per-app and portfolio-wide.

Closes W4.3 from the apps SVP+ hardening plan: per-app cost telemetry rollup
($/eval-call, $/brief, $/proposal, etc.) that any app's RUNBOOK can query
and the L6 promotion gate can use as a secondary regression signal.

Architecture (deliberate):
  - This module is PURE — no I/O, no MCP, no network.
  - It consumes ``QwenSessionMetrics``-shaped records or any iterable of
    :class:`CostSample` dicts. The collector (Qwen telemetry, OTEL spans,
    JSONL replay) is decoupled from the aggregator.
  - Pricing lives in :mod:`tools.cost_telemetry.pricing` so per-model rates
    can be tuned without touching the aggregator.

Usage:
    from tools.cost_telemetry import aggregate_by_app, CostSample

    samples = [
        CostSample(app="apps_eval", model_id="qwen-32b",
                   input_tokens=1200, output_tokens=400, latency_ms=850.0),
        ...
    ]
    rollup = aggregate_by_app(samples)
    print(rollup.summary())

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (W4.3)
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from tools.cost_telemetry.pricing import ModelPricing, PricingTable, default_pricing_table


@dataclass(frozen=True)
class CostSample:
    """One unit of inference cost — typically one LLM call."""

    app: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency_ms: float = 0.0
    success: bool = True


@dataclass(frozen=True)
class AppCostRollup:
    """Per-app cost rollup."""

    app: str
    n_calls: int
    n_failed: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    p50_latency_ms: float
    p95_latency_ms: float
    by_model: dict[str, "AppCostRollup"] = field(default_factory=dict)

    @property
    def cost_per_call_usd(self) -> float:
        return self.total_cost_usd / self.n_calls if self.n_calls else 0.0

    @property
    def success_rate(self) -> float:
        return (self.n_calls - self.n_failed) / self.n_calls if self.n_calls else 0.0


@dataclass(frozen=True)
class PortfolioCostRollup:
    """Portfolio-wide cost rollup with per-app breakdown."""

    by_app: dict[str, AppCostRollup]
    total_cost_usd: float
    total_calls: int

    def summary(self) -> str:
        """Human-readable summary; for RUNBOOK output."""
        lines = [
            f"Portfolio cost rollup: ${self.total_cost_usd:.4f} across {self.total_calls} calls",
            "  Per-app breakdown:",
        ]
        for app in sorted(self.by_app):
            r = self.by_app[app]
            lines.append(
                f"    {app:30s} ${r.total_cost_usd:>9.4f}  "
                f"(n={r.n_calls}, $/call={r.cost_per_call_usd:.5f}, "
                f"success={r.success_rate:.1%}, p95={r.p95_latency_ms:.0f}ms)"
            )
        return "\n".join(lines)


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if pct <= 0:
        return sorted_values[0]
    if pct >= 100:
        return sorted_values[-1]
    # Linear interpolation between sorted_values[k] and sorted_values[k+1].
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = rank - lo
    return sorted_values[lo] + frac * (sorted_values[hi] - sorted_values[lo])


def _cost_for_sample(sample: CostSample, pricing: ModelPricing) -> float:
    return (
        sample.input_tokens * pricing.input_usd_per_token
        + sample.output_tokens * pricing.output_usd_per_token
    )


def aggregate_by_app(
    samples: Iterable[CostSample],
    *,
    pricing_table: PricingTable | None = None,
) -> PortfolioCostRollup:
    """Aggregate cost samples into per-app + portfolio rollups.

    Unknown model IDs are priced at the table's ``unknown_model`` fallback
    (deliberately conservative — surfaces missing-pricing-config as a high
    estimated cost rather than silently $0).
    """
    table = pricing_table or default_pricing_table()
    samples_list = list(samples)
    if not samples_list:
        return PortfolioCostRollup(by_app={}, total_cost_usd=0.0, total_calls=0)

    by_app_buckets: dict[str, list[CostSample]] = defaultdict(list)
    for s in samples_list:
        by_app_buckets[s.app].append(s)

    by_app: dict[str, AppCostRollup] = {}
    portfolio_total_cost = 0.0
    portfolio_total_calls = 0

    for app, app_samples in by_app_buckets.items():
        n_calls = len(app_samples)
        n_failed = sum(1 for s in app_samples if not s.success)
        total_in = sum(s.input_tokens for s in app_samples)
        total_out = sum(s.output_tokens for s in app_samples)
        total_cost = sum(
            _cost_for_sample(s, table.lookup(s.model_id)) for s in app_samples
        )
        latencies = sorted(s.latency_ms for s in app_samples)
        p50 = _percentile(latencies, 50.0)
        p95 = _percentile(latencies, 95.0)

        # Per-model breakdown (recursive 1-level for readability).
        by_model_buckets: dict[str, list[CostSample]] = defaultdict(list)
        for s in app_samples:
            by_model_buckets[s.model_id].append(s)
        by_model: dict[str, AppCostRollup] = {}
        for model_id, model_samples in by_model_buckets.items():
            mn = len(model_samples)
            mfailed = sum(1 for s in model_samples if not s.success)
            mtin = sum(s.input_tokens for s in model_samples)
            mtout = sum(s.output_tokens for s in model_samples)
            mcost = sum(
                _cost_for_sample(s, table.lookup(s.model_id))
                for s in model_samples
            )
            mlat = sorted(s.latency_ms for s in model_samples)
            by_model[model_id] = AppCostRollup(
                app=app,
                n_calls=mn,
                n_failed=mfailed,
                total_input_tokens=mtin,
                total_output_tokens=mtout,
                total_cost_usd=mcost,
                p50_latency_ms=_percentile(mlat, 50.0),
                p95_latency_ms=_percentile(mlat, 95.0),
            )

        by_app[app] = AppCostRollup(
            app=app,
            n_calls=n_calls,
            n_failed=n_failed,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            total_cost_usd=total_cost,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            by_model=by_model,
        )
        portfolio_total_cost += total_cost
        portfolio_total_calls += n_calls

    return PortfolioCostRollup(
        by_app=by_app,
        total_cost_usd=portfolio_total_cost,
        total_calls=portfolio_total_calls,
    )


__all__ = [
    "AppCostRollup",
    "CostSample",
    "PortfolioCostRollup",
    "aggregate_by_app",
]
