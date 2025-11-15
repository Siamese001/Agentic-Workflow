"""Integration-style tests for the constitutional pipeline wiring."""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

from bullet_execution import BulletExecutionStack
from stacks_v10_8.constitutional_engine import ConstitutionalEngine
from stacks_v10_8.policy_stack import PolicyStack
from stacks_v10_8.safety_policy_stack import SafetyPolicyStack


class _PipelineContext(SimpleNamespace):
    def __init__(self) -> None:
        agent_stacks = SimpleNamespace(
            enable_prompt_injection_detection=True,
            bullet_accept_threshold=7.0,
        )
        super().__init__(config=SimpleNamespace(agent_stacks=agent_stacks))
        self.safety_policy = SafetyPolicyStack(self, debug_mode=False)
        self.policy_stack = PolicyStack(self, debug_mode=False)
        self.constitutional_engine = ConstitutionalEngine()


def test_bullet_stack_attaches_constitutional_review() -> None:
    context = _PipelineContext()
    stack = BulletExecutionStack(context)
    state = {"metadata": {"workflow_id": "wf"}, "resume": {"experience": [{"id": 1}]}}
    plan_payload = {"bullets": {"plan": {"target_sections": [1]}}}
    patch = asyncio.run(stack.run_async(state, plan_payload))

    assert "safety_report" in patch
    assert "policy" in patch
    assert patch["constitutional_review"]["passed"] is True


def test_review_node_matches_text_result() -> None:
    engine = ConstitutionalEngine()
    node_output = {"draft": {"sections": {"summary": "Vote for our slate"}}}
    review_from_node = engine.review_node(node_output)
    review_from_text = engine.review_text(json.dumps(node_output, sort_keys=True))
    assert review_from_node.passed == review_from_text.passed
    assert [v.dict() for v in review_from_node.violations] == [
        v.dict() for v in review_from_text.violations
    ]
    assert not review_from_node.passed
