"""REQ-018: all governance artifacts use HMAC-SHA256; signing is deterministic."""

from __future__ import annotations

import hashlib
import hmac

import pytest

from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    hash_artifact_canonical,
    sign_artifact,
    verify_signature,
)
from agentic_core.L0_routing.types.crypto_trust_types import (
    DeterministicTestEnclave,
    KeyRecord,
    KeyStatus,
    SigningAlgorithm,
    TrustRoot,
)

_KEY_ID = "req018-hmac-key"
_KEY_SECRET = b"req018-fixed-hmac-secret-padding!"


def _make_trust_root() -> TrustRoot:
    return TrustRoot(
        keys=(
            KeyRecord(
                key_id=_KEY_ID,
                public_key=_KEY_SECRET,
                created_tick=0,
                status=KeyStatus.ACTIVE,
            ),
        )
    )


@pytest.mark.governance
def test_sign_artifact_uses_hmac_sha256() -> None:
    """SignatureEnvelope.algorithm MUST be HMAC_SHA256."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-001","payload":"run_gate"}'
    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-001", 1)
    assert envelope.algorithm == SigningAlgorithm.HMAC_SHA256


@pytest.mark.governance
def test_sign_artifact_deterministic_across_two_runs() -> None:
    """Two independent sign_artifact calls on identical inputs MUST produce identical signatures."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-002","payload":"determinism_check"}'

    env1 = sign_artifact(artifact, _KEY_ID, enclave, "TR-DET", 42)
    env2 = sign_artifact(artifact, _KEY_ID, enclave, "TR-DET", 42)

    assert env1.signature == env2.signature, "signatures not deterministic across two invocations"
    assert env1.artifact_hash == env2.artifact_hash


@pytest.mark.governance
def test_artifact_hash_is_sha256_hex() -> None:
    """hash_artifact_canonical MUST return lowercase SHA-256 hex (64 chars)."""
    artifact = b"canonical test bytes"
    digest = hash_artifact_canonical(artifact)
    expected = hashlib.sha256(artifact).hexdigest()
    assert digest == expected
    assert len(digest) == 64
    assert digest == digest.lower()


@pytest.mark.governance
def test_signature_is_expected_hmac_hex() -> None:
    """The signature stored in the envelope MUST equal HMAC-SHA256(key, artifact_bytes).hexdigest()."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-003","payload":"hmac_value_check"}'

    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-003", 1)

    expected_sig = hmac.new(_KEY_SECRET, artifact, hashlib.sha256).hexdigest()
    assert envelope.signature == expected_sig


@pytest.mark.governance
def test_verify_signature_round_trip() -> None:
    """sign_artifact followed by verify_signature MUST return True."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"instruction_id":"INS-004","payload":"roundtrip"}'
    envelope = sign_artifact(artifact, _KEY_ID, enclave, "TR-004", 1)
    assert verify_signature(artifact, envelope, trust_root, enclave) is True


@pytest.mark.governance
def test_w2_determinism_digest_format() -> None:
    """SOV-DELTA: phase emits W2-DETERMINISM-DIGEST; two invocations must match."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)
    artifact = b'{"phase":"W2","gate":"determinism"}'
    env_a = sign_artifact(artifact, _KEY_ID, enclave, "W2-DIGEST", 0)
    env_b = sign_artifact(artifact, _KEY_ID, enclave, "W2-DIGEST", 0)
    digest_line_a = f"W2-DETERMINISM-DIGEST: {env_a.signature}"
    digest_line_b = f"W2-DETERMINISM-DIGEST: {env_b.signature}"
    assert digest_line_a == digest_line_b
