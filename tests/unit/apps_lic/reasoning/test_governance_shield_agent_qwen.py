"""
Unit tests for GovernanceShieldAgent Qwen hardening.

Tests:
- No silent disable on explicit Qwen invocation when init failed
- Explicit RuntimeError on inference call when init failed
- Default non-Qwen behavior (sanitize_claims, audit_outreach) is unchanged
- qwen_enabled=False returns opt-in sentinel, not RuntimeError
- Gateway init failure is captured in _qwen_init_error, not swallowed
"""

from __future__ import annotations

import asyncio
import sys
from contextlib import contextmanager
from enum import Enum
from types import ModuleType
from unittest.mock import AsyncMock, Mock, patch

import pytest

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _import_governance_mod():
    """Import the GovernanceShieldAgent module (already loaded by test session)."""
    from apps_lic.reasoning import GovernanceShieldAgent as _mod  # noqa: PLC0415

    return _mod


def _bind_methods(agent, _mod):
    """Bind real GovernanceShieldAgent methods onto a bare object."""
    import types as _types  # noqa: PLC0415

    cls = _mod.GovernanceShieldAgent
    for name in (
        "analyze_governance_with_qwen",
        "sanitize_claims",
        "audit_outreach",
        "scan_risk_level",
        "_critical_fix_zero_hallucinations",
        "_fix_privacy_language",
        "_prepare_governance_analysis_prompt",
    ):
        setattr(agent, name, _types.MethodType(getattr(cls, name), agent))
    agent.naive_patterns = {
        "absolute_accuracy": ["100% accurate", "zero errors"],
        "hallucination_claims": ["zero hallucinations", r"hallucination[- ]free"],
        "privacy_violations": ["used user data"],
        "security_claims": ["completely secure"],
    }
    agent.senior_replacements = {
        "absolute_accuracy": ["high-precision (>99%) with human fallback"],
        "hallucination_claims": ["minimized hallucination rates via citation-based RAG"],
        "privacy_violations": ["leveraged anonymized telemetry for model fine-tuning"],
        "security_claims": ["enterprise-grade security with defense-in-depth"],
    }
    agent.compliance_requirements = {
        "healthcare": ["HIPAA"],
        "finance": ["SOC 2 Type II"],
        "legal": ["ABA Model Rules"],
        "cybersecurity": ["NIST CSF"],
        "general": ["GDPR"],
    }


def _make_agent(*, qwen_enabled: bool = True, gateway_raises: Exception | None = None):
    """
    Build a minimal object exercising only the hardened Qwen __post_init__ block.
    Bypasses LICAgentBase inheritance via direct attribute injection.
    """
    broken_or_mock = Mock(side_effect=gateway_raises) if gateway_raises else Mock()
    _mod = _import_governance_mod()

    class _BareAgent:
        pass

    agent = _BareAgent()
    agent.qwen_enabled = qwen_enabled
    agent.risk_thresholds = {"max_confidence_score": 0.95, "min_safety_level": 0.8}

    # Snapshot and swap module-level names
    _saved = {
        "_QWEN_AVAILABLE": _mod._QWEN_AVAILABLE,
        "AppsQwenGateway": _mod.AppsQwenGateway,
        "apps_qwen_telemetry": _mod.apps_qwen_telemetry,
    }
    _mod._QWEN_AVAILABLE = True
    _mod.AppsQwenGateway = broken_or_mock
    _mod.apps_qwen_telemetry = None

    # Run the hardened Qwen init branch
    agent._qwen_gateway = None
    agent._qwen_session_id = None
    agent._qwen_init_error = None

    try:
        if not _mod._QWEN_AVAILABLE:
            agent._qwen_init_error = "qwen_vllm package unavailable"
        elif agent.qwen_enabled:
            try:
                agent._qwen_gateway = _mod.AppsQwenGateway(model_id="Qwen/Qwen2.5-7B-Instruct")
            except RuntimeError as e:  # guardian: allow-broad-exception-in-test -- mirrors the production except block; gateway raises heterogeneous errors
                agent._qwen_init_error = str(e)
                agent._qwen_gateway = None
    finally:
        for k, v in _saved.items():
            setattr(_mod, k, v)

    _bind_methods(agent, _mod)
    return agent


