"""Tests for capability-token rotation policy (v6 §S4D ledger proof).

Plan ``finish-open-scope-test-harden-38010b``.

The rotation policy operates only on ``token.ttl_seconds`` and
``token.single_use``; we duck-type a minimal token stand-in to avoid the
ceremony of building a full ``CapabilityTokenV4Artifact`` (which requires
PrincipalChain + SemanticClockSnapshot wiring).
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agentic_core.L5_safety.enforcement.capability_token_rotation import (
    RotationDecision,
    RotationPolicy,
    evaluate_rotation,
    must_rotate,
)


@dataclass(frozen=True)
class _StubToken:
    """Duck-typed CapabilityTokenV4Artifact for rotation-policy tests.

    The policy only reads ``ttl_seconds`` and ``single_use``, so a frozen
    dataclass with those fields fully satisfies the structural contract.
    """

    ttl_seconds: int
    single_use: bool = False


# --------------------------------------------------------------------------- #
# Policy validation
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("pct", [0.0, -0.1, 1.1])
def test_policy_rejects_out_of_range_threshold(pct):
    with pytest.raises(ValueError, match="rotation_threshold_pct"):
        RotationPolicy(rotation_threshold_pct=pct)


def test_policy_default_is_eighty_percent():
    assert RotationPolicy().rotation_threshold_pct == 0.8


# --------------------------------------------------------------------------- #
# Decision precedence
# --------------------------------------------------------------------------- #


def test_expired_token_rotates_due_expiry_even_if_single_use_unspent():
    """Expiry beats single-use precedence (most decisive first)."""
    tok = _StubToken(ttl_seconds=100, single_use=True)
    out = evaluate_rotation(tok, age_seconds=100, usage_count=0)
    assert out is RotationDecision.ROTATE_DUE_EXPIRY


def test_expired_token_at_age_greater_than_ttl():
    tok = _StubToken(ttl_seconds=100)
    out = evaluate_rotation(tok, age_seconds=999, usage_count=0)
    assert out is RotationDecision.ROTATE_DUE_EXPIRY


def test_single_use_after_one_call_rotates_due_usage():
    tok = _StubToken(ttl_seconds=3600, single_use=True)
    out = evaluate_rotation(tok, age_seconds=10, usage_count=1)
    assert out is RotationDecision.ROTATE_DUE_USAGE


def test_single_use_unused_does_not_rotate_due_usage():
    tok = _StubToken(ttl_seconds=3600, single_use=True)
    out = evaluate_rotation(tok, age_seconds=10, usage_count=0)
    assert out is RotationDecision.KEEP


def test_multi_use_high_usage_does_not_trigger_usage_rotation():
    """Without single_use, usage_count alone never triggers rotation."""
    tok = _StubToken(ttl_seconds=3600, single_use=False)
    out = evaluate_rotation(tok, age_seconds=10, usage_count=99)
    assert out is RotationDecision.KEEP


def test_threshold_path_at_eighty_percent_rotates():
    tok = _StubToken(ttl_seconds=100)
    out = evaluate_rotation(tok, age_seconds=80, usage_count=0)
    assert out is RotationDecision.ROTATE_DUE_THRESHOLD


def test_threshold_just_below_pct_keeps():
    tok = _StubToken(ttl_seconds=100)
    out = evaluate_rotation(tok, age_seconds=79, usage_count=0)
    assert out is RotationDecision.KEEP


def test_custom_policy_lowers_threshold():
    """HIGH-band sites tighten to 0.5; verify the policy is honored."""
    tok = _StubToken(ttl_seconds=100)
    pol = RotationPolicy(rotation_threshold_pct=0.5)
    out = evaluate_rotation(tok, age_seconds=50, usage_count=0, policy=pol)
    assert out is RotationDecision.ROTATE_DUE_THRESHOLD


def test_fresh_token_keeps():
    tok = _StubToken(ttl_seconds=3600)
    out = evaluate_rotation(tok, age_seconds=0, usage_count=0)
    assert out is RotationDecision.KEEP


# --------------------------------------------------------------------------- #
# Input validation
# --------------------------------------------------------------------------- #


def test_negative_age_raises():
    tok = _StubToken(ttl_seconds=100)
    with pytest.raises(ValueError, match="age_seconds"):
        evaluate_rotation(tok, age_seconds=-1, usage_count=0)


def test_negative_usage_count_raises():
    tok = _StubToken(ttl_seconds=100)
    with pytest.raises(ValueError, match="usage_count"):
        evaluate_rotation(tok, age_seconds=10, usage_count=-1)


# --------------------------------------------------------------------------- #
# Convenience surface
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "age, single_use, usage, expected",
    [
        (0, False, 0, False),
        (50, False, 0, False),
        (80, False, 0, True),
        (100, False, 0, True),
        (10, True, 1, True),
        (10, True, 0, False),
    ],
)
def test_must_rotate_matches_evaluate(age, single_use, usage, expected):
    tok = _StubToken(ttl_seconds=100, single_use=single_use)
    assert must_rotate(tok, age_seconds=age, usage_count=usage) is expected


# --------------------------------------------------------------------------- #
# Determinism — pure function contract
# --------------------------------------------------------------------------- #


def test_evaluate_is_pure():
    """Same inputs -> same output, no hidden state."""
    tok = _StubToken(ttl_seconds=100)
    a = evaluate_rotation(tok, age_seconds=80, usage_count=0)
    b = evaluate_rotation(tok, age_seconds=80, usage_count=0)
    c = evaluate_rotation(tok, age_seconds=80, usage_count=0)
    assert a is b is c is RotationDecision.ROTATE_DUE_THRESHOLD
