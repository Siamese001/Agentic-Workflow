"""Behavioral tests for ``agentic_core.L0_routing.types.crypto_trust_types``.

Covers the P5 Tokenized Authority / Cryptographic Trust artifacts:
- Enum membership: KeyStatus, SigningAlgorithm, HumanResolution.
- KeyRecord validation: non-empty id, non-empty public_key, non-negative tick, type checks.
- TrustRoot duplicate-id detection + get_key lookup semantics.
- SignatureEnvelope required-field validation.
- SignedGuardianArtifact required-field validation + container typing.
- SignedModify required-field validation.
- ReplayGuardRecord / HashMismatchTracker mutable-state semantics + escalation threshold.
- DeterministicTestEnclave: sign/verify round-trip, tampered-signature detection,
  unknown-key handling, revoked-key handling.
"""

from __future__ import annotations

import pytest

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


# ---- Enums ---------------------------------------------------------------


class TestEnums:
    def test_key_status_members(self) -> None:
        assert KeyStatus.ACTIVE.value == "active"
        assert KeyStatus.REVOKED.value == "revoked"

    def test_signing_algorithm_members(self) -> None:
        assert SigningAlgorithm.HMAC_SHA256.value == "hmac-sha256"

    def test_human_resolution_members(self) -> None:
        assert {r.value for r in HumanResolution} == {"APPROVE", "REJECT", "MODIFY"}


# ---- KeyRecord -----------------------------------------------------------


def _kr(**overrides: object) -> KeyRecord:
    kwargs: dict[str, object] = {
        "key_id": "k1",
        "public_key": b"secret-key",
        "created_tick": 0,
        "status": KeyStatus.ACTIVE,
    }
    kwargs.update(overrides)
    return KeyRecord(**kwargs)  # type: ignore[arg-type]


class TestKeyRecord:
    def test_valid(self) -> None:
        kr = _kr()
        assert kr.key_id == "k1"
        assert kr.algorithm is SigningAlgorithm.HMAC_SHA256

    def test_empty_key_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="key_id"):
            _kr(key_id="")

    def test_empty_public_key_rejected(self) -> None:
        with pytest.raises(ValueError, match="public_key"):
            _kr(public_key=b"")

    def test_negative_tick_rejected(self) -> None:
        with pytest.raises(ValueError, match="created_tick"):
            _kr(created_tick=-1)

    def test_bad_status_type_rejected(self) -> None:
        with pytest.raises(TypeError, match="status"):
            _kr(status="active")  # type: ignore[arg-type]

    def test_bad_algorithm_type_rejected(self) -> None:
        with pytest.raises(TypeError, match="algorithm"):
            _kr(algorithm="hmac-sha256")  # type: ignore[arg-type]

    def test_is_frozen(self) -> None:
        kr = _kr()
        with pytest.raises(AttributeError):
            kr.key_id = "other"  # type: ignore[misc]


# ---- TrustRoot -----------------------------------------------------------


class TestTrustRoot:
    def test_valid_empty(self) -> None:
        tr = TrustRoot(keys=())
        assert tr.keys == ()

    def test_valid_with_keys(self) -> None:
        k1, k2 = _kr(key_id="a"), _kr(key_id="b")
        tr = TrustRoot(keys=(k1, k2))
        assert len(tr.keys) == 2

    def test_duplicate_keys_rejected(self) -> None:
        k1, k2 = _kr(key_id="dup"), _kr(key_id="dup")
        with pytest.raises(ValueError, match="duplicate"):
            TrustRoot(keys=(k1, k2))

    def test_non_tuple_rejected(self) -> None:
        with pytest.raises(TypeError, match="tuple"):
            TrustRoot(keys=[_kr()])  # type: ignore[arg-type]

    def test_get_key_hit(self) -> None:
        k = _kr(key_id="found")
        tr = TrustRoot(keys=(k,))
        assert tr.get_key("found") is k

    def test_get_key_miss(self) -> None:
        tr = TrustRoot(keys=(_kr(key_id="a"),))
        assert tr.get_key("missing") is None


# ---- SignatureEnvelope ---------------------------------------------------


