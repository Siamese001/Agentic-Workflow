"""Bind tier helper (W1)."""

from __future__ import annotations

from tools.refactor_decisions.author_gate_w1_bind import merge_precedent_verdict, outcome_bind_tier


def test_merge_precedent_order():
    assert merge_precedent_verdict("strong", "none", "suggestive") == "strong"
    assert merge_precedent_verdict(None, "suggestive", "strong") == "suggestive"
    assert merge_precedent_verdict(None, None, "none") == "none"
    assert merge_precedent_verdict(None, None, None) is None


def test_outcome_bind_tier_override_disputed():
    assert (
        outcome_bind_tier(
            precedent_verdict="strong",
            override_vs_recommendation=1,
            reason_code=None,
            degraded_scope=False,
            tests_passed=1,
            regression_found=0,
            rollback_required=0,
        )
        == "disputed_bind"
    )


def test_outcome_bind_tier_strong_downgrade_tests():
    assert (
        outcome_bind_tier(
            precedent_verdict="strong",
            override_vs_recommendation=0,
            reason_code=None,
            degraded_scope=False,
            tests_passed=0,
            regression_found=0,
            rollback_required=0,
        )
        == "weak_bind"
    )


def test_outcome_bind_tier_degraded_strong():
    assert (
        outcome_bind_tier(
            precedent_verdict="strong",
            override_vs_recommendation=0,
            reason_code=None,
            degraded_scope=True,
            tests_passed=1,
            regression_found=0,
            rollback_required=0,
        )
        == "weak_bind"
    )
