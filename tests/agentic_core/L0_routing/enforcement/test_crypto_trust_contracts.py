"""Tests for crypto_trust_contracts.py module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
    hash_artifact_canonical,
    SigningError,
    sign_artifact,
    VerificationError,
    verify_signature,
    ReplayDetectedError,
    ReplayGuardStore,
    record_and_block_replay,
    EscalationRequiredError,
    record_hash_mismatch,
    SignedGuardianError,
    build_signed_guardian_artifact,
)
from agentic_core.L0_routing.types.crypto_trust_types import (
    SignatureEnvelope,
    SignatureEnclave,
    TrustRoot,
    KeyStatus,
    SigningAlgorithm,
    ReplayGuardRecord,
    HashMismatchTracker,
    SignedGuardianArtifact,
)


class TestHashArtifactCanonical:
    """Tests for hash_artifact_canonical function."""

    def test_hash_artifact_canonical(self):
        """Test hash_artifact_canonical returns SHA-256 hash."""
        artifact_bytes = b"test artifact content"
        result = hash_artifact_canonical(artifact_bytes)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex string length

    def test_hash_artifact_canonical_deterministic(self):
        """Test hash_artifact_canonical is deterministic."""
        artifact_bytes = b"test artifact content"
        result1 = hash_artifact_canonical(artifact_bytes)
        result2 = hash_artifact_canonical(artifact_bytes)
        assert result1 == result2

    def test_hash_artifact_canonical_different_content(self):
        """Test hash_artifact_canonical differs for different content."""
        artifact_bytes1 = b"content 1"
        artifact_bytes2 = b"content 2"
        result1 = hash_artifact_canonical(artifact_bytes1)
        result2 = hash_artifact_canonical(artifact_bytes2)
        assert result1 != result2


class TestSignArtifact:
    """Tests for sign_artifact function."""

    def test_sign_artifact_success(self):
        """Test sign_artifact with valid inputs."""
        artifact_bytes = b"test artifact"
        key_id = "test_key"
        enclave = MagicMock()
        enclave.sign.return_value = b"signature"
        key_record = MagicMock()
        key_record.algorithm = SigningAlgorithm.HMAC_SHA256
        enclave.get_key_record.return_value = key_record
        
        envelope = sign_artifact(artifact_bytes, key_id, enclave, "trace-123", 1)
        
        assert envelope.artifact_hash == hash_artifact_canonical(artifact_bytes)
        assert envelope.key_id == key_id
        assert envelope.signature == b"signature"
        assert envelope.algorithm == SigningAlgorithm.HMAC_SHA256
        assert envelope.trace_id == "trace-123"
        assert envelope.semantic_clock_tick == 1

    def test_sign_artifact_key_error(self):
        """Test sign_artifact raises SigningError on KeyError."""
        artifact_bytes = b"test artifact"
        key_id = "test_key"
        enclave = MagicMock()
        enclave.sign.side_effect = KeyError("Key not found")
        
        with pytest.raises(SigningError, match="Signing failed"):
            sign_artifact(artifact_bytes, key_id, enclave, "trace-123", 1)

    def test_sign_artifact_permission_error(self):
        """Test sign_artifact raises SigningError on PermissionError."""
        artifact_bytes = b"test artifact"
        key_id = "test_key"
        enclave = MagicMock()
        enclave.sign.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(SigningError, match="Signing failed"):
            sign_artifact(artifact_bytes, key_id, enclave, "trace-123", 1)

    def test_sign_artifact_os_error(self):
        """Test sign_artifact raises SigningError on OSError."""
        artifact_bytes = b"test artifact"
        key_id = "test_key"
        enclave = MagicMock()
        enclave.sign.side_effect = OSError("IO error")
        
        with pytest.raises(SigningError, match="Unexpected signing error"):
            sign_artifact(artifact_bytes, key_id, enclave, "trace-123", 1)

    def test_sign_artifact_runtime_error(self):
        """Test sign_artifact raises SigningError on RuntimeError."""
        artifact_bytes = b"test artifact"
        key_id = "test_key"
        enclave = MagicMock()
        enclave.sign.side_effect = RuntimeError("Runtime error")
        
        with pytest.raises(SigningError, match="Unexpected signing error"):
            sign_artifact(artifact_bytes, key_id, enclave, "trace-123", 1)


class TestVerifySignature:
    """Tests for verify_signature function."""

    def test_verify_signature_success(self):
        """Test verify_signature with valid signature."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash=hash_artifact_canonical(artifact_bytes),
            key_id="test_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        trust_root = MagicMock()
        key_record = MagicMock()
        key_record.status = KeyStatus.ACTIVE
        trust_root.get_key.return_value = key_record
        enclave = MagicMock()
        enclave.verify.return_value = True
        
        result = verify_signature(artifact_bytes, envelope, trust_root, enclave)
        assert result is True

    def test_verify_signature_hash_mismatch(self):
        """Test verify_signature raises VerificationError on hash mismatch."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash="wrong_hash",
            key_id="test_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        trust_root = MagicMock()
        enclave = MagicMock()
        
        with pytest.raises(VerificationError, match="artifact_hash mismatch"):
            verify_signature(artifact_bytes, envelope, trust_root, enclave)

    def test_verify_signature_unknown_key(self):
        """Test verify_signature raises VerificationError for unknown key."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash=hash_artifact_canonical(artifact_bytes),
            key_id="unknown_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        trust_root = MagicMock()
        trust_root.get_key.return_value = None
        enclave = MagicMock()
        
        with pytest.raises(VerificationError, match="Unknown key_id"):
            verify_signature(artifact_bytes, envelope, trust_root, enclave)

    def test_verify_signature_revoked_key(self):
        """Test verify_signature raises VerificationError for revoked key."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash=hash_artifact_canonical(artifact_bytes),
            key_id="test_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        trust_root = MagicMock()
        key_record = MagicMock()
        key_record.status = KeyStatus.REVOKED
        trust_root.get_key.return_value = key_record
        enclave = MagicMock()
        
        with pytest.raises(VerificationError, match="Key.*is REVOKED"):
            verify_signature(artifact_bytes, envelope, trust_root, enclave)

    def test_verify_signature_invalid(self):
        """Test verify_signature raises VerificationError for invalid signature."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash=hash_artifact_canonical(artifact_bytes),
            key_id="test_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        trust_root = MagicMock()
        key_record = MagicMock()
        key_record.status = KeyStatus.ACTIVE
        trust_root.get_key.return_value = key_record
        enclave = MagicMock()
        enclave.verify.return_value = False
        
        with pytest.raises(VerificationError, match="Signature verification failed"):
            verify_signature(artifact_bytes, envelope, trust_root, enclave)


