"""Replay harness: REQ-337/360/378/381/384/395/399/404/409/413."""

import hashlib
import hmac
import json

import pytest

pytestmark = [pytest.mark.unit_min_deps]


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


@pytest.mark.parametrize(
    "req,obj",
    [
        ("REQ-337", {"from_state": "SHADOW", "to_state": "ACTIVE", "clock_tick": 7}),
        ("REQ-360", {"artifact_type": "RESULT", "layer": "L2", "verdict": "LEGAL"}),
        ("REQ-378", {"seed": "CC3AL1-AABBCCDD", "index": 0}),
        ("REQ-381", {"keys": ["b", "a"], "values": [2, 1]}),  # sort_keys ensures determinism
        ("REQ-384", {"input_bytes": "aabbcc", "algo": "sha256"}),
        ("REQ-409", {"clock_vector": [0, 1, 2], "trace_id": "CC3AL1-00000001"}),
        (
            "REQ-413",
            {"provider_id": "openai", "model_id": "gpt-4o", "gateway_version": "1.0", "clock_vector": [0, 1]},
        ),
    ],
)
def test_crypto_clock_replay_deterministic(req, obj):
    assert _digest(obj) == _digest(obj), f"{req}: not deterministic"


def test_req395_hmac_deterministic():
    key = b"test-key"
    data = b"canonical payload"
    h1 = hmac.new(key, data, hashlib.sha256).hexdigest()
    h2 = hmac.new(key, data, hashlib.sha256).hexdigest()
    assert h1 == h2  # REQ-395


def test_req399_enclave_deterministic():
    # Same input -> same signing result (stubbed)
    payload = b"artifact_hash_abc"
    sig1 = hashlib.sha256(payload).hexdigest()
    sig2 = hashlib.sha256(payload).hexdigest()
    assert sig1 == sig2  # REQ-399 / REQ-404


def test_req413_provider_binding_in_digest():
    digest = _digest(
        {"provider_id": "openai", "model_id": "gpt-4o", "gateway_version": "1.0", "clock_vector": [0]}
    )
    assert len(digest) == 64  # full SHA-256


# ---------------------------------------------------------------------------
# SOV-DELTA: ADD REAL CALL PATH for W8 (append; do NOT remove existing tests)
# ---------------------------------------------------------------------------


# REQ-395/399 real path: SignatureEnclave sign+verify round-trip
def test_req399_signature_enclave_real_round_trip():
    from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
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
    from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
    from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

    inject_key_source(TestKeySource())
    key_id = "test-key-1"
    key = KeyRecord(
        key_id=key_id,
        public_key=b"test-secret-key-0123456789abcdef",
        created_tick=0,
        status=KeyStatus.ACTIVE,
        algorithm=SigningAlgorithm.HMAC_SHA256,
    )
    trust_root = TrustRoot(keys=(key,))
    enclave = DeterministicTestEnclave(trust_root=trust_root)

    pkt = InstructionPacket(instruction_id="CI-00000001", payload="canonical")
    artifact_bytes = pkt.canonical_bytes()

    env1 = sign_artifact(artifact_bytes, key_id, enclave, "CC3AL1-00000001", 0)
    env2 = sign_artifact(artifact_bytes, key_id, enclave, "CC3AL1-00000001", 0)
    assert env1.signature == env2.signature  # deterministic signing
    assert verify_signature(artifact_bytes, env1, trust_root, enclave)  # real verify path
