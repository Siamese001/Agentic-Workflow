"""
Unit tests for RfpOrchestrator — apps_rfp.

Tests:
- Local-first Qwen routing: Phase 1 explicit routing behaviour
- State Integrity: _qwen_init_error populated on gateway failure
- Logic Branching: LOCAL_VLLM vs OPUS escalation paths
- Mocking: Zero network calls
"""

import asyncio
import sys
from contextlib import contextmanager
from enum import Enum
from types import ModuleType
from unittest.mock import AsyncMock, Mock, patch

import pytest


# ---------------------------------------------------------------------------
# Stub routing types (vllm_routing_predicates imports tools.canonical_hash
# which is archived; construct minimal stubs for unit tests)
# ---------------------------------------------------------------------------


class _Provider(Enum):
    OPUS = "opus"
    LOCAL_VLLM = "local_vllm"


class _RoutingDecision:
    def __init__(self, provider, predicate_evaluation_hash="test", routing_version="1"):
        self.provider = provider
        self.predicate_evaluation_hash = predicate_evaluation_hash
        self.routing_version = routing_version


def _make_routing_module(evaluate_fn):
    mod = ModuleType("agentic_core.L4_state.config.vllm_routing_predicates")
    mod.Provider = _Provider
    mod.RoutingDecision = _RoutingDecision
    mod.evaluate = evaluate_fn
    return mod


@contextmanager
def _routing_module_patch(evaluate_fn):
    stub = _make_routing_module(evaluate_fn)
    key = "agentic_core.L4_state.config.vllm_routing_predicates"
    prev = sys.modules.pop(key, None)
    sys.modules[key] = stub
    try:
        yield stub
    finally:
        sys.modules.pop(key, None)
        if prev is not None:
            sys.modules[key] = prev


@pytest.fixture(autouse=True)
def mock_external_services():
    with (
        patch("redis.Redis", return_value=Mock()),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "ANTHROPIC_API_KEY": "test-key"}),
    ):
        yield


# ---------------------------------------------------------------------------
# Stub VLLMGatewayAdapter
# ---------------------------------------------------------------------------


def _make_adapter_stub(*, route_to_gemini: bool = False):
    mock_telemetry = Mock()
    mock_telemetry.as_dict.return_value = {
        "provider_selected": "local_fast" if not route_to_gemini else "gemini",
        "token_budget_ok": not route_to_gemini,
        "queue_full": route_to_gemini,
        "queue_depth": 0,
        "breaker_state": "closed",
    }
    mock_result = Mock()
    mock_result.route_to_gemini = route_to_gemini
    mock_result.telemetry = mock_telemetry
    mock_adapter = Mock()
    mock_adapter.evaluate.return_value = mock_result
    mock_adapter.record_local_success = Mock()
    mock_adapter.record_local_failure = Mock()
    stub_class = Mock(return_value=mock_adapter)
    return stub_class, mock_adapter


@contextmanager
def _adapter_patch(*, route_to_gemini: bool = False):
    stub_class, mock_adapter = _make_adapter_stub(route_to_gemini=route_to_gemini)
    with patch(
        "agentic_core.L2_execution.types.vllm_gateway_adapter_types.VLLMGatewayAdapter",
        stub_class,
    ):
        yield mock_adapter


class _ProposalStatusNS:
    """Namespace shim: ProposalStatus is a Literal alias, not an Enum; the orchestrator uses .ATTR syntax."""

    GENERATING = "generating"
    GATE_CHECKING = "gate_checking"
    COMPLETE = "complete"
    FAILED = "failed"
    DRY_RUN = "dry_run"


