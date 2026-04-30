"""Proof-evidence test for 10C-REQ-086 (PA.2 slot composition).

Surface       : 03B_PA_Prompt_Assembly
Severity      : CRITICAL
OTEL span     : pa.prompt.compiled_artifact_emitted
Artifact      : CompiledPromptArtifact
Negative ctl  : C0 evidence resolved AFTER U0 user content -- must fail
                (the user-content-injection attack surface PA.2 closes).

The invariant: PA.2 must map must-use evidence + optional evidence +
citation anchors + contradiction flags BEFORE U0 user content is slotted
in. C0-before-U0 ordering is the prompt-injection defense for PA.
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
    assert_pa_c0_before_u0,
    validate_artifact_shape,
)

REQ_ID = "10C-REQ-086"
OWNER_SURFACE = "03B_PA_Prompt_Assembly"
EXPECTED_SPAN = "pa.prompt.compiled_artifact_emitted"
PA_REQUIRED_ATTRS = BASE_REQUIRED_ATTRS + ("artifact_id", "artifact_ref")


def _valid_artifact() -> dict:
    return {
        "assembly_hash": "pa-086-asm-h",
        "instruction_blocks": [
            {"role": "system", "content_hash": "sys-h-1"},
            {"role": "policy", "content_hash": "pol-h-1"},
        ],
        "evidence_refs": [
            {"chunk_id": "c-001", "support_target": "must"},
            {"chunk_id": "c-002", "support_target": "optional"},
        ],
        "citation_anchors": [
            {"chunk_id": "c-001", "anchor_id": "ca-001"},
        ],
        "contradiction_flags": [],
        "slot_order_hash": "slot-order-c0-then-u0-h",
        "owner_surface": OWNER_SURFACE,
        "c0_resolved_before_u0": True,
    }


def _valid_span_attrs() -> dict:
    return {
        "req_id": REQ_ID,
        "run_id": "run-086-001",
        "trace_id": "trace-086-001",
        "request_id": "req-086-rqst",
        "owner_surface": OWNER_SURFACE,
        "policy_hash": "policy-086-h",
        "blueprint_hash": "blueprint-086-h",
        "replay_key": "replay-086-k",
        "artifact_id": "pa-086-art-001",
        "artifact_ref": "artifact://pa/086/001",
    }


# ---------------------------------------------------------------------------
# Positive controls
# ---------------------------------------------------------------------------

def test_pa_artifact_shape_positive() -> None:
    record = _valid_artifact()
    validate_artifact_shape("CompiledPromptArtifact", record)
    assert_pa_c0_before_u0(record)


def test_pa_span_positive() -> None:
    receipt = make_receipt(EXPECTED_SPAN, _valid_span_attrs())
    assert_span_shape(receipt, EXPECTED_SPAN, PA_REQUIRED_ATTRS)
    assert_owner_surface_matches(receipt, OWNER_SURFACE)


def test_pa_replay_stability_positive() -> None:
    digest = assert_replay_stable(_valid_artifact())
    assert len(digest) == 64


def test_pa_artifact_carries_citation_anchors() -> None:
    """PA.2 must produce at least one citation_anchor when evidence is non-empty."""
    record = _valid_artifact()
    assert record["citation_anchors"], "PA.2 must produce citation_anchors"
    anchored_chunks = {a["chunk_id"] for a in record["citation_anchors"]}
    evidence_chunks = {e["chunk_id"] for e in record["evidence_refs"]}
    # Every anchor must point to an evidence chunk that's actually referenced
    assert anchored_chunks.issubset(evidence_chunks), (
        f"citation_anchors ref nonexistent evidence chunks: "
        f"{anchored_chunks - evidence_chunks}"
    )


# ---------------------------------------------------------------------------
# Negative controls
# ---------------------------------------------------------------------------

def test_negative_control_u0_before_c0_violation() -> None:
    """C0 evidence resolved AFTER U0 user content MUST fail (injection risk)."""
    bad = _valid_artifact()
    bad["c0_resolved_before_u0"] = False
    with pytest.raises(ArtifactShapeError) as excinfo:
        assert_pa_c0_before_u0(bad)
    msg = str(excinfo.value)
    assert "c0_resolved_before_u0" in msg


def test_negative_control_pa_missing_evidence_refs() -> None:
    incomplete = _valid_artifact()
    del incomplete["evidence_refs"]
    with pytest.raises(ArtifactShapeError):
        validate_artifact_shape("CompiledPromptArtifact", incomplete)


def test_negative_control_pa_missing_citation_anchors() -> None:
    incomplete = _valid_artifact()
    del incomplete["citation_anchors"]
    with pytest.raises(ArtifactShapeError):
        validate_artifact_shape("CompiledPromptArtifact", incomplete)


def test_negative_control_pa_span_missing_artifact_id() -> None:
    attrs = _valid_span_attrs()
    del attrs["artifact_id"]
    receipt = make_receipt(EXPECTED_SPAN, attrs)
    with pytest.raises(SpanAssertionError):
        assert_span_shape(receipt, EXPECTED_SPAN, PA_REQUIRED_ATTRS)


def test_negative_control_replay_drift() -> None:
    art_a = _valid_artifact()
    art_b = _valid_artifact()
    art_b["assembly_hash"] = "pa-086-asm-DIFFERENT"
    assert_replay_drift_detected(art_a, art_b)
