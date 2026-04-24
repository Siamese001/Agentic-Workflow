"""Tests for W4 e2_agent_gate decorator (plan c8e4f1)."""
from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.e2_agent_gate import (
    AgentGateConfirmRequired,
    AgentGateRejected,
    e2_agent_gate,
    extract_contract,
)
from agentic_core.L2_execution.types.execution_tool_contract import (
    ToolCategory,
    ToolContract,
)
from agentic_core.L2_execution.types import l2_safety_contracts as _l2sc
from agentic_core.L2_execution.types.l2_safety_contracts import (
    ConsequenceLevel,
    Reversibility,
    SafetyProfile,
    SideEffectClass,
    register_safety_profile,
)


@pytest.fixture(autouse=True)
def _reset_registry():
    # Inline reset — module exposes _profile_registry (dict) for tests.
    _l2sc._profile_registry.clear()
    yield
    _l2sc._profile_registry.clear()


def _make_contract(tool_name: str, metadata: dict | None = None) -> ToolContract:
    return ToolContract.create(
        tool_name=tool_name,
        category=ToolCategory.CODE_EXECUTION,
        args={"x": 1},
        trace_id="trace-abc",
        metadata=metadata or {},
    )


class _SampleAgent:
    """Stand-in agent used to exercise the decorator."""

    @e2_agent_gate
    def do_work(self, payload: dict, *, tool_contract: ToolContract | None = None, **_kw) -> dict:
        return {"status": "ok", "payload": payload}


class TestExtractContract:
    def test_from_kwarg_tool_contract(self):
        c = _make_contract("t.a")
        found = extract_contract((), {"tool_contract": c})
        assert found is c

    def test_from_kwarg_contract(self):
        c = _make_contract("t.b")
        found = extract_contract((), {"contract": c})
        assert found is c

    def test_from_kwarg_e2_contract(self):
        c = _make_contract("t.c")
        found = extract_contract((), {"e2_contract": c})
        assert found is c

    def test_from_positional(self):
        c = _make_contract("t.d")
        found = extract_contract((c, "other"), {})
        assert found is c

    def test_no_contract_returns_none(self):
        assert extract_contract(("nope", 42), {"foo": "bar"}) is None


class TestGateFallThrough:
    def test_no_contract_means_native_behavior(self):
        agent = _SampleAgent()
        out = agent.do_work({"k": "v"})
        assert out == {"status": "ok", "payload": {"k": "v"}}


class TestGateApproved:
    def test_benign_tool_approved(self):
        # Default profile is auto-approve (MINOR/READ_ONLY/REVERSIBLE)
        register_safety_profile(
            SafetyProfile(
                tool_name="t.benign",
                side_effect=SideEffectClass.READ,
                reversibility=Reversibility.REVERSIBLE,
                consequence=ConsequenceLevel.NEGLIGIBLE,
            )
        )
        agent = _SampleAgent()
        contract = _make_contract("t.benign")
        out = agent.do_work({"k": "v"}, tool_contract=contract)
        assert out["status"] == "ok"


class TestGateConfirmRequired:
    def test_critical_mutation_without_approval_raises_confirm(self):
        register_safety_profile(
            SafetyProfile(
                tool_name="t.mutate_critical",
                side_effect=SideEffectClass.MUTATE_STATE,
                reversibility=Reversibility.IRREVERSIBLE,
                consequence=ConsequenceLevel.CRITICAL,
            )
        )
        agent = _SampleAgent()
        contract = _make_contract("t.mutate_critical")
        with pytest.raises(AgentGateConfirmRequired) as excinfo:
            agent.do_work({"k": "v"}, tool_contract=contract)
        assert excinfo.value.agent == "_SampleAgent"
        assert excinfo.value.method == "do_work"
        assert excinfo.value.verdict.decision == "confirm_required"

    def test_approval_ticket_bypasses_confirm(self):
        register_safety_profile(
            SafetyProfile(
                tool_name="t.mutate_critical2",
                side_effect=SideEffectClass.MUTATE_STATE,
                reversibility=Reversibility.IRREVERSIBLE,
                consequence=ConsequenceLevel.CRITICAL,
            )
        )
        agent = _SampleAgent()
        contract = _make_contract(
            "t.mutate_critical2",
            metadata={"e2_hitl_approval_ticket": "ticket-xyz"},
        )
        out = agent.do_work({"k": "v"}, tool_contract=contract)
        assert out["status"] == "ok"


class TestGateHardReject:
    def test_hard_reject_raises_rejected(self):
        register_safety_profile(
            SafetyProfile(
                tool_name="t.forbidden",
                side_effect=SideEffectClass.MUTATE_STATE,
                reversibility=Reversibility.IRREVERSIBLE,
                consequence=ConsequenceLevel.CRITICAL,
            )
        )
        agent = _SampleAgent()
        contract = _make_contract(
            "t.forbidden",
            metadata={"policy_forbid_irreversible_critical": True},
        )
        with pytest.raises(AgentGateRejected) as excinfo:
            agent.do_work({"k": "v"}, tool_contract=contract)
        assert excinfo.value.agent == "_SampleAgent"
        assert excinfo.value.method == "do_work"
        assert excinfo.value.verdict.decision == "rejected"


class TestGateVerdictBreadcrumb:
    def test_approved_path_injects_verdict_breadcrumb(self):
        register_safety_profile(
            SafetyProfile(
                tool_name="t.benign2",
                side_effect=SideEffectClass.READ,
                reversibility=Reversibility.REVERSIBLE,
                consequence=ConsequenceLevel.NEGLIGIBLE,
            )
        )

        captured: dict = {}

        class _InspectAgent:
            @e2_agent_gate
            def do(self, *, tool_contract: ToolContract, **kwargs) -> dict:
                captured.update(kwargs)
                return {"ok": True}

        contract = _make_contract("t.benign2")
        _InspectAgent().do(tool_contract=contract)
        assert "_e2_verdict" in captured
        assert captured["_e2_verdict"]["decision"] == "approved"
