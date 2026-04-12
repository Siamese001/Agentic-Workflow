"""
Unit tests for EvalOrchestrator Qwen hardening.

Tests:
- No silent disable on explicit Qwen invocation when init failed
- Explicit RuntimeError on evaluate_with_qwen when init failed
- Default run() behavior (non-Qwen pipeline) is unchanged
- qwen_enabled=False returns opt-in sentinel, not RuntimeError
- Gateway init failure is captured in _qwen_init_error, not swallowed
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_orchestrator(*, qwen_enabled: bool = True, gateway_raises: Exception | None = None):
    """Build an EvalOrchestrator with all external deps mocked."""
    broken_or_mock = Mock(side_effect=gateway_raises) if gateway_raises else Mock()

    with (
        patch("apps_eval.reasoning.EvalOrchestrator._QWEN_AVAILABLE", True),
        patch("apps_eval.reasoning.EvalOrchestrator.AppsQwenGateway", broken_or_mock),
        patch("apps_eval.reasoning.EvalOrchestrator.AppsQwenRequest", Mock()),
        patch("apps_eval.reasoning.EvalOrchestrator.apps_qwen_telemetry", None),
        patch("apps_eval.reasoning.EvalOrchestrator.ScenarioRunner", Mock(return_value=Mock())),
        patch("apps_eval.reasoning.EvalOrchestrator.ScorecardEngine", Mock(return_value=Mock())),
        patch("apps_eval.reasoning.EvalOrchestrator.RegressionDetector", Mock(return_value=Mock())),
        patch("apps_eval.reasoning.EvalOrchestrator.EvalGateValidator", Mock(return_value=Mock())),
    ):
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator  # noqa: PLC0415

        orch = EvalOrchestrator(qwen_enabled=qwen_enabled, dry_run=True)
    return orch


def _make_orchestrator_qwen_unavailable():
    """Build an orchestrator with Qwen package unavailable."""
    with (
        patch("apps_eval.reasoning.EvalOrchestrator._QWEN_AVAILABLE", False),
        patch("apps_eval.reasoning.EvalOrchestrator.ScenarioRunner", Mock(return_value=Mock())),
        patch("apps_eval.reasoning.EvalOrchestrator.ScorecardEngine", Mock(return_value=Mock())),
        patch("apps_eval.reasoning.EvalOrchestrator.RegressionDetector", Mock(return_value=Mock())),
        patch("apps_eval.reasoning.EvalOrchestrator.EvalGateValidator", Mock(return_value=Mock())),
    ):
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator  # noqa: PLC0415

        orch = EvalOrchestrator(qwen_enabled=True, dry_run=True)
    return orch


# ---------------------------------------------------------------------------
# Init error capture
# ---------------------------------------------------------------------------


class TestEvalOrchestratorInitHardening:
    def test_gateway_init_failure_captured_in_qwen_init_error(self):
        """Gateway init failure must land in _qwen_init_error, not be swallowed."""
        orch = _make_orchestrator(gateway_raises=RuntimeError("vLLM not reachable"))
        assert orch._qwen_init_error is not None
        assert "vLLM not reachable" in orch._qwen_init_error

    def test_gateway_init_failure_does_not_mutate_qwen_enabled(self):
        """qwen_enabled must NOT be flipped to False on init failure."""
        orch = _make_orchestrator(gateway_raises=RuntimeError("port closed"))
        assert orch.qwen_enabled is True

    def test_gateway_init_failure_leaves_gateway_none(self):
        orch = _make_orchestrator(gateway_raises=RuntimeError("port closed"))
        assert orch._qwen_gateway is None

    def test_qwen_unavailable_sets_init_error(self):
        """Package import failure must set _qwen_init_error."""
        orch = _make_orchestrator_qwen_unavailable()
        assert orch._qwen_init_error is not None

    def test_successful_init_leaves_init_error_none(self):
        orch = _make_orchestrator()
        assert orch._qwen_init_error is None

    def test_qwen_disabled_init_is_clean(self):
        """qwen_enabled=False: no error, no gateway, no _qwen_init_error."""
        orch = _make_orchestrator(qwen_enabled=False)
        assert orch._qwen_gateway is None
        assert orch._qwen_init_error is None
        assert orch.qwen_enabled is False


# ---------------------------------------------------------------------------
# evaluate_with_qwen — explicit fail-loud semantics
# ---------------------------------------------------------------------------


class TestEvaluateWithQwenFailLoud:
    def test_raises_runtime_error_when_init_failed(self):
        """Explicit invocation after init failure must raise RuntimeError."""
        orch = _make_orchestrator(gateway_raises=RuntimeError("vLLM not reachable"))
        with pytest.raises(RuntimeError, match="Qwen init failed"):
            asyncio.run(orch.evaluate_with_qwen("some prompt"))

    def test_raises_runtime_error_when_package_unavailable(self):
        orch = _make_orchestrator_qwen_unavailable()
        with pytest.raises(RuntimeError, match="Qwen init failed"):
            asyncio.run(orch.evaluate_with_qwen("some prompt"))

    def test_returns_opt_in_sentinel_when_qwen_disabled(self):
        """qwen_enabled=False returns sentinel dict — does NOT raise."""
        orch = _make_orchestrator(qwen_enabled=False)
        result = asyncio.run(orch.evaluate_with_qwen("some prompt"))
        assert result["success"] is False
        assert result["error"] == "qwen_not_enabled"
        assert result["response"] is None

    def test_returns_gateway_unavailable_when_gateway_none_but_enabled(self):
        """Gateway is None with qwen_enabled=True and no init_error → explicit error key."""
        orch = _make_orchestrator()
        orch._qwen_gateway = None
        orch._qwen_init_error = None

        with (
            patch("apps_eval.reasoning.EvalOrchestrator.AppsQwenRequest", Mock()),
        ):
            result = asyncio.run(orch.evaluate_with_qwen("some prompt"))
        assert result["error"] == "qwen_gateway_unavailable"

    def test_successful_qwen_call_returns_response(self):
        """Happy path: gateway and telemetry available — returns response dict."""
        orch = _make_orchestrator()
        mock_response = Mock(
            success=True,
            response="Code review analysis complete",
            confidence=0.88,
            model_used="Qwen/Qwen2.5-7B-Instruct",
            latency_ms=95,
            error_message=None,
        )
        mock_telemetry = Mock()
        mock_telemetry.record_request_start = Mock()
        mock_telemetry.record_request_success = Mock()

        orch._qwen_gateway = Mock()
        orch._qwen_gateway.infer = AsyncMock(return_value=mock_response)
        orch._qwen_session_id = "test-session-id"

        with patch("apps_eval.reasoning.EvalOrchestrator.apps_qwen_telemetry", mock_telemetry):
            result = asyncio.run(orch.evaluate_with_qwen("review this code"))

        assert result["success"] is True
        assert result["response"] == "Code review analysis complete"


# ---------------------------------------------------------------------------
# Default non-Qwen pipeline behavior unchanged
# ---------------------------------------------------------------------------


class TestEvalOrchestratorNonQwenBehaviorUnchanged:
    def test_run_completes_without_qwen(self):
        """run() must complete in dry_run mode even when Qwen is unavailable."""
        orch = _make_orchestrator_qwen_unavailable()

        mock_scorecard = Mock()
        mock_scorecard.rows = []
        mock_scorecard.overall_score = 0.8
        orch._scorecard.compute = Mock(return_value=mock_scorecard)

        mock_regression = Mock()
        mock_regression.records = []
        mock_regression.regression_count = 0
        orch._regression.detect = Mock(return_value=mock_regression)

        mock_gate = Mock()
        mock_gate.passed = True
        mock_gate.violations = []
        orch._gate.validate = Mock(return_value=mock_gate)

        orch._runner.run_suite = Mock(
            return_value=Mock(
                suite_id="s1",
                display_name="Suite 1",
                scenarios=[],
                pass_rate=1.0,
                mean_latency_ms=10.0,
            )
        )
        orch._specs = Mock(
            benchmark_suites={
                "s1": Mock(
                    display_name="Suite 1",
                    scenario_ids=["sc1"],
                    timeout_sec=30,
                )
            },
            regression=Mock(auto_update_baseline=False),
        )

        from apps_eval.types.eval_types import EvalRequest  # noqa: PLC0415

        request = EvalRequest(suite_ids=["s1"], dry_run=True)
        result = orch.run(request)
        assert result.status == "dry_run"

    def test_run_does_not_call_qwen_gateway_in_default_path(self):
        """run() must never touch _qwen_gateway unless explicitly called."""
        orch = _make_orchestrator()

        mock_scorecard = Mock()
        mock_scorecard.rows = []
        mock_scorecard.overall_score = 0.9
        orch._scorecard.compute = Mock(return_value=mock_scorecard)

        mock_regression = Mock()
        mock_regression.records = []
        mock_regression.regression_count = 0
        orch._regression.detect = Mock(return_value=mock_regression)

        mock_gate = Mock()
        mock_gate.passed = True
        mock_gate.violations = []
        orch._gate.validate = Mock(return_value=mock_gate)

        orch._specs = Mock(
            benchmark_suites={},
            regression=Mock(auto_update_baseline=False),
        )

        from apps_eval.types.eval_types import EvalRequest  # noqa: PLC0415

        request = EvalRequest(suite_ids=[], dry_run=True)
        orch.run(request)

        if orch._qwen_gateway is not None:
            orch._qwen_gateway.infer.assert_not_called()