class TestReplayGuardStore:
    """Tests for ReplayGuardStore class."""

    def test_replay_guard_store_init(self):
        """Test ReplayGuardStore initialization."""
        store = ReplayGuardStore()
        assert store.record_count == 0

    def test_replay_guard_store_first_sighting(self):
        """Test first sighting of artifact hash."""
        store = ReplayGuardStore()
        record = store.check_and_record("hash1", 1)
        assert record.artifact_hash == "hash1"
        assert record.first_seen_tick == 1
        assert store.record_count == 1

    def test_replay_guard_store_replay_detection(self):
        """Test second sighting raises ReplayDetectedError."""
        store = ReplayGuardStore()
        store.check_and_record("hash1", 1)
        
        with pytest.raises(ReplayDetectedError, match="Replay detected"):
            store.check_and_record("hash1", 2)

    def test_replay_guard_store_multiple_hashes(self):
        """Test multiple different hashes can be recorded."""
        store = ReplayGuardStore()
        store.check_and_record("hash1", 1)
        store.check_and_record("hash2", 1)
        store.check_and_record("hash3", 1)
        assert store.record_count == 3

    def test_replay_guard_store_seen_count_increments(self):
        """Test seen count increments on replay attempts."""
        store = ReplayGuardStore()
        store.check_and_record("hash1", 1)
        
        with pytest.raises(ReplayDetectedError):
            store.check_and_record("hash1", 2)
        
        # Verify count increased
        record = store._records["hash1"]
        assert record.seen_count == 2


class TestRecordAndBlockReplay:
    """Tests for record_and_block_replay function."""

    def test_record_and_block_replay_success(self):
        """Test record_and_block_replay with new hash."""
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash="hash1",
            key_id="test_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        store = ReplayGuardStore()
        
        result = record_and_block_replay(envelope, store)
        assert result is True

    def test_record_and_block_replay_replay(self):
        """Test record_and_block_replay raises on replay."""
        envelope = SignatureEnvelope(
            trace_id="trace-123",
            artifact_hash="hash1",
            key_id="test_key",
            signature=b"signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=1,
        )
        store = ReplayGuardStore()
        store.check_and_record("hash1", 1)
        
        with pytest.raises(ReplayDetectedError):
            record_and_block_replay(envelope, store)


