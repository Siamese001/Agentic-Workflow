"""Tests for per-layer GateContext builders."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.ctx_builders import (
    build_c0_ctx,
    build_exit_ctx,
    build_l0_ctx,
    build_l1_ctx,
    build_l2_ctx,
    build_l3_ctx,
    build_l4_ctx,
    build_l6_ctx,
    build_prompt_ctx,
    build_u0_ctx,
    build_uwg_ctx,
    merge_ctx,
)
from agentic_core.L5_safety.runtime_gates.dispatch import LAYER_U0, run_layer
from agentic_core.L5_safety.runtime_gates.contracts import GateContext


def test_build_u0_ctx_runs_layer_clean() -> None:
    ctx = build_u0_ctx(
        request_id="r-1",
        session_id="s-1",
        trace_root="t-1",
        tenant_id="tenant-A",
        intent={"objective": "x", "raw_text": "x", "payload_bytes": 100},
        caller_scope_baseline={"tenant_id": "tenant-A", "session_id": "s-1"},
    )
    result = run_layer(LAYER_U0, ctx)
    assert result.passed


def test_build_u0_ctx_propagates_identity() -> None:
    ctx = build_u0_ctx(
        request_id="r",
        session_id="s",
        trace_root="t",
        tenant_id="tenant-A",
        policy_hash="pol-1",
    )
    assert ctx.tenant_id == "tenant-A"
    assert ctx.policy_hash == "pol-1"


def test_build_l1_ctx() -> None:
    ctx = build_l1_ctx(intent={"objective": "summarize"})
    assert ctx.intent == {"objective": "summarize"}


def test_build_l0_ctx_full() -> None:
    ctx = build_l0_ctx(
        intent={"objective": "x"},
        route_contract={"route_id": "R3"},
        hitl={"review_requested": True, "verdict": "approve"},
        risk_tier="low",
        impact_class="read",
        policy_hash="pol-1",
    )
    assert ctx.route_contract["route_id"] == "R3"
    assert ctx.risk_tier == "low"
    assert ctx.policy_hash == "pol-1"


def test_build_c0_ctx() -> None:
    ctx = build_c0_ctx(
        retrieval_plan={"required": False},
        evidence={"source_ids": ["doc-1"]},
    )
    assert ctx.retrieval_plan["required"] is False
    assert ctx.evidence["source_ids"] == ["doc-1"]


def test_build_prompt_ctx() -> None:
    ctx = build_prompt_ctx(prompt_packet={"slot_order": ["S0", "U0"]})
    assert ctx.prompt_packet["slot_order"] == ["S0", "U0"]


def test_build_l2_ctx_merges_sandbox_and_capability() -> None:
    ctx = build_l2_ctx(
        tool_call={"tool_name": "x"},
        sandbox={"isolated": True},
        capability={"approved": True},
    )
    assert ctx.tool_call["tool_name"] == "x"
    assert ctx.tool_call["sandbox"] == {"isolated": True}
    assert ctx.tool_call["capability"] == {"approved": True}


def test_build_l4_ctx() -> None:
    ctx = build_l4_ctx(memory_op={"is_proposed_mutation": False})
    assert ctx.memory_op["is_proposed_mutation"] is False


def test_build_l3_ctx() -> None:
    ctx = build_l3_ctx(
        workflow_state={"attempt_count": 1},
        budget={"used_tokens": 100, "max_tokens": 1000},
    )
    assert ctx.workflow_state["attempt_count"] == 1
    assert ctx.budget["max_tokens"] == 1000


def test_build_exit_ctx() -> None:
    ctx = build_exit_ctx(
        output={"text": "x", "schema_valid": True},
        trace_artifacts={"replay_key": "rk-1"},
    )
    assert ctx.output["schema_valid"] is True
    assert ctx.trace_artifacts["replay_key"] == "rk-1"


def test_build_uwg_ctx() -> None:
    ctx = build_uwg_ctx(
        memory_op={"is_proposed_mutation": True, "caller_layer": "Exit"},
        compliance_hash="c-1",
        policy_hash="p-1",
    )
    assert ctx.compliance_hash == "c-1"
    assert ctx.memory_op["caller_layer"] == "Exit"


def test_build_l6_ctx() -> None:
    ctx = build_l6_ctx(
        baseline={"tokens": 1000},
        observed={"tokens": 1100},
        learning_signal={"run_status": "in_progress"},
    )
    assert ctx.baseline["tokens"] == 1000
    assert ctx.learning_signal["run_status"] == "in_progress"


# ---- merge_ctx ----


def test_merge_ctx_empty_returns_default() -> None:
    ctx = merge_ctx()
    assert isinstance(ctx, GateContext)
    assert ctx.request_id == ""


def test_merge_ctx_single_returns_same() -> None:
    a = build_u0_ctx(request_id="r-1", session_id="s-1", trace_root="t-1")
    assert merge_ctx(a) is a


def test_merge_ctx_combines_dicts() -> None:
    a = build_l1_ctx(intent={"objective": "x"})
    b = build_l0_ctx(intent={"raw_text": "y"})
    merged = merge_ctx(a, b)
    assert merged.intent == {"objective": "x", "raw_text": "y"}


def test_merge_ctx_later_overrides_dict_keys() -> None:
    a = build_l1_ctx(intent={"objective": "first"})
    b = build_l1_ctx(intent={"objective": "second"})
    merged = merge_ctx(a, b)
    assert merged.intent["objective"] == "second"


def test_merge_ctx_concatenates_lists() -> None:
    a = GateContext()
    a.caller_scope_baseline = {"x": 1}
    b = GateContext()
    b.caller_scope_baseline = {"y": 2}
    merged = merge_ctx(a, b)
    assert merged.caller_scope_baseline == {"x": 1, "y": 2}


def test_merge_ctx_preserves_scalar_fields() -> None:
    a = build_u0_ctx(request_id="r-1", session_id="s-1", trace_root="t-1", tenant_id="T1")
    b = build_l0_ctx(policy_hash="pol-1")
    merged = merge_ctx(a, b)
    assert merged.request_id == "r-1"
    assert merged.tenant_id == "T1"
    assert merged.policy_hash == "pol-1"