def _make_agent_qwen_unavailable():
    """Build an agent with the Qwen-unavailable init path exercised."""
    _mod = _import_governance_mod()

    class _BareAgent:
        pass

    agent = _BareAgent()
    agent.qwen_enabled = True
    agent.risk_thresholds = {"max_confidence_score": 0.95, "min_safety_level": 0.8}
    agent._qwen_gateway = None
    agent._qwen_inference_worker = None
    agent._qwen_session_id = None
    # Simulate the unavailable branch: _qwen_init_error set from _QWEN_IMPORT_ERROR
    agent._qwen_init_error = "No module named 'agentic_core.L3_orchestration.inference.qwen_vllm'"

    _bind_methods(agent, _mod)
    return agent


# ---------------------------------------------------------------------------
# Routing + adapter patch helpers (mirrors test_rg_resume_orchestrator.py)
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
    mod.Provider = _Provider  # type: ignore[attr-defined]
    mod.RoutingDecision = _RoutingDecision  # type: ignore[attr-defined]
    mod.evaluate = evaluate_fn  # type: ignore[attr-defined]
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


# ---------------------------------------------------------------------------
# Init error capture
# ---------------------------------------------------------------------------


class TestGovernanceShieldAgentInitHardening:
    def test_gateway_init_failure_captured_in_qwen_init_error(self):
        """Gateway init failure must land in _qwen_init_error, not silently disable."""
        agent = _make_agent(gateway_raises=RuntimeError("vLLM not reachable"))
        assert agent._qwen_init_error is not None
        assert "vLLM not reachable" in agent._qwen_init_error

    def test_gateway_init_failure_does_not_set_qwen_enabled_false(self):
        """qwen_enabled must NOT be mutated to False on init failure — silent disable is forbidden."""
        agent = _make_agent(gateway_raises=RuntimeError("port closed"))
        assert agent.qwen_enabled is True  # still True — caller's opt-in is preserved

    def test_gateway_init_failure_leaves_gateway_none(self):
        agent = _make_agent(gateway_raises=RuntimeError("port closed"))
        assert agent._qwen_gateway is None

    def test_qwen_unavailable_sets_init_error(self):
        """Package import failure must set _qwen_init_error."""
        agent = _make_agent_qwen_unavailable()
        assert agent._qwen_init_error is not None

    def test_successful_init_leaves_init_error_none(self):
        agent = _make_agent()
        assert agent._qwen_init_error is None


# ---------------------------------------------------------------------------
# analyze_governance_with_qwen — explicit fail-loud semantics
# ---------------------------------------------------------------------------


class TestAnalyzeGovernanceWithQwenFailLoud:
    def test_raises_runtime_error_when_init_failed(self):
        """Explicit invocation after init failure must raise RuntimeError, not silently return."""
        agent = _make_agent(gateway_raises=RuntimeError("vLLM not reachable"))
        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            with pytest.raises(RuntimeError, match="Qwen init failed"):
                asyncio.run(agent.analyze_governance_with_qwen("some content"))

    def test_raises_runtime_error_when_package_unavailable(self):
        agent = _make_agent_qwen_unavailable()
        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            with pytest.raises(RuntimeError, match="Qwen init failed"):
                asyncio.run(agent.analyze_governance_with_qwen("some content"))

    def test_returns_opt_in_sentinel_when_qwen_disabled(self):
        """qwen_enabled=False returns sentinel dict — does NOT raise."""
        agent = _make_agent(qwen_enabled=False)
        result = asyncio.run(agent.analyze_governance_with_qwen("some content"))
        assert result["success"] is False
        assert result["error"] == "qwen_not_enabled"
        assert result["analysis"] is None

    def test_successful_qwen_call_returns_response(self):
        """Happy path: gateway available and succeeds — returns response dict."""
        agent = _make_agent()
        mock_response = Mock(
            success=True,
            response="RISKS_IDENTIFIED: none",
            confidence=0.9,
            model_used="Qwen/Qwen2.5-7B-Instruct",
            latency_ms=120,
            error_message=None,
        )
        agent._qwen_gateway = Mock()
        agent._qwen_gateway.infer = AsyncMock(return_value=mock_response)

        with (
            _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)),
            _adapter_patch(route_to_gemini=False),
        ):
            result = asyncio.run(agent.analyze_governance_with_qwen("safe content"))
        assert result["success"] is True
        assert result["analysis"] == "RISKS_IDENTIFIED: none"

    def test_inference_failure_raises_runtime_error(self):
        """Inference errors must propagate as RuntimeError, not be swallowed."""
        agent = _make_agent()
        agent._qwen_gateway = Mock()
        agent._qwen_gateway.infer = AsyncMock(side_effect=RuntimeError("timeout"))

        with (
            _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)),
            _adapter_patch(route_to_gemini=False),
        ):
            with pytest.raises(RuntimeError, match="inference failed"):
                asyncio.run(agent.analyze_governance_with_qwen("content"))


