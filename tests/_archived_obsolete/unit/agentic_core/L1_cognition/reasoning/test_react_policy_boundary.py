"""Behavioral tests for react_policy_boundary."""

from __future__ import annotations

from agentic_core.react_policy_boundary import ReactPolicyBoundary, is_policy_safe_transition


def test_allowed_tool_within_turn_budget_passes():
    boundary = ReactPolicyBoundary(allowed_tools=("search", "summarize"), max_turns=2)
    assert is_policy_safe_transition(boundary, "search", 1) is True


def test_disallowed_tool_or_turn_budget_fails():
    boundary = ReactPolicyBoundary(allowed_tools=("search",), max_turns=2)
    assert is_policy_safe_transition(boundary, "write", 1) is False
    assert is_policy_safe_transition(boundary, "search", 2) is False
