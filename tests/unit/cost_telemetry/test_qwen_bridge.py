"""Tests for the Qwen telemetry → CostSample bridge."""
from __future__ import annotations

import time
import unittest

from agentic_core.L3_orchestration.inference.qwen_vllm.config.qwen_telemetry import (
    QwenInferenceTelemetry,
    QwenSessionMetrics,
)
from tools.cost_telemetry import CostSample
from tools.cost_telemetry.qwen_bridge import (
    aggregate_telemetry,
    samples_from_session,
    samples_from_telemetry,
)


def _build_session(
    app: str = "apps_eval",
    n: int = 5,
    succ: int = 5,
    tokens: int = 1000,
    latency_total: float = 500.0,
) -> QwenSessionMetrics:
    return QwenSessionMetrics(
        session_id=f"{app}_test",
        app_name=app,
        start_time=time.time(),
        end_time=time.time() + 1.0,
        total_requests=n,
        successful_requests=succ,
        failed_requests=n - succ,
        total_latency_ms=latency_total,
        tokens_used=tokens,
    )


class TestSamplesFromSession(unittest.TestCase):
    def test_zero_request_session_yields_empty(self) -> None:
        s = _build_session(n=0, succ=0, tokens=0, latency_total=0.0)
        out = samples_from_session(s, model_id="qwen-32b")
        self.assertEqual(out, [])

    def test_n_samples_match_total_requests(self) -> None:
        s = _build_session(n=5)
        samples = samples_from_session(s, model_id="qwen-32b")
        self.assertEqual(len(samples), 5)

    def test_token_split_respects_ratio(self) -> None:
        s = _build_session(n=2, tokens=1000)
        samples = samples_from_session(s, model_id="qwen-32b", input_token_ratio=0.7)
        # 1000 tokens / 2 requests = 500/request → 350 input + 150 output
        for sample in samples:
            self.assertEqual(sample.input_tokens, 350)
            self.assertEqual(sample.output_tokens, 150)

    def test_failure_count_preserved(self) -> None:
        s = _build_session(n=4, succ=3)
        samples = samples_from_session(s, model_id="qwen-32b")
        # 1 failure, 3 successes
        self.assertEqual(sum(1 for x in samples if not x.success), 1)
        self.assertEqual(sum(1 for x in samples if x.success), 3)

    def test_invalid_ratio_rejected(self) -> None:
        s = _build_session(n=1)
        with self.assertRaises(ValueError):
            samples_from_session(s, model_id="qwen-32b", input_token_ratio=1.1)
        with self.assertRaises(ValueError):
            samples_from_session(s, model_id="qwen-32b", input_token_ratio=-0.1)

    def test_app_name_threaded_through(self) -> None:
        s = _build_session(app="apps_research", n=3)
        samples = samples_from_session(s, model_id="qwen-32b")
        for sample in samples:
            self.assertEqual(sample.app, "apps_research")

    def test_model_id_threaded_through(self) -> None:
        s = _build_session(n=1)
        samples = samples_from_session(s, model_id="claude-sonnet-4.5")
        self.assertEqual(samples[0].model_id, "claude-sonnet-4.5")


class TestSamplesFromTelemetry(unittest.TestCase):
    def test_empty_telemetry_yields_empty(self) -> None:
        t = QwenInferenceTelemetry()
        self.assertEqual(samples_from_telemetry(t), [])

    def test_full_session_lifecycle_to_samples(self) -> None:
        t = QwenInferenceTelemetry()
        sid = t.start_session("apps_eval")
        t.record_request_start(sid, "apps_eval", "qwen-7b")
        t.record_request_success(
            sid, "apps_eval", "qwen-7b",
            latency_ms=120.0, confidence=0.9, tokens_used=500,
        )
        t.record_request_start(sid, "apps_eval", "qwen-7b")
        t.record_request_success(
            sid, "apps_eval", "qwen-7b",
            latency_ms=80.0, confidence=0.85, tokens_used=300,
        )
        t.end_session(sid)

        samples = samples_from_telemetry(t)
        self.assertEqual(len(samples), 2)
        self.assertTrue(all(s.app == "apps_eval" for s in samples))
        self.assertTrue(all(s.model_id == "qwen-7b" for s in samples))
        # Total tokens recorded = 500 + 300 = 800 across 2 requests = 400/req.
        # With 0.70 ratio: 280 input + 120 output per request.
        for sample in samples:
            self.assertEqual(sample.input_tokens + sample.output_tokens, 400)

    def test_telemetry_to_aggregator_end_to_end(self) -> None:
        t = QwenInferenceTelemetry()
        sid_eval = t.start_session("apps_eval")
        for _ in range(3):
            t.record_request_start(sid_eval, "apps_eval", "qwen-32b")
            t.record_request_success(
                sid_eval, "apps_eval", "qwen-32b",
                latency_ms=100.0, confidence=0.9, tokens_used=400,
            )
        sid_lic = t.start_session("apps_lic")
        for _ in range(2):
            t.record_request_start(sid_lic, "apps_lic", "qwen-32b")
            t.record_request_success(
                sid_lic, "apps_lic", "qwen-32b",
                latency_ms=200.0, confidence=0.8, tokens_used=600,
            )

        rollup = aggregate_telemetry(t)
        self.assertIn("apps_eval", rollup.by_app)
        self.assertIn("apps_lic", rollup.by_app)
        self.assertEqual(rollup.by_app["apps_eval"].n_calls, 3)
        self.assertEqual(rollup.by_app["apps_lic"].n_calls, 2)
        # Total cost is positive and apps_lic's per-call cost > apps_eval's
        # (because apps_lic processes 2x tokens per call).
        self.assertGreater(rollup.total_cost_usd, 0.0)
        self.assertGreater(
            rollup.by_app["apps_lic"].cost_per_call_usd,
            rollup.by_app["apps_eval"].cost_per_call_usd,
        )


if __name__ == "__main__":
    unittest.main()
