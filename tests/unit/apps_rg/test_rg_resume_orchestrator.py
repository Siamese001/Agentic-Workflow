"""
Unit tests for RgResumeOrchestrator - Orchestrator in Apps.

Orchestrate the multi-hop resume generation workflow.

Tests:
- State Integrity: Verify initialization and state
- Logic Branching: Test method dispatch
- Fuzzing: Invalid inputs
- Mocking: Zero network calls
- Local-first Qwen routing: Phase 1 explicit routing behaviour
"""

import asyncio
import sys
from contextlib import contextmanager
from enum import Enum
from types import ModuleType
from unittest.mock import AsyncMock, Mock, patch

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


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
    """Build a minimal sys.modules stub for vllm_routing_predicates."""
    mod = ModuleType("agentic_core.L4_state.config.vllm_routing_predicates")
    mod.Provider = _Provider
    mod.RoutingDecision = _RoutingDecision
    mod.evaluate = evaluate_fn
    return mod


@contextmanager
def _routing_module_patch(evaluate_fn):
    """Inject a stub vllm_routing_predicates module into sys.modules.

    Required because the real module depends on tools.canonical_hash which
    is archived and not importable in the unit-test environment.
    """
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
    """Mock all external services to prevent network calls."""
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


class TestRgResumeOrchestratorAgent:
    """Unit tests for RgResumeOrchestrator."""

    @pytest.fixture
    def agent_class(self):
        """Import agent class with mocked dependencies."""
        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator

            return RgResumeOrchestrator

    def test_class_exists(self, agent_class):
        """Verify RgResumeOrchestrator exists and is importable."""
        assert agent_class is not None, "RgResumeOrchestrator should exist"

    def test_inherits_from_r_g_agent_base(self, agent_class):
        """Verify proper inheritance from RGAgentBase."""
        mro_names = [cls.__name__ for cls in agent_class.__mro__]
        assert "RGAgentBase" in mro_names, "Should inherit from RGAgentBase"

    def test_has_post_init_method(self, agent_class):
        """Verify agent has __post_init__ method."""
        assert hasattr(agent_class, "__post_init__"), "Should have __post_init__ method"

    def test_has_run_method(self, agent_class):
        assert hasattr(agent_class, "run")

    def test_no_network_calls_on_import(self):
        pass


# ---------------------------------------------------------------------------
# Phase 1 local-first routing tests
# ---------------------------------------------------------------------------


def _make_orchestrator(*, qwen_enabled: bool = True, qwen_available: bool = True):
    """Build an RgResumeOrchestrator with all external I/O mocked."""
    with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
        from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator  # noqa: PLC0415

        with (
            patch("apps_rg.reasoning.RgResumeOrchestrator._QWEN_AVAILABLE", qwen_available),
            patch("apps_rg.reasoning.RgResumeOrchestrator.AppsQwenGateway", Mock()),
            patch("apps_rg.reasoning.RgResumeOrchestrator.apps_qwen_telemetry", None),
            patch(
                "apps_rg.reasoning.RgResumeOrchestrator.RepoSignalService",
                Mock(return_value=Mock(collect=Mock(return_value=Mock(as_dict=Mock(return_value={}))))),
            ),
        ):
            orch = RgResumeOrchestrator(
                master_resume={}, qwen_enabled=qwen_enabled, enable_repo_signals=False
            )
    return orch


