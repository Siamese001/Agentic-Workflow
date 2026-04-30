"""Tests for apps_eval.integrations.promotion_loop — W4.1.

Verifies the apps_eval → L6 promotion-gate adapter:
  - Healthy candidate beating baseline → promote=True
  - Identical samples → promote=False (CIs overlap)
  - Insufficient sample size → promote=False with explicit reason
  - Pre-condition errors raise (no silent acceptance)
  - App mismatch raises (cannot promote across apps)
  - Round-trip provenance preserved on the result

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.1)
"""
from __future__ import annotations

import unittest

from apps_eval.types import EvalRunSummary

from apps_eval.integrations.promotion_loop import (
    CombinedPromotionResult,
    CounterfactualUpliftResult,
    PromotionAdapterResult,
    evaluate_combined_promotion,
    evaluate_counterfactual_uplift,
    evaluate_for_promotion,
)


def _summary(
    *,
    trace_id: str,
    app: str = "apps_eval",
    version: str = "v1",
    n: int,
    passed: int,
    status: str = "complete",
    error: str = "",
) -> EvalRunSummary:
    return EvalRunSummary(
        trace_id=trace_id,
        app=app,
        version=version,
        status=status,
        scenarios_run=n,
        scenarios_passed=passed,
        error=error,
    )


class TestPromotionLoopAdapter(unittest.TestCase):
    def test_strong_candidate_promotes(self) -> None:
        # Candidate 95/100 vs baseline 60/100 — wide separation, big sample.
        cand = _summary(trace_id="c1", n=100, passed=95)
        base = _summary(trace_id="b1", n=100, passed=60)
        result = evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)
        self.assertIsInstance(result, PromotionAdapterResult)
        self.assertTrue(result.promote, f"expected promote=True, got reason={result.reason}")
        self.assertEqual(result.candidate_trace_id, "c1")
        self.assertEqual(result.baseline_trace_id, "b1")

    def test_identical_samples_do_not_promote(self) -> None:
        cand = _summary(trace_id="c1", n=100, passed=80)
        base = _summary(trace_id="b1", n=100, passed=80)
        result = evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)
        self.assertFalse(result.promote)
        self.assertIn("overlap", result.reason.lower())

    def test_insufficient_sample_blocks_promotion(self) -> None:
        cand = _summary(trace_id="c1", n=10, passed=10)
        base = _summary(trace_id="b1", n=10, passed=2)
        result = evaluate_for_promotion(
            candidate_summary=cand, baseline_summary=base, min_n_each_arm=30
        )
        self.assertFalse(result.promote)
        self.assertIn("insufficient sample", result.reason.lower())

    def test_app_mismatch_raises(self) -> None:
        cand = _summary(trace_id="c1", app="apps_eval", n=50, passed=40)
        base = _summary(trace_id="b1", app="apps_research", n=50, passed=30)
        with self.assertRaises(ValueError) as ctx:
            evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)
        self.assertIn("app", str(ctx.exception).lower())

    def test_error_state_rejected(self) -> None:
        cand = _summary(trace_id="c1", n=50, passed=40, status="error", error="judge down")
        base = _summary(trace_id="b1", n=50, passed=30)
        with self.assertRaises(ValueError):
            evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)

    def test_zero_scenarios_run_rejected(self) -> None:
        cand = _summary(trace_id="c1", n=0, passed=0)
        base = _summary(trace_id="b1", n=50, passed=30)
        with self.assertRaises(ValueError):
            evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)

    def test_passed_exceeds_run_rejected(self) -> None:
        cand = _summary(trace_id="c1", n=10, passed=20)
        base = _summary(trace_id="b1", n=50, passed=30)
        with self.assertRaises(ValueError):
            evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)

    def test_provenance_preserved_on_result(self) -> None:
        cand = _summary(trace_id="trace-cand-001", version="v2.1", n=100, passed=90)
        base = _summary(trace_id="trace-base-001", version="v2.0", n=100, passed=70)
        result = evaluate_for_promotion(candidate_summary=cand, baseline_summary=base)
        self.assertEqual(result.candidate_trace_id, "trace-cand-001")
        self.assertEqual(result.baseline_trace_id, "trace-base-001")
        self.assertEqual(result.candidate_version, "v2.1")
        self.assertEqual(result.baseline_version, "v2.0")
        self.assertEqual(result.candidate_app, "apps_eval")


