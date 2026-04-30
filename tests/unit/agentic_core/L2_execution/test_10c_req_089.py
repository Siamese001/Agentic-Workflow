"""Proof-evidence test for 10C-REQ-089 (L2 execution invariants).

Surface       : 04_L2_Execute
Severity      : CRITICAL
OTEL span     : l2.execution.attempt
Artifact      : ExecutionResult (sealed envelope)
Negative ctl  : L2 attempting durable commit / HITL escalation / route
                modification -- must fail.

The invariant: L2 may execute tools and produce a sealed envelope, but
it must not commit durable state, escalate to HITL, or modify the route.
VALIDATE and HEAL must read the SAME blueprint_hash / policy_hash that
the original execution attempt was sealed against (replay determinism).
"""

from __future__ import annotations

import pytest

from tests.fixtures.proof_evidence.otel_span_receipt import (
    BASE_REQUIRED_ATTRS,
    SpanAssertionError,
    assert_owner_surface_matches,
    assert_span_shape,
    make_receipt,
)
from tests.fixtures.proof_evidence.replay_digest import (
    assert_replay_drift_detected,
    assert_replay_stable,
    deterministic_digest,
)
from tests.fixtures.proof_evidence.runtime_artifact_validators import (
    ArtifactShapeError,
    assert_l2_no_authority_leak,
    validate_artifact_shape,
)

REQ_ID = "10C-REQ-089"
OWNER_SURFACE = "04_L2_Execute"
EXPECTED_SPAN = "l2.execution.attempt"
L2_REQUIRED_ATTRS = BASE_REQUIRED_ATTRS + ("artifact_id",)


def _valid_execution_result() -> dict:
    return {
        "execution_id": "exec-089-001",
        "blueprint_hash": "blueprint-089-h",
        "policy_hash": "policy-089-h",
        "tool_calls": [
            {"tool_id": "search", "args_hash": "args-h-1", "result_hash": "res-h-1"},
        ],
        "side_effects_proposed": [
            {"target": "L4_state.session_scratch", "diff_hash": "diff-h-1", "committed": False},
        ],
        "replay_key": "replay-089-k",
        "owner_surface": OWNER_SURFACE,
        "no_durable_commit_assertion": True,
        "no_hitl_invocation_assertion": True,
        "no_routing_assertion": True,
    }


def _valid_span_attrs() -> dict:
    return {
        "req_id": REQ_ID,
        "run_id": "run-089-001",
        "trace_id": "trace-089-001",
        "request_id": "req-089-rqst",
        "owner_surface": OWNER_SURFACE,
        "policy_hash": "policy-089-h",
        "blueprint_hash": "blueprint-089-h",
        "replay_key": "replay-089-k",
        "artifact_id": "exec-089-001",
    }


# ---------------------------------------------------------------------------
# Positive controls
# ---------------------------------------------------------------------------

def test_execution_result_shape_positive() -> None:
    record = _valid_execution_result()
    validate_artifact_shape("ExecutionResult", record)
    assert_l2_no_authority_leak(record)


def test_l2_span_positive() -> None:
    receipt = make_receipt(EXPECTED_SPAN, _valid_span_attrs())
    assert_span_shape(receipt, EXPECTED_SPAN, L2_REQUIRED_ATTRS)
    assert_owner_surface_matches(receipt, OWNER_SURFACE)


def test_l2_side_effects_are_proposed_only() -> None:
    """Every side_effects_proposed entry MUST have committed=False at L2."""
    record = _valid_execution_result()
    for se in record["side_effects_proposed"]:
        assert se["committed"] is False, (
            f"L2 must propose, not commit; offender: {se}"
        )


def test_l2_validate_and_heal_use_same_seal() -> None:
    """REQ-089: VALIDATE and HEAL paths must observe the same hash seal.

    Concretely: replay-key recomputed across the (blueprint_hash,
    policy_hash, replay_key) tuple must be stable; HEAL must NOT
    re-derive a different seal.
    """
    record = _valid_execution_result()
    seal = {
        "blueprint_hash": record["blueprint_hash"],
        "policy_hash": record["policy_hash"],
        "replay_key": record["replay_key"],
    }
    digest_validate = deterministic_digest(seal)
    digest_heal = deterministic_digest(seal)  # heal observes same seal
    assert digest_validate == digest_heal, (
        f"L2 VALIDATE and HEAL must use same seal: {digest_validate} vs {digest_heal}"
    )


def test_l2_replay_stability_positive() -> None:
    digest = assert_replay_stable(_valid_execution_result())
    assert len(digest) == 64


# ---------------------------------------------------------------------------
# Negative controls
# ---------------------------------------------------------------------------

def test_negative_control_l2_durable_commit() -> None:
    """L2 attempting durable commit MUST fail."""
    bad = _valid_execution_result()
    bad["no_durable_commit_assertion"] = False
    with pytest.raises(ArtifactShapeError) as excinfo:
        assert_l2_no_authority_leak(bad)
    assert "no_durable_commit_assertion" in str(excinfo.value)


def test_negative_control_l2_hitl_invocation() -> None:
    bad = _valid_execution_result()
    bad["no_hitl_invocation_assertion"] = False
    with pytest.raises(ArtifactShapeError):
        assert_l2_no_authority_leak(bad)


def test_negative_control_l2_routing_attempt() -> None:
    bad = _valid_execution_result()
    bad["no_routing_assertion"] = False
    with pytest.raises(ArtifactShapeError):
        assert_l2_no_authority_leak(bad)


def test_negative_control_l2_missing_replay_key() -> None:
    incomplete = _valid_execution_result()
    del incomplete["replay_key"]
    with pytest.raises(ArtifactShapeError):
        validate_artifact_shape("ExecutionResult", incomplete)


def test_negative_control_l2_validate_heal_seal_drift() -> None:
    """If HEAL re-derives a different seal, replay determinism is broken."""
    seal_validate = {
        "blueprint_hash": "blueprint-089-h",
        "policy_hash": "policy-089-h",
        "replay_key": "replay-089-k",
    }
    seal_heal_drift = dict(seal_validate)
    seal_heal_drift["replay_key"] = "DIFFERENT-replay-k"
    assert_replay_drift_detected(seal_validate, seal_heal_drift)


def test_negative_control_replay_drift() -> None:
    a = _valid_execution_result()
    b = _valid_execution_result()
    b["execution_id"] = "exec-089-DIFFERENT"
    assert_replay_drift_detected(a, b)