class TestRecordHashMismatch:
    """Tests for record_hash_mismatch function."""

    def test_record_hash_mismatch_no_escalation(self):
        """Test record_hash_mismatch when below threshold."""
        tracker = MagicMock()
        tracker.record_mismatch.return_value = False
        
        result = record_hash_mismatch(tracker)
        assert result is False

    def test_record_hash_mismatch_escalation(self):
        """Test record_hash_mismatch raises when threshold met."""
        tracker = MagicMock()
        tracker.record_mismatch.return_value = True
        tracker.escalation_threshold = 3
        tracker.wave_id = "test_wave"
        
        with pytest.raises(EscalationRequiredError, match="Human escalation required"):
            record_hash_mismatch(tracker)


class TestBuildSignedGuardianArtifact:
    """Tests for build_signed_guardian_artifact function."""

    def test_build_signed_guardian_artifact_success(self):
        """Test build_signed_guardian_artifact with valid inputs."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock()
        enclave.sign.return_value = b"signature"
        
        artifact = build_signed_guardian_artifact(
            trace_id="trace-123",
            prestaged_perms=("perm1", "perm2"),
            environment_metadata={"env": "prod"},
            commit_hash="abc123",
            pass_fail=True,
            artifact_bytes=artifact_bytes,
            key_id="test_key",
            enclave=enclave,
        )
        
        assert artifact.trace_id == "trace-123"
        assert artifact.signature == b"signature"
        assert artifact.prestaged_perms == ("perm1", "perm2")
        assert artifact.environment_metadata == {"env": "prod"}
        assert artifact.commit_hash == "abc123"
        assert artifact.pass_fail is True

    def test_build_signed_guardian_artifact_key_error(self):
        """Test build_signed_guardian_artifact raises on KeyError."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock()
        enclave.sign.side_effect = KeyError("Key not found")
        
        with pytest.raises(SignedGuardianError, match="Cannot sign guardian artifact"):
            build_signed_guardian_artifact(
                trace_id="trace-123",
                prestaged_perms=(),
                environment_metadata={},
                commit_hash="abc123",
                pass_fail=True,
                artifact_bytes=artifact_bytes,
                key_id="test_key",
                enclave=enclave,
            )

    def test_build_signed_guardian_artifact_permission_error(self):
        """Test build_signed_guardian_artifact raises on PermissionError."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock()
        enclave.sign.side_effect = PermissionError("Permission denied")
        
        with pytest.raises(SignedGuardianError, match="Cannot sign guardian artifact"):
            build_signed_guardian_artifact(
                trace_id="trace-123",
                prestaged_perms=(),
                environment_metadata={},
                commit_hash="abc123",
                pass_fail=True,
                artifact_bytes=artifact_bytes,
                key_id="test_key",
                enclave=enclave,
            )

    def test_build_signed_guardian_artifact_value_error(self):
        """Test build_signed_guardian_artifact raises on ValueError."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock()
        enclave.sign.return_value = b"signature"
        
        with pytest.raises(SignedGuardianError, match="SignedGuardianArtifact construction failed"):
            build_signed_guardian_artifact(
                trace_id="trace-123",
                prestaged_perms="invalid",  # type: ignore
                environment_metadata={},
                commit_hash="abc123",
                pass_fail=True,
                artifact_bytes=artifact_bytes,
                key_id="test_key",
                enclave=enclave,
            )

    def test_build_signed_guardian_artifact_type_error(self):
        """Test build_signed_guardian_artifact raises on TypeError."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock()
        enclave.sign.return_value = b"signature"
        
        with pytest.raises(SignedGuardianError, match="SignedGuardianArtifact construction failed"):
            build_signed_guardian_artifact(
                trace_id=123,  # type: ignore
                prestaged_perms=(),
                environment_metadata={},
                commit_hash="abc123",
                pass_fail=True,
                artifact_bytes=artifact_bytes,
                key_id="test_key",
                enclave=enclave,
            )
