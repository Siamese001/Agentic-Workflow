"""Unit tests for W1 of the L2 best-practices gap plan (b7c4e2).

Covers:
- SafetyProfile default-safe lookup
- requires_e2_confirmation truth table
- ToolGuardrailPipeline pre/post + tripwire
- evaluate_work_order: approved / confirm_required / rejected
- HITL approval ticket re-entry path
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.e2_validate_before_execute import (
    ConfirmBeforeExecute,
    E2RejectedBeforeExecute,
    evaluate_work_order,
)
from agentic_core.L2_execution.enforcement.tool_guardrail_pipeline import (
    GuardrailOutput,
    GuardrailPhase,
    ToolGuardrailPipeline,
    TripwireTriggered,
)
from agentic_core.L2_execution.types.execution_tool_contract import (
    ToolCategory,
    ToolContract,
)
from agentic_core.L2_execution.types.l2_safety_contracts import (
    DEFAULT_SAFE_PROFILE,
    ConsequenceLevel,
    Reversibility,
    SafetyProfile,
    SideEffectClass,
    get_safety_profile,
    register_safety_profile,
)


def _contract(name: str = "read.get", meta: dict | None = None) -> ToolContract:
    return ToolContract.create(
        tool_name=name,
        category=ToolCategory.MEMORY_READ,
        args={"k": "v"},
        trace_id="t-1",
        metadata=meta or {},
    )


class TestSafetyProfileRegistry:
    def test_default_when_unregistered(self) -> None:
        prof = get_safety_profile("never.registered.tool")
        assert prof is DEFAULT_SAFE_PROFILE
        assert prof.side_effect is SideEffectClass.READ
        assert prof.requires_e2_confirmation() is False

    def test_register_and_lookup(self) -> None:
        p = SafetyProfile(
            tool_name="ledger.commit",
            side_effect=SideEffectClass.MUTATE_STATE,
            reversibility=Reversibility.IRREVERSIBLE,
            consequence=ConsequenceLevel.HIGH,
        )
        register_safety_profile(p)
        got = get_safety_profile("ledger.commit")
        assert got is p
        assert got.requires_e2_confirmation() is True

    @pytest.mark.parametrize(
        "consequence,side_effect,reversibility,expected",
        [
            (ConsequenceLevel.NEGLIGIBLE, SideEffectClass.READ, Reversibility.REVERSIBLE, False),
            (ConsequenceLevel.LOW, SideEffectClass.WRITE, Reversibility.COMPENSABLE, False),
            (ConsequenceLevel.HIGH, SideEffectClass.WRITE, Reversibility.COMPENSABLE, True),
            (ConsequenceLevel.CRITICAL, SideEffectClass.READ, Reversibility.REVERSIBLE, True),
            (ConsequenceLevel.LOW, SideEffectClass.ACTION, Reversibility.IRREVERSIBLE, True),
            (ConsequenceLevel.LOW, SideEffectClass.READ, Reversibility.IRREVERSIBLE, False),
        ],
    )
    def test_requires_confirmation_truth_table(
        self,
        consequence: ConsequenceLevel,
        side_effect: SideEffectClass,
        reversibility: Reversibility,
        expected: bool,
    ) -> None:
        p = SafetyProfile(
            tool_name=f"t.{consequence.value}.{side_effect.value}.{reversibility.value}",
            side_effect=side_effect,
            reversibility=reversibility,
            consequence=consequence,
        )
        assert p.requires_e2_confirmation() is expected


class TestGuardrailPipeline:
    def test_pre_allows_pass_through(self) -> None:
        pipe = ToolGuardrailPipeline()
        pipe.add_inline(
            "noop-pre",
            GuardrailPhase.PRE_EXECUTE,
            lambda p: GuardrailOutput("noop-pre", GuardrailPhase.PRE_EXECUTE),
        )
        assert pipe.run_pre({"x": 1}) == {"x": 1}

    def test_pre_tripwire_halts(self) -> None:
        pipe = ToolGuardrailPipeline()
        pipe.add_inline(
            "block-all",
            GuardrailPhase.PRE_EXECUTE,
            lambda p: GuardrailOutput(
                "block-all", GuardrailPhase.PRE_EXECUTE, tripwire_triggered=True, reason="deny"
            ),
        )
        with pytest.raises(TripwireTriggered) as exc:
            pipe.run_pre({})
        assert exc.value.output.reason == "deny"

    def test_replacement_payload_flows(self) -> None:
        pipe = ToolGuardrailPipeline()
        pipe.add_inline(
            "redact",
            GuardrailPhase.PRE_EXECUTE,
            lambda p: GuardrailOutput("redact", GuardrailPhase.PRE_EXECUTE, replacement={"x": "[REDACTED]"}),
        )
        assert pipe.run_pre({"x": "secret"}) == {"x": "[REDACTED]"}

    def test_run_all_happy_path(self) -> None:
        pipe = ToolGuardrailPipeline()
        out = pipe.run_all({"a": 1}, execute=lambda p: {"a": p["a"] + 1})
        assert out == {"a": 2}

    def test_run_all_post_tripwire(self) -> None:
        pipe = ToolGuardrailPipeline()
        pipe.add_inline(
            "forbid-neg",
            GuardrailPhase.POST_EXECUTE,
            lambda r: GuardrailOutput(
                "forbid-neg",
                GuardrailPhase.POST_EXECUTE,
                tripwire_triggered=r.get("v", 0) < 0,
                reason="negative result",
            ),
        )
        with pytest.raises(TripwireTriggered):
            pipe.run_all({"v": 1}, execute=lambda p: {"v": -1})


class TestEvaluateWorkOrder:
    def test_approved_for_default_safe(self) -> None:
        v = evaluate_work_order(_contract("tool.safe.read"))
        assert v.decision == "approved"

    def test_confirm_required_for_high_consequence(self) -> None:
        register_safety_profile(
            SafetyProfile(
                tool_name="orders.submit",
                side_effect=SideEffectClass.ACTION,
                reversibility=Reversibility.COMPENSABLE,
                consequence=ConsequenceLevel.HIGH,
            )
        )
        with pytest.raises(ConfirmBeforeExecute) as exc:
            evaluate_work_order(_contract("orders.submit"))
        assert exc.value.verdict.decision == "confirm_required"

    def test_approved_with_hitl_ticket(self) -> None:
        register_safety_profile(
            SafetyProfile(
                tool_name="orders.submit.approved",
                side_effect=SideEffectClass.ACTION,
                reversibility=Reversibility.COMPENSABLE,
                consequence=ConsequenceLevel.HIGH,
            )
        )
        v = evaluate_work_order(
            _contract(
                "orders.submit.approved",
                meta={"e2_hitl_approval_ticket": "ticket-123"},
            )
        )
        assert v.decision == "approved"
        assert v.evidence["approval_ticket_present"] is True

    def test_policy_hard_rejection(self) -> None:
        register_safety_profile(
            SafetyProfile(
                tool_name="ledger.wipe",
                side_effect=SideEffectClass.MUTATE_STATE,
                reversibility=Reversibility.IRREVERSIBLE,
                consequence=ConsequenceLevel.CRITICAL,
            )
        )
        with pytest.raises(E2RejectedBeforeExecute):
            evaluate_work_order(
                _contract(
                    "ledger.wipe",
                    meta={"policy_forbid_irreversible_critical": True},
                )
            )
