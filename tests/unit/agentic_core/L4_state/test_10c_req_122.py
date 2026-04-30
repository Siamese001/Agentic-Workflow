"""Proof-evidence test for 10C-REQ-122 (UWG single-writer-with-pen).

Surface       : 00B_L4_State_Archive_and_UWG
Severity      : CRITICAL
OTEL span     : uwg.commit.validated
Artifact      : CommitRequest -> WriteAdmissionVerdict -> DurableCommitReceipt
Negative ctl  : Two CommitRequests with the same serial_seqno -- must fail
                (race condition; two clerks writing).

The invariant: UWG must have exactly one clerk with the master pen, and
the write queue must be strictly serialized. CommitRequests carry a
single_writer_attestation flag and a monotonic serial_seqno; the gate
fails closed on any seqno collision.
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
)
from tests.fixtures.proof_evidence.runtime_artifact_validators import (
    ArtifactShapeError,
    assert_uwg_single_writer,
    validate_artifact_shape,
)

REQ_ID = "10C-REQ-122"
OWNER_SURFACE = "00B_L4_State_Archive_and_UWG"
EXPECTED_SPAN = "uwg.commit.validated"
UWG_REQUIRED_ATTRS = BASE_REQUIRED_ATTRS + ("commit_request_id",)


def _valid_commit_request(seqno: int = 1) -> dict:
    return {
        "commit_request_id": f"cr-122-{seqno:04d}",
        "writer_identity": "uwg.master_clerk",
        "blueprint_hash": "blueprint-122-h",
        "policy_hash": "policy-122-h",
        "diff_payload_hash": f"diff-122-{seqno:04d}-h",
        "serial_seqno": seqno,
        "owner_surface": OWNER_SURFACE,
        "single_writer_attestation": True,
    }


def _valid_span_attrs() -> dict:
    return {
        "req_id": REQ_ID,
        "run_id": "run-122-001",
        "trace_id": "trace-122-001",
        "request_id": "req-122-rqst",
        "owner_surface": OWNER_SURFACE,
        "policy_hash": "policy-122-h",
        "blueprint_hash": "blueprint-122-h",
        "replay_key": "replay-122-k",
        "commit_request_id": "cr-122-0001",
    }


def _admit(queue: list[dict], request: dict) -> None:
    """Minimal in-test admission gate: enforces seqno monotonicity and
    single-writer attestation. This is the proof fixture for the UWG gate."""
    assert_uwg_single_writer(request)
    if queue:
        last_seqno = queue[-1]["serial_seqno"]
        if request["serial_seqno"] <= last_seqno:
            raise ArtifactShapeError(
                f"UWG seqno collision/regression: incoming {request['serial_seqno']} "
                f"<= last admitted {last_seqno}"
            )
    queue.append(request)


# ---------------------------------------------------------------------------
# Positive controls
# ---------------------------------------------------------------------------

def test_uwg_commit_request_shape_positive() -> None:
    record = _valid_commit_request()
    validate_artifact_shape("CommitRequest", record)
    assert_uwg_single_writer(record)


def test_uwg_span_positive() -> None:
    receipt = make_receipt(EXPECTED_SPAN, _valid_span_attrs())
    assert_span_shape(receipt, EXPECTED_SPAN, UWG_REQUIRED_ATTRS)
    assert_owner_surface_matches(receipt, OWNER_SURFACE)


def test_uwg_serialized_admission_positive() -> None:
    """Admitting strictly-monotonic seqno requests must succeed."""
    queue: list[dict] = []
    for i in (1, 2, 3, 4, 5):
        _admit(queue, _valid_commit_request(seqno=i))
    assert [r["serial_seqno"] for r in queue] == [1, 2, 3, 4, 5]


def test_uwg_replay_stability_positive() -> None:
    digest = assert_replay_stable(_valid_commit_request(seqno=1))
    assert len(digest) == 64


# ---------------------------------------------------------------------------
# Negative controls (matches negative_control_specific from the ledger row)
# ---------------------------------------------------------------------------

def test_negative_control_seqno_collision_two_clerks() -> None:
    """Two CommitRequests with the SAME serial_seqno MUST be rejected."""
    queue: list[dict] = []
    _admit(queue, _valid_commit_request(seqno=1))
    with pytest.raises(ArtifactShapeError) as excinfo:
        _admit(queue, _valid_commit_request(seqno=1))  # collision
    assert "seqno collision" in str(excinfo.value).lower()


def test_negative_control_seqno_regression() -> None:
    """A CommitRequest with a smaller serial_seqno MUST be rejected."""
    queue: list[dict] = []
    _admit(queue, _valid_commit_request(seqno=5))
    with pytest.raises(ArtifactShapeError):
        _admit(queue, _valid_commit_request(seqno=3))


def test_negative_control_missing_single_writer_attestation() -> None:
    bad = _valid_commit_request()
    bad["single_writer_attestation"] = False
    with pytest.raises(ArtifactShapeError) as excinfo:
        assert_uwg_single_writer(bad)
    assert "single_writer_attestation" in str(excinfo.value)


def test_negative_control_negative_seqno() -> None:
    bad = _valid_commit_request()
    bad["serial_seqno"] = -1
    with pytest.raises(ArtifactShapeError):
        assert_uwg_single_writer(bad)


def test_negative_control_uwg_missing_diff_payload_hash() -> None:
    incomplete = _valid_commit_request()
    del incomplete["diff_payload_hash"]
    with pytest.raises(ArtifactShapeError):
        validate_artifact_shape("CommitRequest", incomplete)


def test_negative_control_uwg_span_wrong_name() -> None:
    """Commit emitted under L2 span name MUST fail the gate."""
    receipt = make_receipt("l2.execution.attempt", _valid_span_attrs())
    with pytest.raises(SpanAssertionError):
        assert_span_shape(receipt, EXPECTED_SPAN, UWG_REQUIRED_ATTRS)


def test_negative_control_replay_drift() -> None:
    a = _valid_commit_request(seqno=1)
    b = _valid_commit_request(seqno=2)
    assert_replay_drift_detected(a, b)