class TestCounterfactualUplift(unittest.TestCase):
    def test_shadow_outperforms_prod(self) -> None:
        shadow = _summary(trace_id="s1", n=100, passed=85)
        prod = _summary(trace_id="p1", n=100, passed=70)
        result = evaluate_counterfactual_uplift(
            shadow_summary=shadow, prod_summary=prod
        )
        self.assertIsInstance(result, CounterfactualUpliftResult)
        self.assertAlmostEqual(result.uplift, 0.15, places=4)
        self.assertTrue(result.shadow_outperforms)
        self.assertEqual(result.n_paired, 100)
        self.assertEqual(result.candidate_app, "apps_eval")

    def test_prod_outperforms_shadow(self) -> None:
        shadow = _summary(trace_id="s1", n=50, passed=30)
        prod = _summary(trace_id="p1", n=50, passed=45)
        result = evaluate_counterfactual_uplift(
            shadow_summary=shadow, prod_summary=prod
        )
        self.assertLess(result.uplift, 0.0)
        self.assertFalse(result.shadow_outperforms)

    def test_identical_outcomes_zero_uplift(self) -> None:
        shadow = _summary(trace_id="s1", n=80, passed=64)
        prod = _summary(trace_id="p1", n=80, passed=64)
        result = evaluate_counterfactual_uplift(
            shadow_summary=shadow, prod_summary=prod
        )
        self.assertEqual(result.uplift, 0.0)
        self.assertFalse(result.shadow_outperforms)

    def test_unequal_scenarios_run_rejected(self) -> None:
        shadow = _summary(trace_id="s1", n=50, passed=40)
        prod = _summary(trace_id="p1", n=100, passed=80)
        with self.assertRaises(ValueError) as ctx:
            evaluate_counterfactual_uplift(shadow_summary=shadow, prod_summary=prod)
        self.assertIn("scenarios_run", str(ctx.exception).lower())

    def test_app_mismatch_rejected(self) -> None:
        shadow = _summary(trace_id="s1", app="apps_eval", n=50, passed=40)
        prod = _summary(trace_id="p1", app="apps_research", n=50, passed=30)
        with self.assertRaises(ValueError):
            evaluate_counterfactual_uplift(shadow_summary=shadow, prod_summary=prod)

    def test_error_state_rejected(self) -> None:
        shadow = _summary(trace_id="s1", n=50, passed=40, status="error", error="x")
        prod = _summary(trace_id="p1", n=50, passed=30)
        with self.assertRaises(ValueError):
            evaluate_counterfactual_uplift(shadow_summary=shadow, prod_summary=prod)


class TestCombinedPromotion(unittest.TestCase):
    def test_wilson_promotes_uses_wilson_signal(self) -> None:
        # 90% candidate vs 70% baseline at n=100 → Wilson promotes.
        cand = _summary(trace_id="cand", n=100, passed=90)
        base = _summary(trace_id="base", n=100, passed=70)
        result = evaluate_combined_promotion(
            candidate_summary=cand, baseline_summary=base,
        )
        self.assertTrue(result.promote)
        self.assertEqual(result.primary_signal, "wilson")
        self.assertIsNone(result.counterfactual_result)

    def test_wilson_inconclusive_counterfactual_rescues(self) -> None:
        # Small n where Wilson cannot separate, but counterfactual is positive.
        cand = _summary(trace_id="cand", n=20, passed=14)  # 70%
        base = _summary(trace_id="base", n=20, passed=12)  # 60%
        # Wilson with n=20 won't have non-overlapping CIs.
        shadow = _summary(trace_id="sh", n=100, passed=80)
        prod = _summary(trace_id="pd", n=100, passed=70)
        result = evaluate_combined_promotion(
            candidate_summary=cand, baseline_summary=base,
            shadow_summary=shadow, prod_summary=prod,
        )
        # Wilson alone wouldn't promote; counterfactual should rescue.
        self.assertFalse(result.wilson_result.verdict.promote)
        self.assertTrue(result.promote)
        self.assertEqual(result.primary_signal, "counterfactual")
        self.assertIsNotNone(result.counterfactual_result)
        self.assertGreater(result.counterfactual_result.uplift, 0.0)

    def test_neither_signal_rejects(self) -> None:
        cand = _summary(trace_id="cand", n=50, passed=30)  # worse than baseline
        base = _summary(trace_id="base", n=50, passed=40)
        shadow = _summary(trace_id="sh", n=50, passed=20)
        prod = _summary(trace_id="pd", n=50, passed=40)
        result = evaluate_combined_promotion(
            candidate_summary=cand, baseline_summary=base,
            shadow_summary=shadow, prod_summary=prod,
        )
        self.assertFalse(result.promote)
        self.assertEqual(result.primary_signal, "neither")

    def test_no_counterfactual_pair_skips_rescue(self) -> None:
        # Wilson rejects; no shadow/prod supplied → primary='neither'.
        cand = _summary(trace_id="cand", n=20, passed=14)
        base = _summary(trace_id="base", n=20, passed=12)
        result = evaluate_combined_promotion(
            candidate_summary=cand, baseline_summary=base,
        )
        self.assertFalse(result.promote)
        self.assertEqual(result.primary_signal, "neither")
        self.assertIsNone(result.counterfactual_result)
        self.assertIn("no counterfactual signal supplied", result.reason)

    def test_partial_counterfactual_pair_skipped(self) -> None:
        # Only shadow_summary provided → counterfactual not consulted.
        cand = _summary(trace_id="cand", n=20, passed=14)
        base = _summary(trace_id="base", n=20, passed=12)
        shadow = _summary(trace_id="sh", n=50, passed=40)
        result = evaluate_combined_promotion(
            candidate_summary=cand, baseline_summary=base,
            shadow_summary=shadow,
        )
        self.assertFalse(result.promote)
        self.assertEqual(result.primary_signal, "neither")
        self.assertIsNone(result.counterfactual_result)


if __name__ == "__main__":
    unittest.main()