def _env(**overrides: object) -> SignatureEnvelope:
    kwargs: dict[str, object] = {
        "trace_id": "t1",
        "artifact_hash": "h1",
        "key_id": "k1",
        "signature": "sig",
        "algorithm": SigningAlgorithm.HMAC_SHA256,
        "semantic_clock_tick": 5,
    }
    kwargs.update(overrides)
    return SignatureEnvelope(**kwargs)  # type: ignore[arg-type]


class TestSignatureEnvelope:
    def test_valid(self) -> None:
        e = _env()
        assert e.semantic_clock_tick == 5

    @pytest.mark.parametrize(
        "field",
        ["trace_id", "artifact_hash", "key_id", "signature"],
    )
    def test_empty_string_field_rejected(self, field: str) -> None:
        with pytest.raises(ValueError, match=field):
            _env(**{field: ""})

    def test_negative_tick_rejected(self) -> None:
        with pytest.raises(ValueError, match="semantic_clock_tick"):
            _env(semantic_clock_tick=-1)

    def test_bad_algorithm_rejected(self) -> None:
        with pytest.raises(TypeError, match="algorithm"):
            _env(algorithm="hmac-sha256")  # type: ignore[arg-type]


# ---- SignedGuardianArtifact ---------------------------------------------


def _sga(**overrides: object) -> SignedGuardianArtifact:
    kwargs: dict[str, object] = {
        "trace_id": "t1",
        "signature": "sig",
        "prestaged_perms": ("read", "write"),
        "environment_metadata": {"env": "test"},
        "commit_hash": "abc123",
        "pass_fail": True,
    }
    kwargs.update(overrides)
    return SignedGuardianArtifact(**kwargs)  # type: ignore[arg-type]


class TestSignedGuardianArtifact:
    def test_valid(self) -> None:
        a = _sga()
        assert a.pass_fail is True

    @pytest.mark.parametrize("field", ["trace_id", "signature", "commit_hash"])
    def test_empty_required_field(self, field: str) -> None:
        with pytest.raises(ValueError, match=field):
            _sga(**{field: ""})

    def test_prestaged_perms_must_be_tuple(self) -> None:
        with pytest.raises(TypeError, match="prestaged_perms"):
            _sga(prestaged_perms=["read"])  # type: ignore[arg-type]

    def test_environment_metadata_must_be_dict(self) -> None:
        with pytest.raises(TypeError, match="environment_metadata"):
            _sga(environment_metadata=[("env", "test")])  # type: ignore[arg-type]


# ---- SignedModify --------------------------------------------------------


class TestSignedModify:
    def _base(self, **overrides: object) -> SignedModify:
        kwargs: dict[str, object] = {
            "trace_id": "t1",
            "human_reviewer_id": "reviewer-1",
            "resolution": HumanResolution.MODIFY,
            "modified_manifest": "manifest-body",
            "signature": "sig",
        }
        kwargs.update(overrides)
        return SignedModify(**kwargs)  # type: ignore[arg-type]

    def test_valid(self) -> None:
        m = self._base()
        assert m.resolution is HumanResolution.MODIFY

    @pytest.mark.parametrize(
        "field",
        ["trace_id", "human_reviewer_id", "modified_manifest", "signature"],
    )
    def test_empty_required_field(self, field: str) -> None:
        with pytest.raises(ValueError, match=field):
            self._base(**{field: ""})

    def test_bad_resolution_type(self) -> None:
        with pytest.raises(TypeError, match="resolution"):
            self._base(resolution="APPROVE")  # type: ignore[arg-type]


# ---- ReplayGuardRecord ---------------------------------------------------


