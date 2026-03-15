"""
V15 P5 Compliance Tests — Cryptographic Trust & Signing.

Regression tests proving all 7 P5 items are COMPLIANT:
  §7.4.1 — SignatureEnclave interface (deterministic, no wall-clock)
  §7.4.2 — Pinned Public Keys / TrustRoot
  §7.4   — Signed artifact (SignatureEnvelope)
  §7.2.1 — SignedGuardianArtifact (all required fields)
  §1.7   — SignedModify artifact
  §7.2   — Artifact Guard (replay + signature verification)
  §2.6   — ≥2 hash mismatches → human escalation
"""

from __future__ import annotations

import dataclasses
import hashlib

import pytest

from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
    EscalationRequiredError,
    ReplayDetectedError,
    ReplayGuardStore,
    SignedGuardianError,
    SigningError,
    VerificationError,
    build_signed_guardian_artifact,
    hash_artifact_canonical,
    record_and_block_replay,
    record_hash_mismatch,
    sign_artifact,
    verify_signature,
)
from agentic_core.L0_routing.types.crypto_trust_types import (
    DeterministicTestEnclave,
    HashMismatchTracker,
    HumanResolution,
    KeyRecord,
    KeyStatus,
    ReplayGuardRecord,
    SignatureEnvelope,
    SignedGuardianArtifact,
    SignedModify,
    SigningAlgorithm,
    TrustRoot,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ---- fixtures ---------------------------------------------------------------

FIXED_KEY = b"test-key-material-32-bytes-long!!"
FIXED_KEY_ID = "key-001"

ACTIVE_KEY = KeyRecord(
    key_id=FIXED_KEY_ID,
    public_key=FIXED_KEY,
    created_tick=0,
    status=KeyStatus.ACTIVE,
)

REVOKED_KEY = KeyRecord(
    key_id="key-revoked",
    public_key=b"revoked-key-material-32-bytes!!",
    created_tick=0,
    status=KeyStatus.REVOKED,
)

TEST_TRUST_ROOT = TrustRoot(keys=(ACTIVE_KEY, REVOKED_KEY))
TEST_ENCLAVE = DeterministicTestEnclave(TEST_TRUST_ROOT)

SAMPLE_BYTES = b'{"agent": "StructureHealerAgent", "result": "PASS"}'


# =============================================================================
# §7.4.1 — SignatureEnclave Interface
# =============================================================================


class TestP5_741_SignatureEnclave:
    """§7.4.1: Enclave is deterministic, no wall-clock, no env reads."""

    def test_sign_deterministic(self):
        sig1 = TEST_ENCLAVE.sign(SAMPLE_BYTES, FIXED_KEY_ID)
        sig2 = TEST_ENCLAVE.sign(SAMPLE_BYTES, FIXED_KEY_ID)
        assert sig1 == sig2

    def test_sign_different_bytes_different_sig(self):
        sig1 = TEST_ENCLAVE.sign(b"data-a", FIXED_KEY_ID)
        sig2 = TEST_ENCLAVE.sign(b"data-b", FIXED_KEY_ID)
        assert sig1 != sig2

    def test_sign_unknown_key_raises(self):
        with pytest.raises(KeyError, match="unknown"):
            TEST_ENCLAVE.sign(SAMPLE_BYTES, "nonexistent-key")

    def test_sign_revoked_key_raises(self):
        with pytest.raises(PermissionError, match="REVOKED"):
            TEST_ENCLAVE.sign(SAMPLE_BYTES, "key-revoked")

    def test_verify_valid(self):
        sig = TEST_ENCLAVE.sign(SAMPLE_BYTES, FIXED_KEY_ID)
        assert TEST_ENCLAVE.verify(SAMPLE_BYTES, sig, FIXED_KEY_ID) is True

    def test_verify_wrong_bytes(self):
        sig = TEST_ENCLAVE.sign(SAMPLE_BYTES, FIXED_KEY_ID)
        assert TEST_ENCLAVE.verify(b"tampered", sig, FIXED_KEY_ID) is False

    def test_verify_wrong_sig(self):
        assert TEST_ENCLAVE.verify(SAMPLE_BYTES, "bad-sig", FIXED_KEY_ID) is False

    def test_verify_unknown_key(self):
        sig = TEST_ENCLAVE.sign(SAMPLE_BYTES, FIXED_KEY_ID)
        assert TEST_ENCLAVE.verify(SAMPLE_BYTES, sig, "no-such-key") is False

    def test_verify_revoked_key(self):
        assert TEST_ENCLAVE.verify(SAMPLE_BYTES, "any-sig", "key-revoked") is False

    def test_get_key_record(self):
        rec = TEST_ENCLAVE.get_key_record(FIXED_KEY_ID)
        assert rec is not None
        assert rec.key_id == FIXED_KEY_ID
        assert rec.status == KeyStatus.ACTIVE


# =============================================================================
# §7.4.2 — TrustRoot / KeyRecord
# =============================================================================


class TestP5_742_TrustRoot:
    """§7.4.2: Pinned public keys in trust root."""

    def test_key_record_fields(self):
        required = {"key_id", "public_key", "created_tick", "status", "algorithm"}
        actual = {f.name for f in dataclasses.fields(KeyRecord)}
        assert required.issubset(actual)

    def test_key_record_frozen(self):
        with pytest.raises(dataclasses.FrozenInstanceError):
            ACTIVE_KEY.key_id = "x"  # type: ignore[misc]

    def test_trust_root_frozen(self):
        with pytest.raises(dataclasses.FrozenInstanceError):
            TEST_TRUST_ROOT.keys = ()  # type: ignore[misc]

    def test_trust_root_get_key(self):
        assert TEST_TRUST_ROOT.get_key(FIXED_KEY_ID) is ACTIVE_KEY
        assert TEST_TRUST_ROOT.get_key("nonexistent") is None

    def test_trust_root_rejects_duplicate_ids(self):
        dup = KeyRecord(
            key_id=FIXED_KEY_ID,
            public_key=b"other",
            created_tick=0,
            status=KeyStatus.ACTIVE,
        )
        with pytest.raises(ValueError, match="duplicate"):
            TrustRoot(keys=(ACTIVE_KEY, dup))

    def test_empty_key_id_rejected(self):
        with pytest.raises(ValueError, match="key_id"):
            KeyRecord(
                key_id="",
                public_key=b"k",
                created_tick=0,
                status=KeyStatus.ACTIVE,
            )

    def test_empty_public_key_rejected(self):
        with pytest.raises(ValueError, match="public_key"):
            KeyRecord(
                key_id="k1",
                public_key=b"",
                created_tick=0,
                status=KeyStatus.ACTIVE,
            )


# =============================================================================
# §7.4 — sign_artifact → SignatureEnvelope
# =============================================================================


class TestP5_74_SignArtifact:
    """§7.4: Signing produces deterministic envelope."""

    def test_sign_produces_envelope(self):
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 5)
        assert isinstance(env, SignatureEnvelope)
        assert env.trace_id == "t1"
        assert env.key_id == FIXED_KEY_ID
        assert env.semantic_clock_tick == 5

    def test_envelope_artifact_hash_matches(self):
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        expected = hashlib.sha256(SAMPLE_BYTES).hexdigest()
        assert env.artifact_hash == expected

    def test_sign_deterministic(self):
        e1 = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        e2 = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        assert e1.signature == e2.signature

    def test_sign_unknown_key_fails(self):
        with pytest.raises(SigningError, match="FAIL"):
            sign_artifact(SAMPLE_BYTES, "bad-key", TEST_ENCLAVE, "t1", 0)

    def test_sign_revoked_key_fails(self):
        with pytest.raises(SigningError, match="FAIL"):
            sign_artifact(SAMPLE_BYTES, "key-revoked", TEST_ENCLAVE, "t1", 0)

    def test_envelope_frozen(self):
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            env.signature = "x"  # type: ignore[misc]

    def test_envelope_fields(self):
        required = {
            "trace_id",
            "artifact_hash",
            "key_id",
            "signature",
            "algorithm",
            "semantic_clock_tick",
        }
        actual = {f.name for f in dataclasses.fields(SignatureEnvelope)}
        assert required.issubset(actual)


