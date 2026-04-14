"""Direct tests for agentic_core/seams hardening (seams-hardening phase).

Covers:
  authority.py          — fail-closed _NullAuthority, lru_cache factory
  orchestration_protocols.py — frozen OrchestrationResult, _serialize_handshake_state
  safety_agents.py      — dispatch-table SafetyAgentFactory, protocol check
  workflow_learning_bridge.py — bounded deque, RLock, input validation
"""

from __future__ import annotations

import dataclasses
import math
import os

import pytest


# ---------------------------------------------------------------------------
# G1–G5: _NullAuthority (authority.py)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNullAuthorityFailClosed:
    def setup_method(self):
        from agentic_core.seams.contracts.authority import get_mcp_authority

        get_mcp_authority.cache_clear()

    def teardown_method(self):
        from agentic_core.seams.contracts.authority import get_mcp_authority

        get_mcp_authority.cache_clear()

    def _make(self, reason: str = "test"):
        from agentic_core.seams.contracts.authority import _NullAuthority

        return _NullAuthority(reason)

    def _clear_env(self):
        return os.environ.pop("SEAMS_ALLOW_FAIL_OPEN_AUTHORITY", None)

    def test_fail_closed_by_default(self):
        """G1: is_authorized() returns False when env var absent."""
        backup = self._clear_env()
        try:
            assert self._make().is_authorized() is False
        finally:
            if backup is not None:
                os.environ["SEAMS_ALLOW_FAIL_OPEN_AUTHORITY"] = backup

    def test_authorize_raises_permission_error_when_closed(self):
        """G2: authorize_tool_call raises PermissionError when fail-closed."""
        backup = self._clear_env()
        try:
            with pytest.raises(PermissionError, match="MCP authority unavailable"):
                self._make().authorize_tool_call("my_tool", {})
        finally:
            if backup is not None:
                os.environ["SEAMS_ALLOW_FAIL_OPEN_AUTHORITY"] = backup

    def test_authorize_raises_value_error_for_empty_tool_name(self):
        """G3: authorize_tool_call("") raises ValueError regardless of env."""
        backup = self._clear_env()
        try:
            with pytest.raises(ValueError, match="tool_name must be non-empty"):
                self._make().authorize_tool_call("", {})
        finally:
            if backup is not None:
                os.environ["SEAMS_ALLOW_FAIL_OPEN_AUTHORITY"] = backup

    def test_record_breach_returns_structured_dict(self):
        """G4: record_breach returns dict with trace_id, authorized, reason, error."""
        result = self._make("missing L5").record_breach("bad thing")
        assert isinstance(result, dict)
        assert "trace_id" in result
        assert result["authorized"] is False
        assert result["reason"] == "missing L5"
        assert result["error"] == "bad thing"
        assert len(result["trace_id"]) > 0

    def test_fail_open_via_env_allows_tool_call(self):
        """G5: authorize_tool_call succeeds (no raise) when env=1."""
        old = os.environ.get("SEAMS_ALLOW_FAIL_OPEN_AUTHORITY")
        os.environ["SEAMS_ALLOW_FAIL_OPEN_AUTHORITY"] = "1"
        try:
            self._make("offline").authorize_tool_call("allowed_tool", {"k": "v"})
        finally:
            if old is None:
                os.environ.pop("SEAMS_ALLOW_FAIL_OPEN_AUTHORITY", None)
            else:
                os.environ["SEAMS_ALLOW_FAIL_OPEN_AUTHORITY"] = old

    def test_get_mcp_authority_returns_null_when_l5_absent(self):
        """G6: get_mcp_authority() returns an MCPAuthorityProtocol-conformant object."""
        from agentic_core.seams.contracts.authority import MCPAuthorityProtocol, get_mcp_authority

        auth = get_mcp_authority()
        assert isinstance(auth, MCPAuthorityProtocol)
        assert hasattr(auth, "is_authorized")
        assert hasattr(auth, "record_breach")
        assert hasattr(auth, "authorize_tool_call")


