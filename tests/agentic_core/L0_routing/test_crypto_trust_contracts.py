"""Tests for L0_routing.enforcement.crypto_trust_contracts module."""

from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.enforcement import crypto_trust_contracts
from agentic_core.L0_routing.types.crypto_trust_types import (
    HashMismatchTracker,
    KeyStatus,
    ReplayGuardRecord,
    SignatureEnclave,
    SignatureEnvelope,
    SignedGuardianArtifact,
    SigningAlgorithm,
    TrustRoot,
)


class TestCryptoTrustContracts:
    """Test suite for cryptographic trust contracts."""

    def test_hash_artifact_canonical(self):
        """Test canonical artifact hashing."""
        artifact_bytes = b"test artifact content"
        hash1 = crypto_trust_contracts.hash_artifact_canonical(artifact_bytes)
        hash2 = crypto_trust_contracts.hash_artifact_canonical(artifact_bytes)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex digest

    def test_hash_artifact_different_content(self):
        """Test hashing produces different results for different content."""
        hash1 = crypto_trust_contracts.hash_artifact_canonical(b"content1")
        hash2 = crypto_trust_contracts.hash_artifact_canonical(b"content2")
        
        assert hash1 != hash2

    def test_sign_artifact_success(self):
        """Test successful artifact signing."""
        artifact_bytes = b"test artifact"
        key_id = "key1"
        enclave = MagicMock(spec=SignatureEnclave)
        enclave.sign.return_value = "signature123"
        
        key_record = MagicMock()
        key_record.algorithm = SigningAlgorithm.HMAC_SHA256
        enclave.get_key_record.return_value = key_record
        
        envelope = crypto_trust_contracts.sign_artifact(
            artifact_bytes, key_id, enclave, trace_id="trace123", semantic_clock_tick=42
        )
        
        assert envelope.artifact_hash == crypto_trust_contracts.hash_artifact_canonical(artifact_bytes)
        assert envelope.key_id == key_id
        assert envelope.signature == "signature123"
        assert envelope.trace_id == "trace123"
        assert envelope.semantic_clock_tick == 42

    def test_sign_artifact_key_error(self):
        """Test signing fails on key error."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock(spec=SignatureEnclave)
        enclave.sign.side_effect = KeyError("Key not found")
        
        with pytest.raises(crypto_trust_contracts.SigningError, match="Signing failed"):
            crypto_trust_contracts.sign_artifact(
                artifact_bytes, "key1", enclave, trace_id="trace123", semantic_clock_tick=42
            )

    def test_sign_artifact_permission_error(self):
        """Test signing fails on permission error."""
        artifact_bytes = b"test artifact"
        enclave = MagicMock(spec=SignatureEnclave)
        enclave.sign.side_effect = PermissionError("Access denied")
        
        with pytest.raises(crypto_trust_contracts.SigningError, match="Signing failed"):
            crypto_trust_contracts.sign_artifact(
                artifact_bytes, "key1", enclave, trace_id="trace123", semantic_clock_tick=42
            )

    def test_verify_signature_success(self):
        """Test successful signature verification."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash=crypto_trust_contracts.hash_artifact_canonical(artifact_bytes),
            key_id="key1",
            signature="signature123",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        trust_root = MagicMock(spec=TrustRoot)
        key_record = MagicMock()
        key_record.status = KeyStatus.ACTIVE
        trust_root.get_key.return_value = key_record
        enclave = MagicMock(spec=SignatureEnclave)
        enclave.verify.return_value = True
        
        result = crypto_trust_contracts.verify_signature(
            artifact_bytes, envelope, trust_root, enclave
        )
        assert result is True

    def test_verify_signature_hash_mismatch(self):
        """Test verification fails on hash mismatch."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash="wrong_hash",
            key_id="key1",
            signature="signature123",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        trust_root = MagicMock()
        enclave = MagicMock()
        
        with pytest.raises(crypto_trust_contracts.VerificationError, match="artifact_hash mismatch"):
            crypto_trust_contracts.verify_signature(
                artifact_bytes, envelope, trust_root, enclave
            )

    def test_verify_signature_unknown_key(self):
        """Test verification fails on unknown key."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash=crypto_trust_contracts.hash_artifact_canonical(artifact_bytes),
            key_id="unknown_key",
            signature="signature123",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        trust_root = MagicMock()
        trust_root.get_key.return_value = None
        enclave = MagicMock()
        
        with pytest.raises(crypto_trust_contracts.VerificationError, match="Unknown key_id"):
            crypto_trust_contracts.verify_signature(
                artifact_bytes, envelope, trust_root, enclave
            )

    def test_verify_signature_revoked_key(self):
        """Test verification fails on revoked key."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash=crypto_trust_contracts.hash_artifact_canonical(artifact_bytes),
            key_id="key1",
            signature="signature123",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        trust_root = MagicMock()
        key_record = MagicMock()
        key_record.status = KeyStatus.REVOKED
        trust_root.get_key.return_value = key_record
        enclave = MagicMock()
        
        with pytest.raises(crypto_trust_contracts.VerificationError, match="Key .* is REVOKED"):
            crypto_trust_contracts.verify_signature(
                artifact_bytes, envelope, trust_root, enclave
            )

    def test_verify_signature_invalid(self):
        """Test verification fails on invalid signature."""
        artifact_bytes = b"test artifact"
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash=crypto_trust_contracts.hash_artifact_canonical(artifact_bytes),
            key_id="key1",
            signature="signature123",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        trust_root = MagicMock()
        key_record = MagicMock()
        key_record.status = KeyStatus.ACTIVE
        trust_root.get_key.return_value = key_record
        enclave = MagicMock()
        enclave.verify.return_value = False
        
        with pytest.raises(crypto_trust_contracts.VerificationError, match="Signature verification failed"):
            crypto_trust_contracts.verify_signature(
                artifact_bytes, envelope, trust_root, enclave
            )

    def test_replay_guard_store_check_and_record_first(self):
        """Test replay guard store records first sighting."""
        store = crypto_trust_contracts.ReplayGuardStore()
        artifact_hash = "hash123"
        
        record = store.check_and_record(artifact_hash, current_tick=42)
        
        assert isinstance(record, ReplayGuardRecord)
        assert record.artifact_hash == artifact_hash
        assert record.first_seen_tick == 42
        assert record.seen_count == 1
        assert store.record_count == 1

    def test_replay_guard_store_check_and_record_replay(self):
        """Test replay guard store detects replay."""
        store = crypto_trust_contracts.ReplayGuardStore()
        artifact_hash = "hash123"
        
        # First sighting
        store.check_and_record(artifact_hash, current_tick=42)
        
        # Second sighting should raise
        with pytest.raises(crypto_trust_contracts.ReplayDetectedError, match="Replay detected"):
            store.check_and_record(artifact_hash, current_tick=43)

    def test_replay_guard_store_record_count(self):
        """Test replay guard store record count."""
        store = crypto_trust_contracts.ReplayGuardStore()
        
        assert store.record_count == 0
        
        store.check_and_record("hash1", 1)
        assert store.record_count == 1
        
        store.check_and_record("hash2", 2)
        assert store.record_count == 2

    def test_record_and_block_replay_success(self):
        """Test record and block replay on first sighting."""
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash="hash123",
            key_id="key1",
            signature="sig",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        store = crypto_trust_contracts.ReplayGuardStore()
        
        result = crypto_trust_contracts.record_and_block_replay(envelope, store)
        assert result is True

    def test_record_and_block_replay_detected(self):
        """Test record and block replay raises on replay."""
        envelope = SignatureEnvelope(
            trace_id="trace123",
            artifact_hash="hash123",
            key_id="key1",
            signature="sig",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=42,
        )
        store = crypto_trust_contracts.ReplayGuardStore()
        
        # First sighting
        crypto_trust_contracts.record_and_block_replay(envelope, store)
        
        # Second sighting should raise
        with pytest.raises(crypto_trust_contracts.ReplayDetectedError):
            crypto_trust_contracts.record_and_block_replay(envelope, store)

    def test_record_hash_mismatch_below_threshold(self):
        """Test hash mismatch recording below escalation threshold."""
        tracker = HashMismatchTracker(wave_id="wave1", escalation_threshold=3)
        
        result = crypto_trust_contracts.record_hash_mismatch(tracker)
        assert result is False  # Below threshold, no escalation

    def test_record_hash_mismatch_at_threshold(self):
        """Test hash mismatch recording at escalation threshold."""
        tracker = HashMismatchTracker(wave_id="wave1", escalation_threshold=3)
        
        # Record 3 mismatches to reach threshold
        crypto_trust_contracts.record_hash_mismatch(tracker)
        crypto_trust_contracts.record_hash_mismatch(tracker)
        
        with pytest.raises(crypto_trust_contracts.EscalationRequiredError, match="Human escalation required"):
            crypto_trust_contracts.record_hash_mismatch(tracker)

    def test_build_signed_guardian_artifact_success(self):
        """Test successful signed guardian artifact building."""
        enclave = MagicMock(spec=SignatureEnclave)
        enclave.sign.return_value = "signature123"
        
        artifact = crypto_trust_contracts.build_signed_guardian_artifact(
            trace_id="trace123",
            prestaged_perms=("perm1", "perm2"),
            environment_metadata={"key": "value"},
            commit_hash="abc123",
            pass_fail=True,
            artifact_bytes=b"artifact",
            key_id="key1",
            enclave=enclave,
        )
        
        assert artifact.trace_id == "trace123"
        assert artifact.signature == "signature123"
        assert artifact.pass_fail is True
        assert artifact.commit_hash == "abc123"

    def test_build_signed_guardian_artifact_signing_failure(self):
        """Test signed guardian artifact building fails on signing error."""
        enclave = MagicMock(spec=SignatureEnclave)
        enclave.sign.side_effect = KeyError("Key not found")
        
        with pytest.raises(crypto_trust_contracts.SignedGuardianError, match="Cannot sign guardian artifact"):
            crypto_trust_contracts.build_signed_guardian_artifact(
                trace_id="trace123",
                prestaged_perms=(),
                environment_metadata={},
                commit_hash="abc123",
                pass_fail=True,
                artifact_bytes=b"artifact",
                key_id="key1",
                enclave=enclave,
            )

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(crypto_trust_contracts, "hash_artifact_canonical")
        assert hasattr(crypto_trust_contracts, "sign_artifact")
        assert hasattr(crypto_trust_contracts, "verify_signature")
        assert hasattr(crypto_trust_contracts, "ReplayGuardStore")
        assert hasattr(crypto_trust_contracts, "record_and_block_replay")
        assert hasattr(crypto_trust_contracts, "record_hash_mismatch")
        assert hasattr(crypto_trust_contracts, "build_signed_guardian_artifact")