# =============================================================================
# §7.4.2 — verify_signature
# =============================================================================


class TestP5_742_VerifySignature:
    """§7.4.2: Verification fails closed on any mismatch."""

    def test_valid_signature_passes(self):
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        assert (
            verify_signature(
                SAMPLE_BYTES,
                env,
                TEST_TRUST_ROOT,
                TEST_ENCLAVE,
            )
            is True
        )

    def test_tampered_bytes_fails(self):
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        with pytest.raises(VerificationError, match="artifact_hash mismatch"):
            verify_signature(b"tampered", env, TEST_TRUST_ROOT, TEST_ENCLAVE)

    def test_unknown_key_fails(self):
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        empty_root = TrustRoot(keys=())
        with pytest.raises(VerificationError, match="Unknown key_id"):
            verify_signature(SAMPLE_BYTES, env, empty_root, TEST_ENCLAVE)

    def test_revoked_key_fails(self):
        # Manually construct envelope with revoked key
        env = SignatureEnvelope(
            trace_id="t1",
            artifact_hash=hash_artifact_canonical(SAMPLE_BYTES),
            key_id="key-revoked",
            signature="fake",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=0,
        )
        with pytest.raises(VerificationError, match="REVOKED"):
            verify_signature(SAMPLE_BYTES, env, TEST_TRUST_ROOT, TEST_ENCLAVE)

    def test_wrong_signature_fails(self):
        env = SignatureEnvelope(
            trace_id="t1",
            artifact_hash=hash_artifact_canonical(SAMPLE_BYTES),
            key_id=FIXED_KEY_ID,
            signature="definitely-wrong-signature",
            algorithm=SigningAlgorithm.HMAC_SHA256,
            semantic_clock_tick=0,
        )
        with pytest.raises(VerificationError, match="Signature verification failed"):
            verify_signature(SAMPLE_BYTES, env, TEST_TRUST_ROOT, TEST_ENCLAVE)