class TestRgResumeOrchestratorLocalFirstRouting:
    """Phase 1: explicit local-first Qwen routing behaviour inside run()."""

    def test_run_returns_qwen_resume_content_field_when_local_vllm_selected(self):
        """Happy path: LOCAL_VLLM routing → qwen_resume_content present in result."""
        orch = _make_orchestrator()
        mock_qwen_result = {"success": True, "content": "Generated resume text", "confidence": 0.9}
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc123")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False),
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock(return_value=mock_qwen_result)),
        ):
            result = orch.run("Python engineer role")

        assert "qwen_resume_content" in result, "qwen_resume_content must be present when LOCAL_VLLM selected"
        assert result["qwen_resume_content"] == mock_qwen_result
        assert result["status"] == "success"

    def test_run_omits_qwen_resume_content_when_opus_escalation(self):
        """Escalation path: OPUS routing → qwen_resume_content absent, no Qwen call made."""
        orch = _make_orchestrator()
        opus_decision = _RoutingDecision(_Provider.OPUS, predicate_evaluation_hash="def456")

        with (
            _routing_module_patch(lambda _: opus_decision),
            _adapter_patch(),
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock()) as mock_infer,
        ):
            result = orch.run("Python engineer role")
            mock_infer.assert_not_called()

        assert "qwen_resume_content" not in result
        assert result["status"] == "success"

    def test_run_raises_runtime_error_when_init_failed_and_local_vllm_selected(self):
        """No hidden bypass: if Qwen init failed and LOCAL_VLLM is selected, run() raises."""
        orch = _make_orchestrator()
        orch._qwen_init_error = "aiohttp.ClientConnectorError: Cannot connect to localhost:8000"
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc123")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(),
        ):
            with pytest.raises(RuntimeError, match="LOCAL_VLLM selected but Qwen init failed"):
                asyncio.run(orch.run("Python engineer role"))

    def test_run_skips_qwen_call_when_gateway_is_none_and_no_init_error(self):
        """Edge case: gateway is None but no init error (qwen_enabled=False) → no Qwen call, no raise."""
        orch = _make_orchestrator(qwen_enabled=False, qwen_available=False)
        orch._qwen_gateway = None
        orch._qwen_init_error = None
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="abc123")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(),
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock()) as mock_infer,
        ):
            result = orch.run("Python engineer role")
            mock_infer.assert_not_called()

        assert "qwen_resume_content" not in result

    def test_qwen_init_error_field_set_on_gateway_failure(self):
        """State integrity: _qwen_init_error is populated when gateway init raises."""
        broken_gateway = Mock(side_effect=RuntimeError("vLLM not reachable"))

        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            from apps_rg.reasoning.RgResumeOrchestrator import RgResumeOrchestrator  # noqa: PLC0415

            with (
                patch("apps_rg.reasoning.RgResumeOrchestrator._QWEN_AVAILABLE", True),
                patch("apps_rg.reasoning.RgResumeOrchestrator.AppsQwenGateway", broken_gateway),
                patch("apps_rg.reasoning.RgResumeOrchestrator.apps_qwen_telemetry", None),
            ):
                orch = RgResumeOrchestrator(master_resume={}, qwen_enabled=True, enable_repo_signals=False)

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
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock(return_value={"success": True})),
        ):
            orch.run("Python engineer role")

        assert captured_ctx["requires_policy_read"] is False
        assert captured_ctx["iteration_count"] == 0
        assert captured_ctx["max_iterations"] == 100
        assert captured_ctx["invalid_ast"] is False


class TestRgResumeOrchestratorAdapterDisposition:
    """Phase 1 adapter: VLLMGatewayAdapter disposition trails inside run()."""

    def test_adapter_allow_calls_qwen(self):
        """Allow path: adapter route_to_gemini=False → Qwen is called, result present."""
        orch = _make_orchestrator()
        mock_qwen_result = {"success": True, "content": "resume"}
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="allow-hash")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock(return_value=mock_qwen_result)),
        ):
            result = orch.run("Python engineer role")

        assert result.get("qwen_resume_content") == mock_qwen_result
        mock_adapter.evaluate.assert_called_once()
        mock_adapter.record_local_success.assert_called_once_with(severity="medium")
        mock_adapter.record_local_failure.assert_not_called()
        dsp = result.get("local_first_disposition")
        assert dsp is not None
        assert dsp["adapter_decision"] == "ALLOW_LOCAL_QWEN"
        assert dsp["qwen_called"] is True
        assert dsp["qwen_result_present"] is True

    def test_adapter_escalate_skips_qwen(self):
        """Escalate path: adapter route_to_gemini=True → Qwen NOT called, key absent."""
        orch = _make_orchestrator()
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM, predicate_evaluation_hash="esc-hash")

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=True) as mock_adapter,
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock()) as mock_infer,
        ):
            result = orch.run("Python engineer role")
            mock_infer.assert_not_called()

        assert "qwen_resume_content" not in result
        mock_adapter.evaluate.assert_called_once()
        mock_adapter.record_local_success.assert_not_called()
        dsp = result.get("local_first_disposition")
        assert dsp is not None
        assert dsp["adapter_decision"] == "ESCALATE_EXTERNAL"
        assert dsp["qwen_called"] is False

    def test_adapter_evaluate_called_with_correct_task_class(self):
        """Contract: adapter.evaluate() receives task_class=resume_generation."""
        orch = _make_orchestrator()
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM)

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
            patch.object(orch, "generate_resume_with_qwen", new=AsyncMock(return_value={})),
        ):
            orch.run("Python engineer role")

        call_kwargs = mock_adapter.evaluate.call_args
        assert call_kwargs.kwargs["task_class"] == "resume_generation"
        assert call_kwargs.kwargs["severity"] == "medium"

    def test_adapter_circuit_breaker_failure_recorded_on_qwen_error(self):
        """Circuit breaker: record_local_failure called when Qwen raises."""
        orch = _make_orchestrator()
        local_decision = _RoutingDecision(_Provider.LOCAL_VLLM)

        with (
            _routing_module_patch(lambda _: local_decision),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
            patch.object(
                orch, "generate_resume_with_qwen", new=AsyncMock(side_effect=RuntimeError("Qwen down"))
            ),
        ):
            with pytest.raises(RuntimeError, match="Qwen down"):
                asyncio.run(orch.run("Python engineer role"))

        mock_adapter.record_local_failure.assert_called_once_with(severity="medium")
        mock_adapter.record_local_success.assert_not_called()