# ---------------------------------------------------------------------------
# G7–G9: OrchestrationResult + _serialize_handshake_state
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOrchestrationResultHardening:
    def test_frozen_rejects_assignment(self):
        """G7: Mutating a frozen dataclass field raises FrozenInstanceError."""
        from agentic_core.seams.contracts.orchestration_protocols import OrchestrationResult

        result = OrchestrationResult(success=True, route_mode="B", plan_hash="abc")
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
            result.success = False  # type: ignore[misc]

    def test_to_dict_deepcopies_execution_trace(self):
        """G8: Mutating the returned execution_trace dict does not affect the original."""
        from agentic_core.seams.contracts.orchestration_protocols import OrchestrationResult

        trace = {"step": 1}
        result = OrchestrationResult(success=True, route_mode="C", plan_hash="h1", execution_trace=trace)
        d = result.to_dict()
        d["execution_trace"]["step"] = 999
        assert trace["step"] == 1

    def test_to_dict_none_fields_serialize_correctly(self):
        """G8 edge: None trace/artifact/metadata serialize to None/{} as specified."""
        from agentic_core.seams.contracts.orchestration_protocols import OrchestrationResult

        result = OrchestrationResult(success=False, route_mode="A", plan_hash="x")
        d = result.to_dict()
        assert d["execution_trace"] is None
        assert d["human_decision_artifact"] is None
        assert d["metadata"] == {}

    def test_serialize_handshake_state_none(self):
        """G9: None returns None."""
        from agentic_core.seams.contracts.orchestration_protocols import _serialize_handshake_state

        assert _serialize_handshake_state(None) is None

    def test_serialize_handshake_state_enum_like(self):
        """G9: Object with .value attribute returns .value."""
        from types import SimpleNamespace
        from agentic_core.seams.contracts.orchestration_protocols import _serialize_handshake_state

        obj = SimpleNamespace(value="PENDING")
        assert _serialize_handshake_state(obj) == "PENDING"

    def test_serialize_handshake_state_primitives(self):
        """G9: Primitives pass through unchanged."""
        from agentic_core.seams.contracts.orchestration_protocols import _serialize_handshake_state

        assert _serialize_handshake_state(42) == 42
        assert _serialize_handshake_state("ok") == "ok"
        assert _serialize_handshake_state(True) is True

    def test_serialize_handshake_state_mapping(self):
        """G9: Mapping recurses into values."""
        from agentic_core.seams.contracts.orchestration_protocols import _serialize_handshake_state
        from types import SimpleNamespace

        inner = SimpleNamespace(value="INNER")
        result = _serialize_handshake_state({"k": inner})
        assert result == {"k": "INNER"}

    def test_serialize_handshake_state_list(self):
        """G9: List/tuple/set recurses into elements."""
        from agentic_core.seams.contracts.orchestration_protocols import _serialize_handshake_state

        result = _serialize_handshake_state([1, "two", None])
        assert result == [1, "two", None]


# ---------------------------------------------------------------------------
# G10–G12: SafetyAgentFactory dispatch table
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSafetyAgentFactoryHardening:
    def _factory(self):
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        return SafetyAgentFactory(project_root="/tmp")

    def test_get_empty_name_raises_value_error(self):
        """G10: get('') raises ValueError."""
        with pytest.raises(ValueError, match="agent_name must be non-empty"):
            self._factory().get("")

    def test_get_unknown_agent_returns_none(self):
        """G10: get('BogusAgent') returns None (not in dispatch table)."""
        result = self._factory().get("BogusAgent")
        assert result is None

    def test_get_known_agent_import_failure_returns_none(self):
        """G11: ImportError on a known agent returns None gracefully."""
        from unittest.mock import patch
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        factory = SafetyAgentFactory(project_root="/tmp")
        with patch(
            "agentic_core.seams.contracts.safety_agents.import_module",
            side_effect=ImportError("no L5"),
        ):
            result = factory.get("HygieneGuardianAgent")
        assert result is None

    def test_get_legacy_factory_returns_none_on_import_failure(self):
        """G12: get_legacy_import_healer_factory returns None when import fails."""
        from unittest.mock import patch
        from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

        factory = SafetyAgentFactory(project_root="/tmp")
        with patch(
            "agentic_core.seams.contracts.safety_agents.import_module",
            side_effect=ImportError("no CodeHealerAgent"),
        ):
            result = factory.get_legacy_import_healer_factory()
        assert result is None


# ---------------------------------------------------------------------------
# G13–G20: WorkflowOutcome + WorkflowLearningBridge
# ---------------------------------------------------------------------------


def _make_outcome(**kwargs):
    from agentic_core.seams.workflow_learning_bridge import WorkflowOutcome

    defaults = dict(
        bundle_id="b-001",
        workflow_type="research",
        success=True,
        elapsed_ms=100.0,
        agent_sequence=["AgentA"],
    )
    defaults.update(kwargs)
    return WorkflowOutcome.capture(**defaults)