def _make_orchestrator(*, qwen_enabled: bool = True, qwen_available: bool = True):
    """Build an RfpOrchestrator with all external I/O mocked."""
    with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
        from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator  # noqa: PLC0415

        with (
            patch("apps_rfp.reasoning.RfpOrchestrator._QWEN_AVAILABLE", qwen_available),
            patch("apps_rfp.reasoning.RfpOrchestrator.AppsQwenGateway", Mock()),
            patch("apps_rfp.reasoning.RfpOrchestrator.apps_qwen_telemetry", None),
            patch(
                "apps_rfp.reasoning.RfpOrchestrator.ProposalAssemblyEngine",
                Mock(
                    return_value=Mock(
                        execute=Mock(return_value=Mock(sections=[], roadmap=[], risks=[], assumptions=[]))
                    )
                ),
            ),
            patch(
                "apps_rfp.reasoning.RfpOrchestrator.ProposalGateValidator",
                Mock(
                    return_value=Mock(
                        validate=Mock(return_value=Mock(passed=True, quality_score=0.9, violations=[]))
                    )
                ),
            ),
        ):
            orch = RfpOrchestrator(qwen_enabled=qwen_enabled, dry_run=True)
    return orch


def _make_request():
    from apps_rfp.types.rfp_types import RfpRequest  # noqa: PLC0415

    return RfpRequest(
        problem_statement="Implement an AI-powered underwriting platform for commercial insurance.",
        industry="insurance",
        dry_run=True,
    )


class TestRfpOrchestratorLocalFirstRouting:
    """Phase 1: explicit local-first Qwen routing behaviour inside run()."""

    def test_run_sets_qwen_inference_result_when_local_vllm_selected(self):
        """Happy path: LOCAL_VLLM routing → qwen_inference_result set on result."""
        orch = _make_orchestrator()
        mock_qwen_result = {"success": True, "content": "Proposal content", "confidence": 0.88}
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc123")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False),
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock(return_value=mock_qwen_result)),
        ):
            result = asyncio.run(orch.run(_make_request()))

        assert result.qwen_inference_result == mock_qwen_result

    def test_run_leaves_qwen_inference_result_none_when_opus_escalation(self):
        """Escalation path: OPUS routing → qwen_inference_result is None, no Qwen call."""
        orch = _make_orchestrator()
        opus_decision = _RoutingDecision(_Provider.OPUS, predicate_evaluation_hash="def456")

        with (
            _routing_module_patch(lambda _: opus_decision),
            _adapter_patch(),
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock()) as mock_infer,
        ):
            result = asyncio.run(orch.run(_make_request()))
            mock_infer.assert_not_called()

        assert result.qwen_inference_result is None

    def test_run_raises_runtime_error_when_init_failed_and_local_vllm_selected(self):
        """No hidden bypass: if Qwen init failed and LOCAL_VLLM is selected, run() raises."""
        orch = _make_orchestrator()
        orch._qwen_init_error = "aiohttp.ClientConnectorError: Cannot connect to localhost:8000"
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc123")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(),
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
        ):
            with pytest.raises(RuntimeError, match="LOCAL_VLLM selected but Qwen init failed"):
                asyncio.run(orch.run(_make_request()))

    def test_run_skips_qwen_when_gateway_is_none_and_no_init_error(self):
        """Edge case: gateway is None, no init error → no call, no raise."""
        orch = _make_orchestrator(qwen_enabled=False, qwen_available=False)
        orch._qwen_gateway = None
        orch._qwen_init_error = None
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc123")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(),
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock()) as mock_infer,
        ):
            result = asyncio.run(orch.run(_make_request()))
            mock_infer.assert_not_called()

        assert result.qwen_inference_result is None

    def test_qwen_init_error_field_set_on_gateway_failure(self):
        """State integrity: _qwen_init_error is populated when gateway init raises."""
        broken_gateway = Mock(side_effect=RuntimeError("vLLM not reachable"))

        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            from apps_rfp.reasoning.RfpOrchestrator import RfpOrchestrator  # noqa: PLC0415

            with (
                patch("apps_rfp.reasoning.RfpOrchestrator._QWEN_AVAILABLE", True),
                patch("apps_rfp.reasoning.RfpOrchestrator.AppsQwenGateway", broken_gateway),
                patch("apps_rfp.reasoning.RfpOrchestrator.apps_qwen_telemetry", None),
                patch("apps_rfp.reasoning.RfpOrchestrator.ProposalAssemblyEngine", Mock(return_value=Mock())),
                patch("apps_rfp.reasoning.RfpOrchestrator.ProposalGateValidator", Mock(return_value=Mock())),
            ):
                orch = RfpOrchestrator(qwen_enabled=True)

        assert orch._qwen_init_error is not None
        assert "vLLM not reachable" in orch._qwen_init_error
        assert orch._qwen_gateway is None

    def test_routing_context_uses_phase1_constants(self):
        """Validation: routing context passed to evaluate_routing matches Phase 1 constants."""
        orch = _make_orchestrator()
        captured_ctx = {}

        def capture_routing(ctx):
            captured_ctx.update(ctx)
            return _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc")

        with (
            _routing_module_patch(capture_routing),
            _adapter_patch(route_to_gemini=False),
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock(return_value={"success": True})),
        ):
            asyncio.run(orch.run(_make_request()))

        assert captured_ctx["requires_policy_read"] is False
        assert captured_ctx["iteration_count"] == 0
        assert captured_ctx["max_iterations"] == 100
        assert captured_ctx["invalid_ast"] is False