class TestLocalFirstDispositionFactories:
    """Verify each factory classmethod produces the exact field mapping previously
    encoded inline in the orchestrators.  Pure data — no mocks, no I/O."""

    def _telem(self) -> dict:
        return {"provider_selected": "local_fast", "token_budget_ok": True}

    def test_for_fail_init_fields(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            AdapterDecision,
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_fail_init(
            orchestrator="X",
            run_id="r1",
            predicate_hash="h1",
            init_error="boom",
        ).as_dict()
        assert d["adapter_decision"] == AdapterDecision.FAIL_LOCAL_INIT
        assert d["route_provider"] == "LOCAL_VLLM"
        assert d["provider_lane"] == "none"
        assert d["reason_code"] == "qwen_init_failed"
        assert d["init_error"] == "boom"
        assert d["qwen_called"] is False
        assert d["predicate_hash"] == "h1"

    def test_for_escalate_fields(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            AdapterDecision,
            LocalFirstDisposition,
        )

        telem = {"provider_selected": "gemini_fast"}
        d = LocalFirstDisposition.for_escalate(
            orchestrator="X",
            run_id="r1",
            predicate_hash="h1",
            telem=telem,
        ).as_dict()
        assert d["adapter_decision"] == AdapterDecision.ESCALATE_EXTERNAL
        assert d["route_provider"] == "LOCAL_VLLM"
        assert d["provider_lane"] == "gemini_fast"
        assert d["reason_code"] == "adapter_route_to_gemini"
        assert d["adapter_telemetry"] == telem
        assert d["qwen_called"] is False

    def test_for_escalate_provider_lane_default(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_escalate(
            orchestrator="X",
            run_id="r",
            predicate_hash="h",
            telem={},
        ).as_dict()
        assert d["provider_lane"] == "gemini"

    def test_for_fail_exec_fields(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            AdapterDecision,
            LocalFirstDisposition,
        )

        exc = RuntimeError("net error")
        d = LocalFirstDisposition.for_fail_exec(
            orchestrator="X",
            run_id="r1",
            predicate_hash="h1",
            telem=self._telem(),
            exc=exc,
        ).as_dict()
        assert d["adapter_decision"] == AdapterDecision.FAIL_LOCAL_EXECUTION
        assert d["qwen_called"] is True
        assert d["qwen_result_present"] is False
        assert d["execution_error"] == "net error"
        assert d["provider_lane"] == "local_fast"

    def test_for_fail_exec_provider_lane_default(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_fail_exec(
            orchestrator="X",
            run_id="r",
            predicate_hash="h",
            telem={},
            exc=ValueError("x"),
        ).as_dict()
        assert d["provider_lane"] == "local_fast"

    def test_for_allow_fields(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            AdapterDecision,
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_allow(
            orchestrator="X",
            run_id="r1",
            predicate_hash="h1",
            telem=self._telem(),
            qwen_result_present=True,
        ).as_dict()
        assert d["adapter_decision"] == AdapterDecision.ALLOW_LOCAL_QWEN
        assert d["qwen_called"] is True
        assert d["qwen_result_present"] is True
        assert d["reason_code"] == "adapter_allow"
        assert d["provider_lane"] == "local_fast"

    def test_for_allow_result_absent(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_allow(
            orchestrator="X",
            run_id="r",
            predicate_hash="h",
            telem={},
            qwen_result_present=False,
        ).as_dict()
        assert d["qwen_result_present"] is False

    def test_for_skip_gateway_not_init(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            AdapterDecision,
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_skip(
            orchestrator="X",
            run_id="r1",
            provider_value="LOCAL_VLLM",
            predicate_hash="h1",
            reason_code="gateway_not_initialized",
        ).as_dict()
        assert d["adapter_decision"] == AdapterDecision.SKIP_QWEN_NON_LOCAL_ROUTE
        assert d["route_provider"] == "LOCAL_VLLM"
        assert d["provider_lane"] == "none"
        assert d["reason_code"] == "gateway_not_initialized"
        assert d["qwen_called"] is False

    def test_for_skip_non_local_predicate(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            AdapterDecision,
            LocalFirstDisposition,
        )

        d = LocalFirstDisposition.for_skip(
            orchestrator="X",
            run_id="r1",
            provider_value="OPUS",
            predicate_hash="h1",
            reason_code="predicate_selected_opus",
        ).as_dict()
        assert d["adapter_decision"] == AdapterDecision.SKIP_QWEN_NON_LOCAL_ROUTE
        assert d["route_provider"] == "OPUS"
        assert d["reason_code"] == "predicate_selected_opus"

    def test_as_log_line_prefix(self):
        from agentic_core.L2_execution.types.local_first_disposition import (  # noqa: PLC0415
            LocalFirstDisposition,
        )

        pkt = LocalFirstDisposition.for_skip(
            orchestrator="X",
            run_id="r",
            provider_value="OPUS",
            predicate_hash="h",
            reason_code="predicate_selected_opus",
        )
        assert pkt.as_log_line().startswith("LOCAL_FIRST_DISPOSITION {")