# =============================================================================
# §7.2 — Replay Guard
# =============================================================================


class TestP5_72_ReplayGuard:
    """§7.2: Replay guard fails closed on second sighting."""

    def test_first_sighting_passes(self):
        store = ReplayGuardStore()
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        assert record_and_block_replay(env, store) is True

    def test_second_sighting_blocked(self):
        store = ReplayGuardStore()
        env = sign_artifact(SAMPLE_BYTES, FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        record_and_block_replay(env, store)
        with pytest.raises(ReplayDetectedError, match="Replay detected"):
            record_and_block_replay(env, store)

    def test_different_artifacts_not_replay(self):
        store = ReplayGuardStore()
        e1 = sign_artifact(b"data-1", FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        e2 = sign_artifact(b"data-2", FIXED_KEY_ID, TEST_ENCLAVE, "t2", 1)
        record_and_block_replay(e1, store)
        assert record_and_block_replay(e2, store) is True

    def test_replay_guard_record_count(self):
        store = ReplayGuardStore()
        e1 = sign_artifact(b"a", FIXED_KEY_ID, TEST_ENCLAVE, "t1", 0)
        e2 = sign_artifact(b"b", FIXED_KEY_ID, TEST_ENCLAVE, "t2", 1)
        record_and_block_replay(e1, store)
        record_and_block_replay(e2, store)
        assert store.record_count == 2

    def test_replay_guard_record_fields(self):
        required = {"artifact_hash", "first_seen_tick", "seen_count"}
        actual = {f.name for f in dataclasses.fields(ReplayGuardRecord)}
        assert required.issubset(actual)


# =============================================================================
# §7.2.1 — SignedGuardianArtifact
# =============================================================================


class TestP5_721_SignedGuardianArtifact:
    """§7.2.1: Signed guardian artifact with all required fields."""

    def test_all_required_fields(self):
        required = {
            "trace_id",
            "signature",
            "prestaged_perms",
            "environment_metadata",
            "commit_hash",
            "pass_fail",
        }
        actual = {f.name for f in dataclasses.fields(SignedGuardianArtifact)}
        assert required.issubset(actual)

    def test_frozen(self):
        art = build_signed_guardian_artifact(
            trace_id="t1",
            prestaged_perms=("read", "write"),
            environment_metadata={"os": "linux", "python": "3.11"},
            commit_hash="abc123",
            pass_fail=True,
            artifact_bytes=SAMPLE_BYTES,
            key_id=FIXED_KEY_ID,
            enclave=TEST_ENCLAVE,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            art.trace_id = "x"  # type: ignore[misc]

    def test_builds_valid(self):
        art = build_signed_guardian_artifact(
            trace_id="t1",
            prestaged_perms=("read",),
            environment_metadata={"os": "win"},
            commit_hash="def456",
            pass_fail=False,
            artifact_bytes=SAMPLE_BYTES,
            key_id=FIXED_KEY_ID,
            enclave=TEST_ENCLAVE,
        )
        assert art.trace_id == "t1"
        assert art.pass_fail is False
        assert len(art.signature) > 0

    def test_revoked_key_fails(self):
        with pytest.raises(SignedGuardianError, match="FAIL"):
            build_signed_guardian_artifact(
                trace_id="t1",
                prestaged_perms=(),
                environment_metadata={},
                commit_hash="abc",
                pass_fail=True,
                artifact_bytes=SAMPLE_BYTES,
                key_id="key-revoked",
                enclave=TEST_ENCLAVE,
            )

    def test_empty_trace_id_rejected(self):
        with pytest.raises(SignedGuardianError, match="FAIL"):
            build_signed_guardian_artifact(
                trace_id="",
                prestaged_perms=(),
                environment_metadata={},
                commit_hash="abc",
                pass_fail=True,
                artifact_bytes=SAMPLE_BYTES,
                key_id=FIXED_KEY_ID,
                enclave=TEST_ENCLAVE,
            )


# =============================================================================
# §1.7 — SignedModify Artifact
# =============================================================================


class TestP5_17_SignedModify:
    """§1.7 / §2.7.1: SignedModify artifact for human MODIFY resolution."""

    def test_all_required_fields(self):
        required = {
            "trace_id",
            "human_reviewer_id",
            "resolution",
            "modified_manifest",
            "signature",
        }
        actual = {f.name for f in dataclasses.fields(SignedModify)}
        assert required.issubset(actual)

    def test_frozen(self):
        sm = SignedModify(
            trace_id="t1",
            human_reviewer_id="reviewer-1",
            resolution=HumanResolution.MODIFY,
            modified_manifest="new manifest",
            signature="sig-001",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            sm.trace_id = "x"  # type: ignore[misc]

    def test_valid_construction(self):
        sm = SignedModify(
            trace_id="t1",
            human_reviewer_id="reviewer-1",
            resolution=HumanResolution.APPROVE,
            modified_manifest="manifest-data",
            signature="sig-001",
        )
        assert sm.resolution == HumanResolution.APPROVE

    def test_empty_trace_id_rejected(self):
        with pytest.raises(ValueError, match="trace_id"):
            SignedModify(
                trace_id="",
                human_reviewer_id="r1",
                resolution=HumanResolution.REJECT,
                modified_manifest="m",
                signature="s",
            )

    def test_empty_signature_rejected(self):
        with pytest.raises(ValueError, match="signature"):
            SignedModify(
                trace_id="t1",
                human_reviewer_id="r1",
                resolution=HumanResolution.MODIFY,
                modified_manifest="m",
                signature="",
            )

    def test_resolution_enum_values(self):
        assert HumanResolution.APPROVE.value == "APPROVE"
        assert HumanResolution.REJECT.value == "REJECT"
        assert HumanResolution.MODIFY.value == "MODIFY"


# =============================================================================
# §2.6 — Hash Mismatch Escalation
# =============================================================================


class TestP5_26_HashMismatchEscalation:
    """§2.6: ≥2 hash mismatches in a wave forces human escalation."""

    def test_first_mismatch_no_escalation(self):
        tracker = HashMismatchTracker(wave_id="w1")
        assert record_hash_mismatch(tracker) is False
        assert tracker.mismatch_count == 1
        assert tracker.escalated is False

    def test_second_mismatch_triggers_escalation(self):
        tracker = HashMismatchTracker(wave_id="w1")
        record_hash_mismatch(tracker)
        with pytest.raises(EscalationRequiredError, match="Human escalation"):
            record_hash_mismatch(tracker)
        assert tracker.escalated is True

    def test_custom_threshold(self):
        tracker = HashMismatchTracker(wave_id="w1", escalation_threshold=THRESHOLD)
        record_hash_mismatch(tracker)
        record_hash_mismatch(tracker)
        assert tracker.escalated is False
        with pytest.raises(EscalationRequiredError):
            record_hash_mismatch(tracker)

    def test_empty_wave_id_rejected(self):
        with pytest.raises(ValueError, match="wave_id"):
            HashMismatchTracker(wave_id="")


# =============================================================================
# Canonical Hashing
# =============================================================================


class TestP5_CanonicalHash:
    """Canonical hashing is SHA-256, deterministic."""

    def test_deterministic(self):
        h1 = hash_artifact_canonical(SAMPLE_BYTES)
        h2 = hash_artifact_canonical(SAMPLE_BYTES)
        assert h1 == h2

    def test_matches_stdlib(self):
        h = hash_artifact_canonical(SAMPLE_BYTES)
        assert h == hashlib.sha256(SAMPLE_BYTES).hexdigest()

    def test_different_bytes_different_hash(self):
        h1 = hash_artifact_canonical(b"a")
        h2 = hash_artifact_canonical(b"b")
        assert h1 != h2
