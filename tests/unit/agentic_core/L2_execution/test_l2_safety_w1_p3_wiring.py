"""W1-P1.3 wiring tests for the L2 best-practices gap plan (b7c4e2).

Covers:
- ``L2ExecutionAgent.run_l2_phases`` E2 short-circuit when a ToolContract
  with a high-consequence SafetyProfile is attached.
- Approved path when HITL approval ticket is present.
- Default (no tool_contract) path is unchanged.
- ``CallInterceptor.intercept`` E2 short-circuit surfacing
  ``needs_hitl_confirmation`` and ``e2_verdict``.
"""

from __future__ import annotations

from agentic_core.L2_execution.capability.call_interceptor import CallInterceptor
from agentic_core.L2_execution.types.execution_tool_contract import (
    ToolCategory,
    ToolContract,
)
from agentic_core.L2_execution.types.l2_execution_contract import (
    L2ExecutionAgent,
    L2ExecutionContext,
    L2ExecutionPhase,
    L2PhaseResult,
)
from agentic_core.L2_execution.types.l2_safety_contracts import (
    ConsequenceLevel,
    Reversibility,
    SafetyProfile,
    SideEffectClass,
    register_safety_profile,
)


class _StubExecAgent(L2ExecutionAgent):
    """Minimal L2ExecutionAgent that records which phases ran."""

    def __init__(self) -> None:
        super().__init__(agent_id="stub")
        self.executed = False

    def l2_init(self, context: L2ExecutionContext) -> L2PhaseResult:
        return L2PhaseResult(phase=L2ExecutionPhase.INIT, success=True, output={})

    def l2_execute(self, context: L2ExecutionContext) -> L2PhaseResult:
        self.executed = True
        return L2PhaseResult(phase=L2ExecutionPhase.EXECUTE, success=True, output={"done": True})

    def l2_synthesize(self, context: L2ExecutionContext) -> L2PhaseResult:
        return L2PhaseResult(phase=L2ExecutionPhase.SYNTHESIZE, success=True, output={})


def _high_consequence_contract(meta: dict | None = None) -> ToolContract:
    register_safety_profile(
        SafetyProfile(
            tool_name="wire.high.consequence",
            side_effect=SideEffectClass.ACTION,
            reversibility=Reversibility.COMPENSABLE,
            consequence=ConsequenceLevel.HIGH,
        )
    )
    return ToolContract.create(
        tool_name="wire.high.consequence",
        category=ToolCategory.EXTERNAL_API,
        args={"operation": "send"},
        trace_id="wire-t1",
        metadata=meta or {},
    )


class TestRunL2PhasesE2Gate:
    def test_default_path_unchanged_without_tool_contract(self) -> None:
        agent = _StubExecAgent()
        result = agent.run_l2_phases(inputs={"operation": "noop"})
        assert result["success"] is True
        assert agent.executed is True
        assert "INIT" in result["phases_completed"]
        assert "EXECUTE" in result["phases_completed"]

    def test_short_circuits_on_high_consequence(self) -> None:
        agent = _StubExecAgent()
        contract = _high_consequence_contract()
        result = agent.run_l2_phases(inputs={"tool_contract": contract})
        assert result["success"] is False
        assert result["interrupted_at"] == "INIT"
        assert agent.executed is False  # E3 never reached

    def test_approved_path_with_hitl_ticket(self) -> None:
        agent = _StubExecAgent()
        contract = _high_consequence_contract(meta={"e2_hitl_approval_ticket": "approved-1"})
        result = agent.run_l2_phases(inputs={"tool_contract": contract})
        assert result["success"] is True
        assert agent.executed is True

    def test_non_toolcontract_in_inputs_is_ignored(self) -> None:
        agent = _StubExecAgent()
        result = agent.run_l2_phases(inputs={"tool_contract": "not-a-contract"})
        # The gate must be a no-op for non-ToolContract objects; execution
        # proceeds normally.
        assert result["success"] is True
        assert agent.executed is True


class TestCallInterceptorE2Gate:
    def test_allows_safe_call_without_tool_contract(self) -> None:
        ci = CallInterceptor()
        r = ci.intercept(
            target="read.sample",
            args={"operation": "read"},
            context={},
        )
        assert r.is_allowed is True
        assert r.needs_hitl_confirmation is False
        assert r.e2_verdict is None

    def test_short_circuits_on_high_consequence(self) -> None:
        ci = CallInterceptor()
        contract = _high_consequence_contract()
        r = ci.intercept(
            target="wire.high.consequence",
            args={"operation": "send"},
            context={"tool_contract": contract},
        )
        assert r.is_allowed is False
        assert r.needs_hitl_confirmation is True
        assert r.rejection_reason == "e2_hitl_required"
        assert r.e2_verdict is not None
        assert r.e2_verdict["decision"] == "confirm_required"

    def test_allows_with_hitl_ticket(self) -> None:
        ci = CallInterceptor()
        contract = _high_consequence_contract(meta={"e2_hitl_approval_ticket": "ticket-xyz"})
        r = ci.intercept(
            target="wire.high.consequence",
            args={"operation": "send"},
            context={"tool_contract": contract},
        )
        assert r.is_allowed is True
        assert r.needs_hitl_confirmation is False
