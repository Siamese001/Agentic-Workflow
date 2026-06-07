"""Tests for tools.cost_telemetry — W4.3.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (W4.3)
"""
from __future__ import annotations

import unittest

from tools.cost_telemetry import (
    CostSample,
    PortfolioCostRollup,
    PricingTable,
    aggregate_by_app,
    default_pricing_table,
)
from tools.cost_telemetry.pricing import ModelPricing


class TestPricingTable(unittest.TestCase):
    def test_default_table_has_known_models(self) -> None:
        table = default_pricing_table()
        self.assertIn("claude-sonnet-4.5", table.by_model)
        self.assertIn("qwen-32b", table.by_model)

    def test_unknown_model_falls_back(self) -> None:
        table = default_pricing_table()
        unknown = table.lookup("imaginary-future-model-9000")
        # Fallback is non-zero — surfaces missing config as visible cost.
        self.assertGreater(unknown.input_usd_per_token, 0.0)
        self.assertGreater(unknown.output_usd_per_token, 0.0)

    def test_known_model_returns_specific_pricing(self) -> None:
        table = default_pricing_table()
        sonnet = table.lookup("claude-sonnet-4.5")
        # Output rate must be at least input rate for hosted Anthropic.
        self.assertGreaterEqual(
            sonnet.output_usd_per_token, sonnet.input_usd_per_token
        )


class TestAggregator(unittest.TestCase):
    def test_empty_input_returns_empty_rollup(self) -> None:
        result = aggregate_by_app([])
        self.assertIsInstance(result, PortfolioCostRollup)
        self.assertEqual(result.total_calls, 0)
        self.assertEqual(result.total_cost_usd, 0.0)
        self.assertEqual(result.by_app, {})

    def test_single_sample_aggregates_correctly(self) -> None:
        sample = CostSample(
            app="apps_eval",
            model_id="qwen-32b",
            input_tokens=1000,
            output_tokens=500,
            latency_ms=100.0,
        )
        result = aggregate_by_app([sample])
        self.assertEqual(result.total_calls, 1)
        self.assertIn("apps_eval", result.by_app)
        rollup = result.by_app["apps_eval"]
        self.assertEqual(rollup.n_calls, 1)
        self.assertEqual(rollup.n_failed, 0)
        self.assertEqual(rollup.total_input_tokens, 1000)
        self.assertEqual(rollup.total_output_tokens, 500)
        # qwen-32b: 1000 * 0.5e-6 + 500 * 1.0e-6 = 0.0005 + 0.0005 = 0.001
        self.assertAlmostEqual(rollup.total_cost_usd, 0.001, places=6)
        self.assertAlmostEqual(rollup.cost_per_call_usd, 0.001, places=6)
        self.assertEqual(rollup.success_rate, 1.0)

    def test_multi_app_separation(self) -> None:
        samples = [
            CostSample(app="apps_eval", model_id="qwen-32b",
                       input_tokens=100, output_tokens=50, latency_ms=10.0),
            CostSample(app="apps_lic", model_id="qwen-32b",
                       input_tokens=200, output_tokens=100, latency_ms=20.0),
        ]
        result = aggregate_by_app(samples)
        self.assertEqual(result.total_calls, 2)
        self.assertEqual(result.by_app["apps_eval"].n_calls, 1)
        self.assertEqual(result.by_app["apps_lic"].n_calls, 1)
        # apps_lic processed 2x the tokens → 2x the cost.
        self.assertAlmostEqual(
            result.by_app["apps_lic"].total_cost_usd,
            2.0 * result.by_app["apps_eval"].total_cost_usd,
            places=8,
        )

    def test_failure_rate_tracked(self) -> None:
        samples = [
            CostSample(app="apps_eval", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=1.0,
                       success=True),
            CostSample(app="apps_eval", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=1.0,
                       success=False),
            CostSample(app="apps_eval", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=1.0,
                       success=True),
        ]
        result = aggregate_by_app(samples)
        rollup = result.by_app["apps_eval"]
        self.assertEqual(rollup.n_failed, 1)
        self.assertAlmostEqual(rollup.success_rate, 2 / 3, places=4)

    def test_per_model_breakdown(self) -> None:
        samples = [
            CostSample(app="apps_eval", model_id="qwen-32b",
                       input_tokens=100, output_tokens=50, latency_ms=10.0),
            CostSample(app="apps_eval", model_id="claude-sonnet-4.5",
                       input_tokens=100, output_tokens=50, latency_ms=10.0),
        ]
        result = aggregate_by_app(samples)
        rollup = result.by_app["apps_eval"]
        self.assertEqual(rollup.n_calls, 2)
        self.assertEqual(len(rollup.by_model), 2)
        self.assertIn("qwen-32b", rollup.by_model)
        self.assertIn("claude-sonnet-4.5", rollup.by_model)
        # claude-sonnet > qwen-32b on per-token cost — sanity check.
        self.assertGreater(
            rollup.by_model["claude-sonnet-4.5"].total_cost_usd,
            rollup.by_model["qwen-32b"].total_cost_usd,
        )

    def test_p95_latency_with_skewed_distribution(self) -> None:
        # 19 fast + 1 slow = p95 should reflect the slow one.
        samples = [
            CostSample(app="apps_exec", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=10.0)
            for _ in range(19)
        ]
        samples.append(
            CostSample(app="apps_exec", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=5000.0)
        )
        result = aggregate_by_app(samples)
        rollup = result.by_app["apps_exec"]
        # p50 should still be 10ms (well below the outlier), p95 should be elevated.
        self.assertLess(rollup.p50_latency_ms, 100.0)
        self.assertGreater(rollup.p95_latency_ms, 100.0)

    def test_summary_includes_all_apps(self) -> None:
        samples = [
            CostSample(app="apps_eval", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=1.0),
            CostSample(app="apps_lic", model_id="qwen-32b",
                       input_tokens=10, output_tokens=5, latency_ms=1.0),
        ]
        text = aggregate_by_app(samples).summary()
        self.assertIn("apps_eval", text)
        self.assertIn("apps_lic", text)
        self.assertIn("Portfolio cost rollup", text)

    def test_custom_pricing_table_used(self) -> None:
        # Custom pricing 100x default — verify aggregator honors override.
        custom = PricingTable(
            by_model={
                "qwen-32b": ModelPricing(
                    input_usd_per_token=0.000_050,
                    output_usd_per_token=0.000_100,
                )
            },
        )
        sample = CostSample(
            app="apps_eval", model_id="qwen-32b",
            input_tokens=1000, output_tokens=500, latency_ms=10.0,
        )
        result_default = aggregate_by_app([sample])
        result_custom = aggregate_by_app([sample], pricing_table=custom)
        self.assertGreater(
            result_custom.total_cost_usd,
            result_default.total_cost_usd * 10,
            "custom pricing should yield much higher cost",
        )


if __name__ == "__main__":
    unittest.main()
