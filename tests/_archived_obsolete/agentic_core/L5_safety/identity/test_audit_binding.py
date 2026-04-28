"""Tests for L5_safety/identity/audit_binding.py."""

import pytest

from agentic_core.interfaces.principal_chain_types import InvokingUserKind, PrincipalChain
from agentic_core.interfaces.principal_aware_egress import PrincipalEgressEnvelope
from agentic_core.interfaces.principal_aware_write import PrincipalAttachedWrite
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.audit_binding import (
    PrincipalAuditRecord,
    _canonical_json,
    emit_principal_audit_record,
    reconstruct_audit_digest,
)
from agentic_core.L5_safety.identity.principal_verifier import (
    VerificationResult,
    VerificationStatus,
)


@pytest.fixture
def sample_verification_result() -> VerificationResult:
    """Sample verification result for testing."""
    return VerificationResult(
        status=VerificationStatus.PASS,
        failures=(),
        required_rung="mutate",
        token_rung="mutate",
        delegation_depth=0,
        delegation_cap=3,
    )


@pytest.fixture
def sample_write_envelope(sample_principal_chain) -> PrincipalAttachedWrite:
    """Sample write envelope for testing."""
    return PrincipalAttachedWrite(
        plan_hash="plan_hash_abc123",
        tool_calls=("tool1", "tool2"),
        stdout_digest="stdout_digest_456",
        state_diff_hash="state_diff_789",
        principal_chain=sample_principal_chain,
        principal_chain_digest="principal_digest_012",
        principal_replay_key="replay_key_345",
    )


@pytest.fixture
def sample_egress_envelope(sample_principal_chain) -> PrincipalEgressEnvelope:
    """Sample egress envelope for testing."""
    return PrincipalEgressEnvelope(
        egress_kind="http_tool",
        target_id="http_tool",
        request_digest="request_digest_abc",
        response_digest="response_digest_def",
        principal_chain=sample_principal_chain,
        principal_chain_digest="principal_digest_012",
        egress_replay_key="egress_replay_key_678",
    )


def test_principal_audit_record_validation_requires_token_v4_trace_id(
    sample_verification_result,
):
    """Test PrincipalAuditRecord requires token_v4_trace_id."""
    with pytest.raises(ValueError, match="token_v4_trace_id required"):
        PrincipalAuditRecord(
            token_v4_trace_id="",
            token_v3_trace_id="v3_trace_123",
            policy_version="v4.0.0",
            registry_digest="registry_digest_abc",
            attribution={"user": "user@example.com"},
            verification=sample_verification_result.to_dict(),
            writes=(),
            egresses=(),
            audit_digest="digest_123",
        )


def test_principal_audit_record_validation_requires_token_v3_trace_id(
    sample_verification_result,
):
    """Test PrincipalAuditRecord requires token_v3_trace_id."""
    with pytest.raises(ValueError, match="token_v3_trace_id required"):
        PrincipalAuditRecord(
            token_v4_trace_id="v4_trace_456",
            token_v3_trace_id="",
            policy_version="v4.0.0",
            registry_digest="registry_digest_abc",
            attribution={"user": "user@example.com"},
            verification=sample_verification_result.to_dict(),
            writes=(),
            egresses=(),
            audit_digest="digest_123",
        )


def test_principal_audit_record_validation_requires_audit_digest(
    sample_verification_result,
):
    """Test PrincipalAuditRecord requires audit_digest."""
    with pytest.raises(ValueError, match="audit_digest required"):
        PrincipalAuditRecord(
            token_v4_trace_id="v4_trace_456",
            token_v3_trace_id="v3_trace_123",
            policy_version="v4.0.0",
            registry_digest="registry_digest_abc",
            attribution={"user": "user@example.com"},
            verification=sample_verification_result.to_dict(),
            writes=(),
            egresses=(),
            audit_digest="",
        )


def test_principal_audit_record_to_dict(sample_verification_result):
    """Test PrincipalAuditRecord.to_dict serialization."""
    record = PrincipalAuditRecord(
        token_v4_trace_id="v4_trace_456",
        token_v3_trace_id="v3_trace_123",
        policy_version="v4.0.0",
        registry_digest="registry_digest_abc",
        attribution={"user": "user@example.com"},
        verification=sample_verification_result.to_dict(),
        writes=(),
        egresses=(),
        audit_digest="digest_123",
    )

    d = record.to_dict()
    assert d["token_v4_trace_id"] == "v4_trace_456"
    assert d["token_v3_trace_id"] == "v3_trace_123"
    assert d["policy_version"] == "v4.0.0"
    assert d["registry_digest"] == "registry_digest_abc"
    assert d["attribution"] == {"user": "user@example.com"}
    assert d["verification"] == sample_verification_result.to_dict()
    assert d["writes"] == []
    assert d["egresses"] == []
    assert d["audit_digest"] == "digest_123"


