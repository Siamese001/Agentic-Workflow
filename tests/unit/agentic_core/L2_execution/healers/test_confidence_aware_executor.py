"""Wave 3 — ConfidenceAwareExecutor primary-path routing tests.

Plan ref: ``docs/archive/windsurf/legacy-tree/plans/qwen-confidence-routing-hardening-d4e7b1.md`` Wave 3.

Coverage matrix:

  | confidence | expected tier | expected sub-tier | expected model         |
  |-----------:|--------------|-------------------|------------------------|
  |     0.95   | HIGH         |  -                | local_deterministic    |
  |     0.85   | MEDIUM       |  -                | Qwen2.5-32B-AWQ        |
  |     0.65   | MEDIUM       |  -                | Qwen2.5-32B-AWQ        |
  |     0.45   | LOW          | FLASH             | gemini-flash           |
  |     0.30   | LOW          | FLASH             | gemini-flash           |
  |     0.15   | LOW          | PRO               | gemini-pro             |
  |    -0.10   | (clamped 0)  | LOW PRO           | gemini-pro             |
  |     1.50   | (clamped 1)  | HIGH              | local_deterministic    |

Plus integration scenarios:
  - MEDIUM with healthy vLLM → executor returns MEDIUM
  - MEDIUM with unhealthy vLLM → executor returns LOW (FLASH) with cascade reason
  - LOW direct dispatch → returns LOW with empty fallback_reason
  - is_adoption_enabled() respects USE_CONFIDENCE_AWARE_EXECUTOR
"""

from __future__ import annotations

import os
import unittest
from typing import Any
from unittest.mock import patch

from agentic_core.L2_execution.healers import vllm_health_probe
from agentic_core.L2_execution.healers.confidence_aware_executor import (
    ADOPTION_ENV,
    ConfidenceAwareExecutor,
    confidence_to_tier,
    execute,
    is_adoption_enabled,
    reset_for_tests,
)
from agentic_core.L2_execution.healers.confidence_scorer import HealTier


def _stub_qwen_response(success: bool = True, response: str = "ok") -> Any:
    class _R:
        def __init__(self) -> None:
            self.success = success
            self.response = response if success else None
            self.model_used = "Qwen/Qwen2.5-32B-Instruct-AWQ"
            self.error_message = None if success else "stub_fail"
            self.tokens_used = 7
            self.cached = False
            self.latency_ms = 12.3
            self.confidence = 0.82

    return _R()


class ConfidenceTierMappingTest(unittest.TestCase):
    """confidence → (tier, sub-tier) is pure — no I/O."""

    def test_high_confidence_maps_to_high(self) -> None:
        self.assertEqual(confidence_to_tier(0.95), (HealTier.HIGH, ""))
        self.assertEqual(confidence_to_tier(1.0), (HealTier.HIGH, ""))

    def test_medium_band_maps_to_medium(self) -> None:
        self.assertEqual(confidence_to_tier(0.85), (HealTier.MEDIUM, ""))
        self.assertEqual(confidence_to_tier(0.65), (HealTier.MEDIUM, ""))

    def test_below_medium_maps_to_low_flash(self) -> None:
        self.assertEqual(confidence_to_tier(0.45), (HealTier.LOW, "FLASH"))
        self.assertEqual(confidence_to_tier(0.30), (HealTier.LOW, "FLASH"))

    def test_very_low_maps_to_low_pro(self) -> None:
        self.assertEqual(confidence_to_tier(0.15), (HealTier.LOW, "PRO"))
        self.assertEqual(confidence_to_tier(0.0), (HealTier.LOW, "PRO"))


