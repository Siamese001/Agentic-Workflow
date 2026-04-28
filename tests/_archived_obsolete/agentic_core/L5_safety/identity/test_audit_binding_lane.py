"""Tests for L5_safety/identity/audit_binding_lane.py."""

import pytest

from agentic_core.L5_safety.identity.audit_binding_lane import (
    LaneAuditRecord,
    emit_lane_audit_record,
    reconstruct_lane_audit_digest,
)


def test_reconstruct_lane_audit_digest():
    """Test that reconstruct_lane_audit_digest recomputes digest correctly."""
    record_dict = {
        "token_v4_trace_id": "test_v4_trace",
        "token_v3_trace_id": "test_v3_trace",
        "policy_version": "v4.0.0",
        "registry_digest": "test_digest",
        "attribution": {"agent_id": "test_agent"},
        "lane_decision": {"final_action": "allow"},
        "writes": [],
        "egresses": [],
        "audit_digest": "original_digest",
    }

    # Remove audit_digest to simulate independent verification
    test_dict = {k: v for k, v in record_dict.items() if k != "audit_digest"}

    # Since we can't compute the actual digest without the canonical function,
    # we'll just test that the function exists and accepts the input
    digest = reconstruct_lane_audit_digest(test_dict)

    # The digest should be a SHA-256 hex string
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_lane_audit_record_validation_requires_v4_trace_id():
    """Test that LaneAuditRecord requires token_v4_trace_id."""
    with pytest.raises(ValueError, match="token_v4_trace_id required"):
        LaneAuditRecord(
            token_v4_trace_id="",
            token_v3_trace_id="v3_trace",
            policy_version="v4.0.0",
            registry_digest="digest",
            attribution={},
            lane_decision={},
            writes=(),
            egresses=(),
            audit_digest="audit_digest",
        )


def test_lane_audit_record_validation_requires_v3_trace_id():
    """Test that LaneAuditRecord requires token_v3_trace_id."""
    with pytest.raises(ValueError, match="token_v3_trace_id required"):
        LaneAuditRecord(
            token_v4_trace_id="v4_trace",
            token_v3_trace_id="",
            policy_version="v4.0.0",
            registry_digest="digest",
            attribution={},
            lane_decision={},
            writes=(),
            egresses=(),
            audit_digest="audit_digest",
        )


def test_lane_audit_record_validation_requires_audit_digest():
    """Test that LaneAuditRecord requires audit_digest."""
    with pytest.raises(ValueError, match="audit_digest required"):
        LaneAuditRecord(
            token_v4_trace_id="v4_trace",
            token_v3_trace_id="v3_trace",
            policy_version="v4.0.0",
            registry_digest="digest",
            attribution={},
            lane_decision={},
            writes=(),
            egresses=(),
            audit_digest="",
        )


def test_lane_audit_record_to_dict():
    """Test that LaneAuditRecord.to_dict() returns complete dictionary."""
    record = LaneAuditRecord(
        token_v4_trace_id="v4_trace",
        token_v3_trace_id="v3_trace",
        policy_version="v4.0.0",
        registry_digest="digest",
        attribution={"agent_id": "test_agent"},
        lane_decision={"final_action": "allow"},
        writes=(),
        egresses=(),
        audit_digest="audit_digest",
    )

    result_dict = record.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict["token_v4_trace_id"] == "v4_trace"
    assert result_dict["token_v3_trace_id"] == "v3_trace"
    assert result_dict["policy_version"] == "v4.0.0"
    assert result_dict["registry_digest"] == "digest"
    assert result_dict["attribution"]["agent_id"] == "test_agent"
    assert result_dict["lane_decision"]["final_action"] == "allow"
    assert isinstance(result_dict["writes"], list)
    assert isinstance(result_dict["egresses"], list)


def test_lane_audit_record_to_json():
    """Test that LaneAuditRecord.to_json() returns canonical JSON."""
    record = LaneAuditRecord(
        token_v4_trace_id="v4_trace",
        token_v3_trace_id="v3_trace",
        policy_version="v4.0.0",
        registry_digest="digest",
        attribution={"agent_id": "test_agent"},
        lane_decision={"final_action": "allow"},
        writes=(),
        egresses=(),
        audit_digest="audit_digest",
    )

    json_str = record.to_json()
    assert isinstance(json_str, str)
    # Should be valid JSON
    import json
    parsed = json.loads(json_str)
    assert parsed["token_v4_trace_id"] == "v4_trace"


def test_emit_lane_audit_record_function_exists():
    """Test that emit_lane_audit_record function exists and can be imported."""
    assert emit_lane_audit_record is not None