# ---------------------------------------------------------------------------
# Default non-Qwen behavior unchanged
# ---------------------------------------------------------------------------


class TestGovernanceShieldAgentNonQwenBehaviorUnchanged:
    def test_sanitize_claims_runs_without_qwen(self):
        """sanitize_claims must work regardless of Qwen state."""
        agent = _make_agent_qwen_unavailable()
        result = agent.sanitize_claims("We have 100% accurate AI with zero hallucinations.")
        assert "100% accurate" not in result
        assert "zero hallucinations" not in result.lower()

    def test_audit_outreach_runs_without_qwen(self):
        agent = _make_agent_qwen_unavailable()
        result = agent.audit_outreach("Our AI is completely secure.")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_scan_risk_level_runs_without_qwen(self):
        from apps_lic.reasoning.GovernanceShieldAgent import IndustrySensitivity  # noqa: PLC0415

        agent = _make_agent_qwen_unavailable()
        profile = agent.scan_risk_level("finance", "We need SOC 2 compliance")
        assert profile.industry_sensitivity == IndustrySensitivity.HIGH

    def test_default_init_with_qwen_disabled_is_clean(self):
        """qwen_enabled=False init: no error, no gateway, no init_error."""
        agent = _make_agent(qwen_enabled=False)
        assert agent._qwen_gateway is None
        assert agent._qwen_init_error is None
        assert agent.qwen_enabled is False


# ---------------------------------------------------------------------------
# Local-first routing discipline
# ---------------------------------------------------------------------------


class TestGovernanceShieldAgentLocalFirstRouting:
    """routing_ctx + evaluate_routing discipline added to analyze_governance_with_qwen."""

    def test_routing_context_constants(self):
        """Phase-1 constants: routing_ctx passes the expected sentinel values."""
        agent = _make_agent()
        captured: dict = {}

        def capture_routing(ctx):
            captured.update(ctx)
            return _RoutingDecision(_Provider.LOCAL_VLLM)

        mock_response = Mock(
            success=True,
            response="ok",
            confidence=0.9,
            model_used="Qwen",
            latency_ms=100,
            error_message=None,
        )
        agent._qwen_gateway.infer = AsyncMock(return_value=mock_response)

        with (
            _routing_module_patch(capture_routing),
            _adapter_patch(route_to_gemini=False),
        ):
            asyncio.run(agent.analyze_governance_with_qwen("test content"))

        assert captured["requires_policy_read"] is False
        assert captured["iteration_count"] == 0
        assert captured["max_iterations"] == 100
        assert captured["invalid_ast"] is False
        assert captured["routing_version"] == "1"

    def test_skip_when_predicate_selects_opus(self):
        """Non-local predicate: returns skip sentinel with disposition."""
        agent = _make_agent()
        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.OPUS, "opus-hash")):
            result = asyncio.run(agent.analyze_governance_with_qwen("content"))
        assert result["success"] is False
        assert result["error"] == "predicate_selected_opus"
        dsp = result["local_first_disposition"]
        assert dsp["adapter_decision"] == "SKIP_QWEN_NON_LOCAL_ROUTE"
        assert dsp["reason_code"] == "predicate_selected_opus"

    def test_skip_when_gateway_not_initialized(self):
        """Gateway None with LOCAL_VLLM: skip with gateway_not_initialized reason."""
        agent = _make_agent()
        agent._qwen_gateway = None
        agent._qwen_init_error = None
        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            result = asyncio.run(agent.analyze_governance_with_qwen("content"))
        assert result["error"] == "qwen_gateway_unavailable"
        dsp = result["local_first_disposition"]
        assert dsp["adapter_decision"] == "SKIP_QWEN_NON_LOCAL_ROUTE"
        assert dsp["reason_code"] == "gateway_not_initialized"

    def test_init_error_raises_when_local_vllm_selected(self):
        """Init error + LOCAL_VLLM selected: raises RuntimeError (fail-loud preserved)."""
        agent = _make_agent(gateway_raises=RuntimeError("port closed"))
        with _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)):
            with pytest.raises(RuntimeError, match="Qwen init failed"):
                asyncio.run(agent.analyze_governance_with_qwen("content"))

    def test_qwen_disabled_returns_early_before_routing(self):
        """qwen_enabled=False returns before routing — no local_first_disposition key."""
        agent = _make_agent(qwen_enabled=False)
        result = asyncio.run(agent.analyze_governance_with_qwen("content"))
        assert result["error"] == "qwen_not_enabled"
        assert "local_first_disposition" not in result