class TestReplayGuardRecord:
    def test_valid_defaults(self) -> None:
        r = ReplayGuardRecord(artifact_hash="h", first_seen_tick=0)
        assert r.seen_count == 1

    def test_empty_hash_rejected(self) -> None:
        with pytest.raises(ValueError, match="artifact_hash"):
            ReplayGuardRecord(artifact_hash="", first_seen_tick=0)

    def test_negative_tick_rejected(self) -> None:
        with pytest.raises(ValueError, match="first_seen_tick"):
            ReplayGuardRecord(artifact_hash="h", first_seen_tick=-1)

    def test_zero_seen_count_rejected(self) -> None:
        with pytest.raises(ValueError, match="seen_count"):
            ReplayGuardRecord(artifact_hash="h", first_seen_tick=0, seen_count=0)

    def test_seen_count_mutable(self) -> None:
        r = ReplayGuardRecord(artifact_hash="h", first_seen_tick=0)
        r.seen_count = 5
        assert r.seen_count == 5


# ---- HashMismatchTracker -------------------------------------------------


class TestHashMismatchTracker:
    def test_defaults(self) -> None:
        t = HashMismatchTracker(wave_id="w1")
        assert t.mismatch_count == 0
        assert t.escalation_threshold == 2
        assert t.escalated is False

    def test_empty_wave_id_rejected(self) -> None:
        with pytest.raises(ValueError, match="wave_id"):
            HashMismatchTracker(wave_id="")

    def test_single_mismatch_no_escalation(self) -> None:
        t = HashMismatchTracker(wave_id="w1")
        assert t.record_mismatch() is False
        assert t.mismatch_count == 1
        assert t.escalated is False

    def test_threshold_triggers_escalation(self) -> None:
        t = HashMismatchTracker(wave_id="w1")
        t.record_mismatch()
        assert t.record_mismatch() is True  # 2nd mismatch = escalate
        assert t.escalated is True
        assert t.mismatch_count == 2

    def test_custom_threshold(self) -> None:
        t = HashMismatchTracker(wave_id="w1", escalation_threshold=3)
        assert t.record_mismatch() is False
        assert t.record_mismatch() is False
        assert t.record_mismatch() is True

    def test_once_escalated_stays_escalated(self) -> None:
        t = HashMismatchTracker(wave_id="w1")
        t.record_mismatch()
        t.record_mismatch()
        assert t.record_mismatch() is True  # still escalated on further mismatches
        assert t.escalated is True


# ---- DeterministicTestEnclave -------------------------------------------


@pytest.fixture
def trust_root() -> TrustRoot:
    return TrustRoot(
        keys=(
            KeyRecord(
                key_id="active-1",
                public_key=b"super-secret-active-key",
                created_tick=0,
                status=KeyStatus.ACTIVE,
            ),
            KeyRecord(
                key_id="revoked-1",
                public_key=b"super-secret-revoked-key",
                created_tick=1,
                status=KeyStatus.REVOKED,
            ),
        ),
    )


class TestDeterministicTestEnclave:
    def test_sign_verify_roundtrip(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        payload = b"artifact-bytes"
        sig = enclave.sign(payload, "active-1")
        assert enclave.verify(payload, sig, "active-1") is True

    def test_sign_is_deterministic(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        payload = b"payload"
        sig1 = enclave.sign(payload, "active-1")
        sig2 = enclave.sign(payload, "active-1")
        assert sig1 == sig2

    def test_verify_rejects_tampered(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        sig = enclave.sign(b"original", "active-1")
        assert enclave.verify(b"tampered", sig, "active-1") is False

    def test_verify_rejects_bad_signature(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        assert enclave.verify(b"payload", "deadbeef", "active-1") is False

    def test_sign_unknown_key_raises(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        with pytest.raises(KeyError, match="unknown key_id"):
            enclave.sign(b"x", "missing")

    def test_sign_revoked_key_raises(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        with pytest.raises(PermissionError, match="REVOKED"):
            enclave.sign(b"x", "revoked-1")

    def test_verify_unknown_key_returns_false(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        assert enclave.verify(b"x", "abc", "missing") is False

    def test_verify_revoked_key_returns_false(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        # Even if signature would match, revoked keys never verify
        assert enclave.verify(b"x", "whatever", "revoked-1") is False

    def test_get_key_record_delegates(self, trust_root: TrustRoot) -> None:
        enclave = DeterministicTestEnclave(trust_root)
        assert enclave.get_key_record("active-1") is not None
        assert enclave.get_key_record("missing") is None
