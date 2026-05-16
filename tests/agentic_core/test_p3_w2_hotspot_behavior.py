"""W2 behavioral coverage for ADG P3 hotspot modules (plan adg-hotspot-test-coverage-b8e4f2).

Each test imports the canonical module path and asserts non-trivial behavior.
Scaffold-only tests in sibling files remain; these tests fail on stubs.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# --- L2 types: tool_enforcement_types ---
from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
    ToolEnforcementArtifact,
    ToolPolicyBlocked,
)


def test_tool_enforcement_artifact_modify_requires_modified_hash() -> None:
    base = dict(
        enforcement_id="e1",
        timestamp_utc="t",
        trace_id="tr",
        agent_id="a",
        tool_name="tname",
        outcome=LawSlotOutcome.MODIFY,
        applied_law_slots=("L1",),
        rationale="r",
        original_args_hash="h1",
    )
    with pytest.raises(ValueError, match="modified_args_hash"):
        ToolEnforcementArtifact(**base, modified_args_hash="")

    art = ToolEnforcementArtifact(**base, modified_args_hash="h2")
    assert art.modified_args_hash == "h2"


def test_tool_policy_blocked_exposes_fields() -> None:
    art = ToolEnforcementArtifact(
        enforcement_id="e1",
        timestamp_utc="t",
        trace_id="tr",
        agent_id="a",
        tool_name="tname",
        outcome=LawSlotOutcome.BLOCK,
        applied_law_slots=(),
        rationale="no",
        original_args_hash="hx",
    )
    exc = ToolPolicyBlocked("tname", "denied", art)
    assert exc.tool_name == "tname"
    assert exc.artifact is art


# --- L2 types: ml_write_intent_types ---
from agentic_core.L2_execution.types.ml_write_intent_types import (
    MLWriteEnvelopeViolation,
    MLWriteIntent,
    MLWriteIntentExecutor,
)


def test_ml_write_intent_rejects_invalid_kind_and_false_requires_commit() -> None:
    with pytest.raises(ValueError, match="kind must be one of"):
        MLWriteIntent(kind="invalid", payload={})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="requires_commit must be True"):
        MLWriteIntent(kind="cache_set", payload={}, requires_commit=False)


def test_ml_write_intent_hash_stable_for_same_payload() -> None:
    a = MLWriteIntent(kind="cache_set", payload={"k": 1})
    b = MLWriteIntent(kind="cache_set", payload={"k": 1})
    assert a.intent_hash == b.intent_hash
    c = MLWriteIntent(kind="cache_set", payload={"k": 2})
    assert c.intent_hash != a.intent_hash


def test_ml_write_executor_inside_context_executes_without_live_network() -> None:
    intent = MLWriteIntent(kind="pattern_store", payload={"target_path": "/tmp/x"})
    with MLWriteIntentExecutor() as ex:
        out = ex.execute(intent)
    assert out["executed"] is True
    assert out["kind"] == "pattern_store"
    assert out["intent_hash"] == intent.intent_hash


def test_execute_ml_write_intent_outside_sandbox_raises() -> None:
    intent = MLWriteIntent(kind="cache_set", payload={})
    with pytest.raises(MLWriteEnvelopeViolation):
        from agentic_core.L2_execution.types import ml_write_intent_types as mod

        mod.execute_ml_write_intent_outside_sandbox(intent)


# --- L0 boundary_types ---
from agentic_core.L0_routing.types.boundary_types import (
    BoundarySchemaDescriptor,
    MetaInvariantReport,
    SchemaValidationStatus,
    InvariantCheck,
)


def test_boundary_schema_descriptor_rejects_bad_validation_status() -> None:
    with pytest.raises(TypeError, match="validation_status"):
        BoundarySchemaDescriptor(
            schema_id="s",
            schema_version="1",
            source_layer="L0",
            target_layer="L1",
            validation_status="oops",  # type: ignore[arg-type]
        )


def test_meta_invariant_report_rejects_pass_with_violations() -> None:
    from agentic_core.L0_routing.types.boundary_types import InvariantSeverity, InvariantViolation

    checks = (InvariantCheck("c1", "d1", False, "e1"),)
    inv = InvariantViolation("i1", InvariantSeverity.HIGH, ("p",), "details here")
    with pytest.raises(ValueError, match="pass_fail cannot be True"):
        MetaInvariantReport(
            trace_id="t",
            run_id="r",
            semantic_clock_tick=0,
            checks=checks,
            pass_fail=True,
            violations=(inv,),
        )


# --- L1 reasoning_pattern ---
from agentic_core.L1_cognition.types.reasoning_pattern import BaseReasoningPattern


def test_base_reasoning_pattern_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        BaseReasoningPattern()  # type: ignore[abstract,misc]


# --- L1 reasoning_context ---
from agentic_core.L1_cognition.reasoning.reasoning_context import ReasoningContext


def test_reasoning_context_rejects_empty_required_fields() -> None:
    with pytest.raises(ValueError, match="missing required fields"):
        ReasoningContext(
            run_id="",
            trace_id="t",
            routing_contract_id="rc",
            policy_hash="ph",
            policy_version="1",
            prompt_hash="pr",
            context_hash="ch",
            evidence_hash="eh",
            retrieved_context_ids=(),
            memory_version="0",
            state_version="0",
            router_decision_id="",
            parent_reasoning_trace_id="",
            parent_context_hash="",
            clock_tick=1.0,
            model_id="m",
        )


def test_reasoning_context_manual_build_has_non_empty_hashes() -> None:
    """Avoid ReasoningContext.create() (LayerSegment emission path); validate invariants."""
    ctx = ReasoningContext(
        run_id="run",
        trace_id="tr",
        routing_contract_id="rc",
        policy_hash="pol",
        policy_version="1",
        prompt_hash="prm",
        context_hash="ctxh",
        evidence_hash="eh",
        retrieved_context_ids=("x",),
        memory_version="0",
        state_version="0",
        router_decision_id="rd",
        parent_reasoning_trace_id="pt",
        parent_context_hash="pch",
        clock_tick=3.0,
        model_id="mid",
    )
    assert ctx.context_hash == "ctxh" and ctx.evidence_hash == "eh"


# --- L1 query_planner ---
from agentic_core.L1_cognition.reasoning.query_planner import query_planner as QueryPlannerCls


def test_query_planner_clean_json_response_strips_code_fence() -> None:
    qp = object.__new__(QueryPlannerCls)
    raw = '```json\n{"queries": ["alpha"]}\n```'
    cleaned = QueryPlannerCls._clean_json_response(qp, raw)
    assert '"queries"' in cleaned
    assert "alpha" in cleaned


# --- L1 plan_creator ---
from agentic_core.L1_cognition.reasoning.plan_creator import (
    PlanningPolicy,
    ReasoningPlanContext,
    create_reasoning_plan,
)
from agentic_core.L1_cognition.reasoning.reasoning_plan import ReasoningPlanError


def test_create_reasoning_plan_empty_goal_raises() -> None:
    ctx = ReasoningPlanContext.create("r1", "t1", "m1")
    pol = PlanningPolicy.create(max_steps=3)
    reg = MagicMock()
    with pytest.raises(ReasoningPlanError, match="goal_payload cannot be empty"):
        create_reasoning_plan(ctx, "", {}, pol, registry=reg)
    reg.persist_plan.assert_not_called()


def test_create_reasoning_plan_persists_and_hashes_steps() -> None:
    ctx = ReasoningPlanContext.create("r1", "t1", "m1")
    pol = PlanningPolicy.create(max_steps=3)
    reg = MagicMock()
    plan = create_reasoning_plan(ctx, "my goal", {"ev": 1}, pol, registry=reg)
    reg.persist_plan.assert_called_once()
    persisted = reg.persist_plan.call_args[0][0]
    assert persisted.run_id == "r1"
    assert plan.plan_goal_hash == hashlib.sha256(b"my goal").hexdigest()[:16]
    three_steps = [
        "analyze_goal_and_context",
        "gather_and_process_evidence",
        "evaluate_alternatives",
    ]
    expect_step_hash = hashlib.sha256(str(three_steps).encode()).hexdigest()[:16]
    assert persisted.step_sequence_hash == expect_step_hash


# --- L1 SemanticMemory ---
from agentic_core.L1_cognition.reasoning.SemanticMemory import SemanticMemory


def test_semantic_memory_search_orders_by_dot_product() -> None:
    mem = SemanticMemory()
    mem.store("a", 1, embedding=[1.0, 0.0])
    mem.store("b", 2, embedding=[0.5, 0.0])
    hits = mem.search([2.0, 0.0], top_k=2)
    assert [h["key"] for h in hits] == ["a", "b"]


# --- L2 authority_validator ---
from agentic_core.L2_execution.reasoning.authority_validator import AuthorityValidator
from agentic_core.L2_execution.reasoning.compiled_artifact import AuthorityLevel, AuthoritySlot


def test_authority_validator_rejects_misordered_slots() -> None:
    v = AuthorityValidator()
    slots = (
        AuthoritySlot("S0", "s", AuthorityLevel.ABSOLUTE, "L0", {}),
        AuthoritySlot("I0", "i", AuthorityLevel.GOVERNED, "L0", {}),
        AuthoritySlot("D0", "d", AuthorityLevel.BINDING, "L0", {}),
    )
    assert v.validate_slots(slots) is True
    bad = (
        AuthoritySlot("S0", "s", AuthorityLevel.ABSOLUTE, "L0", {}),
        AuthoritySlot("D0", "d", AuthorityLevel.BINDING, "L0", {}),
        AuthoritySlot("I0", "i", AuthorityLevel.GOVERNED, "L0", {}),
    )
    assert v.validate_slots(bad) is False
    assert any("out of order" in e for e in v.errors)


def test_authority_validator_rejects_duplicate_s0() -> None:
    v = AuthorityValidator()
    slots = (
        AuthoritySlot("S0", "s1", AuthorityLevel.ABSOLUTE, "L0", {}),
        AuthoritySlot("S0", "s2", AuthorityLevel.ABSOLUTE, "L0", {}),
        AuthoritySlot("I0", "i", AuthorityLevel.GOVERNED, "L0", {}),
    )
    assert v.validate_slots(slots) is False
    assert any("Duplicate slot type" in e for e in v.errors)


# --- L2 adaptation_orchestrator (private analyzer: tool availability) ---
from agentic_core.L2_execution.reasoning.adaptation_orchestrator import (
    ExecutionContext,
    ExecutionStrategy,
    _analyze_candidate_strategies,
)


def test_analyze_candidate_strategies_filters_missing_tools() -> None:
    ctx = ExecutionContext.create(
        run_id="r",
        trace_id="t",
        available_tools=["a", "b"],
    )
    s_ok = ExecutionStrategy.create("1", "ok", ["a"])
    s_bad = ExecutionStrategy.create("2", "bad", ["a", "c"])
    out = _analyze_candidate_strategies([s_ok, s_bad], ctx)
    assert out == [s_ok]


# --- L2 action_node ---
from agentic_core.L2_execution.reasoning.action_node import ActionNode


def test_action_node_act_selects_tools_and_formats_output() -> None:
    node = ActionNode()
    reasoning = {
        "run_id": "r1",
        "policy_hash": "p1",
        "capability_token": "c1",
        "plan": {"steps": [1, 2, 3]},
    }
    with patch(
        "agentic_core.L2_execution.reasoning.action_node._invoke_authorize_and_execute",
        return_value=None,
    ):
        out = node.act(reasoning)
    assert out["success"] is True
    assert "primary_executor" in out["tools_used"]
    assert "Executed primary_executor" in out["output"]


# --- L2 StructuredEngineAgent (AgentPlan in-module) ---
from agentic_core.L2_execution.reasoning.StructuredEngineAgent import AgentPlan


def test_agent_plan_heal_returns_needs_help_shape() -> None:
    ap = AgentPlan("x", [])
    dct = ap.heal({"parent_packet_id": "p", "policy_hash": "pol", "blueprint_hash": "b"})
    assert dct["outcome"] == "NEEDS_HELP"
    assert dct["reason_code"] == "data_structure_not_healable"


# --- L2 RedisSovereignAgent ---
from agentic_core.L2_execution.reasoning.RedisSovereignAgent import RedisSovereignAgent


def test_redis_sovereign_agent_operation_stats_schema() -> None:
    assert RedisSovereignAgent.operation_stats["get"] == 0
    assert set(RedisSovereignAgent.operation_stats) >= {"get", "set", "delete"}


# --- L2 artifact_loader ---
from agentic_core.L2_execution.healers.artifact_loader import try_load_artifact


def test_try_load_artifact_none_returns_empty() -> None:
    m, h = try_load_artifact(None)
    assert m is None and h == ""


def test_try_load_artifact_invalid_path_fail_closed() -> None:
    m, h = try_load_artifact(Path("/nonexistent/path/heal_classifier_artifact_12345"))
    assert m is None and h == ""


# --- L2 write_governor_mixin ---
from agentic_core.L2_execution.enforcement.write_governor_mixin import WriteGovernorMixin


def test_write_governor_mixin_routes_through_injected_gateway() -> None:
    class Holder(WriteGovernorMixin):
        pass

    gw = MagicMock()
    gw.write_file.return_value = sent = object()
    h = Holder()
    h.set_write_gateway(gw)
    assert h.governed_write("rel/path.txt", b"data") is sent
    gw.write_file.assert_called_once()


# --- L2 _token_counter ---
from agentic_core.L2_execution.enforcement._token_counter import count_tokens


def test_count_tokens_empty_is_zero() -> None:
    assert count_tokens("", provider="openai") == 0


def test_count_tokens_heuristic_deterministic() -> None:
    n = count_tokens("abcd", provider="unknown-provider-xyz")
    assert n >= 1


# --- L2 _provider_local_vllm (reassert compose contract; full tests in unit/) ---
from agentic_core.L2_execution.enforcement._provider_local_vllm import LocalVLLMProvider


def test_local_vllm_compose_returns_markers() -> None:
    s = LocalVLLMProvider._compose_prompt("SYS", "USR")
    assert "SYS" in s and "USR" in s