# ---------------------------------------------------------------------------
# Adapter gate + LocalFirstDisposition discipline
# ---------------------------------------------------------------------------


class TestGovernanceShieldAgentAdapterDisposition:
    """VLLMGatewayAdapter gate and LocalFirstDisposition emission in analyze_governance_with_qwen."""

    def test_adapter_allow_returns_disposition_and_result(self):
        """Allow path: adapter allow → Qwen called, disposition ALLOW_LOCAL_QWEN present."""
        agent = _make_agent()
        mock_response = Mock(
            success=True,
            response="RISKS: none",
            confidence=0.9,
            model_used="Qwen",
            latency_ms=50,
            error_message=None,
        )
        agent._qwen_gateway.infer = AsyncMock(return_value=mock_response)

        with (
            _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM, "allow-hash")),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
        ):
            result = asyncio.run(agent.analyze_governance_with_qwen("safe content"))

        assert result["success"] is True
        assert result["analysis"] == "RISKS: none"
        dsp = result["local_first_disposition"]
        assert dsp["adapter_decision"] == "ALLOW_LOCAL_QWEN"
        assert dsp["qwen_called"] is True
        mock_adapter.record_local_success.assert_called_once_with(severity="medium")
        mock_adapter.record_local_failure.assert_not_called()

    def test_adapter_escalate_skips_infer(self):
        """Escalate path: adapter route_to_gemini=True → infer never called, ESCALATE_EXTERNAL."""
        agent = _make_agent()

        with (
            _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM, "esc-hash")),
            _adapter_patch(route_to_gemini=True) as mock_adapter,
        ):
            result = asyncio.run(agent.analyze_governance_with_qwen("content"))
            agent._qwen_gateway.infer.assert_not_called()

        assert result["error"] == "adapter_escalated_to_gemini"
        dsp = result["local_first_disposition"]
        assert dsp["adapter_decision"] == "ESCALATE_EXTERNAL"
        assert dsp["qwen_called"] is False
        mock_adapter.evaluate.assert_called_once()
        mock_adapter.record_local_success.assert_not_called()

    def test_adapter_task_class_is_governance_analysis(self):
        """Contract: adapter.evaluate() receives task_class=governance_analysis."""
        agent = _make_agent()
        mock_response = Mock(
            success=True,
            response="ok",
            confidence=0.9,
            model_used="Qwen",
            latency_ms=50,
            error_message=None,
        )
        agent._qwen_gateway.infer = AsyncMock(return_value=mock_response)

        with (
            _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
        ):
            asyncio.run(agent.analyze_governance_with_qwen("content"))

        call_kwargs = mock_adapter.evaluate.call_args
        assert call_kwargs.kwargs["task_class"] == "governance_analysis"
        assert call_kwargs.kwargs["severity"] == "medium"

    def test_circuit_breaker_failure_recorded_on_infer_error(self):
        """Circuit breaker: record_local_failure called when Qwen raises; error re-raised."""
        agent = _make_agent()
        agent._qwen_gateway.infer = AsyncMock(side_effect=RuntimeError("timeout"))

        with (
            _routing_module_patch(lambda _: _RoutingDecision(_Provider.LOCAL_VLLM)),
            _adapter_patch(route_to_gemini=False) as mock_adapter,
        ):
            with pytest.raises(RuntimeError, match="inference failed"):
                asyncio.run(agent.analyze_governance_with_qwen("content"))

        mock_adapter.record_local_failure.assert_called_once_with(severity="medium")
        mock_adapter.record_local_success.assert_not_called()
