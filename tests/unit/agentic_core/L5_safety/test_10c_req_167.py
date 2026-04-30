"""Proof-evidence test for 10C-REQ-167 (L5 policy plane invariant).

Surface       : 00A_L5_Governance_Safety
Severity      : CRITICAL
OTEL span     : l5.certification.evidence_emitted
Artifact      : L5CertificationResult + L5AuthorityEvidenceReceipt + L5PolicyBindingReceipt
Negative ctl  : L5 emitting a runtime ALLOW/DENY disposition -- must fail.

The invariant: L5 acts as Safety Officer with cross-cutting authority,
but it does NOT emit live runtime dispositions. Live ALLOW/DENY belongs
to Runtime Gates (00C). L5 emits certification / evidence receipts that
are consumed by Exit (X3) and UWG, never bypassing them.
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
    assert_replay_drift_detected,
    assert_replay_stable,
)
from tests.fixtures.proof_evidence.runtime_artifact_validators import (
    ArtifactShapeError,
    assert_l5_is_certification_only,
    validate_artifact_shape,
)

REQ_ID = "10C-REQ-167"
OWNER_SURFACE = "00A_L5_Governance_Safety"
EXPECTED_SPAN = "l5.certification.evidence_emitted"


def _valid_certification() -> dict:
    return {
        "certification_id": "cert-167-001",
        "certification_class": "policy_plane_authority_evidence",
        "policy_hash": "policy-167-h",
        "blueprint_hash": "blueprint-167-h",
        "evidence_refs": ["evidence://run/167/auth-bind", "evidence://run/167/policy-bind"],
        "owner_surface": OWNER_SURFACE,
        "issued_at_utc": _dt.datetime(2026, 4, 30, 12, 0, 0, tzinfo=_dt.timezone.utc).isoformat(),
        "is_runtime_disposition": False,
    }


def _valid_span_attrs() -> dict:
    return {
        "req_id": REQ_ID,
        "run_id": "run-167-001",
        "trace_id": "trace-167-001",
        "request_id": "req-167-rqst",
        "owner_surface": OWNER_SURFACE,
        "policy_hash": "policy-167-h",
        "blueprint_hash": "blueprint-167-h",
        "replay_key": "replay-167-k",
    }


# ---------------------------------------------------------------------------
# Positive controls
# ---------------------------------------------------------------------------

def test_l5_certification_shape_positive() -> None:
    """A well-formed L5CertificationResult must validate cleanly."""
    record = _valid_certification()
    validate_artifact_shape("L5CertificationResult", record)
    assert_l5_is_certification_only(record)


def test_l5_certification_span_positive() -> None:
    receipt = make_receipt(EXPECTED_SPAN, _valid_span_attrs())
    assert_span_shape(receipt, EXPECTED_SPAN, BASE_REQUIRED_ATTRS)
    assert_owner_surface_matches(receipt, OWNER_SURFACE)


def test_l5_replay_stability_positive() -> None:
    digest = assert_replay_stable(_valid_certification())
    assert len(digest) == 64


# ---------------------------------------------------------------------------
# Negative controls
# ---------------------------------------------------------------------------

def test_negative_control_l5_emits_live_disposition() -> None:
    """L5 emitting a live runtime disposition MUST fail."""
    bad = _valid_certification()
    bad["is_runtime_disposition"] = True  # the constitutional violation
    with pytest.raises(ArtifactShapeError) as excinfo:
        assert_l5_is_certification_only(bad)
    msg = str(excinfo.value)
    assert "is_runtime_disposition" in msg
    assert "certification" in msg.lower()


def test_negative_control_l5_missing_policy_hash() -> None:
    incomplete = _valid_certification()
    del incomplete["policy_hash"]
    with pytest.raises(ArtifactShapeError) as excinfo:
        validate_artifact_shape("L5CertificationResult", incomplete)
    assert "policy_hash" in str(excinfo.value)


def test_negative_control_l5_missing_blueprint_hash() -> None:
    incomplete = _valid_certification()
    del incomplete["blueprint_hash"]
    with pytest.raises(ArtifactShapeError):
        validate_artifact_shape("L5CertificationResult", incomplete)


def test_negative_control_l5_span_wrong_name() -> None:
    """L5 span emitted under a runtime-gate name MUST fail."""
    receipt = make_receipt("runtime_gate.verdict_emitted", _valid_span_attrs())
    with pytest.raises(SpanAssertionError):
        assert_span_shape(receipt, EXPECTED_SPAN, BASE_REQUIRED_ATTRS)


def test_negative_control_replay_drift() -> None:
    cert_a = _valid_certification()
    cert_b = _valid_certification()
    cert_b["evidence_refs"] = ["evidence://run/167/different"]
    assert_replay_drift_detected(cert_a, cert_b)