def test_principal_audit_record_to_dict_with_writes_and_egresses(
    sample_verification_result,
    sample_write_envelope,
    sample_egress_envelope,
):
    """Test PrincipalAuditRecord.to_dict with writes and egresses."""
    record = PrincipalAuditRecord(
        token_v4_trace_id="v4_trace_456",
        token_v3_trace_id="v3_trace_123",
        policy_version="v4.0.0",
        registry_digest="registry_digest_abc",
        attribution={"user": "user@example.com"},
        verification=sample_verification_result.to_dict(),
        writes=(sample_write_envelope.to_dict(),),
        egresses=(sample_egress_envelope.to_dict(),),
        audit_digest="digest_123",
    )

    d = record.to_dict()
    assert len(d["writes"]) == 1
    assert len(d["egresses"]) == 1
    assert d["writes"][0]["plan_hash"] == "plan_hash_abc123"
    assert d["egresses"][0]["target_id"] == "http_tool"


def test_principal_audit_record_to_json(sample_verification_result):
    """Test PrincipalAuditRecord.to_json returns canonical JSON."""
    record = PrincipalAuditRecord(
        token_v4_trace_id="v4_trace_456",
        token_v3_trace_id="v3_trace_123",
        policy_version="v4.0.0",
        registry_digest="registry_digest_abc",
        attribution={"user": "user@example.com"},
        verification=sample_verification_result.to_dict(),
        writes=(),
        egresses=(),
        audit_digest="digest_123",
    )

    json_str = record.to_json()
    assert isinstance(json_str, str)
    assert "token_v4_trace_id" in json_str
    assert "token_v3_trace_id" in json_str
    assert "policy_version" in json_str


def test_canonical_json_sorts_keys():
    """Test _canonical_json sorts keys deterministically."""
    obj = {"z": 1, "a": 2, "m": 3}
    json_str = _canonical_json(obj)
    assert json_str == '{"a":2,"m":3,"z":1}'


def test_canonical_json_compact_format():
    """Test _canonical_json uses compact separators."""
    obj = {"a": 1, "b": 2}
    json_str = _canonical_json(obj)
    assert " " not in json_str  # No spaces
    assert "\n" not in json_str  # No newlines


def test_emit_principal_audit_record_basic(
    sample_v4_token,
    sample_verification_result,
):
    """Test emit_principal_audit_record with minimal inputs."""
    record = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
    )

    assert record.token_v4_trace_id == sample_v4_token.v4_trace_id
    assert record.token_v3_trace_id == sample_v4_token.v3_artifact.trace_id
    assert record.policy_version == sample_v4_token.policy_version
    assert record.registry_digest == sample_v4_token.registry_digest
    assert record.attribution is not None
    assert record.verification == sample_verification_result.to_dict()
    assert len(record.writes) == 0
    assert len(record.egresses) == 0
    assert record.audit_digest is not None
    assert len(record.audit_digest) == 64  # SHA-256 hex string


def test_emit_principal_audit_record_with_writes(
    sample_v4_token,
    sample_verification_result,
    sample_write_envelope,
):
    """Test emit_principal_audit_record with write envelopes."""
    record = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
        writes=(sample_write_envelope,),
    )

    assert len(record.writes) == 1
    assert record.writes[0]["plan_hash"] == "plan_hash_abc123"
    assert record.writes[0]["principal_chain"]["invoking_user"] == "user@example.com"


def test_emit_principal_audit_record_with_egresses(
    sample_v4_token,
    sample_verification_result,
    sample_egress_envelope,
):
    """Test emit_principal_audit_record with egress envelopes."""
    record = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
        egresses=(sample_egress_envelope,),
    )

    assert len(record.egresses) == 1
    assert record.egresses[0]["target_id"] == "http_tool"
    assert record.egresses[0]["principal_chain"]["invoking_user"] == "user@example.com"