class TestRfpOrchestratorAdapterDisposition:
    """Phase 1 adapter: VLLMGatewayAdapter disposition trails inside run()."""

    def test_adapter_allow_calls_qwen(self):
        """Allow path: adapter route_to_gemini=False → Qwen is called, result set."""
        orch = _make_orchestrator()
        mock_qwen_result = {"success": True, "content": "proposal"}
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="allow-hash")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock(return_value=mock_qwen_result)),
        ):
            result = asyncio.run(orch.run(_make_request()))

        assert result.qwen_inference_result == mock_qwen_result
        mock_adapter.evaluate.assert_called_once()
        mock_adapter.record_local_success.assert_called_once_with(severity="medium")
        mock_adapter.record_local_failure.assert_not_called()
        assert result.local_first_disposition is not None
        assert result.local_first_disposition["adapter_decision"] == "ALLOW_LOCAL_QWEN"
        assert result.local_first_disposition["qwen_called"] is True
        assert result.local_first_disposition["qwen_result_present"] is True

    def test_adapter_escalate_skips_qwen(self):
        """Escalate path: adapter route_to_gemini=True → Qwen NOT called, result is None."""
        orch = _make_orchestrator()
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="esc-hash")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=True) as mock_adapter,
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock()) as mock_infer,
        ):
            result = asyncio.run(orch.run(_make_request()))
            mock_infer.assert_not_called()

        assert result.qwen_inference_result is None
        mock_adapter.evaluate.assert_called_once()
        mock_adapter.record_local_success.assert_not_called()
        assert result.local_first_disposition is not None
        assert result.local_first_disposition["adapter_decision"] == "ESCALATE_EXTERNAL"
        assert result.local_first_disposition["qwen_called"] is False

    def test_adapter_evaluate_called_with_correct_task_class(self):
        """Contract: adapter.evaluate() receives task_class=proposal_generation."""
        orch = _make_orchestrator()
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM)

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(orch, "generate_proposal_with_qwen", new=AsyncMock(return_value={})),
        ):
            asyncio.run(orch.run(_make_request()))

        call_kwargs = mock_adapter.evaluate.call_args
        assert call_kwargs.kwargs["task_class"] == "proposal_generation"
        assert call_kwargs.kwargs["severity"] == "medium"

    def test_adapter_circuit_breaker_failure_recorded_on_qwen_error(self):
        """Circuit breaker: record_local_failure called when Qwen raises."""
        orch = _make_orchestrator()
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM)

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
            patch("apps_rfp.reasoning.RfpOrchestrator.ProposalStatus", _ProposalStatusNS),
            patch("apps_rfp.reasoning.RfpOrchestrator.RfpRunSummary", Mock(return_value=Mock())),
            patch.object(
                orch, "generate_proposal_with_qwen", new=AsyncMock(side_effect=RuntimeError("Qwen down"))
            ),
        ):
            with pytest.raises(RuntimeError, match="Qwen down"):
                asyncio.run(orch.run(_make_request()))

        mock_adapter.record_local_failure.assert_called_once_with(severity="medium")
        mock_adapter.record_local_success.assert_not_called()
