"""Focused unit tests for OutreachStack helpers."""

import pytest

from src.lic_agentic.core import PolicyUpdate


def test_max_retrieval_calls_respects_budget_and_bounds(outreach_stack):
    outreach_stack.policy.budget_multiplier = 10.0
    max_calls = outreach_stack._max_retrieval_calls()
    assert 1 <= max_calls <= 6
    outreach_stack.policy.budget_multiplier = 0.05
    assert outreach_stack._max_retrieval_calls() == 1


def test_apply_policy_update_refreshes_toggles_and_architect(outreach_stack):
    update = PolicyUpdate(
        budget_multiplier=0.9,
        temperature_cap=0.33,
        tot_branches=2,
        tool_weights={},
    )
    old_toggle = outreach_stack.toggles
    outreach_stack._apply_policy_update(update)
    assert outreach_stack.toggles.temperature_cap == pytest.approx(0.33)
    assert outreach_stack.toggles.tot_branches == 2
    assert outreach_stack.architect.toggles is outreach_stack.toggles
    assert outreach_stack.toggles is not old_toggle


def test_rehydrate_restores_all_pii_placeholders(outreach_stack):
    mapping = {"<PII_EMAIL_1>": "alice@example.com", "<PII_NAME_1>": "Alice"}
    draft = "Hello <PII_NAME_1>\n\nReach me at <PII_EMAIL_1>"
    restored = outreach_stack._rehydrate(draft, mapping)
    assert "alice@example.com" in restored and "<PII_EMAIL_1>" not in restored
    assert "Alice" in restored
