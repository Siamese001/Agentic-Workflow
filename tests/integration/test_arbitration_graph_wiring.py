"""Integration tests for arbitration-driven routing helpers."""
from types import SimpleNamespace

import pytest

pytest.importorskip("langgraph")

from agent_orchestration_v10_7 import (  # noqa: E402  (import guarded by importorskip)
    NODE_RESULT_KEY,
    check_bullets_passed,
    check_qa_passed,
    node_success,
)
from core_v10_7_services import ArbitrationEngine, RobustnessStack, SelfCorrectionManager


class _WorkflowContextStub:
    def __init__(self) -> None:
        agent_stacks = SimpleNamespace(max_local_retries=1)
        self.config = SimpleNamespace(agent_stacks=agent_stacks)
        self.robustness_stack = RobustnessStack(retry_limits={"bullets_quality": 1, "qa_validation": 1})
        self.self_correction_manager = SelfCorrectionManager()
        self.arbitration_engine = ArbitrationEngine(
            robustness_stack=self.robustness_stack,
            self_correction_manager=self.self_correction_manager,
        )


def test_bullet_conditional_prefers_arbitration_route() -> None:
    ctx = _WorkflowContextStub()
    payload = {
        "bullets": {"critiqued_bullets": []},
        "arbitration": {
            "bullets_post_selection": {
                "suggested_route": "RETRY_BULLETS",
            }
        },
    }
    state = {
        NODE_RESULT_KEY: node_success("run_critique_bullets", payload),
        "arbitration": payload["arbitration"],
    }
    assert check_bullets_passed(state, ctx) == "retry_bullets"


def test_qa_conditional_routes_to_replanner_on_global_signal() -> None:
    ctx = _WorkflowContextStub()
    payload = {
        "qa": {"qa_passed": False},
        "arbitration": {
            "qa_post_validation": {
                "suggested_route": "GLOBAL_REPLAN",
            }
        },
    }
    state = {
        NODE_RESULT_KEY: node_success("run_qa_validation", payload),
        "arbitration": payload["arbitration"],
    }
    assert check_qa_passed(state, ctx) == "global_replanner"
