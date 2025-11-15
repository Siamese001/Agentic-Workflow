"""Unit tests for the PolicyStack rule evaluation."""
from __future__ import annotations

from stacks_v10_8.policy_stack import ContentPolicyRule, PolicyDecision, PolicyStack


def test_forbidden_term_matching_blocks_input() -> None:
    stack = PolicyStack(
        workflow_context=object(),
        rulebook=[
            ContentPolicyRule(
                id="r1",
                description="Blocks mentions of explosives.",
                forbidden_terms=["explosive"],
            )
        ],
    )

    decision = stack.guard_user_input("The payload contains an explosive device.")

    assert not decision.allowed
    assert "explosive" in (decision.reason or "")


def test_multi_rule_evaluation_returns_first_match() -> None:
    rules = [
        ContentPolicyRule(id="alpha", description="rule alpha", forbidden_terms=["alpha"]),
        ContentPolicyRule(id="beta", description="rule beta", forbidden_terms=["beta"]),
    ]
    stack = PolicyStack(workflow_context=object(), rulebook=rules)

    decision = stack.guard_plan({"text": "alpha and beta"})

    assert decision.reason is not None
    assert "alpha" in decision.reason


def test_policy_decision_allows_safe_output() -> None:
    stack = PolicyStack(workflow_context=object())

    decision = stack.guard_output({"summary": "All good here."})

    assert isinstance(decision, PolicyDecision)
    assert decision.allowed is True
    assert decision.reason is None