class ConfidenceAwareExecutorTest(unittest.TestCase):
    def setUp(self) -> None:
        vllm_health_probe.reset_cache_for_tests()
        reset_for_tests()
        os.environ.pop("DISABLE_QWEN_FALLBACK", None)
        os.environ.pop(ADOPTION_ENV, None)

    def tearDown(self) -> None:
        vllm_health_probe.reset_cache_for_tests()
        reset_for_tests()
        os.environ.pop("DISABLE_QWEN_FALLBACK", None)
        os.environ.pop(ADOPTION_ENV, None)

    # ----------------------------------------------------- HIGH tier
    def test_high_confidence_returns_deterministic_sentinel(self) -> None:
        executor = ConfidenceAwareExecutor()
        result = executor.execute(prompt="x", confidence=0.95, app_name="t")
        self.assertTrue(result.success)
        self.assertEqual(result.tier_attempted, "HIGH")
        self.assertEqual(result.tier_used, "HIGH")
        self.assertEqual(result.model_used, "local_deterministic")
        self.assertIsNone(result.response)  # HIGH never invokes an LLM
        self.assertEqual(result.fallback_reason, "")

    # ----------------------------------------------------- MEDIUM tier
    def test_medium_confidence_dispatches_to_qwen_when_healthy(self) -> None:
        with (
            patch(
                "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
                return_value=True,
            ),
            patch("asyncio.run", return_value=_stub_qwen_response(success=True)),
        ):
            result = ConfidenceAwareExecutor().execute(
                prompt="hello",
                confidence=0.80,
                app_name="t",
            )
        self.assertTrue(result.success, msg=str(result))
        self.assertEqual(result.tier_attempted, "MEDIUM")
        self.assertEqual(result.tier_used, "MEDIUM")
        self.assertIn("Qwen", result.model_used)
        self.assertEqual(result.fallback_reason, "")

    def test_medium_confidence_falls_through_when_qwen_down(self) -> None:
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            return_value=False,
        ):
            result = ConfidenceAwareExecutor().execute(
                prompt="hello",
                confidence=0.80,
                app_name="t",
            )
        self.assertEqual(result.tier_attempted, "MEDIUM")
        self.assertEqual(result.tier_used, "LOW")
        self.assertEqual(result.fallback_reason, "qwen_health_probe_failed")

    # ----------------------------------------------------- LOW tier (direct)
    def test_low_confidence_dispatches_directly_to_low(self) -> None:
        result = ConfidenceAwareExecutor().execute(
            prompt="hello",
            confidence=0.45,
            app_name="t",
        )
        # No Gemini gateway provisioned → dry_plan path; tier accounting is
        # the contract under test, not whether Gemini is reachable.
        self.assertEqual(result.tier_attempted, "LOW")
        self.assertEqual(result.tier_used, "LOW")
        self.assertEqual(result.fallback_reason, "")

    # ----------------------------------------------------- Clamping
    def test_negative_confidence_clamps_to_zero(self) -> None:
        result = ConfidenceAwareExecutor().execute(
            prompt="x",
            confidence=-0.5,
            app_name="t",
        )
        self.assertEqual(result.confidence, 0.0)
        # 0.0 → LOW PRO
        self.assertEqual(result.tier_attempted, "LOW")

    def test_above_one_confidence_clamps_to_one(self) -> None:
        result = ConfidenceAwareExecutor().execute(
            prompt="x",
            confidence=2.0,
            app_name="t",
        )
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.tier_attempted, "HIGH")

    # ----------------------------------------------------- Module-level execute()
    def test_module_level_execute_uses_singleton(self) -> None:
        result1 = execute(prompt="x", confidence=0.95)
        result2 = execute(prompt="x", confidence=0.95)
        self.assertTrue(result1.success)
        self.assertTrue(result2.success)
        # Both via the same singleton — call_count should reflect 2 calls
        from agentic_core.L2_execution.healers.confidence_aware_executor import (
            _shared_executor,
        )

        self.assertEqual(_shared_executor().call_count, 2)

    # ----------------------------------------------------- Adoption flag
    def test_adoption_disabled_by_default(self) -> None:
        self.assertFalse(is_adoption_enabled())

    def test_adoption_enabled_via_env(self) -> None:
        os.environ[ADOPTION_ENV] = "1"
        try:
            self.assertTrue(is_adoption_enabled())
        finally:
            del os.environ[ADOPTION_ENV]

    def test_adoption_truthy_aliases(self) -> None:
        for value in ("true", "yes", "on", "TRUE", "Yes"):
            os.environ[ADOPTION_ENV] = value
            try:
                self.assertTrue(is_adoption_enabled(), msg=f"value={value!r}")
            finally:
                del os.environ[ADOPTION_ENV]


if __name__ == "__main__":
    unittest.main()