def test_emit_principal_audit_record_with_both(
    sample_v4_token,
    sample_verification_result,
    sample_write_envelope,
    sample_egress_envelope,
):
    """Test emit_principal_audit_record with both writes and egresses."""
    record = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
        writes=(sample_write_envelope,),
        egresses=(sample_egress_envelope,),
    )

    assert len(record.writes) == 1
    assert len(record.egresses) == 1


def test_emit_principal_audit_record_attribution_includes_principal_chain(
    sample_v4_token,
    sample_verification_result,
):
    """Test emit_principal_audit_record includes principal chain in attribution."""
    record = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
    )

    assert "invoking_user" in record.attribution
    assert record.attribution["invoking_user"] == "user@example.com"
    assert "agent_id" in record.attribution
    assert record.attribution["agent_id"] == "test_agent"


def test_emit_principal_audit_record_digest_deterministic(
    sample_v4_token,
    sample_verification_result,
):
    """Test emit_principal_audit_record produces deterministic digest."""
    record1 = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
    )
    record2 = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
    )

    assert record1.audit_digest == record2.audit_digest


def test_reconstruct_audit_digest_basic(sample_verification_result):
    """Test reconstruct_audit_digest recomputes digest from record dict."""
    record_dict = {
        "token_v4_trace_id": "v4_trace_456",
        "token_v3_trace_id": "v3_trace_123",
        "policy_version": "v4.0.0",
        "registry_digest": "registry_digest_abc",
        "attribution": {"user": "user@example.com"},
        "verification": sample_verification_result.to_dict(),
        "writes": [],
        "egresses": [],
        "audit_digest": "original_digest",
    }

    reconstructed = reconstruct_audit_digest(record_dict)
    assert isinstance(reconstructed, str)
    assert len(reconstructed) == 64  # SHA-256 hex string
    assert reconstructed != "original_digest"  # Should be recomputed


def test_reconstruct_audit_digest_excludes_audit_digest_field(
    sample_verification_result,
):
    """Test reconstruct_audit_digest excludes audit_digest from computation."""
    record_dict = {
        "token_v4_trace_id": "v4_trace_456",
        "token_v3_trace_id": "v3_trace_123",
        "policy_version": "v4.0.0",
        "registry_digest": "registry_digest_abc",
        "attribution": {"user": "user@example.com"},
        "verification": sample_verification_result.to_dict(),
        "writes": [],
        "egresses": [],
        "audit_digest": "should_be_ignored",
    }

    reconstructed = reconstruct_audit_digest(record_dict)
    # Changing the audit_digest field should not affect reconstruction
    record_dict["audit_digest"] = "different_value"
    reconstructed2 = reconstruct_audit_digest(record_dict)
    assert reconstructed == reconstructed2


def test_reconstruct_audit_digest_with_writes_and_egresses(
    sample_verification_result,
    sample_write_envelope,
    sample_egress_envelope,
):
    """Test reconstruct_audit_digest includes writes and egresses in computation."""
    record_dict = {
        "token_v4_trace_id": "v4_trace_456",
        "token_v3_trace_id": "v3_trace_123",
        "policy_version": "v4.0.0",
        "registry_digest": "registry_digest_abc",
        "attribution": {"user": "user@example.com"},
        "verification": sample_verification_result.to_dict(),
        "writes": [sample_write_envelope.to_dict()],
        "egresses": [sample_egress_envelope.to_dict()],
        "audit_digest": "original_digest",
    }

    reconstructed = reconstruct_audit_digest(record_dict)
    assert isinstance(reconstructed, str)
    assert len(reconstructed) == 64


def test_emit_and_reconstruct_digest_roundtrip(
    sample_v4_token,
    sample_verification_result,
):
    """Test that emit and reconstruct produce matching digests."""
    record = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
    )

    record_dict = record.to_dict()
    reconstructed = reconstruct_audit_digest(record_dict)

    assert reconstructed == record.audit_digest


def test_emit_principal_audit_record_digest_changes_with_content(
    sample_v4_token,
    sample_verification_result,
):
    """Test that digest changes when content changes."""
    record1 = emit_principal_audit_record(
        token=sample_v4_token,
        verification=sample_verification_result,
    )

    # Change verification status
    different_verification = VerificationResult(
        status=VerificationStatus.FAIL,
        failures=("TEST_FAILURE",),
        required_rung="mutate",
        token_rung="read",
        delegation_depth=0,
        delegation_cap=3,
    )
    record2 = emit_principal_audit_record(
        token=sample_v4_token,
        verification=different_verification,
    )

    assert record1.audit_digest != record2.audit_digest
