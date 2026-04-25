"""Wave 1 tests — vLLM health probe + Qwen→Flash cascade fallback.

Plan ref: ``.windsurf/plans/qwen-confidence-routing-hardening-d4e7b1.md`` Wave 1.

Coverage matrix:

  | health | qwen_call   | env DISABLE_QWEN_FALLBACK | expected tier_used | reason         |
  |--------|-------------|---------------------------|--------------------|----------------|
  |  up    | success     |   off                     | MEDIUM             | ""             |
  |  up    | success     |   on                      | MEDIUM             | ""             |
  |  up    | exception   |   off                     | LOW                | qwen_dispatch_*|
  |  up    | exception   |   on                      | MEDIUM (fail)      | ""             |
  |  up    | success=False |  off                    | LOW                | qwen_unsuccessful*|
  |  down  | -           |   off                     | LOW                | qwen_health_*  |
  |  down  | -           |   on                      | MEDIUM (fail probe doesn't run, dispatch tries) | ?  |

Probe-cache TTL is reset at every test entry to avoid bleed-through.
"""

from __future__ import annotations

import os
import unittest
from typing import Any
from unittest.mock import patch

from agentic_core.L2_execution.healers import vllm_health_probe
from agentic_core.L2_execution.healers.confidence_scorer import ConfidenceScore, HealTier
from agentic_core.L2_execution.healers.failure_signal import FailureSignal
from agentic_core.L2_execution.healers.healing_router import (
    HealingRouter,
    RoutingDecision,
)


def _decision(tier: HealTier = HealTier.MEDIUM) -> RoutingDecision:
    return RoutingDecision(
        tier=tier,
        target_model="Qwen/Qwen2.5-32B-Instruct-AWQ",
        timeout_seconds=30,
        max_tokens=256,
        requires_sandbox=True,
        reasoning="test",
        gate_applied="NO_OVERRIDE",
        gemini_subtier="",
        cost_demoted=False,
    )


def _stub_response(success: bool = True, response: str = "ok", error: str | None = None) -> Any:
    class _R:
        def __init__(self) -> None:
            self.success = success
            self.response = response if success else None
            self.model_used = "Qwen/Qwen2.5-32B-Instruct-AWQ"
            self.error_message = error
            self.tokens_used = 7
            self.cached = False
            self.latency_ms = 12.3
            self.confidence = 0.82

    return _R()


class _HealthOK:
    """Probe replacement that reports healthy + Qwen model."""

    @staticmethod
    def is_qwen_available(*_a: Any, **_k: Any) -> bool:
        return True


class _HealthDown:
    @staticmethod
    def is_qwen_available(*_a: Any, **_k: Any) -> bool:
        return False


