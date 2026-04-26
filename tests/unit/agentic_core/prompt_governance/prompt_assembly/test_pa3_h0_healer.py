"""Unit tests for PA.3 H0 healer reentry."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.pa3_h0_healer import (
    DEFAULT_MAX_RETRIES,
    validate_h0_reentry,
)


def _kwargs(**overrides):
    base = dict(
        h0_content="Try again with explicit citations.",
        h0_policy_hash="ph",
        h0_blueprint_hash="bp",
        current_policy_hash="ph",
        current_blueprint_hash="bp",
        retry_count=1,
    )
    base.update(overrides)
    return base


def test_h0_accepted_happy_path():
    res = validate_h0_reentry(**_kwargs())
    assert res.accepted is True
    assert res.rejection_reason == ""


def test_h0_empty_rejected():
    res = validate_h0_reentry(**_kwargs(h0_content=""))
    assert res.accepted is False
    assert res.rejection_reason == "h0_empty"


def test_h0_policy_hash_mismatch():
    res = validate_h0_reentry(**_kwargs(h0_policy_hash="OTHER"))
    assert res.accepted is False
    assert res.rejection_reason == "h0_policy_hash_mismatch"


def test_h0_blueprint_hash_mismatch():
    res = validate_h0_reentry(**_kwargs(h0_blueprint_hash="OTHER"))
    assert res.accepted is False
    assert res.rejection_reason == "h0_blueprint_hash_mismatch"


def test_h0_retry_threshold_exceeded():
    res = validate_h0_reentry(**_kwargs(retry_count=DEFAULT_MAX_RETRIES + 1))
    assert res.accepted is False
    assert res.rejection_reason == "h0_retry_threshold_exceeded"


def test_h0_scope_widening_detected():
    res = validate_h0_reentry(
        **_kwargs(
            original_task_keywords=("summarize", "article"),
            h0_task_keywords=("summarize", "article", "translate", "rewrite", "code"),
        )
    )
    assert res.accepted is False
    assert res.rejection_reason == "h0_scope_widening_detected"


def test_h0_minor_keyword_addition_allowed():
    res = validate_h0_reentry(
        **_kwargs(
            original_task_keywords=("summarize",),
            h0_task_keywords=("summarize", "concise"),
        )
    )
    assert res.accepted is True