@pytest.mark.unit
class TestWorkflowOutcomeCapture:
    def test_blank_bundle_id_raises(self):
        """G13: blank bundle_id raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowOutcome

        with pytest.raises(ValueError, match="bundle_id must be non-empty"):
            WorkflowOutcome.capture(
                bundle_id="   ",
                workflow_type="t",
                success=True,
                elapsed_ms=1.0,
                agent_sequence=["A"],
            )

    def test_negative_elapsed_ms_raises(self):
        """G14: negative elapsed_ms raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowOutcome

        with pytest.raises(ValueError, match="elapsed_ms must be >= 0"):
            WorkflowOutcome.capture(
                bundle_id="b",
                workflow_type="t",
                success=True,
                elapsed_ms=-0.001,
                agent_sequence=["A"],
            )

    def test_nan_quality_score_raises(self):
        """G14: NaN quality_score raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowOutcome

        with pytest.raises(ValueError, match="quality_score must be finite"):
            WorkflowOutcome.capture(
                bundle_id="b",
                workflow_type="t",
                success=True,
                elapsed_ms=1.0,
                agent_sequence=["A"],
                quality_score=float("nan"),
            )

    def test_inf_quality_score_raises(self):
        """G14 edge: inf quality_score also raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowOutcome

        with pytest.raises(ValueError, match="quality_score must be finite"):
            WorkflowOutcome.capture(
                bundle_id="b",
                workflow_type="t",
                success=True,
                elapsed_ms=1.0,
                agent_sequence=["A"],
                quality_score=math.inf,
            )

    def test_all_whitespace_agents_raises(self):
        """G15: agent_sequence with only whitespace entries raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowOutcome

        with pytest.raises(ValueError, match="at least one non-empty agent name"):
            WorkflowOutcome.capture(
                bundle_id="b",
                workflow_type="t",
                success=True,
                elapsed_ms=1.0,
                agent_sequence=["  ", "\t"],
            )

    def test_capture_normalizes_whitespace_agents(self):
        """Happy path: leading/trailing whitespace stripped from agents."""
        outcome = _make_outcome(agent_sequence=["  AgentA  ", "AgentB"])
        assert outcome.agent_sequence == ("AgentA", "AgentB")

    def test_capture_happy_path_hash_is_24_chars(self):
        """Happy path: outcome_hash is deterministic 24-char hex."""
        o1 = _make_outcome()
        o2 = _make_outcome()
        assert len(o1.outcome_hash) == 24
        assert o1.outcome_hash == o2.outcome_hash


@pytest.mark.unit
class TestWorkflowLearningBridgeHardening:
    def setup_method(self):
        from agentic_core.seams.workflow_learning_bridge import reset_workflow_learning_bridge

        reset_workflow_learning_bridge()

    def teardown_method(self):
        from agentic_core.seams.workflow_learning_bridge import reset_workflow_learning_bridge

        reset_workflow_learning_bridge()

    def test_zero_ledger_limit_raises(self):
        """G16: ledger_limit=0 raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        with pytest.raises(ValueError, match="ledger_limit must be > 0"):
            WorkflowLearningBridge(ledger_limit=0)

    def test_negative_ledger_limit_raises(self):
        """G16 edge: ledger_limit<0 also raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        with pytest.raises(ValueError, match="ledger_limit must be > 0"):
            WorkflowLearningBridge(ledger_limit=-5)

    def test_duplicate_name_different_callback_raises(self):
        """G17: registering same name with a different callback raises ValueError."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge()
        bridge.register_learner("sl", lambda o: None)
        with pytest.raises(ValueError, match="already registered with a different callback"):
            bridge.register_learner("sl", lambda o: None)

    def test_duplicate_name_same_callback_is_idempotent(self):
        """Happy path: re-registering same name+same callback object is allowed."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge()
        cb = lambda o: None
        bridge.register_learner("sl", cb)
        bridge.register_learner("sl", cb)
        assert bridge.has_learner("sl")

    def test_contribute_isolates_failing_learner(self):
        """G18: a crashing learner does not prevent other learners from receiving the outcome."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge()
        received = []

        def bad(o):
            raise RuntimeError("simulated crash")

        def good(o):
            received.append(o.bundle_id)

        bridge.register_learner("bad", bad)
        bridge.register_learner("good", good)
        outcome = _make_outcome(bundle_id="b-isolate")
        bridge.contribute(outcome)
        assert "b-isolate" in received

    def test_has_learner_before_and_after_register(self):
        """G19: has_learner returns False before, True after register."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge()
        assert bridge.has_learner("sl") is False
        bridge.register_learner("sl", lambda o: None)
        assert bridge.has_learner("sl") is True

    def test_reset_clears_singleton(self):
        """G20: reset_workflow_learning_bridge forces new instance on next get()."""
        from agentic_core.seams.workflow_learning_bridge import (
            get_workflow_learning_bridge,
            reset_workflow_learning_bridge,
        )

        b1 = get_workflow_learning_bridge()
        b1.register_learner("marker", lambda o: None)
        reset_workflow_learning_bridge()
        b2 = get_workflow_learning_bridge()
        assert b2 is not b1
        assert not b2.has_learner("marker")

    def test_ledger_bounded_by_limit(self):
        """Edge: entries beyond ledger_limit evict oldest (deque maxlen)."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge(ledger_limit=3)
        for i in range(5):
            bridge.contribute(_make_outcome(bundle_id=f"b-{i:03d}"))
        ledger = bridge.ledger()
        assert len(ledger) == 3
        assert ledger[0].bundle_id == "b-002"
        assert ledger[-1].bundle_id == "b-004"

    def test_success_rate_reflects_contributions(self):
        """Happy path: success_rate computed correctly."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge()
        bridge.contribute(_make_outcome(bundle_id="b-ok", success=True))
        bridge.contribute(_make_outcome(bundle_id="b-fail", success=False))
        assert bridge.success_rate() == pytest.approx(0.5)

    def test_empty_bridge_callbacks(self):
        """Edge: contribute on bridge with no learners does not raise."""
        from agentic_core.seams.workflow_learning_bridge import WorkflowLearningBridge

        bridge = WorkflowLearningBridge()
        bridge.contribute(_make_outcome())
        assert bridge.success_rate() == 1.0