class QwenCascadeFallbackTest(unittest.TestCase):
    def setUp(self) -> None:
        vllm_health_probe.reset_cache_for_tests()
        # Always start clean
        os.environ.pop("DISABLE_QWEN_FALLBACK", None)
        self.router = HealingRouter()
        self.signal = FailureSignal(
            check_id="chk-1",
            retry_count=0,
            error_code="E_GENERIC",
            error_message="x",
            lineage_hash="",
            context_snapshot={},
            source_layer="L2_execution",
            operation="test",
            timestamp=0.0,
        )

    def tearDown(self) -> None:
        os.environ.pop("DISABLE_QWEN_FALLBACK", None)
        vllm_health_probe.reset_cache_for_tests()

    # ------------------------------------------------------------- A. Healthy
    def test_healthy_qwen_success_no_fallback(self) -> None:
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthOK.is_qwen_available,
        ), patch("asyncio.run", return_value=_stub_response(success=True)):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        self.assertTrue(result["success"], msg=str(result))
        self.assertEqual(result["executor"], "qwen_vllm")
        self.assertEqual(result["tier_attempted"], "MEDIUM")
        self.assertEqual(result["tier_used"], "MEDIUM")
        self.assertEqual(result["fallback_reason"], "")

    def test_healthy_qwen_success_with_fallback_disabled(self) -> None:
        os.environ["DISABLE_QWEN_FALLBACK"] = "1"
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthOK.is_qwen_available,
        ), patch("asyncio.run", return_value=_stub_response(success=True)):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        self.assertTrue(result["success"])
        self.assertEqual(result["tier_used"], "MEDIUM")

    # ----------------------------------------------------------- B. Live fail
    def test_qwen_exception_falls_through_to_flash(self) -> None:
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthOK.is_qwen_available,
        ), patch("asyncio.run", side_effect=RuntimeError("boom")):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        self.assertEqual(result["tier_attempted"], "MEDIUM")
        self.assertEqual(result["tier_used"], "LOW")
        self.assertTrue(result["fallback_reason"].startswith("qwen_dispatch_error:"))
        # Gemini gateway is not provisioned in this test → dry_plan returned
        self.assertIn("dry_plan", result)
        self.assertEqual(result.get("gemini_subtier"), "FLASH")

    def test_qwen_exception_with_fallback_disabled_returns_failure(self) -> None:
        os.environ["DISABLE_QWEN_FALLBACK"] = "1"
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthOK.is_qwen_available,
        ), patch("asyncio.run", side_effect=RuntimeError("boom")):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        self.assertFalse(result["success"])
        self.assertEqual(result["executor"], "qwen_vllm")
        self.assertEqual(result["tier_used"], "MEDIUM")  # no demotion
        self.assertEqual(result["fallback_reason"], "")
        self.assertIn("qwen_dispatch_error:", result["error"])

    def test_qwen_unsuccessful_envelope_falls_through(self) -> None:
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthOK.is_qwen_available,
        ), patch(
            "asyncio.run",
            return_value=_stub_response(success=False, error="rate_limit"),
        ):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        self.assertEqual(result["tier_used"], "LOW")
        self.assertTrue(result["fallback_reason"].startswith("qwen_unsuccessful:"))

    # ----------------------------------------------------------- C. Health-down preflight
    def test_health_down_preflight_demotes_without_dispatch(self) -> None:
        async_run_called = {"n": 0}

        def _spy(*_a: Any, **_kw: Any) -> Any:
            async_run_called["n"] += 1
            return _stub_response(success=True)

        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthDown.is_qwen_available,
        ), patch("asyncio.run", side_effect=_spy):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        self.assertEqual(result["tier_used"], "LOW")
        self.assertEqual(result["fallback_reason"], "qwen_health_probe_failed")
        self.assertEqual(async_run_called["n"], 0, "preflight must short-circuit live dispatch")

    def test_health_down_with_fallback_disabled_attempts_dispatch(self) -> None:
        os.environ["DISABLE_QWEN_FALLBACK"] = "1"
        with patch(
            "agentic_core.L2_execution.healers.healing_router.is_qwen_available",
            new=_HealthDown.is_qwen_available,
        ), patch("asyncio.run", return_value=_stub_response(success=True)):
            result = self.router._dispatch_qwen("p", "test_app", _decision())
        # Preflight skipped → live dispatch ran → success
        self.assertTrue(result["success"])
        self.assertEqual(result["tier_used"], "MEDIUM")

    # ----------------------------------------------------------- D. Public route() unchanged
    def test_route_returns_medium_for_medium_score(self) -> None:
        score = ConfidenceScore(
            score=0.75,
            tier=HealTier.MEDIUM,
            confidence_in_score=0.9,
            reasoning="medium-confidence",
        )
        decision = self.router.route(score, self.signal)
        self.assertEqual(decision.tier, HealTier.MEDIUM)
        self.assertIn("Qwen", decision.target_model)


class VLLMHealthProbeUnitTest(unittest.TestCase):
    """Unit tests for the probe itself (no router involvement)."""

    def setUp(self) -> None:
        vllm_health_probe.reset_cache_for_tests()

    def test_probe_caches_results_within_ttl(self) -> None:
        from agentic_core.L2_execution.healers.vllm_health_probe import VLLMHealth, probe

        called = {"n": 0}

        def _stub(_url: str, _timeout: float) -> VLLMHealth:
            called["n"] += 1
            import time

            return VLLMHealth(
                status="healthy",
                model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
                latency_ms=10.0,
                checked_at=time.time(),
                error=None,
            )

        with patch("agentic_core.L2_execution.healers.vllm_health_probe._do_probe", side_effect=_stub):
            r1 = probe(base_url="http://localhost:8000/v1", ttl_seconds=60)
            r2 = probe(base_url="http://localhost:8000/v1", ttl_seconds=60)
        self.assertTrue(r1.is_healthy)
        self.assertTrue(r2.is_healthy)
        self.assertEqual(called["n"], 1, "second call should be served from cache")

    def test_probe_force_refresh_bypasses_cache(self) -> None:
        from agentic_core.L2_execution.healers.vllm_health_probe import VLLMHealth, probe

        called = {"n": 0}

        def _stub(_url: str, _timeout: float) -> VLLMHealth:
            called["n"] += 1
            import time

            return VLLMHealth(
                status="healthy",
                model_id="Qwen",
                latency_ms=1.0,
                checked_at=time.time(),
            )

        with patch("agentic_core.L2_execution.healers.vllm_health_probe._do_probe", side_effect=_stub):
            probe(base_url="http://localhost:8000/v1")
            probe(base_url="http://localhost:8000/v1", force_refresh=True)
        self.assertEqual(called["n"], 2)

    def test_is_qwen_available_false_on_unhealthy(self) -> None:
        from agentic_core.L2_execution.healers.vllm_health_probe import (
            VLLMHealth,
            is_qwen_available,
        )

        def _stub(_url: str, _timeout: float) -> VLLMHealth:
            import time

            return VLLMHealth(
                status="unhealthy",
                model_id="",
                latency_ms=0.0,
                checked_at=time.time(),
                error="url_error:Connection refused",
            )

        with patch("agentic_core.L2_execution.healers.vllm_health_probe._do_probe", side_effect=_stub):
            self.assertFalse(is_qwen_available(base_url="http://localhost:8000/v1"))


if __name__ == "__main__":
    unittest.main()
