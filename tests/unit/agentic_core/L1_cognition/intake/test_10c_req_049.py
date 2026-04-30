"""Proof-evidence test for 10C-REQ-049 (U0 ingress invariant).

Surface       : 01_U0_Request_Intake
Severity      : CRITICAL
OTEL span     : u0.intake.invariant_enforced
Artifact      : ValidatedRequest
Negative ctl  : U0 carrying L1 plan / L0 route / C0 retrieval / L2 / UWG
                state -- must fail.

The invariant: U0 owns identity, transport, schema, and quota only. It
must not perform semantic routing, L1 planning, C0 retrieval, external
calls, or mutation. Any ValidatedRequest that leaks those keys is a
proof failure.
"""

from __future__ import annotations

import datetime as _dt
import pytest

from tests.fixtures.proof_evidence.otel_span_receipt import (
    BASE_REQUIRED_ATTRS,
    SpanAssertionError,
    assert_owner_surface_matches,
    assert_span_shape,
    make_receipt,
)
from tests.fixtures.proof_evidence.replay_digest import (
    ReplayStabilityError,
    assert_replay_drift_detected,
    assert_replay_stable,
)
from tests.fixtures.proof_evidence.runtime_artifact_validators import (
    ArtifactShapeError,
    assert_u0_no_authority_leak,
    validate_artifact_shape,
)

REQ_ID = "10C-REQ-049"
OWNER_SURFACE = "01_U0_Request_Intake"
EXPECTED_SPAN = "u0.intake.invariant_enforced"
U0_REQUIRED_ATTRS = BASE_REQUIRED_ATTRS + ("tenant", "identity", "session_id")


def _valid_envelope() -> dict:
    return {
        "request_id": "req-049-pos-001",
        "session_id": "sess-049-001",
        "trace_root": "trace-049-001",
        "tenant": "tenant-A",
        "transport": "https",
        "ingress_envelope": {"schema_version": "v1", "method": "POST"},
        "caller_scope_baseline": {"role": "user", "scopes": ["read"]},
        "ingress_time_utc": _dt.datetime(2026, 4, 30, 12, 0, 0, tzinfo=_dt.timezone.utc).isoformat(),
        "owner_surface": OWNER_SURFACE,
    }


def _valid_span_attrs() -> dict:
    return {
        "req_id": REQ_ID,
        "run_id": "run-049-001",
        "trace_id": "trace-049-001",
        "request_id": "req-049-pos-001",
        "owner_surface": OWNER_SURFACE,
        "policy_hash": "policy-049-h",
        "blueprint_hash": "blueprint-049-h",
        "replay_key": "replay-049-k",
        "tenant": "tenant-A",
        "identity": "user-049",
        "session_id": "sess-049-001",
    }


# ---------------------------------------------------------------------------
# Positive controls
# ---------------------------------------------------------------------------

def test_validated_request_shape_positive() -> None:
    """A well-formed ValidatedRequest must validate cleanly."""
    record = _valid_envelope()
    validate_artifact_shape("ValidatedRequest", record)
    assert_u0_no_authority_leak(record)


def test_intake_span_shape_positive() -> None:
    """The u0.intake.invariant_enforced span must carry all required attrs."""
    receipt = make_receipt(EXPECTED_SPAN, _valid_span_attrs())
    assert_span_shape(receipt, EXPECTED_SPAN, U0_REQUIRED_ATTRS)
    assert_owner_surface_matches(receipt, OWNER_SURFACE)


def test_replay_digest_stability_positive() -> None:
    """Same envelope yields the same digest across runs."""
    digest = assert_replay_stable(_valid_envelope())
    assert len(digest) == 64  # sha256 hex


# ---------------------------------------------------------------------------
# Negative controls (matches negative_control_specific from the ledger row)
# ---------------------------------------------------------------------------

def test_negative_control_authority_leak() -> None:
    """U0 carrying L1/L0/C0/L2/L5 state MUST fail validation."""
    leaky = _valid_envelope()
    leaky["plan_proposal"] = {"steps": ["fetch", "summarize"]}  # L1 leak
    with pytest.raises(ArtifactShapeError) as excinfo:
        assert_u0_no_authority_leak(leaky)
    assert "plan_proposal" in str(excinfo.value)


def test_negative_control_route_id_leak() -> None:
    leaky = _valid_envelope()
    leaky["route_id"] = "R-99"  # L0 leak
    with pytest.raises(ArtifactShapeError):
        assert_u0_no_authority_leak(leaky)


def test_negative_control_durable_commit_intent_leak() -> None:
    leaky = _valid_envelope()
    leaky["durable_commit_intent"] = {"diff": "..."}  # UWG leak
    with pytest.raises(ArtifactShapeError):
        assert_u0_no_authority_leak(leaky)


def test_negative_control_missing_required_field() -> None:
    incomplete = _valid_envelope()
    del incomplete["tenant"]
    with pytest.raises(ArtifactShapeError) as excinfo:
        validate_artifact_shape("ValidatedRequest", incomplete)
    assert "tenant" in str(excinfo.value)


def test_negative_control_span_missing_owner_surface() -> None:
    attrs = _valid_span_attrs()
    del attrs["owner_surface"]
    receipt = make_receipt(EXPECTED_SPAN, attrs)
    with pytest.raises(SpanAssertionError):
        assert_span_shape(receipt, EXPECTED_SPAN, U0_REQUIRED_ATTRS)


def test_negative_control_replay_drift() -> None:
    """Two semantically different envelopes MUST produce different digests."""
    env_a = _valid_envelope()
    env_b = _valid_envelope()
    env_b["request_id"] = "req-049-different"
    assert_replay_drift_detected(env_a, env_b)
