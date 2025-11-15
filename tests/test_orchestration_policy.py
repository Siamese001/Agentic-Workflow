"""Unit tests for orchestration routing policy."""
from __future__ import annotations

from types import SimpleNamespace

from core_v10_7 import NodeStatus
from core_v10_7_services import RobustnessStack

from orchestration_policy import OrchestrationRoutingPolicy


def _make_context() -> SimpleNamespace:
    agent_stacks = SimpleNamespace(
        bullet_accept_threshold=7.0,
        qa_retry_limit=1,
        max_local_retries=1,
        hil_max_reentry_loops=2,
    )
    config = SimpleNamespace(agent_stacks=agent_stacks)
    return SimpleNamespace(config=config)


def test_after_prompt_injection_detects_block():
    policy = OrchestrationRoutingPolicy(_make_context())
    state = {"safety": {"injection_detected": True}}
    assert policy.after_prompt_injection(state) == "injection_detected"
    assert policy.after_prompt_injection({"safety": {"injection_detected": False}}) == "injection_safe"


def test_after_bullet_critique_accepts_arbitration_route():
    policy = OrchestrationRoutingPolicy(_make_context())
    state = {
        "__node_result__": {
            "node": "run_critique_bullets",
            "status": NodeStatus.SUCCESS,
            "payload": {
                "arbitration": {
                    "bullets_post_selection": {"suggested_route": "ACCEPT"}
                }
            },
        }
    }
    assert policy.after_bullet_critique(state) == "bullets_passed"


def test_after_bullet_critique_retries_then_escalates():
    robustness = RobustnessStack(retry_limits={"bullets_quality": 1, "qa_validation": 1})
    policy = OrchestrationRoutingPolicy(_make_context(), robustness=robustness)
    state = {
        "__node_result__": {
            "node": "run_critique_bullets",
            "status": NodeStatus.SUCCESS,
            "payload": {
                "bullets": {
                    "critiqued_bullets": [
                        {"critique": {"score": 5}},
                        {"critique": {"score": 6}},
                    ]
                }
            },
        }
    }
    assert policy.after_bullet_critique(state) == "retry_bullets"
    assert policy.after_bullet_critique(state) == "global_replanner"


def test_after_qa_validation_routes_on_acceptance():
    robustness = RobustnessStack(retry_limits={"bullets_quality": 1, "qa_validation": 1})
    policy = OrchestrationRoutingPolicy(_make_context(), robustness=robustness)
    state = {
        "__node_result__": {
            "node": "run_qa_validation",
            "status": NodeStatus.SUCCESS,
            "payload": {
                "qa": {"qa_passed": True},
            },
        }
    }
    assert policy.after_qa_validation(state) == "qa_passed"


def test_after_hil_reentry_limits_loops():
    policy = OrchestrationRoutingPolicy(_make_context())
    state = {"hil": {"retries": 1}}
    assert policy.after_hil_reentry(state) == "continue"
    state["hil"]["retries"] = 3
    assert policy.after_hil_reentry(state) == "halt"


def test_after_rag_execution_emits_retry_decision():
    policy = OrchestrationRoutingPolicy(_make_context())
    decision = policy.after_rag_execution({"rag": {"needs_retry": True}})
    assert decision.should_retry is True
    assert decision.reason == "rag_retry_requested"
    assert policy.after_rag_execution({"rag": {"needs_retry": False}}).route == "rag_complete"
